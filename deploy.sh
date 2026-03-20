#!/bin/bash

# AI News Dashboard Production Deployment Script
# Usage: ./deploy.sh

set -e

echo "🚀 Starting AI News Dashboard Production Deployment..."

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please create .env.production with your production settings."
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Build and deploy with Docker Compose
echo "🐳 Building and starting production containers..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check health
echo "🔍 Checking service health..."
curl -f http://localhost:8001/health || {
    echo "❌ Backend health check failed!"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
}

curl -f http://localhost/ || {
    echo "❌ Frontend health check failed!"
    docker-compose -f docker-compose.prod.yml logs frontend
    exit 1
}

echo "✅ Deployment completed successfully!"
echo "🌐 Frontend: http://localhost"
echo "🔧 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"

# Show running containers
echo "📦 Running containers:"
docker-compose -f docker-compose.prod.yml ps
