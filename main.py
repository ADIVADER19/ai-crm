from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat, crm, auth, upload

app = FastAPI(title="AI CRM Chatbot", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(chat.router)
app.include_router(crm.router)
app.include_router(auth.router)
app.include_router(upload.router)

@app.get("/")
def home():
    return {"message": "Welcome to AI-CRM Chatbot API"}
