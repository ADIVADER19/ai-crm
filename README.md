# RentRadar Chatbot

A sophisticated AI-powered CRM chatbot system built with FastAPI, OpenAI GPT, and RAG (Retrieval-Augmented Generation) capabilities for real estate property management.

## Features

- **AI-Powered Chat**: GPT-based conversational AI with context awareness
- **RAG Integration**: Retrieval-Augmented Generation using property knowledge base
- **User Management**: Complete CRM system for user creation and management
- **Conversation History**: Persistent chat history and conversation tracking
- **File Upload**: CSV data upload for knowledge base expansion
- **Authentication**: JWT-based authentication system
- **REST API**: Complete RESTful API with FastAPI
- **Vector Search**: FAISS-powered semantic search for property data

## Project Structure

```
ai-crm-chatbot/
├── ai-crm-frontend         # react based frontend (to set up read it's README)
├── main.py                 # FastAPI application entry point
├── helpers.py              # Some helper functions used throughout the application
├── start_server.py         # Server startup script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── HackathonInternalKnowledgeBase.csv  # Sample property data
├── models/
│   ├── user.py            # User data models
├── routes/
│   ├── auth.py            # Authentication endpoints
│   ├── chat.py            # Chat endpoints
│   ├── crm.py             # CRM endpoints
|   ├── reset.py           # Reset endpoint
│   └── upload.py          # File upload endpoints
├── services/
│   ├── db_service.py      # Database connection
│   ├── crm_service.py     # CRM business logic
│   ├── openai_service.py  # OpenAI integration
│   └── rag_service.py     # RAG and vector search
└── scripts/
    └── csv_mongo.py       # Data import utility
```

## Quick Start

### Prerequisites

- Python 3.10+
- MongoDB Atlas account or local MongoDB
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-crm-chatbot
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Windows (Command Prompt):
   venv\Scripts\activate.bat
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Update `.env` file with your credentials:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MONGO_URI=your_mongodb_connection_string_here
   JWT_SECRET_KEY=your_jwt_secret_key_here
   ```

5. **Start the server**
   ```bash
   python start_server.py
   ```
   
   Or manually:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   - API Server: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc

### Additional Documentation
- **API Contracts**: See `API_CONTRACTS.md` for detailed endpoint specifications and examples
- **System Architecture**: See `ARCHITECTURE.md` for system design and mermaid diagrams  
- **Sample Conversations**: See `SAMPLE_CONVERSATIONS.md` for example interactions and testing scenarios

## Usage

### API Endpoints

#### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `POST /auth/verify` - Verify token
- `POST /auth/logout` - User logout

#### CRM Management
- `POST /crm/create_user` - Create new user
- `PUT /crm/update_user/{user_id}` - Update user
- `GET /crm/user/{user_id}` - Get user details
- `GET /crm/conversations/{user_id}` - Get conversation history

#### Chat System
- `POST /chat/` - Send message to chatbot
- `GET /chat/categories` - Get conversation categories

#### File Upload
- `POST /upload_docs/` - Upload documents (PDF, TXT, CSV, JSON)

#### Reset
- `PUT /reset` - Clear conversation memory

### Sample API Requests

#### Create a User
```bash
curl -X POST "http://localhost:8000/crm/create_user" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Gojo saturo",
  "email": "gojo@example.com",
  "company": "ABC Real Estate",
  "preferences": "Looking for Manhattan properties under $2500/month",
  "password":"123"
  }'
```

#### Send a Chat Message
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Show me properties in Manhattan under $2000/month"
  }'
```

## Data Import

### Using the CSV Script

Import the sample property data:

```bash
python scripts/csv_mongo.py
```

### Manual Upload via API

Upload files through the upload endpoint:

```bash
curl -X POST "http://localhost:8000/upload_docs/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@HackathonInternalKnowledgeBase.csv"
```

## Architecture

### Components

1. **FastAPI Server**: RESTful API with automatic documentation
2. **MongoDB**: Document database for users, conversations, and property data
3. **OpenAI GPT**: Conversational AI for natural language processing
4. **FAISS Vector Store**: Semantic search for property matching
5. **LangChain**: RAG pipeline for knowledge retrieval

### Data Flow

1. User sends a message through chat endpoint
2. System retrieves conversation history from MongoDB
3. RAG service searches relevant property data using FAISS
4. Context is built with history + retrieved knowledge
5. OpenAI generates response using enriched context
6. Response is saved to conversation history

### Testing

Test the API using:
- Interactive docs at `/docs`
- API testing tools like Postman or curl

## Configuration

### Environment Variables

`OPENAI_API_KEY` : OpenAI API key for GPT access 
`MONGO_URI`      : MongoDB connection string     
`SECRET_KEY` : Secret key for JWT tokens 
`ALGORITHM` : Hashing algorithm for token

### MongoDB Collections

- `users`: User account information
- `conversations`: Chat history and messages
- `knowledge_base`: Property data for RAG search
