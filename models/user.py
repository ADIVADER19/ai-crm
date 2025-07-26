from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    company: Optional[str] = "Demo Company"
    preferences: Optional[str] = None
    password: str
    role: Optional[str] = "user"  # Default role is "user", can be "admin"
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    preferences: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None

class GoogleUserUpdate(BaseModel):
    """Update model for Google OAuth users - limited fields they can update"""
    preferences: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: str
    company: Optional[str] = None
    preferences: Optional[str] = None
    role: str
    phone: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


