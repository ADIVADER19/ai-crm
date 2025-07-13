from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, crm, auth, reset, upload

app = FastAPI(title="AI CRM Chatbot", version="1.0.0")

# Add CORS middleware to allow cookies
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
