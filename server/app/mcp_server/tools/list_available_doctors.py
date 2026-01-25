from sqlalchemy.orm import Session
from app.db.models import User, UserRole
import logging
logger = logging.getLogger(__name__)

def list_available_doctors(db: Session) -> dict:
    """
    Fetches all registered doctors.
    """
    try:
        # 1. search for doctors
        doctors = db.query(User).filter(
            User.role == UserRole.doctor
        ).order_by(User.full_name.asc()).all()

        # 2. if no doctors found
        if not doctors:
            logger.info("Query successful but no doctors found in database")
            return {
                "status": "empty",
                "message": "There are currently no doctors registered in the system. Please try again later.",
                "doctors": []
            }

        # 3. return list of doctors
        return {
            "status": "success",
            "total_count": len(doctors),
            "doctors": [
                {
                    "id": str(doc.id),
                    "full_name": doc.full_name,
                }
                for doc in doctors
            ]
        }

    except Exception as e:
        # 4. Case: Database connection or query crash
        logger.error(f"Database error in list_available_doctors: {e}")
        return {
            "status": "error",
            "message": "I encountered a technical issue while fetching the doctor list. Please notify the administrator.",
            "technical_details": str(e)
        }