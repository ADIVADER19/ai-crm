from fastapi import APIRouter, HTTPException
from models.user import UserCreate, UserUpdate
from services.crm_service import create_user, update_user, get_user, get_conversations
from helpers import convert_objectid_to_str

router = APIRouter(prefix="/crm")

@router.post("/create_user")
def create_user_route(user: UserCreate):
    user_id = create_user(user.model_dump())
    return {"user_id": user_id}

@router.put("/update_user/{user_id}")
def update_user_route(user_id: str, user: UserUpdate):
    updated_user = update_user(user_id, user.model_dump(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = convert_objectid_to_str(updated_user)
    if "_id" in updated_user:
        updated_user.pop("_id")
    return {"message": "User updated successfully", "user": updated_user}

@router.get("/user/{user_id}")
def get_user_route(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = convert_objectid_to_str(user)
    if "_id" in user:
        user.pop("_id")
    return {"user": user}

@router.get("/conversations/{user_id}")
def get_conversations_route(user_id: str):
    conversations = get_conversations(user_id)
    conversations = convert_objectid_to_str(conversations)
    return {"conversations": conversations}
