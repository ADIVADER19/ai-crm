from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    company: Optional[str] = "Demo Company"
    preferences: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    preferences: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


