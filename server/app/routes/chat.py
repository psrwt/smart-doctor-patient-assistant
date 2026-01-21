from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.dependencies import get_current_user
from app.services.agent_service import MedicalAgent
from pydantic import BaseModel
from typing import List, Dict, Optional

router = APIRouter(prefix="/agent/chat", tags=["Agent"])


class ChatRequest(BaseModel):
    message: str
    messages: List[Dict[str, str]]  # conversation history

@router.post("")
async def chat_with_agent(
    payload: ChatRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Initialize Agent for current user
    agent = MedicalAgent(db, current_user)

    # Format frontend conversation for agent
    formatted_history = [
        {"role": m["role"], "content": m["text"]} for m in payload.messages
    ]
    
    # Run agent
    response = await agent.run(payload.message, history=formatted_history)
    
    return {"reply": response}

@router.post("/get-summary")
async def get_doctor_summary(
    date: Optional[str] = Query(None, description="Optional date for summary (YYYY-MM-DD). Defaults to today"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Endpoint to trigger the doctor's summary report.
    Sends a prompt to the agent to generate a summary for a given date.
    """

    # Initialize agent
    agent = MedicalAgent(db, current_user)

    # Predefined prompt
    if date:
        user_input = f"Generate summary report for {date}"
    else:
        user_input = "Generate summary report of all future appointments"

    # Run agent (no conversation history needed for button)
    response = await agent.run(user_input, history=[])

    return {"message": response}
