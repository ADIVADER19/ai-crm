import uvicorn
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("=== AI CRM Chatbot Startup ===")
    print("Initializing database connections...")

    from services.db_service import client
    from services.rag_service import build_vectorstore, get_vector_store_status
    
    try:
        client.admin.command('ping')
        print("MongoDB connection successful")
        
        print("Initializing RAG vector store...")
        success = build_vectorstore()
        
        if success:
            print("RAG vector store ready")
        else:
            print("RAG vector store initialization failed")
            print("Server will continue but RAG functionality may be limited")
            
        # show vector store status
        status = get_vector_store_status()
        print(f"Vector store status: {status}")
        
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
