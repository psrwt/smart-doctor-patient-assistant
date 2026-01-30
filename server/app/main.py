from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.db import models
from app.routes import auth
from app.routes import chat

from fastapi import APIRouter, Depends
from app.services.dependencies import require_role
from contextlib import asynccontextmanager
from app.services.agent.mcp_client import init_mcp, shutdown_mcp

# =================================================================
# 🚨 CRITICAL FIX FOR VERCEL 🚨
# Vercel "Tree Shakes" (deletes) files that aren't imported.
# Since we run the server as a subprocess, Vercel doesn't see it.
# We MUST explicitly import them here so they are included in the build.
# =================================================================
try:
    import fastmcp 
    import app.mcp_server.server 
except ImportError:
    pass
# =================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Connect to DB
    print("📦 Connecting to DB and creating tables...")
    models.Base.metadata.create_all(bind=engine)
    
    # 2. Startup: Connect to MCP Server
    print("🚀 Starting up MCP Connection...")
    try:
        await init_mcp()
    except Exception as e:
        # We catch this so the whole server doesn't crash if MCP fails
        print(f"⚠️ MCP Startup Failed: {e}")
        print("Server will continue running, but AI tools may be unavailable.")
    
    yield
    
    # 3. Shutdown: Clean up
    print("🛑 Shutting down MCP Connection...")
    await shutdown_mcp()

# Initialize App with Lifespan (This replaces on_event)
app = FastAPI(lifespan=lifespan)

# CORS SETTINGS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://smart-doctor-patient-assistant.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES ---
app.include_router(auth.router)
app.include_router(chat.router)

# Protected router
router = APIRouter(tags=["Protected"])

@router.get("/doctor/dashboard")
def doctor_dashboard(current_user=Depends(require_role(["doctor"]))):
    return {"msg": f"Welcome Doctor {current_user['id']}"}

@router.get("/patient/dashboard")
def patient_dashboard(current_user=Depends(require_role(["patient"]))):
    return {"msg": f"Welcome Patient {current_user['id']}"}

app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204) # 204 means "No Content" - tells the browser to stop asking