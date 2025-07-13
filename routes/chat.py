from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import time
from services.openai_service import generate_response
from services.crm_service import (
    get_or_create_active_conversation, 
    add_message_to_conversation,
    get_conversation_categories,
    get_conversation_by_id,
    should_use_existing_category
)
from routes.auth import verify_token, get_user_from_token

router = APIRouter(prefix="/chat")

class ChatMessage(BaseModel):
    message: str
    
class ChatResponse(BaseModel):
    reply: str
    user_id: str
    conversation_id: str
    category: str
    response_time_ms: float

class ConversationHistory(BaseModel):
    user_id: str
    conversations: List[dict]
    total: int

@router.post("/", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    user_details: dict = Depends(get_user_from_token)
):
    start_time = time.time()
    user_id = user_details["user_id"]
    
    if not chat_message.message or not chat_message.message.strip():
        raise HTTPException(
            status_code=400, 
            detail="Message cannot be empty"
        )

    try:# detect category
        ai_response, detected_category = generate_response(user_id, chat_message.message, user_details)
        #finalize category
        final_category = should_use_existing_category(user_id, detected_category)
        # find or make conversation
        conversation_id = get_or_create_active_conversation(user_id, final_category)        
        # add messages to conversation
        add_message_to_conversation(conversation_id, chat_message.message, ai_response)

        response_time_ms = round((time.time() - start_time) * 1000, 2)
        
        return ChatResponse(
            reply=ai_response,
            user_id=user_id,
            conversation_id=conversation_id,
            category=final_category,
            response_time_ms=response_time_ms
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.get("/categories")
async def get_categories(user_id: str = Depends(verify_token)):
# get conversation categories for the user
    try:
        categories = get_conversation_categories(user_id)
        return {"user_id": user_id, "categories": categories}
    except Exception as e:
        print(f"Categories error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")

