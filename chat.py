#!/usr/bin/env python3
"""
Standalone chat script for testing the AI CRM Chatbot
Can be used to test the chatbot functionality without the web interface
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "http://localhost:8000"

class ChatClient:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.user_id = None
        self.token = None
    
    def create_user(self, name, email, company=None):
        """Create a new user"""
        url = f"{self.base_url}/crm/create_user"
        data = {
            "name": name,
            "email": email,
            "company": company
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.user_id = result["user_id"]
            print(f"User created with ID: {self.user_id}")
            return self.user_id
        else:
            print(f"Error creating user: {response.text}")
            return None
    
    def login(self, email, password="demo"):
        """Login user (demo implementation)"""
        url = f"{self.base_url}/auth/login"
        data = {
            "email": email,
            "password": password
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result["access_token"]
                print("Login successful!")
                return True
            else:
                print(f"Login failed: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print("Could not connect to API. Make sure the server is running.")
            return False
    
    def send_message(self, message):
        """Send a message to the chatbot"""
        if not self.user_id:
            print("No user ID set. Please create a user first.")
            return None
        
        url = f"{self.base_url}/chat/"
        data = {
            "user_id": self.user_id,
            "message": message
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                return result["reply"]
            else:
                print(f"Error sending message: {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            print("Could not connect to API. Make sure the server is running.")
            return None
    
    def get_conversations(self):
        """Get user's conversation history"""
        if not self.user_id:
            print("No user ID set. Please create a user first.")
            return None
        
        url = f"{self.base_url}/crm/conversations/{self.user_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()["conversations"]
            else:
                print(f"Error getting conversations: {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            print("Could not connect to API. Make sure the server is running.")
            return None

def main():
    print("=== AI CRM Chatbot - Test Client ===")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    client = ChatClient()
    
    # Setup user
    print("Setting up user...")
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    company = input("Enter your company (optional): ") or None
    
    user_id = client.create_user(name, email, company)
    if not user_id:
        print("Failed to create user. Exiting.")
        return
    
    print("\n=== Chat Session Started ===")
    print("Type 'quit' to exit, 'history' to see conversation history")
    print()
    
    while True:
        try:
            user_input = input(f"{name}: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'history':
                conversations = client.get_conversations()
                if conversations:
                    print("\n=== Conversation History ===")
                    for i, conv in enumerate(conversations, 1):
                        print(f"\nConversation {i}:")
                        for msg in conv.get("messages", []):
                            role = "You" if msg["role"] == "user" else "Bot"
                            print(f"  {role}: {msg['content']}")
                    print("========================\n")
                else:
                    print("No conversation history found.\n")
                continue
            elif not user_input:
                continue
            
            reply = client.send_message(user_input)
            if reply:
                print(f"Bot: {reply}")
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
