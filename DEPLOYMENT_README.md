# Mewayz Platform Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git (to clone the repository)

### Deployment Options

#### Option 1: Using Docker Compose (Recommended)

**Windows:**
```bash
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

#### Option 2: Manual Docker Compose
```bash
# Stop any existing containers
docker-compose down

# Build and start services
docker-compose up --build -d

# Check status
docker-compose ps
```

## 📊 Service Architecture

| Service | Port | Description |
|---------|------|-------------|
| Frontend (React) | 3000 | User interface |
| Backend (FastAPI) | 8000 | API server |
| MongoDB | 5000 | Database |

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: localhost:5000

## 🔧 Configuration

### Environment Variables

#### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_STRIPE_PUBLISHABLE_KEY=your_stripe_key
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

#### Backend (docker-compose.yml)
```yaml
environment:
  - MONGODB_URL=mongodb://mongodb:27017/mewayz
  - JWT_SECRET=your-super-secret-jwt-key
  - CORS_ORIGINS=http://localhost:3000
```

## 🗄️ Database

### MongoDB Collections
- `users` - User accounts and profiles
- `workspaces` - Workspace management
- `subscriptions` - Subscription data
- `payments` - Payment records
- `integrations` - Third-party integrations
- `ai_usage` - AI feature usage tracking
- `social_posts` - Social media posts
- `analytics` - Analytics data

### Database Access
```bash
# Connect to MongoDB container
docker exec -it mewayz-mongodb mongosh

# Use the database
use mewayz

# List collections
show collections
```

## 🛠️ Development

### Running Services Individually

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### MongoDB
```bash
docker run -d -p 5000:27017 --name mewayz-mongodb mongo:7.0
```

## 📝 Useful Commands

### Docker Management
```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Rebuild specific service
docker-compose up --build -d backend
```

### Database Management
```bash
# Backup database
docker exec mewayz-mongodb mongodump --db mewayz --out /backup

# Restore database
docker exec mewayz-mongodb mongorestore --db mewayz /backup/mewayz
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :3000
   # Kill the process or change ports in docker-compose.yml
   ```

2. **MongoDB connection failed**
   ```bash
   # Check MongoDB container status
   docker-compose logs mongodb
   
   # Restart MongoDB
   docker-compose restart mongodb
   ```

3. **Frontend can't connect to backend**
   - Check if backend is running: http://localhost:8000/health
   - Verify CORS settings in backend
   - Check proxy configuration in package.json

4. **Build failures**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Health Checks

- **Backend Health**: http://localhost:8000/health
- **API Health**: http://localhost:8000/api/health
- **Readiness**: http://localhost:8000/readiness
- **Liveness**: http://localhost:8000/liveness

## 🔒 Security Notes

- Change default JWT secret in production
- Use strong MongoDB passwords
- Configure proper CORS origins for production
- Set up SSL/TLS for production deployment
- Use environment variables for sensitive data

## 📈 Production Deployment

For production deployment:

1. Update environment variables with production values
2. Set up SSL certificates
3. Configure proper CORS origins
4. Use production MongoDB instance
5. Set up monitoring and logging
6. Configure backup strategies

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Test individual endpoints
4. Check the troubleshooting section above

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Docker Documentation](https://docs.docker.com/) 