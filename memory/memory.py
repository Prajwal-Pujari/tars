import os
import time
import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
import uuid

load_dotenv()

logger = logging.getLogger(__name__)

# Qdrant client
_qdrant_client = None
_embeddings_model = None

COLLECTIONS = [
    "conversations",
    "codebase",
    "documents",
    "decisions",
    "agent_logs"
]

def init_qdrant():
    """Initialize Qdrant client and collections with retry logic."""
    global _qdrant_client, _embeddings_model
    max_retries = 5
    retry_delay = 5
    
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
        
    for attempt in range(max_retries):
        try:
            _qdrant_client = QdrantClient(host=host, port=port)
            # Ping Qdrant to ensure it's up
            _qdrant_client.get_collections()
            logger.info("Qdrant client initialized.")

            # Initialize Ollama embeddings
            model_name = os.getenv("EMBED_MODEL", "bge-m3")
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            _embeddings_model = OllamaEmbeddings(
                model=model_name,
                base_url=ollama_url
            )
            logger.info(f"Ollama embeddings model '{model_name}' initialized.")

            # Ensure collections exist
            vector_size = 1024 
            
            for collection in COLLECTIONS:
                if not _qdrant_client.collection_exists(collection_name=collection):
                    _qdrant_client.create_collection(
                        collection_name=collection,
                        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                    )
                    logger.info(f"Created Qdrant collection: {collection}")
                else:
                    logger.debug(f"Qdrant collection {collection} already exists.")
            return
                    
        except Exception as e:
            logger.warning(f"Qdrant not ready or Ollama not reachable (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                logger.error("Failed to connect to Qdrant after multiple attempts.")
                raise
            time.sleep(retry_delay)

def get_qdrant_client():
    if not _qdrant_client:
        init_qdrant()
    return _qdrant_client

def get_embeddings_model():
    if not _embeddings_model:
        init_qdrant()
    return _embeddings_model

def store_memory(collection_name, text, metadata=None):
    """Embed text and store in Qdrant collection."""
    if collection_name not in COLLECTIONS:
        raise ValueError(f"Invalid collection: {collection_name}")
        
    client = get_qdrant_client()
    embedder = get_embeddings_model()
    
    try:
        vector = embedder.embed_query(text)
        point_id = str(uuid.uuid4())
        
        payload = metadata or {}
        payload["text"] = text
        
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        logger.debug(f"Stored memory in {collection_name} with id {point_id}")
        return point_id
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise

def search_memory(collection_name, query_text, limit=5, filter_dict=None):
    """Search Qdrant collection by semantic meaning."""
    if collection_name not in COLLECTIONS:
        raise ValueError(f"Invalid collection: {collection_name}")
        
    client = get_qdrant_client()
    embedder = get_embeddings_model()
    
    try:
        query_vector = embedder.embed_query(query_text)
        
        qdrant_filter = None
        if filter_dict:
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter_dict.items()
            ]
            qdrant_filter = Filter(must=conditions)
            
        search_result = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=qdrant_filter
        )
        
        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in search_result
        ]
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        return []
