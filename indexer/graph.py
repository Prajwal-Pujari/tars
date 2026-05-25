import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_driver = None

def init_neo4j():
    global _driver
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "tars2024")
    try:
        _driver = GraphDatabase.driver(uri, auth=(user, password))
        # Verify connection
        _driver.verify_connectivity()
        logger.info("Neo4j connected successfully.")
    except Exception as e:
        logger.warning(f"Failed to connect to Neo4j: {e}")

def get_driver():
    if not _driver:
        init_neo4j()
    return _driver

def create_call_relationship(caller, callee, file_path):
    """Create a CALLS relationship between two functions in Neo4j."""
    driver = get_driver()
    if not driver:
        return
        
    query = """
    MERGE (c1:Function {name: $caller})
    MERGE (c2:Function {name: $callee})
    MERGE (c1)-[r:CALLS {file: $file_path}]->(c2)
    """
    try:
        with driver.session() as session:
            session.run(query, caller=caller, callee=callee, file_path=file_path)
            logger.debug(f"Created Neo4j relationship: {caller} -> {callee}")
    except Exception as e:
        logger.error(f"Error creating Neo4j relationship: {e}")
