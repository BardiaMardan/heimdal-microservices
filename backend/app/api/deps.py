from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from app.core.config import settings
from app.core.exceptions import AuthError, NotFoundError
from app.models.user import TokenData, User, users_db

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

def get_current_user(token: Annotated[str, Depends(reusable_oauth2)]) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise AuthError(message="Could not validate credentials")
    user = users_db.get(token_data.sub if hasattr(token_data, 'sub') else payload.get("sub"))
    if not user:
        raise NotFoundError(message="User not found")
    return user
