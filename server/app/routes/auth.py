from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

# -------- SCHEMAS --------

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # 'patient' or 'doctor'

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

# -------- ROUTES --------

@router.post("/signup", status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    # 1. Validate the role string against the Enum defined in models.py
    try:
        user_role = models.UserRole(payload.role.lower())
    except ValueError:
        valid_roles = [r.value for r in models.UserRole]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    # 2. Attempt to create the user
    user = auth_service.create_user(
        db=db,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        role=user_role,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 3. Generate access token
    # We must convert user.id (UUID) to str for the JWT payload
    token = auth_service.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return {
        "message": "Account created successfully",
        "access_token": token,
        "token_type": "bearer",
        "user_role": user.role.value,
        "user_name": user.full_name,
        "user_email": user.email,
        "user_id": str(user.id),
    }


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1. Authenticate credentials
    user = auth_service.authenticate_user(db, payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Generate access token
    token = auth_service.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    # 3. Return response matching TokenResponse schema
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_role": user.role.value,
        "user_name": user.full_name,
        "user_email": user.email,
        "user_id": str(user.id),
    }