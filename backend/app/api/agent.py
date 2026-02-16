from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.models.agent import ChatRequest, ChatResponse
from app.services.llm_service import llm_service

router = APIRouter()

# TODO : In-memory history (will be Redis/Postgres later)
history = []

@router.post("/chat")
async def chat_with_agent(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    return StreamingResponse(
        llm_service.chat_stream(request.message),
        media_type="text/plain"
    )

@router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    # TODO : Return history
    return history
