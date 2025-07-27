@echo off
echo 🚀 Starting Mewayz Platform Deployment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service status
echo 📊 Service Status:
docker-compose ps

echo.
echo ✅ Deployment complete!
echo.
echo 🌐 Services available at:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    MongoDB: localhost:5000
echo.
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo 🔍 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
pause 