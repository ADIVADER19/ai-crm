#!/usr/bin/env python3
"""
Startup script for the AI CRM Chatbot
This script initializes the database and starts the FastAPI server
"""

import uvicorn
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("=== AI CRM Chatbot Startup ===")
    print("Initializing database connections...")
    
    # Import after loading env vars
    from services.db_service import client
    from services.rag_service import build_vectorstore, get_vector_store_status
    
    try:
        # Test database connection
        client.admin.command('ping')
        print("✓ MongoDB connection successful")
        
        # Initialize vector store (will check cache first)
        print("Initializing RAG vector store...")
        success = build_vectorstore()
        
        if success:
            print("✓ RAG vector store ready")
        else:
            print("⚠ RAG vector store initialization failed")
            print("  Server will continue but RAG functionality may be limited")
            
        # Show vector store status
        status = get_vector_store_status()
        print(f"  Status: Loaded={status['loaded']}, Available={status['available']}, Cache={status['cache_exists']}")
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        print("Please check your MongoDB connection and try again.")
        return
    
    print("\n=== Starting FastAPI Server ===")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print()
    
    # Start the server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
