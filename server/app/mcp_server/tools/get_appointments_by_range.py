from datetime import datetime, time, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.models import Appointment, User, AppointmentStatus
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

def get_doctor_appointments_range(db: Session, doctor_id: str, start_date_str: str, end_date_str: str) -> dict:
    """
    Fetches and groups appointments for a doctor by date within a range.
    """
    try:

        # 1. Parse and Validate Date Range
        try:
            start_date = datetime.fromisoformat(start_date_str).date()
            end_date = datetime.fromisoformat(end_date_str).date()
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid date format. Please use YYYY-MM-DD."
            }

        if start_date > end_date:
            return {
                "status": "error",
                "message": "The start date cannot be after the end date."
            }
        
        # Make the range inclusive (start of first day to end of last day)
        start_ist = datetime.combine(start_date, time.min).replace(tzinfo=IST)
        end_ist =  datetime.combine(end_date, time.max).replace(tzinfo=IST)

        # 2. Query with Join to get Patient Names
        appointments = db.query(Appointment, User).join(
            User, Appointment.patient_id == User.id
        ).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.booked,
            and_(
                Appointment.start_at >= start_ist,
                Appointment.start_at <= end_ist
            )
        ).order_by(Appointment.start_at.asc()).all()

        # 3. Handle Empty Results
        if not appointments:
            return {
                "status": "success",
                "total_count": 0,
                "message": f"You have no appointments scheduled between {start_date_str} and {end_date_str}.",
                "schedule": {}
            }

        # 4. Group by Date with IST Conversion
        grouped_schedule = defaultdict(list)
        for appt, patient in appointments:
            # Explicitly ensure the timestamp is converted to IST for display
            start_at_ist = appt.start_at.astimezone(IST) 
            
            date_key = start_at_ist.strftime("%Y-%m-%d (%A)")
            grouped_schedule[date_key].append({
                "time": start_at_ist.strftime("%I:%M %p"), 
                "patient_name": patient.full_name,
                "symptoms": appt.symptoms or "Not specified"
            })

        # 5. Build final structured response
        return {
            "status": "success",
            "range": f"{start_date_str} to {end_date_str}",
            "total_count": len(appointments),
            "summary": f"I found {len(appointments)} appointments for this period.",
            "schedule": dict(grouped_schedule)
        }

    except Exception as e:
        logger.error(f"Error fetching appointment range for {doctor_id}: {e}")
        return {
            "status": "error",
            "message": "Failed to retrieve the appointment schedule due to a database error."
        }