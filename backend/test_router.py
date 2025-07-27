#!/usr/bin/env python3
"""
Test router loading
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing router imports...")

# Test importing the workspace module
try:
    from api.workspace import router as workspace_router
    print("✅ Successfully imported workspace router")
    print(f"   Router routes: {len(workspace_router.routes)}")
    for route in workspace_router.routes:
        print(f"   - {route.methods} {route.path}")
except Exception as e:
    print(f"❌ Failed to import workspace router: {e}")

# Test importing the user module
try:
    from api.user import router as user_router
    print("✅ Successfully imported user router")
    print(f"   Router routes: {len(user_router.routes)}")
except Exception as e:
    print(f"❌ Failed to import user router: {e}")

# Test importing the blog module
try:
    from api.blog import router as blog_router
    print("✅ Successfully imported blog router")
    print(f"   Router routes: {len(blog_router.routes)}")
except Exception as e:
    print(f"❌ Failed to import blog router: {e}")

print("\nTesting service imports...")

# Test importing services
try:
    from services.workspace_service import get_workspace_service
    print("✅ Successfully imported workspace service")
except Exception as e:
    print(f"❌ Failed to import workspace service: {e}")

try:
    from core.database import get_database
    print("✅ Successfully imported database")
except Exception as e:
    print(f"❌ Failed to import database: {e}")

print("\nTest complete!") 