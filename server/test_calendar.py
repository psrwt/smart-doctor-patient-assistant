from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build("calendar", "v3", credentials=credentials)

start = datetime.now()
end = start + timedelta(minutes=30)

event = {
    "summary": "Test Appointment from Backend",
    "description": "Testing Google Calendar API integration",
    "start": {
        "dateTime": start.isoformat(),
        "timeZone": "Asia/Kolkata",
    },
    "end": {
        "dateTime": end.isoformat(),
        "timeZone": "Asia/Kolkata",
    },
}

created_event = service.events().insert(
    calendarId=CALENDAR_ID,
    body=event
).execute()

print("Event created:", created_event.get("htmlLink"))
