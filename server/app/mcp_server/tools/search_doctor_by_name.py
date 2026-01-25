from sqlalchemy.orm import Session
from app.db.models import User, UserRole
import logging
logger = logging.getLogger(__name__)

def search_doctor_by_name(db: Session, name_query: str) -> dict:
    """
    Search for _id of doctors by name.
    """
    try:
        # 1. Input cleaning
        # Removes common prefixes and extra whitespace
        clean_query = name_query.lower().replace("dr.", "").replace("dr ", "").strip()

        if len(clean_query) < 2:
            return {
                "status": "error",
                "message": "The search query is too short. Please provide at least 2 characters of the doctor's name."
            }
        
        # 2. search by name using ILIKE
        # The % symbol means 'match anything before or after'
        search_pattern = f"%{clean_query}%"
        
        doctors = db.query(User).filter(
            User.role == UserRole.doctor,
            User.full_name.ilike(search_pattern)
        ).all()

        # 3. if no doctor found
        if not doctors:
            logger.info(f"No doctor found matching: {name_query}")
            return {
                "status": "not_found",
                "message": f"I couldn't find any doctor matching '{name_query}'. Would you like to see a list of all available doctors?"
            }

        # 4. Handle Success (Single or Multiple)
        results = [
            {"id": str(doc.id), "full_name": doc.full_name} 
            for doc in doctors
        ]

        return {
            "status": "success",
            "match_count": len(results),
            "doctors": results,
            "note": "If multiple doctors are returned, please ask the user to specify." if len(results) > 1 else None
        }

    except Exception as e:
        logger.error(f"Error searching for doctor '{name_query}': {e}")
        return {
            "status": "error",
            "message": "The search service is temporarily unavailable. Please try again in a few moments."
        }
