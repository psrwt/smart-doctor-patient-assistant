from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.db import models
from app.routes import auth
from app.routes import chat

from fastapi import APIRouter, Depends
from app.services.dependencies import get_current_user, require_role

app = FastAPI()

# ✅ CORS SETTINGS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db():
    print("📦 Connecting to DB and creating tables if not exist...")
    models.Base.metadata.create_all(bind=engine)

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

# Include the protected router
app.include_router(router)



@app.get("/")
def health():
    return {"status": "ok"}

