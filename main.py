from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, crm, auth, reset, upload
from services.rag_service import initialize_vector_store

app = FastAPI(title="RentRadar Chatbot", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize vector store on server startup"""
    print("🚀 Starting RentRadar server...")
    initialize_vector_store()
    print("✅ Server startup complete!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(crm.router)
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(reset.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI-CRM Chatbot API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-crm-chatbot"}
