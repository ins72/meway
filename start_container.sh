#!/bin/bash
# Container startup script - ensures everything is ready

echo "🚀 CONTAINER STARTUP SCRIPT"
echo "Timestamp: $(date)"

# Set environment variables for container
export PYTHONUNBUFFERED=1
export PYTHONPATH=/app/backend
export PORT=8001

# Log environment info
echo "📊 Environment Variables:"
echo "  PYTHONPATH=$PYTHONPATH"
echo "  PORT=$PORT"
echo "  PWD=$(pwd)"

# Change to backend directory
cd /app/backend

echo "📁 Working directory: $(pwd)"
echo "📄 Files in directory:"
ls -la

# Test Python and FastAPI import
echo "🐍 Testing Python import..."
python -c "
import sys
print(f'Python: {sys.version}')
try:
    from main import app
    print('✅ FastAPI app imported successfully')
    print(f'✅ App title: {app.title}')
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Container startup verification passed"
    echo "🚀 Starting API server..."
    
    # Start the API server
    exec python -m uvicorn main:app --host=0.0.0.0 --port=8001 --log-level=info
else
    echo "❌ Container startup verification failed"
    exit 1
fi