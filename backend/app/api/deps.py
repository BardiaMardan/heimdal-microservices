from typing import Annotated, Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.exceptions import AuthError
from app.models.user import TokenData, User
from app.services import user_service

reusable_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(reusable_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise AuthError(message="Not authenticated")

    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
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
