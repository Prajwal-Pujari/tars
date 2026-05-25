import os
import argparse
import logging
from indexer.parser import extract_functions
from indexer.graph import create_call_relationship
from memory.memory import store_memory
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def index_file(file_path):
    """Index a single file into Qdrant and Neo4j."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Store entire file in Qdrant
        store_memory(
            collection_name="codebase", 
            text=content, 
            metadata={"file": file_path, "type": "file"}
        )
        
        # 2. Extract functions and store AST segments
        funcs = extract_functions(file_path)
        for func in funcs:
            store_memory(
                collection_name="codebase", 
                text=func["body"], 
                metadata={
                    "file": file_path, 
                    "type": "function", 
                    "name": func["name"]
                }
            )
            
            # 3. If there were explicit calls found, update Neo4j
            # create_call_relationship(func["name"], "some_called_func", file_path)
            
        logger.info(f"Successfully indexed: {file_path}")
    except Exception as e:
        logger.error(f"Error indexing {file_path}: {e}")

def index_project(path):
    """Traverse and index an entire project directory."""
    logger.info(f"Starting indexing for project at {path}")
    
    valid_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.rs', '.go']
    ignore_dirs = ['venv', '.git', '__pycache__', 'node_modules', 'dist', 'build']
    
    for root, dirs, files in os.walk(path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in valid_extensions:
                file_path = os.path.join(root, file)
                index_file(file_path)
                
    logger.info("Project indexing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index a codebase for TARS.")
    parser.add_argument("--path", type=str, default=".", help="Path to project directory")
    args = parser.parse_args()
    
    # Configure basic logging for CLI usage
    logging.basicConfig(level=logging.INFO)
    index_project(args.path)
