import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["rentbot"]
collection = db["knowledge_base"]
df = pd.read_csv("HackathonInternalKnowledgeBase.csv")
records = df.to_dict(orient="records")
collection.insert_many(records)
print(f"Inserted {len(records)} documents into MongoDB.")
