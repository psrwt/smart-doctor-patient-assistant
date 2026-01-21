# app/mcp/tools.py  (updated)
from sqlalchemy.orm import Session
from app.db.models import User, UserRole, Appointment, AppointmentStatus
from datetime import datetime, date, time, timedelta
from sqlalchemy.exc import SQLAlchemyError
import uuid
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
from zoneinfo import ZoneInfo
from typing import Optional

from app.services.email_service import send_appointment_confirmation_email

load_dotenv()

# === CONFIG ===
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
DEFAULT_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
SCOPES = ["https://www.googleapis.com/auth/calendar"]
DEFAULT_TZ_NAME = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
DEFAULT_TZ = ZoneInfo(DEFAULT_TZ_NAME)
UTC = ZoneInfo("UTC")

if not SERVICE_ACCOUNT_FILE:
    raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable")
if not DEFAULT_CALENDAR_ID:
    raise ValueError("Missing GOOGLE_CALENDAR_ID environment variable")


# === Helpers ===
def _parse_date_time_to_local_and_utc(
    appointment_date: str, time_str: str
) -> Optional[tuple]:
    """
    Parse appointment_date (YYYY-MM-DD) and time_str (many formats) into:
      (local_dt, utc_dt) both timezone-aware datetimes.
    Returns None on failure.
    """
    # try several time formats
    time_formats = ["%H:%M:%S", "%H:%M", "%I:%M %p", "%I %p", "%I:%M%p"]
    for fmt in time_formats:
        try:
            naive = datetime.strptime(
                f"{appointment_date} {time_str}", f"%Y-%m-%d {fmt}"
            )
            # treat as local timezone
            local_dt = naive.replace(tzinfo=DEFAULT_TZ)
            utc_dt = local_dt.astimezone(UTC)
            return local_dt, utc_dt
        except ValueError:
            continue
    # attempt ISO-like parse
    try:
        iso = datetime.fromisoformat(f"{appointment_date}T{time_str}")
        if iso.tzinfo is None:
            iso_local = iso.replace(tzinfo=DEFAULT_TZ)
        else:
            iso_local = iso.astimezone(DEFAULT_TZ)
        return iso_local, iso_local.astimezone(UTC)
    except Exception:
        return None


def _parse_flexible_datetime(value: str) -> Optional[tuple]:
    """
    Parse a flexible datetime string (ISO or 'YYYY-MM-DD HH:MM' etc.)
    Return (local_dt, utc_dt) timezone-aware.
    """
    try:
        # try strict ISO first
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt_local = dt.replace(tzinfo=DEFAULT_TZ)
        else:
            dt_local = dt.astimezone(DEFAULT_TZ)
        return dt_local, dt_local.astimezone(UTC)
    except Exception:
        # try common space-separated format
        try:
            parts = value.strip().split()
            if len(parts) >= 2:
                d = parts[0]
                t = parts[1]
                return _parse_date_time_to_local_and_utc(d, t)
        except Exception:
            return None
    return None


# tools -----
def fetch_doctors_from_db(db: Session):
    rows = db.query(User.full_name).filter(User.role == UserRole.doctor).all()
    return [{"name": r.full_name} for r in rows]


def fetch_doctor_availability(db: Session, doctor_name: str):
    doctor = (
        db.query(User)
        .filter(User.full_name == doctor_name, User.role == UserRole.doctor)
        .first()
    )
    if not doctor:
        return f"No doctor found with the name '{doctor_name}'."

    # compare by appointment_date (date) using local date
    now_local = datetime.now(tz=DEFAULT_TZ)
    today_local_date = now_local.date()

    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= today_local_date,
            Appointment.status == AppointmentStatus.booked,
        )
        .order_by(Appointment.appointment_date, Appointment.start_time)
        .all()
    )

    if not appointments:
        return f"No future appointments found for Dr. {doctor_name}. So, we can schedule an appointment."

    out = []
    for appt in appointments:
        # stored start_time/end_time are UTC-aware datetimes in DB
        start_utc = appt.start_time
        end_utc = appt.end_time
        # convert to local timezone for display
        start_local = start_utc.astimezone(DEFAULT_TZ)
        end_local = end_utc.astimezone(DEFAULT_TZ)
        out.append(
            {
                "appointment_date": start_local.strftime("%Y-%m-%d"),
                "start_time": start_local.strftime("%H:%M"),
                "end_time": end_local.strftime("%H:%M"),
                "status": appt.status.value
                if hasattr(appt.status, "value")
                else appt.status,
            }
        )
    return out


def make_appointment(
    db: Session,
    doctor_name: str,
    patient_id: str,
    appointment_date: str,
    start_time: str,
    end_time: str,
):
    """
    Make an appointment in the database.
    appointment_date: YYYY-MM-DD
    start_time/end_time: flexible (HH:MM, 3:00 PM, HH:MM:SS, ISO etc.)
    Stored times are normalized to UTC-aware datetimes.
    """
    print(
        f"DEBUG: make_appointment received: date='{appointment_date}', start='{start_time}', end='{end_time}'"
    )
    doctor = (
        db.query(User)
        .filter(User.full_name == doctor_name, User.role == UserRole.doctor)
        .first()
    )
    if not doctor:
        return f"No doctor found with the name '{doctor_name}'."

    parsed_start = _parse_date_time_to_local_and_utc(appointment_date, start_time)
    parsed_end = _parse_date_time_to_local_and_utc(appointment_date, end_time)

    if not parsed_start or not parsed_end:
        return (
            f"Invalid date/time format. Use YYYY-MM-DD for date ({appointment_date}) "
            f"and a supported time format for start/end (received start: {start_time}, end: {end_time})."
        )

    start_local, start_utc = parsed_start
    end_local, end_utc = parsed_end

    if start_utc >= end_utc:
        return "Start time must be before end time."

    new_appt = Appointment(
        id=uuid.uuid4(),
        doctor_id=doctor.id,
        patient_id=patient_id,
        appointment_date=start_local.date(),  # store local date for readability/queries
        start_time=start_utc,  # store UTC-aware datetime
        end_time=end_utc,
        status=AppointmentStatus.booked,
    )

    try:
        db.add(new_appt)
        db.commit()
        db.refresh(new_appt)

        patient = db.query(User).filter(User.id == patient_id).first()

        # Format email-time strings using local timezone (readable)
        start_str_local = start_local.strftime("%I:%M %p")
        end_str_local = end_local.strftime("%I:%M %p")
        date_str_local = start_local.strftime("%d %b %Y")

        send_appointment_confirmation_email(
            to_email=patient.email,
            patient_name=patient.full_name,
            doctor_name=doctor.full_name,
            appointment_date=date_str_local,
            start_time=start_str_local,
            end_time=end_str_local,
        )
    except SQLAlchemyError as e:
        db.rollback()
        return f"Failed to create appointment: {str(e)}"

    return f"Appointment successfully booked with Dr. {doctor.full_name} on {start_local.strftime('%Y-%m-%d')} from {start_local.strftime('%H:%M')} to {end_local.strftime('%H:%M')}."


# === GOOGLE CALENDAR tool ===
def book_google_calendar_event(
    doctor_name: str,
    start_time: str,
    end_time: str,
    summary: str = "Appointment",
):
    """
    Book an appointment in Google Calendar.
    start_time/end_time can be flexible strings (ISO or 'YYYY-MM-DD HH:MM', or full ISO with tz).
    The event is created with the DEFAULT_TZ timezone.
    """
    # parse start and end into timezone-aware datetimes
    parsed_s = _parse_flexible_datetime(start_time)
    parsed_e = _parse_flexible_datetime(end_time)
    if not parsed_s or not parsed_e:
        return "start_time and end_time must be parseable datetimes (ISO or 'YYYY-MM-DD HH:MM')"

    start_local, start_utc = parsed_s
    end_local, end_utc = parsed_e

    if start_utc >= end_utc:
        return "Start time must be before end time"

    # Use RFC3339 / ISO with offset in event body and send the event using the local timezone
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=credentials)

        event = {
            "summary": f"{summary} : {doctor_name}",
            "start": {
                # RFC3339 with offset; use the local timezone time and include tzName field
                "dateTime": start_local.isoformat(),
                "timeZone": DEFAULT_TZ_NAME,
            },
            "end": {
                "dateTime": end_local.isoformat(),
                "timeZone": DEFAULT_TZ_NAME,
            },
        }
        created_event = (
            service.events()
            .insert(calendarId=DEFAULT_CALENDAR_ID, body=event)
            .execute()
        )
        return "Google Calendar appointment booked"
    except Exception as e:
        return f"Failed to book appointment in Google Calendar: {str(e)}"
