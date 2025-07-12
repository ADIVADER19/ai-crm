import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from typing import Optional
from services.crm_service import get_user, create_user
from helpers import create_access_token, verify_token_payload

router = APIRouter(prefix="/auth")
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str = "demo"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user_id = verify_token_payload(token)
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest):
    from services.db_service import users_collection
    
    user = users_collection.find_one({"email": login_request.email})
    
    if not user:
        user_data = {
            "email": login_request.email,
            "name": login_request.email.split("@")[0],
            "company": "Demo Company"
        }
        user_id = create_user(user_data)
        user = {"_id": user_id, **user_data}
    
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/verify")
def verify_user_token(user_id: str = Depends(verify_token)):
    return {"valid": True, "user_id": user_id}

@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: str = Depends(verify_token)):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        user_id=str(user["_id"]),
        email=user.get("email", ""),
        name=user.get("name")
    )

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
