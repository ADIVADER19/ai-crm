#!/usr/bin/env python3
"""
Script to view stored Google user data in MongoDB
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

def view_google_users():
    """View all users created via Google OAuth"""
    
    # MongoDB connection
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "ai_crm")
    
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    users_collection = db.users
    
    print("🔍 Google OAuth Users in Database")
    print("=" * 60)
    
    # Find users with Firebase authentication
    google_users = users_collection.find({"auth_provider": "firebase"})
    
    count = 0
    for user in google_users:
        count += 1
        print(f"\n👤 User #{count}")
        print(f"📧 Email: {user.get('email', 'N/A')}")
        print(f"👨‍💼 Name: {user.get('name', 'N/A')}")
        print(f"🆔 Firebase UID: {user.get('firebase_uid', 'N/A')}")
        print(f"🖼️ Picture: {user.get('picture', 'N/A')}")
        print(f"✅ Email Verified: {user.get('email_verified', False)}")
        print(f"🔗 Provider: {user.get('provider', 'N/A')}")
        print(f"🏢 Company: {user.get('company', 'Not provided')}")
        print(f"📱 Phone: {user.get('phone', 'Not provided')}")
        print(f"🎭 Role: {user.get('role', 'user')}")
        print(f"📅 Created: {user.get('created_at', 'N/A')}")
        print(f"🔄 Last Login: {user.get('last_login', 'N/A')}")
        print("-" * 40)
    
    if count == 0:
        print("No Google OAuth users found in database.")
        print("\n💡 To create users:")
        print("1. Visit your frontend login page")
        print("2. Click 'Continue with Google'")
        print("3. Complete Google OAuth flow")
        print("4. Run this script again to see stored data")
    else:
        print(f"\n📊 Total Google OAuth users: {count}")
    
    # Also show regular users count for comparison
    regular_count = users_collection.count_documents({"auth_provider": {"$ne": "firebase"}})
    
    if regular_count > 0:
        print(f"\n📋 Regular (non-Google) users: {regular_count}")
    
    client.close()

if __name__ == "__main__":
    view_google_users()
