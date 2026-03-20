# 🚀 Render Deployment Guide

This guide explains how to deploy the AI News Dashboard on Render.com using the provided configuration files.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Connect your GitHub repository to Render
3. **Environment Variables**: Prepare your production credentials

## 🗂️ Configuration Files

### **Backend Deployment** (`render-backend.yaml`)
- **Service Type**: Docker Web Service
- **Runtime**: Python 3.12 with Docker
- **Health Check**: `/health` endpoint
- **Auto-deploy**: Enabled on main branch push
- **Database**: PostgreSQL with 1GB storage

### **Frontend Deployment** (`render-frontend.yaml`)
- **Service Type**: Static Site
- **Build**: `npm ci && npm run build`
- **Output**: Static files from `frontend/dist`
- **Security Headers**: Production-grade security headers

### **Database Service** (`render-db.yaml`)
- **Type**: PostgreSQL
- **Plan**: Free tier (upgradable)
- **Backups**: Enabled with 7-day retention
- **Network**: Private (internal only)

## 🔧 Environment Variables Setup

### **Required Variables**
```bash
# Backend Environment
DATABASE_URL=postgresql+asyncpg://username:password@hostname:port/database_name
GROQ_API_KEY=your_groq_api_key_here
ENVIRONMENT=production
LOG_LEVEL=INFO

# Frontend Environment  
VITE_API_URL=https://your-backend-service.onrender.com
```

### **How to Set Up in Render**
1. Go to your service dashboard
2. Click "Environment" tab
3. Add each variable with "Sync" = false for sensitive data
4. Save and redeploy the service

## 🚀 Deployment Steps

### **Option 1: Blueprint Deployment (Recommended)**
1. Fork the repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Select the appropriate YAML file:
   - Backend: `render-backend.yaml`
   - Frontend: `render-frontend.yaml`
   - Database: `render-db.yaml`

### **Option 2: Manual Service Creation**
1. **Create Database First**:
   - Go to "New +" → "PostgreSQL"
   - Name: `ai-news-dashboard-db`
   - Create database
   - Copy connection string

2. **Create Backend Service**:
   - Go to "New +" → "Web Service"
   - Connect GitHub repository
   - Set environment variables
   - Deploy

3. **Create Frontend Service**:
   - Go to "New +" → "Static Site"
   - Connect GitHub repository
   - Set build command and publish path
   - Deploy

## 🔗 Service URLs After Deployment

Once deployed, your services will be available at:
- **Backend API**: `https://ai-news-dashboard-backend.onrender.com`
- **Frontend App**: `https://ai-news-dashboard-frontend.onrender.com`
- **API Health Check**: `https://ai-news-dashboard-backend.onrender.com/health`

## ⚡ Performance Optimizations

### **Backend Optimizations**
- ✅ Gunicorn WSGI server with optimized workers
- ✅ PostgreSQL connection pooling
- ✅ Health checks with graceful restarts
- ✅ Non-root container execution

### **Frontend Optimizations**
- ✅ Static asset optimization
- ✅ Security headers
- ✅ Gzip compression
- ✅ SPA routing support

## 📊 Monitoring & Logs

### **Render Dashboard Features**
- **Real-time Logs**: View application logs
- **Metrics**: CPU, memory, and response times
- **Health Status**: Service health monitoring
- **Deploy History**: Track deployment changes

### **Log Access**
```bash
# View live logs
render logs ai-news-dashboard-backend

# View service metrics
render dashboard
```

## 🔒 Security Considerations

### **Render Security Features**
- ✅ HTTPS by default
- ✅ Private database networking
- ✅ Environment variable encryption
- ✅ Automatic SSL certificates

### **Recommended Practices**
- Use environment variables for all secrets
- Enable database backups
- Monitor service health regularly
- Set up alerting for errors

## 🔄 CI/CD Integration

### **Automatic Deployments**
Render automatically deploys when:
- Push to `main` branch
- Environment variables are updated
- Manual redeploy is triggered

### **Deployment Hooks**
```yaml
# Custom deployment hooks can be added to render.yaml
preDeploy:
  - echo "Starting deployment..."
postDeploy:
  - echo "Deployment complete!"
```

## 🆕 Scaling Options

### **Backend Scaling**
- **Free Tier**: 512MB RAM, 0.25 CPU
- **Standard Tier**: 1GB RAM, 1 CPU
- **Performance Tier**: 2GB RAM, 2 CPUs

### **Database Scaling**
- **Free**: 256MB storage
- **Standard**: 10GB storage
- **Production**: 100GB storage

## 🛠️ Troubleshooting

### **Common Issues**
1. **Build Failures**: Check package.json and Dockerfile
2. **Database Connection**: Verify DATABASE_URL format
3. **API Errors**: Check environment variables
4. **Frontend 404s**: Verify VITE_API_URL

### **Debug Commands**
```bash
# Check service status
render ps

# View recent logs
render logs --tail 100 ai-news-dashboard-backend

# Trigger manual redeploy
render redeploy ai-news-dashboard-backend
```

## 💡 Pro Tips

1. **Use Custom Domains**: Add your own domain in service settings
2. **Set Up Monitoring**: Configure alerts for downtime
3. **Database Backups**: Enable automatic backups
4. **Environment Groups**: Use separate environments for staging/production
5. **Performance Monitoring**: Use Render's metrics dashboard

---

**Need help?** Check out [Render's Documentation](https://render.com/docs) or contact their support team.
