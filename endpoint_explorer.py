#!/usr/bin/env python3
"""
🔍 MEWAYZ V2 PLATFORM - DETAILED ENDPOINT EXPLORATION - JANUARY 2025 🔍

This script explores available endpoints to understand the current system state better.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://bd15977c-5d37-4fb8-991c-847ae2409f32.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class EndpointExplorer:
    def __init__(self):
        self.session = None
        self.auth_token = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"}
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self):
        """Get authentication token"""
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            async with self.session.post(url, json=login_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if "access_token" in response_data:
                        self.auth_token = response_data["access_token"]
                        print("✅ Authentication successful")
                        return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
        
        return False
    
    async def test_endpoint(self, endpoint: str, method: str = "GET", data: dict = None):
        """Test a specific endpoint"""
        try:
            url = f"{BACKEND_URL}/api{endpoint}"
            headers = {}
            
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    status = response.status
                    text = await response.text()
                    return status, text
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    status = response.status
                    text = await response.text()
                    return status, text
                    
        except Exception as e:
            return 0, f"Request failed: {str(e)}"
    
    async def explore_system_endpoints(self):
        """Explore various system endpoints"""
        print("\n🔍 EXPLORING SYSTEM ENDPOINTS")
        print("=" * 50)
        
        # Try different system endpoints
        endpoints_to_test = [
            "/health",
            "/docs",
            "/openapi.json",
            "/metrics",
            "/status",
            "/info"
        ]
        
        for endpoint in endpoints_to_test:
            status, response = await self.test_endpoint(endpoint)
            print(f"{endpoint}: Status {status} ({len(response)} chars)")
            if status == 200 and len(response) < 500:
                print(f"  Response: {response[:200]}...")
    
    async def explore_business_endpoints(self):
        """Explore business system endpoints"""
        print("\n🏢 EXPLORING BUSINESS ENDPOINTS")
        print("=" * 50)
        
        # Test various business endpoints
        business_endpoints = [
            "/financial/dashboard",
            "/financial/overview",
            "/financial",
            "/complete-admin-dashboard/overview",
            "/complete-admin-dashboard/dashboard",
            "/complete-admin-dashboard",
            "/analytics-system/overview",
            "/analytics-system/dashboard",
            "/analytics-system",
            "/complete-multi-workspace/workspaces",
            "/complete-multi-workspace/dashboard",
            "/complete-multi-workspace"
        ]
        
        for endpoint in business_endpoints:
            status, response = await self.test_endpoint(endpoint)
            print(f"{endpoint}: Status {status} ({len(response)} chars)")
            if status == 200:
                print(f"  ✅ Working endpoint found!")
                if len(response) < 300:
                    print(f"  Sample: {response[:150]}...")
    
    async def explore_integration_endpoints(self):
        """Explore integration endpoints in detail"""
        print("\n🔗 EXPLORING INTEGRATION ENDPOINTS")
        print("=" * 50)
        
        # Test referral system endpoints
        print("\n📢 Referral System Endpoints:")
        referral_endpoints = [
            "/referral-system/health",
            "/referral-system",
            "/referral-system/dashboard",
            "/referral-system/programs",
            "/referral-system/referrals",
            "/complete-referral-system/health",
            "/complete-referral-system",
            "/referral/health",
            "/referral"
        ]
        
        for endpoint in referral_endpoints:
            status, response = await self.test_endpoint(endpoint)
            print(f"  {endpoint}: Status {status} ({len(response)} chars)")
            if status == 200:
                print(f"    ✅ Working!")
        
        # Test Twitter endpoints
        print("\n🐦 Twitter API Endpoints:")
        twitter_endpoints = [
            "/twitter/health",
            "/twitter",
            "/twitter/search",
            "/twitter/profile",
            "/twitter/leads"
        ]
        
        for endpoint in twitter_endpoints:
            status, response = await self.test_endpoint(endpoint)
            print(f"  {endpoint}: Status {status} ({len(response)} chars)")
            if status == 200:
                print(f"    ✅ Working!")
        
        # Test TikTok endpoints
        print("\n🎵 TikTok API Endpoints:")
        tiktok_endpoints = [
            "/tiktok/health",
            "/tiktok",
            "/tiktok/search",
            "/tiktok/profile",
            "/tiktok/leads"
        ]
        
        for endpoint in tiktok_endpoints:
            status, response = await self.test_endpoint(endpoint)
            print(f"  {endpoint}: Status {status} ({len(response)} chars)")
            if status == 200:
                print(f"    ✅ Working!")
        
        # Test Stripe endpoints
        print("\n💳 Stripe Integration Endpoints:")
        stripe_endpoints = [
            "/stripe-integration/health",
            "/stripe-integration",
            "/stripe-integration/payment-intents",
            "/stripe-integration/customers",
            "/stripe-integration/test"
        ]
        
        for endpoint in stripe_endpoints:
            status, response = await self.test_endpoint(endpoint)
            print(f"  {endpoint}: Status {status} ({len(response)} chars)")
            if status == 200:
                print(f"    ✅ Working!")
    
    async def run_exploration(self):
        """Run comprehensive endpoint exploration"""
        print("🔍 MEWAYZ V2 PLATFORM - DETAILED ENDPOINT EXPLORATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Started: {datetime.now().isoformat()}")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Authenticate first
            await self.authenticate()
            
            # Explore different endpoint categories
            await self.explore_system_endpoints()
            await self.explore_business_endpoints()
            await self.explore_integration_endpoints()
            
        except Exception as e:
            print(f"❌ Critical error during exploration: {e}")
        finally:
            await self.cleanup_session()
        
        print(f"\n📅 Exploration Completed: {datetime.now().isoformat()}")

async def main():
    """Main exploration execution"""
    explorer = EndpointExplorer()
    await explorer.run_exploration()

if __name__ == "__main__":
    asyncio.run(main())