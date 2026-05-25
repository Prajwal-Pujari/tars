import os
import json
import time
import redis
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Redis client
_redis_client = None

def init_redis():
    """Initialize Redis connection with retry logic."""
    global _redis_client
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            _redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=0,
                decode_responses=True
            )
            # Test connection
            _redis_client.ping()
            logger.info("Redis connected successfully.")
            return
        except redis.ConnectionError as e:
            logger.warning(f"Redis not ready (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                logger.error("Failed to connect to Redis after multiple attempts.")
                raise
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Error connecting to Redis: {e}")
            raise

def get_client():
    if not _redis_client:
        init_redis()
    return _redis_client

def set_state(key, value, expire=None):
    """Set a session state key-value pair."""
    client = get_client()
    try:
        val_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        client.set(key, val_str, ex=expire)
    except Exception as e:
        logger.error(f"Redis set error for {key}: {e}")

def get_state(key, as_json=False):
    """Get a session state value."""
    client = get_client()
    try:
        val = client.get(key)
        if val and as_json:
            return json.loads(val)
        return val
    except Exception as e:
        logger.error(f"Redis get error for {key}: {e}")
        return None

def delete_state(key):
    """Delete a session state key."""
    client = get_client()
    try:
        client.delete(key)
    except Exception as e:
        logger.error(f"Redis delete error for {key}: {e}")

# High level functions for specific state
def set_current_plan(plan_content):
    set_state("current_plan", plan_content)

def get_current_plan():
    return get_state("current_plan")

def set_approval_status(status):
    """Status can be: waiting, approved, executing, complete"""
    set_state("plan_approval_status", status)

def get_approval_status():
    return get_state("plan_approval_status")
