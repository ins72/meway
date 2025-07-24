from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/health")
def health_api():
    return {"status": "healthy"}

@app.get("/readiness")
def readiness():
    return {"ready": True}

@app.get("/liveness")
def liveness():
    return {"alive": True}