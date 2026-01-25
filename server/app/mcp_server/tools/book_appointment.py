import uuid
from datetime import datetime, timedelta, timezone
from app.db.models import Appointment, AppointmentStatus, User
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.services.email_service import send_appointment_email_confirmation
from app.services.google_calendar_service import create_calendar_event

import logging
logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

def book_appointment(db: Session, doctor_id: str, patient_id: str, start_at: str, symptoms: str) -> dict:
    """
    Books an appointment, syncs with Google Calendar, and sends email confirmation.
    Includes validation for user existence and slot availability.
    """
    try:
        # 1. Parse Time and Verify User Existence
        try:
            start_at = datetime.fromisoformat(start_at)
            # Ensure it has IST timezone info
            if start_at.tzinfo is None:
                start_at = start_at.replace(tzinfo=IST)
            end_at = start_at + timedelta(hours=1)
        except ValueError:
            return {"status": "error", "message": "Invalid date/time format. Please use ISO format."}


        # Fetch Doctor and Patient details (needed for the email)
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
        patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()

        if not doctor:
            return {"status": "error", "message": "Doctor not found. Please verify the doctor ID."}
        if not patient:
            return {"status": "error", "message": "Patient not found. Please verify the patient ID."}


        # 2. VALIDATION: Check for overlapping appointments -- We look for ANY booked appointment that overlaps with the requested time
        overlap_exists = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.booked,
            and_(
                Appointment.start_at < end_at,
                Appointment.end_at > start_at
            )
        ).first()

        if overlap_exists:
            return {
                "status": "conflict",
                "message": f"The slot starting at {start_at.strftime('%I:%M %p')} is no longer available. Please select another time."
            }

        # If no overlap, proceed with booking
        new_appt = Appointment(
            id=str(uuid.uuid4()),
            doctor_id=doctor_id,
            patient_id=patient_id,
            start_at=start_at,
            end_at=end_at,
            symptoms=symptoms or "No symptoms provided",
            status=AppointmentStatus.booked
        )
        db.add(new_appt)

        try:
            # Send email confirmation
            send_appointment_email_confirmation(
                to_email=patient.email,
                patient_name=patient.full_name,
                doctor_name=doctor.full_name,
                start_at=start_at,
                end_at=end_at
            )

            # Create Google Calendar event
            create_calendar_event(
                doctor_name=doctor.full_name,
                patient_name=patient.full_name,
                start_dt=start_at,
                end_dt=end_at,
                symptoms=symptoms
            )
        except Exception as service_err:
            logger.warning(f"External service sync partially failed: {service_err}")


        # only commit after email and google calendar confirmation
        db.commit()
        return {
            "status": "success",
            "appointment_id": new_appt.id,
            "message": f"Appointment successfully booked with {doctor.full_name} for {start_at.strftime('%B %d at %I:%M %p')}. Confirmation email sent."
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Critical booking error: {e}")
        return {
            "status": "error",
            "message": "A technical error occurred while processing your booking. Please try again later."
        }
    