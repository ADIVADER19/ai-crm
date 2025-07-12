from .db_service import users_collection, conversations_collection
from bson import ObjectId
from datetime import datetime, timedelta

def create_user(data):
    result = users_collection.insert_one(data)
    return str(result.inserted_id)

def update_user(user_id, data):
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return True

def get_user(user_id):
    return users_collection.find_one({"_id": ObjectId(user_id)})

def get_conversations(user_id):
    return list(conversations_collection.find({"user_id": user_id}).sort("created_at", -1))

def get_or_create_active_conversation(user_id, category="general"):
    """Get the most recent conversation or create a new one if none exists or last one is old"""
    
    # Look for recent conversation (within last 30 minutes)
    cutoff_time = datetime.utcnow() - timedelta(minutes=30)
    
    recent_conversation = conversations_collection.find_one({
        "user_id": user_id,
        "category": category,
        "resolved": False,
        "updated_at": {"$gte": cutoff_time}
    }, sort=[("updated_at", -1)])
    
    if recent_conversation:
        return str(recent_conversation["_id"])
    
    # Create new conversation if none found
    new_conversation = {
        "user_id": user_id,
        "messages": [],
        "category": category,
        "resolved": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = conversations_collection.insert_one(new_conversation)
    return str(result.inserted_id)

def add_message_to_conversation(conversation_id, user_message, ai_response):
    """Add both user and AI messages to existing conversation"""
    
    new_messages = [
        {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow()
        },
        {
            "role": "assistant", 
            "content": ai_response,
            "timestamp": datetime.utcnow()
        }
    ]
    
    conversations_collection.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$push": {"messages": {"$each": new_messages}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return True

def log_conversation(user_id, messages, category="general", resolved=False):
    """Legacy function - still works but creates new conversation each time"""
    result = conversations_collection.insert_one({
        "user_id": user_id,
        "messages": messages,
        "category": category,
        "resolved": resolved,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    return str(result.inserted_id)

def get_conversation_by_id(conversation_id):
    return conversations_collection.find_one({"_id": ObjectId(conversation_id)})

def update_conversation(conversation_id, data):
    data["updated_at"] = datetime.utcnow()
    conversations_collection.update_one(
        {"_id": ObjectId(conversation_id)}, 
        {"$set": data}
    )
    return True

def delete_conversation(conversation_id):
    result = conversations_collection.delete_one({"_id": ObjectId(conversation_id)})
    return result.deleted_count > 0

def get_conversation_categories(user_id):
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    categories = list(conversations_collection.aggregate(pipeline))
    return [{"category": cat["_id"], "count": cat["count"]} for cat in categories]

def resolve_conversation(conversation_id):
    """Mark conversation as resolved"""
    return update_conversation(conversation_id, {"resolved": True})

def get_recent_conversations(user_id, limit=5):
    conversations = list(conversations_collection.find(
        {"user_id": user_id}
    ).sort("updated_at", -1).limit(limit))
    

    for conv in conversations:
        if len(conv.get("messages", [])) > 4:
            conv["messages"] = conv["messages"][-4:]
    
    return conversations
