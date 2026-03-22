# 🚂 Railway Deployment Guide

This guide explains how to deploy the AI News Dashboard on Railway.app.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Connect your repository to Railway
3. **Groq API Key**: Get from [Groq Console](https://console.groq.com)

## 🛠️ Railway Setup

### **Step 1: Create Railway Project**
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub repository
4. Select the AI News Dashboard repository

### **Step 2: Configure Environment Variables**
Add these environment variables in Railway project settings:

```bash
# Database (Railway will provide this automatically)
DATABASE_URL=postgresql+asyncpg://username:password@hostname:port/database_name

# Groq AI (required)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# News Ingestion
FETCH_INTERVAL_MINUTES=15
MAX_ITEMS_PER_SOURCE=50

# Email Broadcast (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_FROM=your-email@gmail.com
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password

# Frontend API URL
VITE_API_URL=https://your-app-name.railway.app
```

### **Step 3: Add PostgreSQL Database**
1. In Railway project, click "+ New"
2. Select "PostgreSQL"
3. Railway will automatically set `DATABASE_URL`

### **Step 4: Configure Services**
The `railway.toml` file will automatically configure:
- **Backend**: Port 8000 with health checks
- **Frontend**: Port 80 with health checks
- **Database**: PostgreSQL with persistent storage

## 🐳 Local Testing

Before deploying to Railway, test locally:

```bash
# 1. Copy Railway environment template
cp .env.railway .env.local

# 2. Fill in your actual credentials in .env.local
# - Groq API Key
# - Database URL (use local PostgreSQL for testing)
# - Email credentials (optional)

# 3. Build and run with Railway Docker Compose
docker-compose -f docker-compose.railway.yml up -d

# 4. Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:8000
# Health Check: http://localhost:8000/health
```

## 🚀 Railway Deployment

### **Automatic Deployment**
Railway will automatically:
1. Build Docker images using `docker-compose.railway.yml`
2. Start services in correct order
3. Set up networking between services
4. Configure health checks
5. Assign public URLs

### **Service URLs**
After deployment, your services will be available at:
- **Frontend**: `https://your-app-name.railway.app`
- **Backend API**: `https://your-backend-name.railway.app`
- **Database**: Internal connection only

## 📊 Railway Features

### **Automatic Scaling**
- **Free Tier**: 500 hours/month
- **Hobby Tier**: $5/month, auto-scaling
- **Pro Tier**: Custom pricing

### **Monitoring**
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, network usage
- **Health Checks**: Automatic service monitoring
- **Alerts**: Email notifications for issues

### **Database**
- **Managed PostgreSQL**: Automatic backups
- **Persistent Storage**: Data survives restarts
- **Connection Pooling**: Optimized performance
- **SSL**: Encrypted connections

## 🔧 Configuration Details

### **railway.toml Configuration**
```toml
[build]
builder = "NIXPACKS"  # Railway's build system

[deploy]
startCommand = "docker-compose -f docker-compose.railway.yml up"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[services]]
name = "frontend"
[services.ports]
port = 80
[services.health_checks]
grace_period = 30
interval = "15s"
timeout = "10s"
retries = 3
```

### **Docker Configuration**
- **Backend**: Production Dockerfile with Gunicorn
- **Frontend**: Multi-stage build with Nginx
- **Database**: PostgreSQL 15 Alpine
- **Networking**: Internal service communication

## 🔄 CI/CD Pipeline

Railway automatically:
1. **Detects Changes**: GitHub webhook integration
2. **Builds Images**: Uses Docker configuration
3. **Runs Tests**: Health check validation
4. **Deploys Services**: Zero-downtime deployment
5. **Updates DNS**: Automatic URL assignment

## 🛡️ Security

### **Railway Security Features**
- ✅ HTTPS by default
- ✅ Private networking between services
- ✅ Environment variable encryption
- ✅ Automatic SSL certificates
- ✅ Isolated containers

### **Best Practices**
- Use environment variables for all secrets
- Enable database backups
- Monitor service health regularly
- Set up alerting for errors

## 📈 Performance Optimization

### **Backend Optimizations**
- ✅ Gunicorn WSGI server
- ✅ PostgreSQL connection pooling
- ✅ Health checks with graceful restarts
- ✅ Non-root container execution

### **Frontend Optimizations**
- ✅ Nginx reverse proxy
- ✅ Static asset optimization
- ✅ Gzip compression
- ✅ SPA routing support

## 🔍 Troubleshooting

### **Common Issues**

**Build Failures**
- Check Dockerfile syntax
- Verify environment variables
- Review build logs

**Database Connection**
- Verify `DATABASE_URL` format
- Check database service status
- Test connection locally

**Service Health**
- Review health check endpoints
- Check service logs
- Verify port configuration

### **Debug Commands**
```bash
# Check service status
railway status

# View logs
railway logs

# Restart services
railway restart

# Access service shell
railway shell service-name
```

## 💡 Pro Tips

1. **Custom Domains**: Add your own domain in service settings
2. **Environment Groups**: Use separate environments for staging/production
3. **Database Backups**: Enable automatic backups in database settings
4. **Monitoring**: Set up alerting for downtime and errors
5. **Scaling**: Configure auto-scaling based on traffic

## 🆙 Scaling Options

### **Service Scaling**
- **Free**: 500 hours/month
- **Hobby**: $5/month, auto-scaling
- **Pro**: Custom pricing and limits

### **Database Scaling**
- **Hobby**: 1GB storage, 10 connections
- **Pro**: 10GB storage, 100 connections
- **Enterprise**: Custom specifications

---

**Need help?** Check out [Railway's Documentation](https://docs.railway.app) or contact their support team.
