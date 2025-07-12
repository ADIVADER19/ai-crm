from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from routes.auth import verify_token

router = APIRouter()

@router.post("/reset")
async def reset_conversations(user_id: str = Depends(verify_token)):
    try:
        from services.db_service import conversations_collection
        
        result = conversations_collection.update_many(
            {"user_id": user_id, "resolved": False},
            {"$set": {"resolved": True, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": f"Reset {result.modified_count} active conversations",
            "user_id": user_id
        }
        
    except Exception as e:
        print(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset conversations")