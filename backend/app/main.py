from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv(".env")

app = FastAPI(
    title="ClosetMind Agent API",
    description="Multi-agent stylist and lifestyle orchestrator utilizing Google ADK",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception middleware for logging 500s
@app.middleware("http")
async def db_session_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        import traceback
        logger.error(f"Global Exception Caught: {e}")
        logger.error(traceback.format_exc())
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# Serves uploaded images as static files
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/health")
def health_check():
    return {"status": "ok", "system": "adk_ready"}

from app.api.v1 import wardrobe, agents, user
app.include_router(wardrobe.router, prefix="/api/v1/wardrobe", tags=["Wardrobe"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
