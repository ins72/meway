#!/usr/bin/env python3
"""
Debug Authentication - Check User and Password
"""

import asyncio
import sys
sys.path.append('/app/backend')

from core.database import connect_to_mongo, get_database_async
from core.auth import verify_password
import json

async def debug_auth():
    """Debug authentication issues"""
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        db = await get_database_async()
        users_collection = db.users
        
        # Find user
        user = await users_collection.find_one({"email": "tmonnens@outlook.com"})
        if not user:
            print("❌ User not found")
            return
        
        print(f"✅ User found: {user['email']}")
        print(f"   Full name: {user.get('full_name', 'N/A')}")
        print(f"   Active: {user.get('is_active', 'N/A')}")
        print(f"   Admin: {user.get('is_admin', 'N/A')}")
        print(f"   Has hashed_password: {'hashed_password' in user}")
        
        # Test password verification
        if 'hashed_password' in user:
            password_valid = verify_password("Voetballen5", user["hashed_password"])
            print(f"   Password valid: {password_valid}")
        else:
            print("   No hashed_password field found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_auth())