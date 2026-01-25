from sqlalchemy.orm import Session
from app.db.models import Appointment, AppointmentStatus
from datetime import datetime, time, timezone, timedelta 
from sqlalchemy import and_
import logging
logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

def fetch_available_appointment_slots(db: Session, doctor_id: str, date_str: str) -> dict:
    """
    Calculates 1-hour gaps. Returns a summary for the LLM and raw data for tools.
    """
    try:
        # 1. Parse date and check if it's in the past
        target_date = datetime.fromisoformat(date_str).date()
        today_ist = datetime.now(IST).date()
        
        if target_date < today_ist:
            return {
                "status": "error",
                "summary": "I cannot check slots for past dates. Please provide a current or future date.",
                "available": False,
                "slots": []
            }
        
        # 2. Define the 10 AM - 5 PM IST window
        search_start_utc = datetime.combine(target_date, time(10, 0)).replace(tzinfo=IST)
        search_end_utc = datetime.combine(target_date, time(17, 0)).replace(tzinfo=IST)

        # 3. Fetch Booked appointments
        booked_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.booked,
            and_(
                Appointment.start_at < search_end_utc,
                Appointment.end_at > search_start_utc
            )
        ).all()

        # 4. Calculate available slots
        available_slots = []
        now_ist = datetime.now(IST)

        for hour in range(10, 17):
            slot_start = datetime.combine(target_date, time(hour, 0)).replace(tzinfo=IST)
            slot_end = slot_start + timedelta(hours=1)

            # Skip slots that have already passed if the target date is today
            if slot_end < now_ist:
                continue

            # Check for overlaps
            is_blocked = any(slot_start < appt.end_at and slot_end > appt.start_at for appt in booked_appointments)
            
            if not is_blocked:
                available_slots.append({
                    "iso_start": slot_start.isoformat(), # Essential for the booking tool
                    "time": slot_start.strftime("%I:%M %p"),
                    "display": f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
                })

        
        # 5. Handle Scenarios
        if not available_slots:
            msg = "The doctor is fully booked for today." if target_date == today_ist else f"No slots available on {date_str}."
            return {
                "status": "fully_booked",
                "summary": msg,
                "available": False,
                "slots": []
            }

        times_text = ", ".join([s['time'] for s in available_slots])
        return {
            "status": "success",
            "date": date_str,
            "summary": f"On {date_str}, the following slots are available: {times_text}.",
            "available": True,
            "slots": available_slots
        }

    except ValueError:
        return {"status": "error", "summary": "Invalid date format. Please use YYYY-MM-DD."}
    except Exception as e:
        logger.error(f"Error for {doctor_id} on {date_str}: {e}")
        return {"status": "error", "summary": "Technical error checking availability.", "error": str(e)}