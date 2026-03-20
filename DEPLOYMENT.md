# 🚀 Production Deployment Guide

## Overview
This guide covers deploying the AI News Dashboard to production using Docker.

## Prerequisites
- Docker and Docker Compose installed
- Production PostgreSQL database (Render, AWS RDS, etc.)
- Domain name (optional but recommended)
- SSL certificate (optional but recommended)

## Environment Setup

### 1. Configure Production Environment
Copy and configure your production environment variables:

```bash
cp .env.example .env.production
```

Edit `.env.production` with your production settings:
- Database URL (PostgreSQL)
- Groq API key
- Email credentials (if using email broadcast)
- Domain names for CORS

### 2. Update CORS Configuration
In `backend/main.py`, update the `allowed_origins` list with your actual domain:

```python
if settings.is_production:
    allowed_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ]
```

## Deployment Options

### Option 1: Docker Compose (Recommended)
Deploy using the provided production Docker Compose:

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Option 2: Manual Docker Compose
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Option 3: Cloud Platform Deployment

#### Render.com
1. Connect your GitHub repository
2. Create two services:
   - **Web Service** (Backend): Docker, port 8000
   - **Static Site** (Frontend): Build with `npm run build:prod`
3. Add environment variables from `.env.production`

#### AWS ECS
1. Build and push Docker images to ECR
2. Create ECS task definitions
3. Set up Application Load Balancer
4. Configure RDS PostgreSQL instance

#### DigitalOcean App Platform
1. Connect repository
2. Create app with two components:
   - Backend (Docker)
   - Frontend (Static)
3. Add environment variables

## Production Features

### Security
- Non-root Docker user
- Security headers (CORS, XSS protection, etc.)
- Environment-based configuration
- No debug mode in production

### Performance
- Gunicorn WSGI server with multiple workers
- Nginx reverse proxy with gzip compression
- Static asset caching
- Optimized Docker builds

### Monitoring
- Structured logging
- Health check endpoints
- Container health monitoring

## Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string
- `GROQ_API_KEY`: Groq API key for AI features
- `ENVIRONMENT`: Set to "production"

### Optional
- `SMTP_*`: Email broadcast settings
- `LINKEDIN_ACCESS_TOKEN`: LinkedIn integration
- `WHATSAPP_*`: WhatsApp integration

## SSL/HTTPS Setup

### Option 1: Cloud Provider (Recommended)
Use your cloud provider's built-in SSL:
- Render: Automatic SSL
- AWS: ACM + ALB
- DigitalOcean: Automatic SSL

### Option 2: Let's Encrypt with Nginx
Add to `nginx.conf`:
```nginx
listen 443 ssl;
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

## Monitoring and Logs

### Application Logs
```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Health Checks
- Backend: `GET /health`
- Frontend: `GET /` (returns 200)

### Monitoring Services
Consider adding:
- Prometheus + Grafana
- Sentry for error tracking
- LogDNA or Papertrail for log aggregation

## Scaling

### Horizontal Scaling
```bash
# Scale backend workers
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Database Scaling
- Use managed PostgreSQL service
- Enable connection pooling
- Monitor performance metrics

## Backup Strategy

### Database Backups
```bash
# Create backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql $DATABASE_URL < backup_20231201_120000.sql
```

### Automated Backups
- Use your cloud provider's backup service
- Set up daily automated backups
- Test restore procedures regularly

## Troubleshooting

### Common Issues
1. **Database Connection**: Check DATABASE_URL format
2. **CORS Errors**: Verify allowed origins in main.py
3. **Build Failures**: Check Docker logs and requirements
4. **Memory Issues**: Monitor container resource usage

### Debug Commands
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Enter container for debugging
docker-compose -f docker-compose.prod.yml exec backend bash

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

## Maintenance

### Regular Tasks
- Update dependencies
- Monitor disk space
- Check log file sizes
- Review security updates

### Update Process
```bash
# Pull latest code
git pull origin main

# Redeploy
./deploy.sh
```

## Security Checklist
- [ ] Environment variables set correctly
- [ ] No hardcoded secrets in code
- [ ] SSL certificates configured
- [ ] CORS properly configured
- [ ] Database access restricted
- [ ] Regular security updates applied
