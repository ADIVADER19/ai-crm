# AI-CRM Backend Deployment Guide

This FastAPI backend can be deployed to various platforms. Choose the one that best fits your needs:

## 🚀 Deployment Options

### 1. Heroku (Easy, Free Tier Available)

#### Prerequisites:
- Heroku CLI installed
- Git repository

#### Steps:
```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-ai-crm-backend

# Set environment variables
heroku config:set MONGO_URI="your_mongodb_connection_string"
heroku config:set OPENAI_API_KEY="your_openai_api_key"
heroku config:set JWT_SECRET="your_jwt_secret_key"
heroku config:set ALGORITHM="HS256"

# Deploy
git push heroku master
```

### 2. Railway (Modern, Simple)

#### Steps:
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in Railway dashboard:
   - `MONGO_URI`
   - `OPENAI_API_KEY`
   - `JWT_SECRET`
   - `ALGORITHM`
4. Deploy automatically

### 3. Render (Free Tier Available)

#### Steps:
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in Render dashboard

### 4. Vercel (Serverless)

#### Steps:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables
vercel env add MONGO_URI
vercel env add OPENAI_API_KEY
vercel env add JWT_SECRET
vercel env add ALGORITHM
```

### 5. Docker (Any Platform)

#### Build and run locally:
```bash
# Build the image
docker build -t ai-crm-backend .

# Run the container
docker run -p 8000:8000 \
  -e MONGO_URI="your_mongodb_connection_string" \
  -e OPENAI_API_KEY="your_openai_api_key" \
  -e JWT_SECRET="your_jwt_secret_key" \
  -e ALGORITHM="HS256" \
  ai-crm-backend
```

#### Deploy to cloud platforms:
- **Google Cloud Run**
- **AWS ECS**
- **Azure Container Instances**
- **DigitalOcean App Platform**

### 6. Traditional VPS (DigitalOcean, Linode, etc.)

#### Steps:
```bash
# On your server
git clone https://github.com/ADIVADER19/ai-crm.git
cd ai-crm

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGO_URI="your_mongodb_connection_string"
export OPENAI_API_KEY="your_openai_api_key"
export JWT_SECRET="your_jwt_secret_key"
export ALGORITHM="HS256"

# Run with Gunicorn (production)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔧 Environment Variables Required

Make sure to set these environment variables on your chosen platform:

- `MONGO_URI`: Your MongoDB connection string
- `OPENAI_API_KEY`: Your OpenAI API key
- `JWT_SECRET`: A secure secret key for JWT tokens
- `ALGORITHM`: "HS256" (for JWT)

## 🌐 Frontend Deployment

After deploying the backend, update your frontend's API base URL:

1. In `ai-crm-frontend/.env` or `ai-crm-frontend/.env.production`
2. Set `VITE_API_BASE_URL=https://your-backend-url.com`

## 🛡️ Security Considerations

For production deployment:

1. **Use HTTPS**: Ensure your deployment platform provides SSL/TLS
2. **Secure JWT Secret**: Use a strong, randomly generated secret
3. **MongoDB Security**: Use MongoDB Atlas with IP whitelist or proper firewall rules
4. **CORS Configuration**: Update CORS settings in `main.py` for your frontend domain
5. **Rate Limiting**: Consider adding rate limiting for API endpoints

## 📊 Monitoring

Consider adding monitoring and logging:
- **Sentry** for error tracking
- **New Relic** or **DataDog** for performance monitoring
- **Health check endpoints** for uptime monitoring

## 🚀 Recommended Quick Start: Railway

Railway is recommended for beginners due to its simplicity:

1. Push your code to GitHub
2. Go to railway.app and connect your repo
3. Add environment variables
4. Deploy with one click!

Your API will be available at `https://your-app-name.railway.app`
