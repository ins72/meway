# 🚀 Mewayz Professional Platform

A comprehensive SaaS platform built with React frontend, FastAPI backend, and MongoDB database. Features include workspace management, subscription handling, AI-powered content generation, and social media integration.

## 🌟 Features

### Core Platform
- **Multi-workspace Management** - Create and manage multiple workspaces
- **User Authentication** - Secure JWT-based authentication system
- **Subscription Management** - Flexible subscription plans with Stripe integration
- **AI Content Generation** - AI-powered content creation and optimization
- **Social Media Integration** - Connect and manage multiple social media accounts
- **Analytics Dashboard** - Comprehensive analytics and reporting
- **Real-time Notifications** - Live updates and notifications

### Technical Stack
- **Frontend**: React 18 with Tailwind CSS
- **Backend**: FastAPI with Python 3.11+
- **Database**: MongoDB with Motor async driver
- **Authentication**: JWT tokens with bcrypt
- **Payments**: Stripe integration
- **Deployment**: Docker with docker-compose

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (optional - simplified mode available)
- Docker (optional)

### Option 1: Quick Start (Windows)
```bash
# Run the automated startup script
start_services.bat
```

### Option 2: Manual Setup
```bash
# 1. Start Backend
cd backend
pip install -r requirements.txt
python main_simple.py

# 2. Start Frontend (in new terminal)
cd frontend
npm install
npm start
```

### Option 3: Docker Deployment
```bash
# Install Docker Desktop first, then:
docker-compose up --build -d
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: localhost:5000

## 📋 API Endpoints

### Health Checks
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/health` - API health
- `GET /readiness` - Kubernetes readiness
- `GET /liveness` - Kubernetes liveness

### Core API
- `GET /api/users` - Get users
- `GET /api/workspaces` - Get workspaces
- `GET /api/subscription/plans` - Get subscription plans
- `POST /api/auth/login` - Login
- `GET /api/ai/generate` - AI content generation

## 🗄️ Database Schema

### Collections
- `users` - User accounts and profiles
- `workspaces` - Workspace management
- `subscriptions` - Subscription data
- `payments` - Payment records
- `integrations` - Third-party integrations
- `ai_usage` - AI feature usage tracking
- `social_posts` - Social media posts
- `analytics` - Analytics data

## 🔧 Configuration

### Environment Variables

#### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_STRIPE_PUBLISHABLE_KEY=your_stripe_key
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

#### Backend
```env
MONGODB_URL=mongodb://localhost:27017/mewayz
JWT_SECRET=your-super-secret-jwt-key
CORS_ORIGINS=http://localhost:3000
```

## 🛠️ Development

### Project Structure
```
mewayz/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   └── main.py            # Main application
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── contexts/       # React contexts
│   └── public/            # Static files
├── docker/                # Docker configuration
├── docker-compose.yml     # Service orchestration
└── docs/                  # Documentation
```

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Production Deployment
1. Update environment variables with production values
2. Set up SSL certificates
3. Configure proper CORS origins
4. Use production MongoDB instance
5. Set up monitoring and logging
6. Configure backup strategies

### Docker Deployment
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- Rate limiting
- Secure headers

## 📈 Monitoring

- Health check endpoints
- Application logging
- Error tracking
- Performance monitoring
- Database monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [DEPLOYMENT_README.md](DEPLOYMENT_README.md)
- **Issues**: Create an issue on GitHub
- **Email**: support@mewayz.com

## 🚀 Roadmap

- [ ] Advanced AI features
- [ ] Mobile app
- [ ] White-label solution
- [ ] Enterprise features
- [ ] Advanced analytics
- [ ] Multi-language support

---

**Built with ❤️ by the Mewayz Team**