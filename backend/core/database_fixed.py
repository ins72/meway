
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mewayz_professional")

# Async client for FastAPI
async_client = None
database = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global async_client, database
    try:
        async_client = AsyncIOMotorClient(MONGODB_URL)
        database = async_client[DATABASE_NAME]
        # Test connection
        await async_client.admin.command('ping')
        print("✅ MongoDB connected successfully")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

async def close_mongo_connection():
    """Close MongoDB connection"""
    global async_client
    if async_client:
        async_client.close()

def get_database():
    """Get database instance"""
    return database

# Sync client for testing
def get_sync_client():
    """Get synchronous MongoDB client"""
    return MongoClient(MONGODB_URL)
