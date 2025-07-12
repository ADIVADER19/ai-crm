from .db_service import users_collection, conversations_collection
from bson import ObjectId

def create_user(data):
    result = users_collection.insert_one(data)
    return str(result.inserted_id)

def update_user(user_id, data):
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return True

def get_user(user_id):
    return users_collection.find_one({"_id": ObjectId(user_id)})

def get_conversations(user_id):
    return list(conversations_collection.find({"user_id": user_id}))

def log_conversation(user_id, messages, category="general", resolved=False):
    conversations_collection.insert_one({
        "user_id": user_id,
        "messages": messages,
        "category": category,
        "resolved": resolved
    })
