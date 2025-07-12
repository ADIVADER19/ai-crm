from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["rentbot"]
users_collection = db["users"]
conversations_collection = db["conversations"]
knowledge_base_collection = db["knowledge_base"]

def get_database():
    return db

def get_collections():
    return {
        "users": users_collection,
        "conversations": conversations_collection,
        "knowledge_base": knowledge_base_collection
    }

def test_connection():
    try:
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def get_collection_stats():
    try:
        stats = {}
        for name, collection in get_collections().items():
            stats[name] = collection.count_documents({})
        return stats
    except Exception as e:
        print(f"Error getting collection stats: {e}")
        return {}
