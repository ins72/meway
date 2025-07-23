#!/usr/bin/env python3
"""
Create Test User for Authentication Testing
Creates the test user tmonnens@outlook.com with password Voetballen5
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from core.database import connect_to_mongo, get_users_collection
from core.auth import get_password_hash
from datetime import datetime
import uuid

async def create_test_user():
    """Create the test user for authentication"""
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        users_collection = get_users_collection()
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": "tmonnens@outlook.com"})
        if existing_user:
            print("✅ Test user already exists")
            return
        
        # Create test user
        hashed_password = get_password_hash("Voetballen5")
        user_data = {
            "_id": str(uuid.uuid4()),
            "email": "tmonnens@outlook.com",
            "hashed_password": hashed_password,
            "full_name": "Tom Onnens",
            "is_active": True,
            "is_admin": True,  # Make admin for testing
            "role": "admin",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await users_collection.insert_one(user_data)
        print(f"✅ Test user created successfully: {user_data['email']}")
        print(f"   User ID: {user_data['_id']}")
        print(f"   Admin: {user_data['is_admin']}")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_test_user())