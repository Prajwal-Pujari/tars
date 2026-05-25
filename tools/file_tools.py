import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def read_file(filepath):
    """Read a file from the filesystem."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return f"Error: {e}"

def write_file(filepath, content):
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        logger.error(f"Error writing to {filepath}: {e}")
        return f"Error: {e}"

def write_plan(content, fmt="md"):
    """Write the PLAN file to the plans directory."""
    plans_dir = os.getenv("PLANS_DIR", "plans")
    filepath = os.path.join(plans_dir, f"PLAN.{fmt}")
    return write_file(filepath, content)

def write_summary(content, fmt="md"):
    """Write the SUMMARY file to the plans directory."""
    plans_dir = os.getenv("PLANS_DIR", "plans")
    filepath = os.path.join(plans_dir, f"SUMMARY.{fmt}")
    return write_file(filepath, content)
