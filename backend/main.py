"""
EMERGENCY MINIMAL BACKEND FOR CONTAINER DEPLOYMENT
This is the most basic FastAPI app possible - guaranteed to work in any container
"""

from fastapi import FastAPI
from datetime import datetime
import logging
import sys

# Minimal logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("emergency")

# Create app with absolute minimum configuration
app = FastAPI()

# Enable CORS for all origins
@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

logger.info("Emergency API starting...")

@app.get("/")
def root():
    return {"status": "running", "time": datetime.utcnow().isoformat()}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/health")
def api_health():
    return {"status": "healthy"}

@app.get("/readiness")
def readiness():
    return {"ready": True}

@app.get("/liveness")
def liveness():
    return {"alive": True}

# Catch everything else
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def catch_all():
    return {"message": "API available", "time": datetime.utcnow().isoformat()}

logger.info("Emergency API ready")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)