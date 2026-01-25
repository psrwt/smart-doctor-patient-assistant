from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db import models

# -------- CONFIG --------
SECRET_KEY = "dev-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# -------- JWT --------
def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, full_name: str, email: str, password: str, role: models.UserRole):
    existing = get_user_by_email(db, email)
    if existing:
        return None

    user = models.User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user