"""
Database Connection and Models
Professional Mewayz Platform
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import asyncio
import os
import logging
from .config import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection - production optimized"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/mewayz_professional")
    database_name = "mewayz_professional"
    
    logger.info(f"🔗 Connecting to MongoDB...")
    logger.info(f"   Database: {database_name}")
    
    try:
        db.client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )
        db.database = db.client[database_name]
        
        # Quick ping test
        await db.client.admin.command('ping')
        logger.info(f"✅ MongoDB connected successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        # Set db to None so app knows database is unavailable
        db.client = None
        db.database = None
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("✅ Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database

async def get_database_async():
    """Get database instance (async version for compatibility)"""
    return db.database

# Collection getters - these will return the actual collections
def get_users_collection():
    return db.database.users

def get_workspaces_collection():
    return db.database.workspaces

def get_bio_sites_collection():
    return db.database.bio_sites

def get_analytics_collection():
    return db.database.analytics_events

def get_bookings_collection():
    return db.database.bookings

def get_services_collection():
    return db.database.services

def get_contacts_collection():
    return db.database.contacts

def get_campaigns_collection():
    return db.database.email_campaigns

def get_ai_conversations_collection():
    return db.database.ai_conversations

def get_ai_conversations_collection():
    return db.database.ai_conversations

def get_bio_sites_collection():
    return db.database.bio_sites

def get_notifications_collection():
    return db.database.notifications