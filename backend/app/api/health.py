from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    llm_status = "disconnected"
    if settings.OPENAI_API_KEY:
        llm_status = "connected"
    
    return {
        "status": "healthy",
        "llm_api": llm_status
    }
