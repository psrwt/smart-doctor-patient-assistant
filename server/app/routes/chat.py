from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.dependencies import get_current_user
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.services.agent.agent import run_agent_chat

router = APIRouter(prefix="/agent/chat", tags=["Agent"])

# New sub-model to handle the {user} data from useAuth()
class UserContext(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    messages: List[Dict[str, str]]  # History: [{"role": "user", "content": "..."}]
    user_info: Optional[UserContext] = None  # Matches the 'user' key from React

@router.post("")
async def chat_with_agent(
    payload: ChatRequest,
    current_user = Depends(get_current_user),
):
    
    result = await run_agent_chat(
        user_message = payload.message,
        history = payload.messages,
        current_user = current_user,
        user_info = payload.user_info.model_dump() if payload.user_info else None
    )
    
    return result
    
    

    
    
    
    

