# AI-CRM

A simple AI-powered Customer Relationship Management system with admin functionality.

## Features

- 🤖 **AI Chatbot** - Intelligent responses powered by OpenAI
- 👥 **User Management** - Admin dashboard to manage users and roles
- 🔐 **Authentication** - Secure login/signup with JWT
- 📄 **File Upload** - Admin-only document upload capability
- 🎨 **Modern UI** - Clean React frontend

## Quick Start

### Backend
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables:
   ```
   MONGODB_URI=your_mongodb_connection_string
   SECRET_KEY=your_jwt_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ```
3. Run: `uvicorn main:app --reload`

### Frontend
1. Go to `ai-crm-frontend` folder
2. Install: `npm install`
3. Set backend URL in `.env`:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```
4. Run: `npm run dev`

## Admin Features
- View all users with filtering (name, email, phone)
- Promote users to admin role
- Admin-only file upload access

## Tech Stack
- **Backend**: FastAPI, MongoDB, OpenAI API
- **Frontend**: React, Vite
- **Deploy**: Render (backend), Vercel (frontend)

---
*Simple hobby project for learning AI and web development* 🚀
