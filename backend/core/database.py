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
    """Create database connection - production optimized for Atlas"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/mewayz_professional")
    
    # Extract database name from URL or use default
    if "mongodb+srv://" in mongo_url or "mongodb://" in mongo_url:
        # For Atlas URLs, extract database name from path
        if "/" in mongo_url.split("://")[1]:
            database_name = mongo_url.split("/")[-1].split("?")[0]
        else:
            database_name = "mewayz_professional"
    else:
        database_name = "mewayz_professional"
    
    logger.info(f"🔗 Connecting to MongoDB...")
    logger.info(f"   URL: {mongo_url[:30]}...")
    logger.info(f"   Database: {database_name}")
    
    try:
        # Production-optimized connection settings for Atlas
        connection_settings = {
            "serverSelectionTimeoutMS": 15000,  # 15 seconds for Atlas
            "connectTimeoutMS": 15000,
            "socketTimeoutMS": 15000,
            "maxPoolSize": 50,  # Higher for production
            "minPoolSize": 5,
            "retryWrites": True,
            "retryReads": True,
        }
        
        # Add Atlas-specific settings if it's an Atlas URL
        if "mongodb+srv://" in mongo_url:
            connection_settings.update({
                "ssl": True,
                "tlsAllowInvalidCertificates": False,
            })
        
        db.client = AsyncIOMotorClient(mongo_url, **connection_settings)
        db.database = db.client[database_name]
        
        # Quick ping test with timeout
        await asyncio.wait_for(db.client.admin.command('ping'), timeout=15.0)
        logger.info(f"✅ MongoDB connected successfully to {database_name}")
        
        return True
        
    except asyncio.TimeoutError:
        logger.error(f"❌ MongoDB connection timeout after 15 seconds")
        db.client = None
        db.database = None
        raise
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
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