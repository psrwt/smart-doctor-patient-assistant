from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.db.database import Base


class UserRole(str, enum.Enum):
    patient = "patient"
    doctor = "doctor"

class AppointmentStatus(str, enum.Enum):
    booked = "booked"
    cancelled = "cancelled"
    completed = "completed"



class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    appointment_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    status = Column(Enum(AppointmentStatus, name="appointment_status"),
    nullable=False,
                    default=AppointmentStatus.booked)

    symptoms = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
