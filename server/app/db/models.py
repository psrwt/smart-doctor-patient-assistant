import uuid
import enum
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # RELATIONSHIPS
    # We use primaryjoin because both doctor and patient link to the same table (User)
    doctor_appointments = relationship(
        "Appointment", 
        foreign_keys="[Appointment.doctor_id]", 
        back_populates="doctor"
    )
    patient_appointments = relationship(
        "Appointment", 
        foreign_keys="[Appointment.patient_id]", 
        back_populates="patient"
    )

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Explicitly link to the User table
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    start_at = Column(DateTime(timezone=True), nullable=False, index=True)
    end_at = Column(DateTime(timezone=True), nullable=False)

    status = Column(
        Enum(AppointmentStatus),
        nullable=False,
        default=AppointmentStatus.booked
    )

    symptoms = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # RELATIONSHIPS
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments")
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_appointments")