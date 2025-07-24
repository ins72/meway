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
    """Create database connection"""
    mongo_url = settings.MONGO_URL
    
    # Log connection attempt (without exposing credentials)
    print(f"🔗 Attempting to connect to MongoDB...")
    print(f"   Database name: {settings.DATABASE_NAME}")
    
    try:
        db.client = AsyncIOMotorClient(mongo_url)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Test connection with timeout
        await asyncio.wait_for(
            db.client.admin.command('ping'), 
            timeout=10.0
        )
        print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
        
        # Also test database access
        collections = await db.database.list_collection_names()
        print(f"   📋 Available collections: {len(collections)}")
        
    except asyncio.TimeoutError:
        print(f"❌ MongoDB connection timeout")
        raise Exception("Database connection timeout - check connection string and network")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print(f"   Check if MONGO_URL environment variable is set correctly")
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