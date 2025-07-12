#!/usr/bin/env python3
"""
Setup verification script for AI CRM Chatbot
This script checks if all dependencies and configurations are properly set up
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check environment variables"""
    print("=== Environment Check ===")
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY", "MONGO_URI"]
    optional_vars = ["JWT_SECRET_KEY"]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"✗ {var}: Missing")
        else:
            print(f"✓ {var}: Set")
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✓ {var}: Set")
        else:
            print(f"⚠ {var}: Not set (will use default)")
    
    return len(missing_vars) == 0

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n=== Dependencies Check ===")
    
    required_packages = [
        "fastapi", "uvicorn", "pymongo", "openai", "python-dotenv",
        "langchain", "langchain_openai", "langchain_community", 
        "faiss", "pydantic", "jwt", "pandas", "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "faiss":
                __import__("faiss")
            elif package == "jwt":
                __import__("jwt")
            elif package == "python-dotenv":
                __import__("dotenv")
            elif package == "langchain_openai":
                __import__("langchain_openai")
            elif package == "langchain_community":
                __import__("langchain_community")
            else:
                __import__(package)
            print(f"✓ {package}: Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}: Missing")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
    
    return len(missing_packages) == 0

def check_database():
    """Check database connection"""
    print("\n=== Database Check ===")
    
    try:
        from pymongo import MongoClient
        mongo_uri = os.getenv("MONGO_URI")
        
        if not mongo_uri:
            print("✗ MONGO_URI not set")
            return False
        
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("✓ MongoDB: Connection successful")
        
        # Check collections
        db = client["rentbot"]
        collections = db.list_collection_names()
        print(f"✓ Database: Found {len(collections)} collections")
        
        # Check knowledge base
        kb_collection = db["knowledge_base"]
        kb_count = kb_collection.count_documents({})
        print(f"✓ Knowledge base: {kb_count} documents")
        
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def check_openai():
    """Check OpenAI API connection"""
    print("\n=== OpenAI API Check ===")
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("✗ OPENAI_API_KEY not set")
            return False
        
        client = OpenAI(api_key=api_key)
        
        # Test API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("✓ OpenAI API: Connection successful")
        return True
        
    except Exception as e:
        print(f"✗ OpenAI API connection failed: {e}")
        return False

def main():
    print("AI CRM Chatbot - Setup Verification")
    print("=" * 40)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Dependencies", check_dependencies),
        ("Database Connection", check_database),
        ("OpenAI API", check_openai)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name}: Error during check - {e}")
            results.append((name, False))
    
    print("\n=== Summary ===")
    all_passed = True
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to start the server.")
        print("Run: python start_server.py")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
