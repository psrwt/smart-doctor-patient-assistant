import os
import logging
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Config
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Global variable to cache the service object
_calendar_service = None

def get_calendar_service():
    """Returns a cached Google Calendar service instance."""
    global _calendar_service
    if _calendar_service is None:
        if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise RuntimeError(f"Service account file not found at: {SERVICE_ACCOUNT_FILE}")
            
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        _calendar_service = build("calendar", "v3", credentials=creds)
    return _calendar_service

def create_calendar_event(
    doctor_name: str,
    patient_name: str,
    start_dt: datetime,
    end_dt: datetime,
    symptoms: str = "No symptoms provided",
):
    """
    Creates a Google Calendar event. 
    Expects timezone-aware datetime objects.
    """
    try:
        service = get_calendar_service()

        event_body = {
            "summary": f"🩺 Appointment: {patient_name} x {doctor_name}",
            "location": "Virtual / Clinic Address",
            "description": f"Patient: {patient_name}\nSymptoms: {symptoms}",
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 30},
                ],
            },
        }

        event = service.events().insert(
            calendarId=CALENDAR_ID, 
            body=event_body
        ).execute()

        logger.info(f"Calendar event created: {event.get('htmlLink')}")
        return event.get('htmlLink')

    except HttpError as error:
        logger.error(f"Google Calendar API Error: {error}")
        raise RuntimeError(f"Could not create calendar event: {error.reason}")
    except Exception as e:
        logger.error(f"Unexpected error in calendar service: {e}")
        raise RuntimeError(f"Calendar service failed: {str(e)}")