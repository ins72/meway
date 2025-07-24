#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - DETAILED CRUD INVESTIGATION
Investigating specific CRUD endpoint failures
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://112c0499-f547-4297-a3d4-b823824978f4.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "tmonnens@outlook.com",
    "password": "Voetballen5"
}

async def investigate_crud_endpoints():
    """Investigate CRUD endpoint failures in detail"""
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        # First, get authentication token
        async with session.post(
            f"{BACKEND_URL}/api/auth/login",
            json=TEST_CREDENTIALS,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                auth_data = await response.json()
                auth_token = auth_data.get("access_token")
                print(f"✅ Authentication successful, token length: {len(auth_token) if auth_token else 0}")
            else:
                print(f"❌ Authentication failed: {response.status}")
                return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        # Test different CRUD endpoint patterns
        crud_endpoints_to_test = [
            # Financial endpoints
            ("GET", "/api/complete-financial/transactions", "Financial GET"),
            ("POST", "/api/complete-financial/transactions", "Financial POST", {
                "type": "income",
                "amount": 1500.00,
                "description": "Test Transaction",
                "category": "consulting"
            }),
            ("GET", "/api/financial/transactions", "Financial Alt GET"),
            ("POST", "/api/financial/transactions", "Financial Alt POST", {
                "type": "income",
                "amount": 1500.00,
                "description": "Test Transaction"
            }),
            
            # Referral endpoints
            ("GET", "/api/referral/referrals", "Referral GET"),
            ("POST", "/api/referral/referrals", "Referral POST", {
                "referral_code": "TEST123",
                "referred_email": "test@example.com"
            }),
            ("GET", "/api/referrals", "Referral Alt GET"),
            ("POST", "/api/referrals", "Referral Alt POST", {
                "code": "TEST123",
                "email": "test@example.com"
            }),
            
            # Workspace endpoints
            ("GET", "/api/complete-multi-workspace/workspaces", "Workspace GET"),
            ("POST", "/api/complete-multi-workspace/workspaces", "Workspace POST", {
                "name": "Test Workspace",
                "description": "Test workspace"
            }),
            ("GET", "/api/workspaces", "Workspace Alt GET"),
            ("POST", "/api/workspaces", "Workspace Alt POST", {
                "name": "Test Workspace"
            }),
        ]

        for test_data in crud_endpoints_to_test:
            method = test_data[0]
            endpoint = test_data[1]
            test_name = test_data[2]
            data = test_data[3] if len(test_data) > 3 else None

            try:
                async with session.request(
                    method,
                    f"{BACKEND_URL}{endpoint}",
                    json=data,
                    headers=headers
                ) as response:
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"text": await response.text()}
                    
                    status_icon = "✅" if 200 <= response.status < 300 else "❌"
                    print(f"{status_icon} {test_name}: Status {response.status}")
                    
                    if response.status != 200:
                        print(f"   Error: {response_data}")
                    else:
                        print(f"   Success: {len(str(response_data))} chars response")
                        
            except Exception as e:
                print(f"❌ {test_name}: Exception - {e}")

        # Also test the health endpoints that are working
        print("\n🔍 Testing working health endpoints for comparison:")
        health_endpoints = [
            "/api/complete-financial/health",
            "/api/referral/health", 
            "/api/complete-multi-workspace/health"
        ]
        
        for endpoint in health_endpoints:
            try:
                async with session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                    response_data = await response.json()
                    status_icon = "✅" if response.status == 200 else "❌"
                    print(f"{status_icon} {endpoint}: Status {response.status}")
                    if response.status == 200:
                        print(f"   Response: {response_data}")
            except Exception as e:
                print(f"❌ {endpoint}: Exception - {e}")

if __name__ == "__main__":
    asyncio.run(investigate_crud_endpoints())