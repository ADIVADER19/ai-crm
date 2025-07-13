# RentRadar Chatbot - API Contracts

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require JWT Bearer token in Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Authentication Endpoints

### POST /auth/login
**Description**: Authenticate user and get JWT token

**Request Body**:
```json
{
  "email": "soham@example.com",
  "password": "123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### GET /auth/me
**Description**: Get current user information
**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "user_id": "6871f142763a555490a74496",
  "email": "soham@example.com",
  "name": "Soham"
}
```

---

## 2. Chat Endpoints

### POST /chat
**Description**: Send message to AI chatbot with RAG integration
**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "message": "Show me properties under $100,000 per month"
}
```

**Response**:
```json
{
  "reply": "Based on your $90,000 budget and Times Square preference, here are relevant Manhattan properties:\n\n1. **221-223 W 37th St** - $94,623/month...",
  "user_id": "6871f142763a555490a74496",
  "conversation_id": "conv_789",
  "category": "property_search",
  "response_time_ms": 1245.67
}
```

### GET /chat/categories
**Description**: Get conversation categories for user
**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "user_id": "6871f142763a555490a74496",
  "categories": ["property_search", "general_inquiry", "pricing_inquiry"]
}
```

---

## 3. Document Upload Endpoints

### POST /upload_docs/
**Description**: Upload documents (PDF/TXT/CSV/JSON) to populate RAG knowledge base
**Headers**: `Authorization: Bearer <token>`

**Request**: Multipart form data
```
file: <binary_file_data>
```

**Response (Success)**:
```json
{
  "message": "Successfully uploaded 200 documents from CSV file",
  "inserted_count": 200,
  "file_type": "csv",
  "vector_store_built": true,
  "note": "Previous knowledge base was replaced with new upload"
}
```

**Response (Vector Store Failed)**:
```json
{
  "message": "Documents uploaded to database but vector store failed to build",
  "inserted_count": 200,
  "file_type": "csv",
  "vector_store_built": false,
  "note": "Try uploading a different document. RAG functionality may not work until vector store is built successfully"
}
```

---

## 4. CRM Endpoints

### POST /crm/create_user
**Description**: Create new user profile

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "company": "ABC Real Estate",
  "preferences": "Looking for Manhattan properties, budget $150k/month"
}
```

**Response**:
```json
{
  "user_id": "6871f142763a555490a74497"
}
```

### PUT /crm/update_user/{user_id}
**Description**: Update user information

**Request Body**:
```json
{
  "preferences": "Updated: Looking for timesquare properties, budget increased to $90000/month",
  "company": "XYZ Real Estate Group"
}
```

**Response**:
```json
{
  "message": "User updated successfully",
  "user": {
    "name": "Soham",
    "email": "soham@example.com",
    "company": "XYZ Real Estate Group",
    "preferences": "Updated: Looking for timesquare properties, budget increased to $90000/month"
  }
}
```

### GET /crm/user/{user_id}
**Description**: Get user profile information

**Response**:
```json
{
  "user": {
    "name": "Soham",
    "email": "soham@example.com",
    "company": "XYZ Real Estate Group",
    "preferences": "Updated: Looking for timesquare properties, budget increased to $90000/month"
  }
}
```

### GET /crm/conversations/{user_id}
**Description**: Get full conversation history for user

**Response**:
```json
{
  "conversations": [
    {
      "conversation_id": "conv_789",
      "category": "property_search",
      "created_at": "2025-01-12T10:30:00Z",
      "messages": [
        {
          "role": "user",
          "content": "Show me properties under $100k",
          "timestamp": "2025-01-12T10:30:00Z"
        },
        {
          "role": "assistant",
          "content": "Here are Manhattan properties under $100k...",
          "timestamp": "2025-01-12T10:30:02Z"
        }
      ]
    }
  ]
}
```

---

## 5. Reset Endpoints

### PUT /reset
**Description**: Clear conversation memory
**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "message": "Conversations reset successfully",
  "response_time_ms": 123.45
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Message cannot be empty"
}
```

### 401 Unauthorized
```json
{
  "detail": "Token has expired"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to process chat message"
}
```

---

## Sample Usage Flow

1. **Login**: `POST /auth/login` → Get JWT token
2. **Upload Data**: `POST /upload_docs/` → Upload CSV with property data
3. **Chat**: `POST /chat` → Send messages and get AI responses
4. **Update Profile**: `PUT /crm/update_user/{user_id}` → Set preferences
5. **View History**: `GET /crm/conversations/{user_id}` → See past conversations

---

## Features

- **JWT Authentication**: Secure token-based authentication
- **RAG Integration**: Retrieval-Augmented Generation with vector search
- **Conversation Memory**: Full chat history persistence
- **User Personalization**: Responses based on user preferences and company
- **Multi-format Upload**: Support for PDF, TXT, CSV, JSON files
- **Real-time Processing**: Response time metadata included
- **Category Classification**: Automatic conversation categorization
