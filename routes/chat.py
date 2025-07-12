from fastapi import APIRouter, HTTPException
from models.conversation import ChatRequest
from services.openai_service import generate_response
from services.crm_service import log_conversation

router = APIRouter(prefix="/chat")

@router.post("/")
async def chat(req: ChatRequest):
    if not req.user_id or not req.message:
        raise HTTPException(status_code=400, detail="user_id and message are required")

    reply = generate_response(req.user_id, req.message)

    log_conversation(req.user_id, [
        {"role": "user", "content": req.message},
        {"role": "assistant", "content": reply}
    ])

    return {"reply": reply}
