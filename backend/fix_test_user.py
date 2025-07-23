#!/usr/bin/env python3
"""
Fix Test User - Update with proper password hash
"""

import asyncio
import sys
sys.path.append('/app/backend')

from core.database import connect_to_mongo, get_database_async
from core.auth import get_password_hash
from datetime import datetime

async def fix_test_user():
    """Fix the test user with proper password hash"""
    try:
        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        db = await get_database_async()
        users_collection = db.users
        
        # Update the existing user with proper password hash
        hashed_password = get_password_hash("Voetballen5")
        
        update_result = await users_collection.update_one(
            {"email": "tmonnens@outlook.com"},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "full_name": "Tom Onnens",
                    "is_active": True,
                    "is_admin": True,
                    "role": "admin",
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        if update_result.modified_count > 0:
            print("✅ Test user updated successfully")
            
            # Verify the update
            user = await users_collection.find_one({"email": "tmonnens@outlook.com"})
            print(f"   Email: {user['email']}")
            print(f"   Full name: {user.get('full_name', 'N/A')}")
            print(f"   Active: {user.get('is_active', 'N/A')}")
            print(f"   Admin: {user.get('is_admin', 'N/A')}")
            print(f"   Has hashed_password: {'hashed_password' in user}")
        else:
            print("❌ No user was updated")
        
    except Exception as e:
        print(f"❌ Error fixing user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_test_user())