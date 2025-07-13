# AI CRM Chatbot - System Architecture

## Mermaid Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Web UI / API Client]
    end
    
    subgraph "API Gateway"
        FastAPI[FastAPI Server<br/>Port 8000]
    end
    
    subgraph "Authentication"
        JWT[JWT Middleware<br/>verify_token]
    end
    
    subgraph "API Routes"
        AuthR[/auth/*<br/>Login, User Info]
        ChatR[/chat<br/>AI Conversations]
        CRMR[/crm/*<br/>User Management]
        UploadR[/upload_docs/<br/>File Upload]
        ResetR[/reset<br/>Clear Memory]
    end
    
    subgraph "Services Layer"
        OpenAI[OpenAI Service<br/>GPT-4o-mini]
        RAG[RAG Service<br/>FAISS Vector Store]
        CRM[CRM Service<br/>User Management]
        DB[Database Service<br/>MongoDB Client]
    end
    
    subgraph "Data Processing"
        Helpers[helpers.py<br/>File Processors]
        CSV[CSV Processor]
        PDF[PDF Processor]
        TXT[TXT Processor]
        JSON[JSON Processor]
    end
    
    subgraph "External Services"
        OpenAIAPI[OpenAI API<br/>gpt-4o-mini]
        MongoDB[(MongoDB Database)]
        VectorDB[(FAISS Vector Store<br/>Local Files)]
    end
    
    subgraph "Database Collections"
        Users[(users_collection)]
        Conversations[(conversations_collection)]
        Knowledge[(knowledge_base_collection)]
    end
    
    %% Client to API
    UI --> FastAPI
    
    %% API to Auth
    FastAPI --> JWT
    
    %% API Routes
    FastAPI --> AuthR
    FastAPI --> ChatR
    FastAPI --> CRMR
    FastAPI --> UploadR
    FastAPI --> ResetR
    
    %% Auth flow
    JWT -.-> AuthR
    JWT -.-> ChatR
    JWT -.-> CRMR
    JWT -.-> UploadR
    JWT -.-> ResetR
    
    %% Routes to Services
    AuthR --> DB
    ChatR --> OpenAI
    ChatR --> RAG
    ChatR --> CRM
    ChatR --> DB
    CRMR --> CRM
    CRMR --> DB
    UploadR --> Helpers
    UploadR --> RAG
    UploadR --> DB
    ResetR --> DB
    
    %% Services to External
    OpenAI --> OpenAIAPI
    DB --> MongoDB
    RAG --> VectorDB
    
    %% File Processing
    Helpers --> CSV
    Helpers --> PDF
    Helpers --> TXT
    Helpers --> JSON
    
    %% Database Collections
    MongoDB --> Users
    MongoDB --> Conversations
    MongoDB --> Knowledge
    
    %% Data Flow for Chat
    ChatR -.->|1. Extract User Context| JWT
    ChatR -.->|2. Get RAG Results| RAG
    ChatR -.->|3. Generate Response| OpenAI
    ChatR -.->|4. Save Conversation| DB
    
    %% Data Flow for Upload
    UploadR -.->|1. Process File| Helpers
    UploadR -.->|2. Clear Knowledge Base| DB
    UploadR -.->|3. Insert Documents| Knowledge
    UploadR -.->|4. Build Vector Store| RAG
    
    %% Styling
    classDef client fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef external fill:#fff3e0
    classDef database fill:#fce4ec
    
    class UI client
    class FastAPI,JWT api
    class AuthR,ChatR,CRMR,UploadR,ResetR api
    class OpenAI,RAG,CRM,DB service
    class Helpers,CSV,PDF,TXT,JSON service
    class OpenAIAPI,MongoDB,VectorDB external
    class Users,Conversations,Knowledge database
```

## System Components

### 1. Client Layer
- **Web UI / API Client**: Frontend applications consuming the REST API

### 2. API Gateway
- **FastAPI Server**: Main application server running on port 8000
- **JWT Middleware**: Token verification for protected endpoints

### 3. API Routes
- **Authentication Routes** (`/auth/*`): Login, user information
- **Chat Routes** (`/chat`): AI conversations with RAG integration
- **CRM Routes** (`/crm/*`): User profile management
- **Upload Routes** (`/upload_docs/`): Document upload and processing
- **Reset Routes** (`/reset`): Clear conversation memory

### 4. Services Layer
- **OpenAI Service**: Integration with GPT-4o-mini for chat responses
- **RAG Service**: FAISS vector store for retrieval-augmented generation
- **CRM Service**: User profile and preference management
- **Database Service**: MongoDB connection and operations

### 5. Data Processing
- **helpers.py**: Centralized file processing utilities
- **File Processors**: Support for CSV, PDF, TXT, JSON formats

### 6. External Services
- **OpenAI API**: GPT-4o-mini for natural language processing
- **MongoDB**: Document database for 
- **FAISS Vector Store**: Local vector database for semantic search

### 7. Database Collections
- **users_collection**: User profiles and preferences
- **conversations_collection**: Chat history and metadata
- **knowledge_base_collection**: RAG document store

## Data Flow

### Chat Request Flow
1. Client sends message to `/chat` endpoint
2. JWT middleware extracts user context (ID, email, company, preferences)
3. RAG service performs semantic search on knowledge base
4. OpenAI service generates personalized response using user context + RAG results
5. Conversation saved to MongoDB with category classification
6. Response returned with metadata (response time, category)

### Document Upload Flow
1. Client uploads file to `/upload_docs/` endpoint
2. File processor (CSV/PDF/TXT/JSON) extracts structured content
3. Existing knowledge base cleared from MongoDB
4. New documents inserted into knowledge_base_collection
5. FAISS vector store rebuilt from new documents
6. Upload confirmation returned with vector store status

## Security Features
- **JWT Authentication**: Secure token-based user authentication
- **Token Verification**: All protected endpoints validate JWT tokens
- **User Context Isolation**: Conversations linked to authenticated users
- **File Type Validation**: Only allowed file formats accepted

