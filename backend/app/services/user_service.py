from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import security
from app.core.exceptions import HeimdallException
from app.models.user import User, UserCreate


def _normalize_email(email: str) -> str:
    """Single source of truth for email comparison: case- and whitespace-
    insensitive. Applied on every read and write so form-login matches register."""
    return email.strip().lower()


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalars(
        select(User).where(User.email == _normalize_email(email))
    ).first()


def create_user(db: Session, payload: UserCreate) -> User:
    email = _normalize_email(payload.email)
    if get_by_email(db, email) is not None:
        raise HeimdallException(
            message="A user with this email already exists.",
            code="USER_EXISTS",
            status_code=409,
        )
    user = User(
        email=email,
        hashed_password=security.get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email)
    if user is None or not security.verify_password(password, user.hashed_password):
        return None
    return user
