from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.core.config import settings
from app.core.exceptions import HeimdallException, AuthError
from app.models.user import User, UserCreate, UserResponse, Token, users_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate):
    if user_in.email in users_db:
        raise HeimdallException(
            status_code=400,
            code="USER_EXISTS",
            message="The user with this username already exists in the system.",
        )
    user_id = len(users_db) + 1
    user = User(
        id=user_id,
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
    )
    users_db[user_in.email] = user
    return user


@router.post("/login/access-token", response_model=Token)
def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users_db.get(form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise AuthError(message="Incorrect email or password")
    elif not user.is_active:
        raise AuthError(message="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
