from datetime import datetime, time, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.models import Appointment, User, AppointmentStatus
import logging

logger = logging.getLogger(__name__)

# Keep consistent with our local India time
IST = timezone(timedelta(hours=5, minutes=30))

def search_appointments_by_symptoms(
    db: Session, 
    doctor_id: str, 
    symptom_keyword: str, 
    start_date_str: str, 
    end_date_str: str
) -> dict:
    """
    Finds all appointments where the symptom matches a keyword within a specific date range.
    """
    try:

        # 1. Input Validation
        if not symptom_keyword or len(symptom_keyword.strip()) < 3:
            return {
                "status": "error",
                "message": "Please provide a symptom keyword with at least 3 characters for a valid search."
            }

        try:
            start_date = datetime.fromisoformat(start_date_str).date()
            end_date = datetime.fromisoformat(end_date_str).date()
        except ValueError:
            return {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}

        
        # 2. Standardize IST boundaries
        start_ist = datetime.combine(start_date, time.min).replace(tzinfo=IST)
        end_ist = datetime.combine(end_date, time.max).replace(tzinfo=IST)

        # 3. Perform Case-Insensitive Fuzzy Search
        # ILIKE %keyword% ensures we catch "High Fever" if searching for "fever"
        appointments = db.query(Appointment, User).join(
            User, Appointment.patient_id == User.id
        ).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.booked,
            Appointment.symptoms.ilike(f"%{symptom_keyword.strip()}%"),
            and_(
                Appointment.start_at >= start_ist,
                Appointment.start_at <= end_ist
            )
        ).order_by(Appointment.start_at.asc()).all()

        # 4. Handle No Matches
        if not appointments:
            return {
                "status": "success",
                "total_count": 0,
                "message": f"I couldn't find any appointments mentioning symptoms like '{symptom_keyword}' between {start_date_str} and {end_date_str}."
            }

        # 5. Format Results
        results = []
        for appt, patient in appointments:
            # Always convert back to IST for the human-readable report
            start_at_ist = appt.start_at.astimezone(IST)
            results.append({
                "date": start_at_ist.strftime("%Y-%m-%d (%A)"),
                "time": start_at_ist.strftime("%I:%M %p"),
                "patient_name": patient.full_name,
                "symptoms": appt.symptoms
            })

        return {
            "status": "success",
            "total_count": len(results),
            "summary": f"Found {len(results)} patients with symptoms matching '{symptom_keyword}'.",
            "results": results
        }

    except Exception as e:
        logger.error(f"Symptom search error for keyword '{symptom_keyword}': {e}")
        return {
            "status": "error", 
            "message": "An error occurred while searching patient records. Please try again later."
        }