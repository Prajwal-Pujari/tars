import os
import time
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Connection pool
_pool = None

def init_db():
    """Initialize PostgreSQL connection pool and create tables with retry logic."""
    global _pool
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            _pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                user=os.getenv("POSTGRES_USER", "tars"),
                password=os.getenv("POSTGRES_PASSWORD", "tars2024"),
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                database=os.getenv("POSTGRES_DB", "tars")
            )
            logger.info("PostgreSQL connection pool created successfully.")
            
            # Create tables if they don't exist
            create_tables()
            return
        except psycopg2.OperationalError as e:
            logger.warning(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                logger.error("Failed to connect to PostgreSQL after multiple attempts.")
                raise
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL pool: {e}")
            raise

def get_connection():
    """Get a connection from the pool."""
    if not _pool:
        init_db()
    return _pool.getconn()

def release_connection(conn):
    """Release a connection back to the pool."""
    if _pool and conn:
        _pool.putconn(conn)

def execute_query(query, params=None, commit=True):
    """Execute a query (INSERT, UPDATE, DELETE)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if commit:
                conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error executing query: {e}")
        raise
    finally:
        release_connection(conn)

def fetch_all(query, params=None):
    """Fetch all results for a query."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise
    finally:
        release_connection(conn)

def fetch_one(query, params=None):
    """Fetch a single result for a query."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise
    finally:
        release_connection(conn)

def create_tables():
    """Create necessary tables."""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS agent_logs (
            id SERIAL PRIMARY KEY,
            agent_name VARCHAR(50) NOT NULL,
            action TEXT NOT NULL,
            details JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS personality_profiles (
            id SERIAL PRIMARY KEY,
            mode VARCHAR(50) UNIQUE NOT NULL,
            honesty_level INT DEFAULT 90,
            humor_level INT DEFAULT 70,
            verbosity INT DEFAULT 60
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS project_config (
            key VARCHAR(100) PRIMARY KEY,
            value JSONB NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    for table_query in tables:
        execute_query(table_query)
    logger.info("PostgreSQL tables checked/created.")
