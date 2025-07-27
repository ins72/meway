#!/bin/bash

# Mewayz Professional Platform - Production Startup Script

echo "Starting Mewayz Professional Platform..."

# Check environment variables
required_vars=("MONGO_URL" "JWT_SECRET_KEY" "STRIPE_SECRET_KEY" "STRIPE_PUBLISHABLE_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var environment variable is not set"
        exit 1
    fi
done

echo "Environment variables verified"

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4 --log-level info
