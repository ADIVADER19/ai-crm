from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["rentbot"]

users_collection = db["users"]
conversations_collection = db["conversations"]
