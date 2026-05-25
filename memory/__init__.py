"""
Memory module for TARS.
Handles PostgreSQL, Qdrant, and Redis connections and operations.
"""
from .postgres import init_db
from .memory import init_qdrant
from .session import init_redis

def init_all():
    """Initialize all memory stores."""
    init_db()
    init_qdrant()
    init_redis()
