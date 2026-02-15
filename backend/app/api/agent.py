from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.models.user import User
from app.services.llm import llm_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Main orchestration endpoint for the home automation agent.
    """
    response = await llm_service.chat(request.message)
    return ChatResponse(response=response)
