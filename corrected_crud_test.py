#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - CORRECTED CRUD TESTING
Testing with the correct endpoint paths from OpenAPI specification
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "tmonnens@outlook.com",
    "password": "Voetballen5"
}

async def test_corrected_crud_endpoints():
    """Test CRUD endpoints with correct paths"""
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        # Get authentication token
        async with session.post(
            f"{BACKEND_URL}/api/auth/login",
            json=TEST_CREDENTIALS,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                auth_data = await response.json()
                auth_token = auth_data.get("access_token")
                print(f"✅ Authentication successful")
            else:
                print(f"❌ Authentication failed: {response.status}")
                return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        # Test the correct CRUD endpoints
        print("\n🔍 Testing CORRECT CRUD endpoints:")
        
        # Financial System CRUD
        print("\n💰 Financial System CRUD:")
        
        # Test GET
        async with session.get(f"{BACKEND_URL}/api/complete-financial/", headers=headers) as response:
            status_icon = "✅" if response.status == 200 else "❌"
            print(f"{status_icon} GET /api/complete-financial/: Status {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"   Response: {len(str(data))} chars")
            else:
                error = await response.text()
                print(f"   Error: {error}")
        
        # Test POST
        financial_data = {
            "type": "income",
            "amount": 1500.00,
            "description": "Review Test Transaction",
            "category": "consulting"
        }
        async with session.post(f"{BACKEND_URL}/api/complete-financial/", json=financial_data, headers=headers) as response:
            status_icon = "✅" if response.status == 200 else "❌"
            print(f"{status_icon} POST /api/complete-financial/: Status {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"   Created: {data}")
            else:
                error = await response.text()
                print(f"   Error: {error}")

        # Referral System CRUD
        print("\n🔗 Referral System CRUD:")
        
        # Test GET
        async with session.get(f"{BACKEND_URL}/api/referral-system/", headers=headers) as response:
            status_icon = "✅" if response.status == 200 else "❌"
            print(f"{status_icon} GET /api/referral-system/: Status {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"   Response: {len(str(data))} chars")
            else:
                error = await response.text()
                print(f"   Error: {error}")
        
        # Test POST
        referral_data = {
            "program_name": "Review Test Program",
            "commission_rate": 0.15,
            "status": "active"
        }
        async with session.post(f"{BACKEND_URL}/api/referral-system/", json=referral_data, headers=headers) as response:
            status_icon = "✅" if response.status == 200 else "❌"
            print(f"{status_icon} POST /api/referral-system/: Status {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"   Created: {data}")
            else:
                error = await response.text()
                print(f"   Error: {error}")

        # Workspace System CRUD
        print("\n🏢 Workspace System CRUD:")
        
        # Test GET
        async with session.get(f"{BACKEND_URL}/api/workspace/", headers=headers) as response:
            status_icon = "✅" if response.status == 200 else "❌"
            print(f"{status_icon} GET /api/workspace/: Status {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"   Response: {len(str(data))} chars")
            else:
                error = await response.text()
                print(f"   Error: {error}")
        
        # Test POST
        workspace_data = {
            "name": f"Review Test Workspace {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "description": "Workspace created during review testing",
            "type": "business"
        }
        async with session.post(f"{BACKEND_URL}/api/workspace/", json=workspace_data, headers=headers) as response:
            status_icon = "✅" if response.status == 200 else "❌"
            print(f"{status_icon} POST /api/workspace/: Status {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"   Created: {data}")
            else:
                error = await response.text()
                print(f"   Error: {error}")

if __name__ == "__main__":
    asyncio.run(test_corrected_crud_endpoints())