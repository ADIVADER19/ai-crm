from fastapi import APIRouter, HTTPException
from models.user import UserCreate, UserUpdate
from services.crm_service import create_user, update_user, get_user, get_conversations

router = APIRouter(prefix="/crm")

@router.post("/create_user")
def create_user_route(user: UserCreate):
    user_id = create_user(user.dict())
    return {"user_id": user_id}

@router.put("/update_user/{user_id}")
def update_user_route(user_id: str, user: UserUpdate):
    update_user(user_id, user.dict(exclude_unset=True))
    return {"message": "User updated successfully"}

@router.get("/user/{user_id}")
def get_user_route(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return {"user": user}

@router.get("/conversations/{user_id}")
def get_conversations_route(user_id: str):
    conversations = get_conversations(user_id)
    return {"conversations": conversations}

@router.get("/debug/sample-docs")
def get_sample_docs():
    from services.db_service import knowledge_base_collection
    
    sample_docs = list(knowledge_base_collection.find().limit(3))
    
    for doc in sample_docs:
        doc["_id"] = str(doc["_id"])
    
    return {"sample_documents": sample_docs}
