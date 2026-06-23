from fastapi import APIRouter
from app.core.config import settings
from app.models.response import success_response

router = APIRouter()

@router.get("/health")
def health_check():
  return success_response(
    data={"environment": settings.ENVIRONMENT},
    message="Service healthy",
  )
