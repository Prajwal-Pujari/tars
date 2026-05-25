import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def web_search(query):
    """Perform a web search using SearXNG."""
    url = os.getenv("SEARXNG_URL", "http://localhost:8080")
    try:
        response = requests.get(f"{url}/search", params={"q": query, "format": "json"})
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[:5]  # Return top 5 results
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"Error performing web search: {e}"
