from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.db import get_db
from app.api.deps import get_current_user
from app.core.exceptions import AuthError
from app.models.response import success_response
from app.models.user import User, UserCreate, UserResponse
from app.services import user_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/register")
def register(user_in: UserCreate, db: DbSession):
  user = user_service.create_user(db, user_in)
  return success_response(
    data=UserResponse.model_validate(user).model_dump(),
    message="User registered successfully",
    code=201,
  )


@router.post("/login/access-token")
def login_access_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  db: DbSession,
):
  user = user_service.authenticate(db, form_data.username, form_data.password)
  if not user:
    raise AuthError(message="Incorrect email or password")
  if not user.is_active:
    raise AuthError(message="Inactive user")

  access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  return success_response(
    data={
      "access_token": security.create_access_token(
        user.email, expires_delta=access_token_expires
      ),
      "token_type": "bearer",
    },
    message="Login successful",
  )


@router.get("/me")
def read_current_user(current_user: CurrentUser):
  return success_response(
    data=UserResponse.model_validate(current_user).model_dump(),
    message="Current user retrieved",
  )
