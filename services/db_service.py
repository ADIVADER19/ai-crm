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
