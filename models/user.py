from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    preferences: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    company: Optional[str]
    preferences: Optional[str]

class UserInDB(UserCreate):
    user_id: str
