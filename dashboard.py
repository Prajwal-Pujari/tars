import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="TARS Dashboard")

static_dir = os.path.join(os.path.dirname(__file__), "dashboard", "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/map")
async def code_map():
    return FileResponse(os.path.join(static_dir, "map.html"))

if __name__ == "__main__":
    port = int(os.getenv("DASHBOARD_PORT", 18888))
    if port == 8888:
        port = 18888
    uvicorn.run(app, host="0.0.0.0", port=port)
