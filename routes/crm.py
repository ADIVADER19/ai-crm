from fastapi import APIRouter, HTTPException, Response, Depends, Query
from pydantic import BaseModel
import bcrypt
from typing import Optional, List
from bson import ObjectId
from services.db_service import users_collection
from services.crm_service import (
    create_user,
    update_user,
    get_user,
    get_conversations,
)
from helpers import create_access_token, convert_objectid_to_str
from models.user import UserCreate, UserUpdate, TokenResponse, UserResponse
from routes.auth import verify_token, verify_admin_token

router = APIRouter(prefix="/crm")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


@router.post("/create_user", response_model=TokenResponse)
def create_user_endpoint(user_data: UserCreate, response: Response):
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user_data.password)

    print(f"Original password: {user_data.password}")
    print(f"Hashed password: {hashed_password}")

    user_document = {
        "name": user_data.name,
        "email": user_data.email,
        "company": user_data.company,
        "preferences": user_data.preferences,
        "password": hashed_password,  # Store hashed password
        "role": user_data.role,  # Add role to user document
        "phone": user_data.phone,  # Add phone to user document
    }
    
    print(f"Document to insert: {user_document}")

    print(f"Document to insert: {user_document}")

    result = users_collection.insert_one(user_document)
    user_id = str(result.inserted_id)
    
    stored_user = users_collection.find_one({"_id": result.inserted_id})
    print(f"Stored user: {stored_user}")

    access_token = create_access_token(data={"sub": user_id})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "company": user_data.company,
            "preferences": user_data.preferences,
            "role": user_data.role,
            "phone": user_data.phone,
        },
    )


@router.put("/update_user/{user_id}")
def update_user_route(
    user_id: str, 
    user: UserUpdate, 
    authenticated_user_id: str = Depends(verify_token)
):
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=403, 
            detail="You can only update your own profile"
        )
    
    updated_user = update_user(user_id, user.model_dump(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = convert_objectid_to_str(updated_user)
    if "_id" in updated_user:
        updated_user.pop("_id")
    return {"message": "User updated successfully", "user": updated_user}


@router.get("/user/{user_id}")
def get_user_route(
    user_id: str, 
    authenticated_user_id: str = Depends(verify_token)
):
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=403, 
            detail="You can only access your own profile"
        )
    
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = convert_objectid_to_str(user)
    if "_id" in user:
        user.pop("_id")
    return {"user": user}


@router.get("/conversations/{user_id}")
def get_conversations_route(
    user_id: str, 
    authenticated_user_id: str = Depends(verify_token)
):
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=403, 
            detail="You can only access your own conversations"
        )
    
    conversations = get_conversations(user_id)
    conversations = convert_objectid_to_str(conversations)
    return {"conversations": conversations}


# Admin-only endpoints
@router.get("/admin/users", response_model=List[UserResponse])
def get_all_users(
    name: Optional[str] = Query(None, description="Filter by name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone"),
    admin_user_id: str = Depends(verify_admin_token)
):
    """Get all users with optional filtering. Admin only."""
    
    # Build filter query
    filter_query = {}
    
    if name:
        filter_query["name"] = {"$regex": name, "$options": "i"}
    if email:
        filter_query["email"] = {"$regex": email, "$options": "i"}
    if phone:
        filter_query["phone"] = {"$regex": phone, "$options": "i"}
    
    users = list(users_collection.find(filter_query, {"password": 0}))  # Exclude password
    
    user_responses = []
    for user in users:
        user_responses.append(UserResponse(
            user_id=str(user["_id"]),
            name=user.get("name", ""),
            email=user.get("email", ""),
            company=user.get("company", ""),
            preferences=user.get("preferences", ""),
            role=user.get("role", "user"),
            phone=user.get("phone", "")
        ))
    
    return user_responses


@router.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: str,
    role: str,
    admin_user_id: str = Depends(verify_admin_token)
):
    """Update user role. Admin only."""
    
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")
    
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": role}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User role updated to {role} successfully"}


@router.get("/admin/users/{user_id}", response_model=UserResponse)
def get_user_by_id_admin(
    user_id: str,
    admin_user_id: str = Depends(verify_admin_token)
):
    """Get any user by ID. Admin only."""
    
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        user_id=str(user["_id"]),
        name=user.get("name", ""),
        email=user.get("email", ""),
        company=user.get("company", ""),
        preferences=user.get("preferences", ""),
        role=user.get("role", "user"),
        phone=user.get("phone", "")
    )
