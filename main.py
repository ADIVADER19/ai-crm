from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, crm, auth, reset, upload
from services.rag_service import initialize_vector_store
import os

app = FastAPI(title="RentRadar Chatbot", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize vector store on server startup"""
    print("🚀 Starting RentRadar server...")
    initialize_vector_store()
    print("✅ Server startup complete!")

# Configure CORS for deployment
allowed_origins = [
    "http://localhost:3000",  # React development
    "http://localhost:5173",  # Vite development
    "http://localhost:4173",  # Vite preview
    "https://rentradarassist.vercel.app"
]

# Add production frontend URLs if environment variables are set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# For production deployment
if os.getenv("RENDER"):
    allowed_origins = ["*"]  # Allow all origins in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
