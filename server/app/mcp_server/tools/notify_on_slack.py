import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.db.models import User
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

# Set up logging for debugging
logger = logging.getLogger(__name__)

def notify_on_slack(db: Session, doctor_id: str, report_content: str) -> dict:
    """
    Sends a formatted medical report or appointment summary to a doctor's Slack DM.
    Returns a dictionary containing the status and result message.
    """
    
    # 1. Initialize Client
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        return {
            "status": "error",
            "error_type": "config_error",
            "message": "SLACK_BOT_TOKEN not set in environment."
        }

    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    doctor_email = doctor.email
    logger.info(f"Doctor email: {doctor_email}")
    logger.info(f"Report content: {report_content}")
        
    client = WebClient(token=token)

    try:
        # 2. Look up the Slack User ID by Email
        lookup = client.users_lookupByEmail(email=doctor_email)
        slack_user_id = lookup["user"]["id"]

        # 3. Send the message
        client.chat_postMessage(
            channel=slack_user_id,
            text="🏥 New Clinical Report",
            blocks=[
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🏥Appointment Summary Report"}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn", 
                        "text": f"*Recipient:* {doctor_email}\n\n{report_content}"
                    }
                },
                {"type": "divider"}
            ]
        )
        
        return {
            "status": "success",
            "recipient": doctor_email,
            "message": "Report delivered successfully."
        }

    except SlackApiError as e:
        error_code = e.response["error"]
        
        # Mapping specific Slack errors to clear dictionary responses
        error_map = {
            "users_not_found": "The email is not associated with any Slack account in this workspace.",
            "invalid_auth": "Slack authentication failed. Please check the Bot Token.",
            "ratelimited": "Slack API rate limit exceeded. Try again later."
        }
        
        return {
            "status": "error",
            "error_type": "api_error",
            "slack_code": error_code,
            "message": error_map.get(error_code, f"Slack API Error: {error_code}")
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error_type": "system_error",
            "message": str(e)
        }