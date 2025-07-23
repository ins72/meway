#!/usr/bin/env python3
"""
Direct Website Builder Service Test
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

async def test_service():
    """Test the service directly"""
    try:
        from services.website_builder_service import get_website_builder_service
        
        service = get_website_builder_service()
        print("✅ Service instance created")
        
        # Test health check
        health_result = await service.health_check()
        print(f"Health check result: {health_result}")
        
        # Test create operation
        test_data = {
            "name": "Test Website",
            "template_id": "modern-business",
            "domain": "test-site.mewayz.com",
            "description": "Test website for audit",
            "category": "business",
            "user_id": "test-user",
            "created_by": "tmonnens@outlook.com"
        }
        
        create_result = await service.create_website(test_data)
        print(f"Create result: {create_result}")
        
        if create_result.get("success"):
            print("✅ CREATE operation working")
        else:
            print(f"❌ CREATE operation failed: {create_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Service test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service())