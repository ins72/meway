@echo off
echo 🚀 Starting Mewayz Platform Services...

echo.
echo 📊 Checking current status...
netstat -an | findstr ":3000\|:8000\|:5000"

echo.
echo 🔧 Starting Backend (Port 8000)...
start "Mewayz Backend" cmd /k "cd backend && python main_simple.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo 🌐 Starting Frontend (Port 3000)...
start "Mewayz Frontend" cmd /k "cd frontend && npm start"

echo.
echo ✅ Services starting...
echo.
echo 🌐 Access Points:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 📝 To stop services, close the command windows or press Ctrl+C
pause 