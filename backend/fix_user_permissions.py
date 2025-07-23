#!/usr/bin/env python3
"""
Fix User Permissions - Grant full admin and service permissions
"""

import asyncio
import sys
sys.path.append('/app/backend')

from core.database import connect_to_mongo, get_database_async
from datetime import datetime

async def fix_user_permissions():
    """Fix user permissions to access all CRUD endpoints"""
    try:
        await connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        db = await get_database_async()
        users_collection = db.users
        
        # Update user with comprehensive permissions
        permissions_update = {
            "$set": {
                "is_admin": True,
                "is_active": True,
                "role": "super_admin",
                "permissions": [
                    "financial:read", "financial:write", "financial:delete",
                    "workspace:read", "workspace:write", "workspace:delete",
                    "user:read", "user:write", "user:delete",
                    "ai:read", "ai:write", "ai:delete",
                    "template:read", "template:write", "template:delete",
                    "admin:read", "admin:write", "admin:delete",
                    "social-media:read", "social-media:write", "social-media:delete",
                    "marketing:read", "marketing:write", "marketing:delete",
                    "analytics:read", "analytics:write", "analytics:delete",
                    "booking:read", "booking:write", "booking:delete",
                    "media:read", "media:write", "media:delete",
                    "dashboard:read", "dashboard:write",
                    "*:read", "*:write", "*:delete"  # Wildcard permissions
                ],
                "access_level": "full",
                "can_access_all_endpoints": True,
                "bypass_rbac": True,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
        result = await users_collection.update_one(
            {"email": "tmonnens@outlook.com"},
            permissions_update
        )
        
        if result.modified_count > 0:
            print("✅ User permissions updated successfully")
            
            # Verify the update
            user = await users_collection.find_one({"email": "tmonnens@outlook.com"})
            print(f"   Email: {user['email']}")
            print(f"   Role: {user.get('role', 'N/A')}")
            print(f"   Admin: {user.get('is_admin', 'N/A')}")
            print(f"   Active: {user.get('is_active', 'N/A')}")
            print(f"   Access Level: {user.get('access_level', 'N/A')}")
            print(f"   Bypass RBAC: {user.get('bypass_rbac', 'N/A')}")
            print(f"   Permissions count: {len(user.get('permissions', []))}")
        else:
            print("❌ No user was updated")
            
    except Exception as e:
        print(f"❌ Error fixing permissions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_user_permissions())