import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_driver = None

def init_neo4j():
    global _driver
    uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
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

def get_graph_data():
    """Retrieve all nodes and links from Neo4j in a format ready for 3d-force-graph."""
    driver = get_driver()
    if not driver:
        return {"nodes": [], "links": []}
        
    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    
    nodes = {}
    links = []
    
    try:
        with driver.session() as session:
            result = session.run(query)
            for record in result:
                # Add source node
                n = record["n"]
                if n and n.get("name") not in nodes:
                    nodes[n.get("name")] = {"id": n.get("name"), "group": 1, "val": 2}
                
                # Add target node
                m = record["m"]
                if m and m.get("name") not in nodes:
                    nodes[m.get("name")] = {"id": m.get("name"), "group": 2, "val": 2}
                    
                # Add relationship link
                r = record["r"]
                if n and m and r:
                    links.append({
                        "source": n.get("name"),
                        "target": m.get("name")
                    })
                    
        return {
            "nodes": list(nodes.values()),
            "links": links
        }
    except Exception as e:
        logger.error(f"Error retrieving Neo4j graph data: {e}")
        return {"nodes": [], "links": []}
