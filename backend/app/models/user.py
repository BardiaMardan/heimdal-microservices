from typing import Optional, Dict
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# In-memory storage for Phase 1
# email -> User
users_db: Dict[str, User] = {}
