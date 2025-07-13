import os
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import bcrypt
from typing import Optional
from bson import ObjectId
from services.crm_service import get_user, create_user
from services.db_service import users_collection
from helpers import create_access_token, verify_token_payload
from bson import ObjectId

router = APIRouter(prefix="/auth")
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user_id = verify_token_payload(token)
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user_id = verify_token_payload(token)
        
        user = get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user_id,
            "email": user.get("email", ""),
            "name": user.get("name", ""),
            "company": user.get("company", ""),
            "preferences": user.get("preferences", "")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest, response: Response):
    # Find user by email
    user = users_collection.find_one({"email": login_request.email})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(login_request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    # Set cookie in response
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", "")
        }
    )

@router.post("/verify")
def verify_user_token(user_id: str = Depends(verify_token)):
    return {"valid": True, "user_id": user_id}

@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: str = Depends(verify_token)):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        user_id=str(user["_id"]),
        email=user.get("email", ""),
        name=user.get("name")
    )

@router.post("/logout")
def logout(response: Response):
    # Clear the cookie
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
