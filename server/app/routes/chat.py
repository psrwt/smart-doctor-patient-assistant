from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.dependencies import get_current_user
from app.services.agent_service import MedicalAgent
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter(prefix="/agent/chat", tags=["Agent"])

class ChatRequest(BaseModel):
    message: str
    messages: List[Dict[str, str]] # converstaion history

@router.post("")
async def chat_with_agent(
    payload: ChatRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # Get role and ID from JWT
):
    # Initialize Agent with the specific user's role (Agentic Discovery)
    agent = MedicalAgent(db, current_user)

    # Convert frontend message format to agent-friendly format
    formatted_history = [
        {"role": m["role"], "content": m["text"]} for m in payload.messages
    ]
    
    # Run the Agentic flow
    response = await agent.run(payload.message, history=formatted_history)
    
    return {"reply": response}