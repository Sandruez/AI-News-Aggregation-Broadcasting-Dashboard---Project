# Railway Deployment Guide (with External Render Database)

## 🚀 Quick Setup

### Prerequisites
- Railway account (https://railway.app)
- Render PostgreSQL database (already set up)
- Groq API key (https://console.groq.com)

### Step 1: Connect GitHub Repository
1. Go to Railway Dashboard
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your AI News Dashboard repository
4. Click "Deploy Now"

### Step 2: Configure Environment Variables
In Railway Dashboard → Settings → Variables, add:

```bash
# Database (from Render)
DATABASE_URL=postgresql+asyncpg://render_user:render_password@your-render-db-host.railway.app:5432/your_database_name

# Groq AI (required)
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=llama3-8b-8192

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# News Ingestion
FETCH_INTERVAL_MINUTES=15
MAX_ITEMS_PER_SOURCE=50

# Optional: Email Broadcasting
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_FROM=your-email@gmail.com
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
```

### Step 3: Deploy Configuration
The project includes:
- ✅ `railway.toml` - Railway service configuration
- ✅ `docker-compose.railway.yml` - Multi-service deployment
- ✅ `.env.railway` - Environment variables template
- ✅ Health checks and automatic restarts

### Step 4: Verify Deployment
After deployment, you should have:
- 🌐 **Frontend**: `https://your-app-name.railway.app`
- 🔧 **Backend**: `https://your-app-name.railway.app/api`
- 📊 **Admin Panel**: `https://your-app-name.railway.app/admin`

## 📋 Configuration Files

### Railway Services
- **Frontend**: Nginx serving React SPA
- **Backend**: FastAPI with Gunicorn
- **Database**: External Render PostgreSQL

### Health Checks
- Frontend: HTTP check on port 80
- Backend: `/health` endpoint on port 8000
- Automatic restarts on failure

## 🔧 Database Setup (Render)

### Get Render Database URL
1. Go to Render Dashboard
2. Select your PostgreSQL service
3. Copy the "External Database URL"
4. Format for SQLAlchemy:
   ```
   postgresql+asyncpg://username:password@host:port/database_name
   ```

### Database Connection
The backend will automatically connect to your Render database using the `DATABASE_URL` environment variable.

## 🎯 Features Deployed

### ✅ Core Features
- News aggregation from multiple sources
- AI-powered content analysis (Groq)
- Duplicate detection and filtering
- Search and categorization
- Favorites system
- Broadcasting to multiple platforms

### ✅ Admin Dashboard
- Real-time analytics and monitoring
- Source distribution charts
- System health monitoring
- Recent activity logs
- Performance metrics

### ✅ Production Optimizations
- Docker containerization
- Health checks and monitoring
- Automatic restarts
- Environment-based configuration
- Optimized builds for production

## 🌐 Accessing Your App

### Main Application
- URL: `https://your-app-name.railway.app`
- Features: News feed, search, favorites, sources

### Admin Panel
- URL: `https://your-app-name.railway.app/admin`
- Features: Analytics, monitoring, system health

### API Endpoints
- Base URL: `https://your-app-name.railway.app/api`
- Documentation: `https://your-app-name.railway.app/docs`

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
**Solution**: Verify `DATABASE_URL` format and Render database is accessible.

#### 2. Groq API Errors
**Solution**: Check `GROQ_API_KEY` is valid and has credits.

#### 3. Frontend Not Loading
**Solution**: Check `VITE_API_URL` matches Railway domain.

#### 4. Admin Panel Empty
**Solution**: Verify all backend endpoints are working.

### Health Check URLs
- Frontend: `https://your-app-name.railway.app/`
- Backend Health: `https://your-app-name.railway.app/api/health`
- Admin API: `https://your-app-name.railway.app/api/admin/overview`

## 📈 Monitoring

### Railway Dashboard
- Service logs and metrics
- Deployment history
- Resource usage
- Environment variables

### Admin Panel
- Real-time system health
- Performance metrics
- Error tracking
- User activity

## 🔄 Updates

### Automatic Deployments
- Push to `main` branch → Auto-deploy
- Railway builds and deploys automatically
- Zero-downtime deployments

### Manual Deployments
- Railway Dashboard → Deployments
- Select branch and commit
- Trigger manual deployment

## 🎉 Success!

Your AI News Dashboard is now running on Railway with:
- ✅ External Render database
- ✅ Production-optimized configuration
- ✅ Health monitoring and auto-restart
- ✅ Admin dashboard with analytics
- ✅ Full feature set deployed

**Ready for production use!** 🚀
