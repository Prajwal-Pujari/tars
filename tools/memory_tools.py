import json
from memory.memory import store_memory, search_memory
from memory.postgres import execute_query

def log_agent_action(agent_name, action, details):
    """Log an agent action to PostgreSQL."""
    query = "INSERT INTO agent_logs (agent_name, action, details) VALUES (%s, %s, %s)"
    execute_query(query, (agent_name, action, json.dumps(details)))

def search_codebase(query):
    """Search the codebase semantic index in Qdrant."""
    return search_memory("codebase", query)
    
def store_memory_tool(text, collection, metadata=None):
    """Expose memory storage as a tool."""
    return store_memory(collection, text, metadata)
