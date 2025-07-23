#!/usr/bin/env python3
"""
Focused Backend Testing for Review Request - January 2025
Testing specific systems mentioned in the review request:
1. Authentication - JWT token generation and validation
2. Referral System - Complete CRUD operations
3. Twitter/X API - Beyond health check (list, create, search)
4. TikTok API - Beyond health check (list, create, search)
5. Stripe Integration - Beyond health check (list, create, get payment methods)
6. Core Business Systems - Financial system, admin dashboard

Admin credentials: tmonnens@outlook.com/Voetballen5
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from frontend .env
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class FocusedBackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_length": len(str(response_data)) if response_data else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request with proper error handling"""
        try:
            url = f"{API_BASE}{endpoint}"
            headers = {}
            
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers, params=params) as response:
                    response_data = await response.json()
                    return response.status, response_data
            elif method.upper() == "POST":
                headers["Content-Type"] = "application/json"
                async with self.session.post(url, headers=headers, json=data) as response:
                    response_data = await response.json()
                    return response.status, response_data
            elif method.upper() == "PUT":
                headers["Content-Type"] = "application/json"
                async with self.session.put(url, headers=headers, json=data) as response:
                    response_data = await response.json()
                    return response.status, response_data
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    response_data = await response.json()
                    return response.status, response_data
                    
        except Exception as e:
            logger.error(f"Request error for {method} {endpoint}: {e}")
            return 500, {"error": str(e)}
    
    async def test_authentication_system(self):
        """Test 1: Authentication - JWT token generation and validation"""
        logger.info("🔐 Testing Authentication System...")
        
        # Test login with admin credentials
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        status, response = await self.make_request("POST", "/auth/login", login_data)
        
        if status == 200 and "access_token" in response:
            self.auth_token = response["access_token"]
            self.log_test_result(
                "Authentication - JWT Token Generation",
                True,
                f"Login successful, token received ({len(str(response))} chars response)",
                response
            )
            
            # Test token validation by accessing protected endpoint
            status, profile_response = await self.make_request("GET", "/auth/me")
            if status == 200:
                self.log_test_result(
                    "Authentication - JWT Token Validation",
                    True,
                    f"Token validation successful ({len(str(profile_response))} chars response)",
                    profile_response
                )
            else:
                self.log_test_result(
                    "Authentication - JWT Token Validation",
                    False,
                    f"Token validation failed: {status} - {profile_response.get('detail', 'Unknown error')}"
                )
        else:
            self.log_test_result(
                "Authentication - JWT Token Generation",
                False,
                f"Login failed: {status} - {response.get('detail', 'Unknown error')}"
            )
            
    async def test_referral_system(self):
        """Test 2: Referral System - Complete CRUD operations"""
        logger.info("🔗 Testing Referral System...")
        
        # Health check
        status, response = await self.make_request("GET", "/referral/health")
        self.log_test_result(
            "Referral System - Health Check",
            status == 200,
            f"Health check: {status} ({len(str(response))} chars response)",
            response
        )
        
        # List referrals
        status, response = await self.make_request("GET", "/referral/")
        self.log_test_result(
            "Referral System - List Referrals",
            status == 200,
            f"List operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Create referral
        referral_data = {
            "referrer_email": ADMIN_EMAIL,
            "referred_email": "test.referral@example.com",
            "referral_code": f"REF_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "commission_rate": 0.1,
            "status": "active"
        }
        
        status, response = await self.make_request("POST", "/referral/", referral_data)
        referral_id = None
        if status == 200 and response.get("success"):
            referral_id = response.get("data", {}).get("id")
            
        self.log_test_result(
            "Referral System - Create Referral",
            status == 200,
            f"Create operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Update referral (if created successfully)
        if referral_id:
            update_data = {"status": "completed", "commission_paid": True}
            status, response = await self.make_request("PUT", f"/referral/{referral_id}", update_data)
            self.log_test_result(
                "Referral System - Update Referral",
                status == 200,
                f"Update operation: {status} ({len(str(response))} chars response)",
                response
            )
            
            # Delete referral
            status, response = await self.make_request("DELETE", f"/referral/{referral_id}")
            self.log_test_result(
                "Referral System - Delete Referral",
                status == 200,
                f"Delete operation: {status} ({len(str(response))} chars response)",
                response
            )
        else:
            self.log_test_result(
                "Referral System - Update Referral",
                False,
                "Cannot test update - referral creation failed"
            )
            self.log_test_result(
                "Referral System - Delete Referral",
                False,
                "Cannot test delete - referral creation failed"
            )
    
    async def test_twitter_api(self):
        """Test 3: Twitter/X API - Beyond health check"""
        logger.info("🐦 Testing Twitter/X API...")
        
        # Health check
        status, response = await self.make_request("GET", "/twitter/health")
        self.log_test_result(
            "Twitter API - Health Check",
            status == 200,
            f"Health check: {status} ({len(str(response))} chars response)",
            response
        )
        
        # List tweets
        status, response = await self.make_request("GET", "/twitter/")
        self.log_test_result(
            "Twitter API - List Tweets",
            status == 200,
            f"List operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Create tweet
        tweet_data = {
            "text": f"Test tweet from Mewayz platform - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            "scheduled_time": None,
            "media_urls": []
        }
        
        status, response = await self.make_request("POST", "/twitter/", tweet_data)
        self.log_test_result(
            "Twitter API - Create Tweet",
            status == 200,
            f"Create operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Search tweets
        status, response = await self.make_request("GET", "/twitter/search", params={"query": "mewayz", "limit": 10})
        self.log_test_result(
            "Twitter API - Search Tweets",
            status == 200,
            f"Search operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Get profile
        status, response = await self.make_request("GET", "/twitter/profile", params={"username": "mewayz"})
        self.log_test_result(
            "Twitter API - Get Profile",
            status == 200,
            f"Profile operation: {status} ({len(str(response))} chars response)",
            response
        )
    
    async def test_tiktok_api(self):
        """Test 4: TikTok API - Beyond health check"""
        logger.info("🎵 Testing TikTok API...")
        
        # Health check
        status, response = await self.make_request("GET", "/tiktok/health")
        self.log_test_result(
            "TikTok API - Health Check",
            status == 200,
            f"Health check: {status} ({len(str(response))} chars response)",
            response
        )
        
        # List posts
        status, response = await self.make_request("GET", "/tiktok/")
        self.log_test_result(
            "TikTok API - List Posts",
            status == 200,
            f"List operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Create post
        post_data = {
            "title": f"Test TikTok post - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "Test post from Mewayz platform",
            "video_url": "https://example.com/test-video.mp4",
            "hashtags": ["#mewayz", "#test", "#platform"]
        }
        
        status, response = await self.make_request("POST", "/tiktok/", post_data)
        self.log_test_result(
            "TikTok API - Create Post",
            status == 200,
            f"Create operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Search videos
        status, response = await self.make_request("GET", "/tiktok/search", params={"query": "business", "limit": 10})
        self.log_test_result(
            "TikTok API - Search Videos",
            status == 200,
            f"Search operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Upload video
        upload_data = {
            "title": "Test Upload",
            "description": "Test video upload",
            "video_data": "base64_encoded_video_data_placeholder",
            "privacy": "public"
        }
        
        status, response = await self.make_request("POST", "/tiktok/upload", upload_data)
        self.log_test_result(
            "TikTok API - Upload Video",
            status == 200,
            f"Upload operation: {status} ({len(str(response))} chars response)",
            response
        )
    
    async def test_stripe_integration(self):
        """Test 5: Stripe Integration - Beyond health check"""
        logger.info("💳 Testing Stripe Integration...")
        
        # Health check
        status, response = await self.make_request("GET", "/stripe-integration/health")
        self.log_test_result(
            "Stripe Integration - Health Check",
            status == 200,
            f"Health check: {status} ({len(str(response))} chars response)",
            response
        )
        
        # List payments
        status, response = await self.make_request("GET", "/stripe-integration/")
        self.log_test_result(
            "Stripe Integration - List Payments",
            status == 200,
            f"List operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Create payment intent
        payment_data = {
            "amount": 2000,  # $20.00 in cents
            "currency": "usd",
            "description": "Test payment from Mewayz platform",
            "customer_email": ADMIN_EMAIL
        }
        
        status, response = await self.make_request("POST", "/stripe-integration/", payment_data)
        self.log_test_result(
            "Stripe Integration - Create Payment Intent",
            status == 200,
            f"Create operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Get payment methods
        status, response = await self.make_request("GET", "/stripe-integration/payment-methods")
        self.log_test_result(
            "Stripe Integration - Get Payment Methods",
            status == 200,
            f"Payment methods: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Create customer
        customer_data = {
            "email": ADMIN_EMAIL,
            "name": "Test Customer",
            "description": "Test customer for Mewayz platform"
        }
        
        status, response = await self.make_request("POST", "/stripe-integration/customers", customer_data)
        self.log_test_result(
            "Stripe Integration - Create Customer",
            status == 200,
            f"Create customer: {status} ({len(str(response))} chars response)",
            response
        )
    
    async def test_core_business_systems(self):
        """Test 6: Core Business Systems - Financial system, admin dashboard"""
        logger.info("🏢 Testing Core Business Systems...")
        
        # Financial System
        status, response = await self.make_request("GET", "/financial/health")
        self.log_test_result(
            "Financial System - Health Check",
            status == 200,
            f"Health check: {status} ({len(str(response))} chars response)",
            response
        )
        
        status, response = await self.make_request("GET", "/financial/")
        self.log_test_result(
            "Financial System - List Financial Records",
            status == 200,
            f"List operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Create financial record
        financial_data = {
            "type": "income",
            "amount": 1500.00,
            "description": "Test financial record",
            "category": "services",
            "date": datetime.utcnow().isoformat()
        }
        
        status, response = await self.make_request("POST", "/financial/", financial_data)
        self.log_test_result(
            "Financial System - Create Financial Record",
            status == 200,
            f"Create operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Admin Dashboard System
        status, response = await self.make_request("GET", "/admin/health")
        self.log_test_result(
            "Admin Dashboard - Health Check",
            status == 200,
            f"Health check: {status} ({len(str(response))} chars response)",
            response
        )
        
        status, response = await self.make_request("GET", "/admin/")
        self.log_test_result(
            "Admin Dashboard - List Admin Records",
            status == 200,
            f"List operation: {status} ({len(str(response))} chars response)",
            response
        )
        
        # Get admin stats
        status, response = await self.make_request("GET", "/admin/stats")
        self.log_test_result(
            "Admin Dashboard - Get Statistics",
            status == 200,
            f"Stats operation: {status} ({len(str(response))} chars response)",
            response
        )
    
    async def run_all_tests(self):
        """Run all focused tests"""
        logger.info("🚀 Starting Focused Backend Testing for Review Request...")
        logger.info(f"Backend URL: {BACKEND_URL}")
        logger.info(f"Admin Credentials: {ADMIN_EMAIL}")
        
        start_time = datetime.utcnow()
        
        try:
            # Test 1: Authentication System
            await self.test_authentication_system()
            
            # Only proceed with other tests if authentication succeeded
            if self.auth_token:
                # Test 2: Referral System
                await self.test_referral_system()
                
                # Test 3: Twitter/X API
                await self.test_twitter_api()
                
                # Test 4: TikTok API
                await self.test_tiktok_api()
                
                # Test 5: Stripe Integration
                await self.test_stripe_integration()
                
                # Test 6: Core Business Systems
                await self.test_core_business_systems()
            else:
                logger.error("❌ Authentication failed - skipping other tests")
                
        except Exception as e:
            logger.error(f"❌ Test execution error: {e}")
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 FOCUSED BACKEND TESTING RESULTS - REVIEW REQUEST ASSESSMENT")
        logger.info("=" * 80)
        logger.info(f"📊 Overall Success Rate: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        logger.info(f"⏱️  Total Duration: {duration:.2f} seconds")
        logger.info(f"🔐 Authentication: {'✅ Working' if self.auth_token else '❌ Failed'}")
        logger.info(f"🌐 Backend URL: {BACKEND_URL}")
        
        # Categorize results
        categories = {
            "Authentication": [],
            "Referral System": [],
            "Twitter API": [],
            "TikTok API": [],
            "Stripe Integration": [],
            "Core Business Systems": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                categories["Authentication"].append(result)
            elif "Referral" in test_name:
                categories["Referral System"].append(result)
            elif "Twitter" in test_name:
                categories["Twitter API"].append(result)
            elif "TikTok" in test_name:
                categories["TikTok API"].append(result)
            elif "Stripe" in test_name:
                categories["Stripe Integration"].append(result)
            elif "Financial" in test_name or "Admin" in test_name:
                categories["Core Business Systems"].append(result)
        
        # Print category summaries
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅ EXCELLENT" if rate >= 80 else "⚠️ PARTIAL" if rate >= 50 else "❌ CRITICAL"
                logger.info(f"📋 {category}: {status} - {rate:.1f}% ({passed}/{total} tests passed)")
        
        # Save detailed results
        results_data = {
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "success_rate": success_rate,
                "duration_seconds": duration,
                "backend_url": BACKEND_URL,
                "authentication_working": bool(self.auth_token),
                "timestamp": start_time.isoformat()
            },
            "test_results": self.test_results
        }
        
        with open("/app/focused_review_test_results.json", "w") as f:
            json.dump(results_data, f, indent=2)
        
        logger.info("💾 Detailed results saved to: /app/focused_review_test_results.json")
        logger.info("=" * 80)
        
        return success_rate

async def main():
    """Main test execution"""
    async with FocusedBackendTester() as tester:
        success_rate = await tester.run_all_tests()
        
        # Return appropriate exit code
        if success_rate >= 75:
            logger.info("🎉 SUCCESS: Platform meets production readiness criteria (≥75% success rate)")
            return 0
        elif success_rate >= 50:
            logger.info("⚠️ PARTIAL: Platform has issues but core functionality working")
            return 1
        else:
            logger.info("❌ CRITICAL: Platform has major issues requiring immediate attention")
            return 2

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)