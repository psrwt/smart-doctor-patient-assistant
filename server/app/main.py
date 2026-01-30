from fastapi import FastAPI, Response, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.db import models
from app.routes import auth, chat
from app.services.dependencies import require_role
from contextlib import asynccontextmanager
from app.services.agent.mcp_client import init_mcp, shutdown_mcp
import fastmcp 
import app.mcp_server.server 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("📦 Connecting to DB and creating tables...")
    models.Base.metadata.create_all(bind=engine)
    
    print("🚀 Initializing MCP Tools...")
    await init_mcp()
    yield
    await shutdown_mcp()

app = FastAPI(lifespan=lifespan)

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

app.include_router(auth.router)
app.include_router(chat.router)

router = APIRouter(tags=["Protected"])

@router.get("/doctor/dashboard")
def doctor_dashboard(current_user=Depends(require_role(["doctor"]))):
    return {"msg": f"Welcome Doctor {current_user['id']}"}

@router.get("/patient/dashboard")
def patient_dashboard(current_user=Depends(require_role(["patient"]))):
    return {"msg": f"Welcome Patient {current_user['id']}"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok"}