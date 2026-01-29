import os
import logging
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import json

logger = logging.getLogger(__name__)

# Config
SERVICE_ACCOUNT_JSON_STR = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Global variable to cache the service object
_calendar_service = None

def get_calendar_service():
    """Returns a cached Google Calendar service instance using service account info."""
    global _calendar_service
    if _calendar_service is None:
        try:
            if not SERVICE_ACCOUNT_JSON_STR:
                raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE environment variable is empty or not set.")

            # Parse the flattened JSON string from .env into a dictionary
            service_account_info = json.loads(SERVICE_ACCOUNT_JSON_STR)
            
            # Use from_service_account_info instead of from_service_account_file
            creds = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
            _calendar_service = build("calendar", "v3", credentials=creds)
            
        except json.JSONDecodeError as je:
            logger.error(f"Failed to parse Google Service Account JSON: {je}")
            raise RuntimeError("Invalid JSON format in GOOGLE_SERVICE_ACCOUNT_FILE")
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            raise RuntimeError(f"Calendar initialization failed: {str(e)}")
            
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