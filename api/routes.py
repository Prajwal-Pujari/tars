from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, WebSocket
from pydantic import BaseModel
from api.auth import verify_token
from api.websocket import manager
from agents.orchestrator import get_orchestrator
from memory.session import get_current_plan, get_approval_status
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class PlanFeedback(BaseModel):
    feedback: str

@router.post("/chat")
async def chat(request: ChatRequest, token: str = Depends(verify_token)):
    # Synchronous for simplicity, in reality dispatch to async queue/task
    response = get_orchestrator().handle_request(request.message)
    await manager.broadcast(f"TARS action: processed user message.")
    return {"response": response}

@router.post("/task")
async def submit_task(request: ChatRequest, token: str = Depends(verify_token)):
    response = get_orchestrator().create_plan(request.message)
    return {"response": response}

@router.post("/plan/approve")
async def approve_plan(token: str = Depends(verify_token)):
    response = get_orchestrator().handle_request("approved")
    return {"response": response}

@router.post("/plan/modify")
async def modify_plan(request: PlanFeedback, token: str = Depends(verify_token)):
    response = get_orchestrator().handle_request(request.feedback)
    return {"response": response}

@router.post("/file")
async def upload_file(file: UploadFile = File(...), token: str = Depends(verify_token)):
    content = await file.read()
    # Mock logic for storing shared file
    logger.info(f"Received file: {file.filename}")
    return {"filename": file.filename, "status": "read by TARS"}

@router.post("/index")
async def trigger_index(background_tasks: BackgroundTasks, path: str = ".", token: str = Depends(verify_token)):
    from indexer.indexer import index_project
    background_tasks.add_task(index_project, path)
    return {"status": "Indexing started in background."}

@router.get("/plan/current")
async def get_plan(token: str = Depends(verify_token)):
    return {
        "status": get_approval_status(),
        "plan": get_current_plan()
    }

@router.get("/health")
async def health_check():
    # A complete health check would verify connections
    return {"status": "healthy", "services": ["ollama", "postgres", "qdrant", "redis"]}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Can be used to pause/interact with agent via dashboard
            await manager.broadcast(f"Received dashboard message: {data}")
    except Exception:
        manager.disconnect(websocket)
