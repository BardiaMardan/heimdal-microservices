from fastapi import APIRouter
from app.core.config import settings
from app.models.response import success_response

router = APIRouter()

@router.get("/health")
def health_check():
  llm_status = "disconnected"
  if settings.GOOGLE_AI_API_KEY:
    llm_status = "connected"

  return success_response(
    data={"llm_api": llm_status},
    message="Service healthy",
  )
