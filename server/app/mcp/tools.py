from sqlalchemy.orm import Session
from app.db.models import User, UserRole, Appointment, AppointmentStatus
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.email_service import send_appointment_confirmation_email


def fetch_doctors_from_db(db: Session):
    rows = db.query(User.full_name).filter(User.role == UserRole.doctor).all()

    return [
        {
            "name": r.full_name,
        }
        for r in rows
    ]


def normalize_doctor_name(name: str):
    import re

    clean_name = re.sub(r"^Dr\.?\s*", "", name.strip())
    return clean_name.title()  # Capitalizes first letters


def fetch_doctor_availability(db: Session, doctor_name: str):
    clean_name = normalize_doctor_name(doctor_name)
    # 1. Get doctor by name
    doctor = (
        db.query(User)
        .filter(User.full_name == clean_name, User.role == "doctor")
        .first()
    )

    if not doctor:
        return f"No doctor found with the name '{doctor_name}'."

    # 2. Fetch only future appointments slots with status "booked"
    now = datetime.utcnow()
    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= now,  # future appointments
            Appointment.status == "booked",
        )
        .order_by(Appointment.appointment_date, Appointment.start_time)
        .all()
    )

    if not appointments:
        return f"No future appointments found for Dr. {doctor_name}. So, we can schedule an appointment."

    # 3. Return appointments in readable format
    return [
        {
            "appointment_date": appt.appointment_date.strftime("%Y-%m-%d"),
            "start_time": appt.start_time.strftime("%H:%M"),
            "end_time": appt.end_time.strftime("%H:%M"),
            "status": appt.status,
        }
        for appt in appointments
    ]


def make_appointment(
    db: Session,
    doctor_name: str,
    patient_id: str,
    appointment_date: str,
    start_time: str,
    end_time: str,
):
    """
    Make an appointment with a doctor.
    appointment_date: "YYYY-MM-DD"
    start_time, end_time: "HH:MM"
    """

    # 1. Normalize doctor name
    clean_name = normalize_doctor_name(doctor_name)

    # 2. Get doctor by name
    doctor = (
        db.query(User)
        .filter(User.full_name == clean_name, User.role == "doctor")
        .first()
    )
    if not doctor:
        return f"No doctor found with the name '{doctor_name}'."

    # 3. Parse appointment_date, start_time, end_time into datetime objects
    try:
        appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        start_dt = datetime.strptime(
            f"{appointment_date} {start_time}", "%Y-%m-%d %H:%M"
        )
        end_dt = datetime.strptime(f"{appointment_date} {end_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return "Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time."

    if start_dt >= end_dt:
        return "Start time must be before end time."

    # 4. Check for conflicting appointments for this doctor
    conflict = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == start_dt.date(),
            Appointment.status == "booked",
            # Overlapping time check
            ((Appointment.start_time < end_dt) & (Appointment.end_time > start_dt)),
        )
        .first()
    )

    if conflict:
        return "This doctor already has an appointment in this time slot. Please choose another time."

    # 5. Create new appointment
    new_appt = Appointment(
        id=uuid.uuid4(),
        doctor_id=doctor.id,
        patient_id=patient_id,
        appointment_date=start_dt.date(),
        start_time=start_dt,
        end_time=end_dt,
        status=AppointmentStatus.booked,
    )

    try:
        db.add(new_appt)
        db.commit()
        db.refresh(new_appt)

        patient = db.query(User).filter(User.id == patient_id).first()
        send_appointment_confirmation_email(
            to_email=patient.email,
            patient_name=patient.full_name,
            doctor_name=doctor.full_name,
            appointment_date=start_time.strftime("%d %b %Y"),
            start_time=start_time.strftime("%I:%M %p"),
            end_time=end_time.strftime("%I:%M %p"),
        )
        print("Email sent successfully...")

    except SQLAlchemyError as e:
        db.rollback()
        return f"Failed to create appointment: {str(e)}"

    return f"Appointment successfully booked with Dr. {doctor.full_name} on {appointment_date} from {start_time} to {end_time}."
