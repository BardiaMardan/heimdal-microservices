from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.exceptions import AuthError
from app.models.user import TokenData, User
from app.services import user_service

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)


def get_current_user(
    token: Annotated[str, Depends(reusable_oauth2)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise AuthError(message="Could not validate credentials")

    if token_data.sub is None:
        raise AuthError(message="Could not validate credentials")

    user = user_service.get_by_email(db, token_data.sub)
    if user is None:
        raise AuthError(message="User not found")
    if not user.is_active:
        raise AuthError(message="Inactive user")
    return user
