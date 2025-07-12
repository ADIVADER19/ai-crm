from .db_service import users_collection, conversations_collection
from bson import ObjectId
from pymongo import ReturnDocument
from datetime import datetime, timedelta

def create_user(data):
    result = users_collection.insert_one(data)
    return str(result.inserted_id)

def update_user(user_id, data):
    updated_user = users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)}, 
        {"$set": data},
        return_document=ReturnDocument.AFTER
    )
    return updated_user

def get_user(user_id):
    return users_collection.find_one({"_id": ObjectId(user_id)})

def get_conversations(user_id):
    return list(conversations_collection.find({"user_id": user_id}).sort("created_at", -1))

def get_or_create_active_conversation(user_id, category="general"):
    
    cutoff_time = datetime.utcnow() - timedelta(minutes=30)
    recent_conversation = conversations_collection.find_one({
        "user_id": user_id,
        "category": category,
        "updated_at": {"$gte": cutoff_time}
    }, sort=[("updated_at", -1)])
    if recent_conversation:
        return str(recent_conversation["_id"])
    
    new_conversation = {
        "user_id": user_id,
        "messages": [],
        "category": category,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = conversations_collection.insert_one(new_conversation)
    return str(result.inserted_id)

def add_message_to_conversation(conversation_id, user_message, ai_response):
    
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

def get_recent_conversations(user_id, limit=5):
    conversations = list(conversations_collection.find(
        {"user_id": user_id}
    ).sort("updated_at", -1).limit(limit))
    

    for conv in conversations:
        if len(conv.get("messages", [])) > 4:
            conv["messages"] = conv["messages"][-4:]
    
    return conversations

def get_user_last_category(user_id):

    try:
        latest_conversation = conversations_collection.find_one(
            {"user_id": user_id}, 
            sort=[("updated_at", -1)]
        )
        return latest_conversation.get("category", "general") if latest_conversation else "general"
    except Exception as e:
        print(f"Error getting user's last category: {e}")
        return "general"

def should_use_existing_category(user_id, new_category):

    last_category = get_user_last_category(user_id)
    # keep same if both same
    if new_category == last_category:
        return new_category
    # use new if last general
    if last_category == "general":
        return new_category    
    # For specific categories like property_search, pricing_inquiry, keep the existing category unless the new one is very different
    category_groups = {
        "property_related": ["property_search", "property_details", "pricing_inquiry"],
        "support_related": ["support", "general_inquiry"],
        "other": ["general"]
    }
    # Find which group each category belongs to
    last_group = None
    new_group = None
    for group, categories in category_groups.items():
        if last_category in categories:
            last_group = group
        if new_category in categories:
            new_group = group
    # If both are in the same group, keep the last category
    if last_group == new_group and last_group == "property_related":
        return last_category
    # Otherwise, use the new
    return new_category
