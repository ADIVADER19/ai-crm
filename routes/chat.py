from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from services.openai_service import generate_response
from services.crm_service import (
    get_or_create_active_conversation, 
    add_message_to_conversation,
    get_conversation_categories,

)
from routes.auth import verify_token

router = APIRouter(prefix="/chat")

class ChatMessage(BaseModel):
    message: str
    category: Optional[str] = "general"
    
class ChatResponse(BaseModel):
    reply: str
    user_id: str
    conversation_id: str
    category: str

class ConversationHistory(BaseModel):
    user_id: str
    conversations: List[dict]
    total: int

@router.post("/", response_model=ChatResponse)
async def chat(
    chat_message: ChatMessage,
    user_id: str = Depends(verify_token)
):
    """
    Chat endpoint with JWT authentication and RAG-enhanced responses.
    
    - **message**: The user's chat message
    - **category**: Optional category for conversation organization (default: "general")
    
    Returns:
    - **reply**: AI-generated response with RAG context
    - **user_id**: Authenticated user ID from JWT token
    - **conversation_id**: ID of the logged conversation
    - **category**: Conversation category
    
    Features:
    - JWT token authentication (user_id extracted from token)
    - RAG-enhanced responses using internal knowledge base
    - Full conversation memory maintained
    - Automatic conversation logging
    """
    
    if not chat_message.message or not chat_message.message.strip():
        raise HTTPException(
            status_code=400, 
            detail="Message cannot be empty"
        )

    try:
        # Get or create active conversation
        conversation_id = get_or_create_active_conversation(user_id, chat_message.category)
        
        # Generate AI response
        ai_response = generate_response(user_id, chat_message.message)
        
        # Add both messages to the conversation
        add_message_to_conversation(conversation_id, chat_message.message, ai_response)
        
        return ChatResponse(
            reply=ai_response,
            user_id=user_id,
            conversation_id=conversation_id,
            category=chat_message.category
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.get("/categories")
async def get_categories(user_id: str = Depends(verify_token)):
    """
    Get all conversation categories for the authenticated user.
    """
    try:
        categories = get_conversation_categories(user_id)
        return {"user_id": user_id, "categories": categories}
    except Exception as e:
        print(f"Categories error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")

@router.put("/conversation/{conversation_id}/resolve")
async def resolve_conversation_route(
    conversation_id: str,
    user_id: str = Depends(verify_token)
):
    """
    Mark a conversation as resolved.
    """
    try:
        from services.crm_service import resolve_conversation, get_conversation_by_id
        
        conversation = get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        if conversation.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        resolve_conversation(conversation_id)
        return {"message": "Conversation marked as resolved"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Resolve error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve conversation")

