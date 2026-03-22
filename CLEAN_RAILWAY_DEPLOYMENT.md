# 🚀 Clean Railway Deployment Guide

## 📋 Project Structure
```
ai-news-dashboard/
├── frontend/
│   ├── Dockerfile.prod          # Frontend Docker build
│   ├── nginx.conf              # Clean nginx config
│   └── src/                    # React app
├── backend/
│   ├── Dockerfile              # Backend Docker build
│   ├── requirements.prod.txt   # Python dependencies
│   └── main.py                 # FastAPI app
├── railway-frontend.toml       # Frontend Railway config
└── railway-backend.toml        # Backend Railway config
```

## 🔧 Backend Deployment

### 1. Create Railway Backend Project
```bash
# Connect your repo to Railway
# Create new project: "ai-news-backend"
# Use railway-backend.toml configuration
```

### 2. Set Backend Environment Variables
Go to Railway → **Variables** → Add:

```env
DATABASE_URL=postgresql+asyncpg://render_user:render_password@your-render-db-host.railway.app:5432/your_database_name
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=production
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

### 3. Get Database Details (Render)
1. **Render Dashboard** → **PostgreSQL** → **Connect** → **External Connection**
2. Copy connection string
3. Convert to format: `postgresql+asyncpg://username:password@host:port/database`

### 4. Get Groq API Key
1. **Groq Console** → **API Keys** → **Create Key**
2. Copy the key

### 5. Deploy Backend
- Railway will auto-deploy from `railway-backend.toml`
- Uses `backend/Dockerfile`
- Health check: `/health`

---

## 🌐 Frontend Deployment

### 1. Create Railway Frontend Project
```bash
# Create new project: "ai-news-frontend"
# Use railway-frontend.toml configuration
```

### 2. Set Frontend Environment Variable
Go to Railway → **Variables** → Add:

```env
VITE_API_URL=https://your-backend-name.railway.app
```

### 3. Get Backend URL
- After backend deployment, Railway gives you URL like:
- `https://ai-news-backend.railway.app`
- Use this for `VITE_API_URL`

### 4. Deploy Frontend
- Railway will auto-deploy from `railway-frontend.toml`
- Uses `frontend/Dockerfile.prod`
- Health check: `/`

---

## ✅ Deployment Order

1. **Deploy Backend First** ✅
   - Set database and API variables
   - Wait for successful deployment
   - Copy backend URL

2. **Deploy Frontend Second** ✅
   - Set `VITE_API_URL` to backend URL
   - Deploy frontend

---

## 🔍 Health Checks

### Backend Health
```bash
curl https://your-backend.railway.app/health
```

### Frontend Health
```bash
curl https://your-frontend.railway.app/
```

---

## 🐛 Troubleshooting

### Backend Issues
- **Database Connection**: Check `DATABASE_URL` format
- **API Key**: Verify `GROQ_API_KEY` is valid
- **Logs**: Railway logs tab (minimal due to disabled logging)

### Frontend Issues
- **API Connection**: Verify `VITE_API_URL` matches backend
- **Build**: Check frontend build logs
- **Nginx**: Ensure static files are served

### Common Issues
- **Rate Limit**: Fixed - logging disabled in production
- **Database**: App starts without DB, connects when available
- **Environment**: All variables properly configured

---

## 🎯 Expected Results

### Backend
- ✅ Healthy at `/health`
- ✅ API endpoints working at `/api/`
- ✅ Database connected (if variables correct)

### Frontend
- ✅ Loads at root URL
- ✅ Connects to backend API
- ✅ All features functional

---

## 📝 Notes

- **Clean Architecture**: No docker-compose, no shared configs
- **Separate Deployments**: Frontend and backend independent
- **Graceful Degradation**: App works without database initially
- **Minimal Logging**: Production logging disabled to avoid rate limits
- **Security**: Proper CORS and nginx headers

🚀 **Your AI News Dashboard is now ready for clean, distributed deployment!**
