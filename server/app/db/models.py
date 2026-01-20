from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.db.database import Base


class UserRole(str, enum.Enum):
    patient = "patient"
    doctor = "doctor"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
