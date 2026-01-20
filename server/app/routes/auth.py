from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import UserRole
from app.services import auth_service

router = APIRouter(prefix="", tags=["Auth"])


# -------- SCHEMAS (keep near routes) --------

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_role: str
    user_name: str
    user_email: str
    user_id: str


    

@router.post("/signup", status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    user = auth_service.create_user(
        db=db,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        role=UserRole(payload.role),
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    token = auth_service.create_access_token(
        {"sub": str(user.id), "role": user.role.value}
    )

    return {
        "message": "Account created successfully",
        "access_token": token,
        "user_role": user.role.value,
        "user_name": user.full_name,
        "user_email": user.email,
        "user_id": str(user.id),
    }


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = auth_service.create_access_token(
        {"sub": str(user.id), "role": user.role.value}
    )

    return {
        "access_token": token,
        "user_role": user.role.value,
        "user_name": user.full_name,
        "user_email": user.email,
        "user_id": str(user.id),
    }
