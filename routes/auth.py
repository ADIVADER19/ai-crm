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
from services.google_oauth import firebase_auth as firebase_service
from helpers import create_access_token, verify_token_payload
from bson import ObjectId

router = APIRouter(prefix="/auth")
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class FirebaseAuthRequest(BaseModel):
    id_token: str
    user_type: str = "user"  # "user" or "admin"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    preferences: Optional[str] = None
    role: Optional[str] = "user"
    picture: Optional[str] = None
    phone: Optional[str] = None
    email_verified: Optional[bool] = False
    provider: Optional[str] = None
    auth_provider: Optional[str] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None

def verify_password(password: str, hashed: str) -> bool:
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

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user_id = verify_token_payload(token)
        
        user = get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
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
            "preferences": user.get("preferences", ""),
            "role": user.get("role", "user")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest, response: Response):
    user = users_collection.find_one({"email": login_request.email})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(login_request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="none",
        max_age=86400
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", ""),
            "role": user.get("role", "user")
        }
    )

@router.post("/firebase-auth", response_model=TokenResponse)
def firebase_auth(auth_request: FirebaseAuthRequest, response: Response):
    """Handle Firebase authentication for both users and admins"""
    
    try:
        # First verify Firebase token to get user email
        firebase_user = firebase_service.verify_firebase_token(auth_request.id_token)
        if not firebase_user:
            raise HTTPException(status_code=401, detail="Invalid Google authentication token. Please try signing in again.")
        
        # Check if user already exists in MongoDB first
        user = users_collection.find_one({
            "$or": [
                {"email": firebase_user["email"]},
                {"firebase_uid": firebase_user.get("firebase_uid", "")}
            ]
        })
        
        if auth_request.user_type == "admin":
            # For admin login - user must already exist with admin role
            if not user:
                raise HTTPException(status_code=403, detail="Admin account not found. Please contact an administrator to set up your admin access.")
            
            if user.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Administrator access required. Your account does not have admin privileges.")
            
            # Update Firebase UID if not set
            if not user.get("firebase_uid"):
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"firebase_uid": firebase_user["firebase_uid"]}}
                )
                print(f"✅ Updated admin Firebase UID: {firebase_user['email']}")
        
        else:
            # For regular users - check MongoDB first, then handle accordingly
            if user:
                # User exists in MongoDB - update with Firebase info if needed
                try:
                    update_data = {}
                    
                    # Update Firebase UID if not present
                    if not user.get("firebase_uid"):
                        update_data["firebase_uid"] = firebase_user["firebase_uid"]
                        update_data["auth_provider"] = "firebase"
                        
                    # Update name if it's empty or different
                    if not user.get("name") or user.get("name") != firebase_user.get("name", ""):
                        update_data["name"] = firebase_user.get("name", "")
                    
                    if update_data:
                        users_collection.update_one(
                            {"_id": user["_id"]},
                            {"$set": update_data}
                        )
                        user = users_collection.find_one({"_id": user["_id"]})
                    
                    print(f"✅ Found existing user in MongoDB, proceeding with Google OAuth: {firebase_user['email']}")
                
                except Exception as e:
                    print(f"❌ Error updating existing user: {str(e)}")
                    raise HTTPException(status_code=500, detail="Failed to update your account. Please try again.")
            
            else:
                # User doesn't exist in MongoDB - create new account
                try:
                    # Create new user account with same structure as normal signup
                    new_user = {
                        "name": firebase_user.get("name", ""),
                        "email": firebase_user["email"],
                        "company": "",  # Empty string like normal signup default
                        "preferences": "",  # Empty string like normal signup default
                        "role": "user",
                        "phone": "",  # Empty string like normal signup default
                        "firebase_uid": firebase_user["firebase_uid"],  # Add for Firebase linking
                        "auth_provider": "firebase"  # Track auth method
                    }
                    
                    result = users_collection.insert_one(new_user)
                    user = users_collection.find_one({"_id": result.inserted_id})
                    
                    if not user:
                        raise HTTPException(status_code=500, detail="Failed to create user account. Please try again.")
                    
                    print(f"✅ User not found in MongoDB, created new Google user: {firebase_user['email']}")
                    
                except Exception as e:
                    print(f"❌ Error creating new user: {str(e)}")
                    raise HTTPException(status_code=500, detail="Failed to create your account. Please try again or contact support.")
        
        # Verify user was properly retrieved/created
        if not user:
            raise HTTPException(status_code=500, detail="Account setup failed. Please try again or contact support.")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user["_id"])})
        
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="none",
            max_age=86400
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "user_id": str(user["_id"]),
                "email": user["email"],
                "name": user.get("name", ""),
                "role": user.get("role", "user"),
                "company": user.get("company", ""),
                "phone": user.get("phone", ""),
                "preferences": user.get("preferences", ""),
                "auth_provider": user.get("auth_provider", "")
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions with custom messages
        raise
    except Exception as e:
        print(f"❌ Unexpected Firebase auth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed due to a server error. Please try again.")

@router.post("/verify")
def verify_user_token(user_id: str = Depends(verify_token)):
    return {"valid": True, "user_id": user_id}

@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: str = Depends(verify_token)):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        email=user.get("email", ""),
        name=user.get("name"),
        role=user.get("role", "user"),
        picture=user.get("picture", ""),
        company=user.get("company", ""),
        phone=user.get("phone", ""),
        preferences=user.get("preferences", ""),
        email_verified=user.get("email_verified", False),
        provider=user.get("provider", ""),
        auth_provider=user.get("auth_provider", ""),
        created_at=str(user.get("created_at", "")),
        last_login=str(user.get("last_login", ""))
    )

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
