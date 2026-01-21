# app/services/calendar_service.py
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
import os

# Load credentials from environment
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")  # Default calendar ID
SCOPES = ["https://www.googleapis.com/auth/calendar"]

if not SERVICE_ACCOUNT_FILE:
    raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable")
if not CALENDAR_ID:
    raise ValueError("Missing GOOGLE_CALENDAR_ID environment variable")


def book_appointment(
    doctor_name: str,
    start_time: str,
    end_time: str,
    summary: str = "Doctor Appointment",
):
    """
    Book an appointment in Google Calendar.

    Args:
        doctor_name (str): Name of the doctor (currently for logging only).
        start_time (str): Start time in ISO 8601 format "YYYY-MM-DDTHH:MM:SS".
        end_time (str): End time in ISO 8601 format "YYYY-MM-DDTHH:MM:SS".
        summary (str): Event title (default "Doctor Appointment").

    Returns:
        str: Success message with Google Calendar link or error message.
    """
    try:
        # Validate ISO format
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
        except ValueError:
            return "start_time and end_time must be in ISO 8601 format: 'YYYY-MM-DDTHH:MM:SS'"

        if start_dt >= end_dt:
            return "Start time must be before end time"

        # Authenticate with service account
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=credentials)

        # Create event
        event = {
            "summary": summary,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        }

        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        return f"Google Calendar appointment booked: {created_event.get('htmlLink')}"

    except Exception as e:
        return f"Failed to book appointment in Google Calendar: {str(e)}"
