import uvicorn
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("=== AI CRM Chatbot Startup ===")
    print("Initializing database connections...")

    from services.db_service import client
    
    try:
        client.admin.command('ping')
        print("MongoDB connection successful")
        
        print("Vector store will be built when documents are uploaded via /upload/upload_docs")
        print("Ready to receive uploads and process conversations")
        
    except Exception as e:
        print(f"Startup warning: {e}")
        print("Server will start anyway...")
    
    print("\nStarting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    
    # start
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
