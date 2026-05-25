import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from api.routes import router
from memory import init_all
from agents.memory_agent import memory_agent_instance
from indexer.watcher import start_watcher

app = FastAPI(title="TARS", description="Self-hosted AI agent infrastructure")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting TARS Infrastructure...")
    
    # 1. Initialize databases and connections
    try:
        init_all()
    except Exception as e:
        logger.error(f"Failed to initialize all databases: {e}")
    
    # 2. Start memory agent background thread
    memory_agent_instance.start()
    
    # 3. Start file watcher if PROJECT_PATH is set
    project_path = os.getenv("PROJECT_PATH", "")
    if project_path and os.path.exists(project_path):
        start_watcher(project_path)
    else:
        logger.info("No PROJECT_PATH provided or path does not exist. Skipping file watcher.")
        
    logger.info("TARS is ready.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down TARS...")
    memory_agent_instance.stop()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port)
