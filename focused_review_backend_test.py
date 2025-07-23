#!/usr/bin/env python3
"""
FOCUSED REVIEW REQUEST BACKEND TESTING - JANUARY 2025
Testing specific areas mentioned in the review request:
1. Twitter API Integration - Test health, search, and CRUD operations with real Twitter API v2 Bearer token authentication
2. Referral System - Test all endpoints to verify they're working after ObjectId serialization fixes
3. TikTok API - Test endpoints to see if they're operational
4. Stripe Integration - Test endpoints for real payment processing
5. Authentication System - Verify JWT token validation is still working properly

Admin credentials: tmonnens@outlook.com/Voetballen5
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Configuration
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class FocusedReviewTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, status, response_data=None, error=None):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "response_length": len(str(response_data)) if response_data else 0,
            "error": error
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌"
        print(f"{status_emoji} {test_name}: {status}")
        if error:
            print(f"   Error: {error}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response: {len(str(response_data))} chars")
            
    def authenticate(self):
        """Authenticate with admin credentials"""
        try:
            print(f"\n🔐 AUTHENTICATING with {ADMIN_EMAIL}...")
            
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log_result("Authentication", "PASS", data)
                    print(f"✅ Authentication successful - Token: {len(self.auth_token)} chars")
                    return True
                else:
                    self.log_result("Authentication", "FAIL", data, "No access token in response")
                    return False
            else:
                self.log_result("Authentication", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", "FAIL", None, str(e))
            return False
    
    def test_twitter_api_integration(self):
        """Test Twitter API Integration - Focus on real API integration"""
        print(f"\n🐦 TESTING TWITTER API INTEGRATION...")
        
        # Test 1: Health Check
        try:
            response = self.session.get(f"{API_BASE}/twitter/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Twitter Health Check", "PASS", data)
            else:
                self.log_result("Twitter Health Check", "FAIL", None, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Twitter Health Check", "FAIL", None, str(e))
        
        # Test 2: Search Functionality (Real Twitter API v2)
        try:
            response = self.session.get(
                f"{API_BASE}/twitter/search",
                params={"query": "python programming", "limit": 10},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Twitter Search", "PASS", data)
            else:
                self.log_result("Twitter Search", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Twitter Search", "FAIL", None, str(e))
        
        # Test 3: Tweet Creation (CRUD Operation)
        try:
            tweet_data = {
                "text": "Test tweet from Mewayz platform API integration",
                "hashtags": ["#MewayzTest", "#APIIntegration"]
            }
            response = self.session.post(
                f"{API_BASE}/twitter/",
                json=tweet_data,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Twitter Tweet Creation", "PASS", data)
            else:
                self.log_result("Twitter Tweet Creation", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Twitter Tweet Creation", "FAIL", None, str(e))
        
        # Test 4: Analytics/Stats
        try:
            response = self.session.get(f"{API_BASE}/twitter/stats", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Twitter Analytics", "PASS", data)
            else:
                self.log_result("Twitter Analytics", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Twitter Analytics", "FAIL", None, str(e))
    
    def test_referral_system(self):
        """Test Referral System - Focus on ObjectId serialization fixes"""
        print(f"\n🎯 TESTING REFERRAL SYSTEM...")
        
        # Test 1: Health Check
        try:
            response = self.session.get(f"{API_BASE}/referral-system/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Referral System Health Check", "PASS", data)
            else:
                self.log_result("Referral System Health Check", "FAIL", None, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Referral System Health Check", "FAIL", None, str(e))
        
        # Test 2: List Referral Programs
        try:
            response = self.session.get(
                f"{API_BASE}/referral-system/",
                params={"limit": 20, "offset": 0},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Referral System List Programs", "PASS", data)
            else:
                self.log_result("Referral System List Programs", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Referral System List Programs", "FAIL", None, str(e))
        
        # Test 3: Create Referral Program (Test ObjectId serialization)
        try:
            program_data = {
                "name": "Test Referral Program",
                "description": "Testing ObjectId serialization fixes",
                "reward_type": "percentage",
                "reward_value": 10.0,
                "max_referrals": 100,
                "active": True
            }
            response = self.session.post(
                f"{API_BASE}/referral-system/",
                json=program_data,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Referral System Create Program", "PASS", data)
                return data.get("id")  # Return ID for further testing
            else:
                self.log_result("Referral System Create Program", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_result("Referral System Create Program", "FAIL", None, str(e))
            return None
        
        # Test 4: Analytics
        try:
            response = self.session.get(f"{API_BASE}/referral-system/stats", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Referral System Analytics", "PASS", data)
            else:
                self.log_result("Referral System Analytics", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Referral System Analytics", "FAIL", None, str(e))
    
    def test_tiktok_api(self):
        """Test TikTok API - Check if endpoints are operational"""
        print(f"\n🎵 TESTING TIKTOK API...")
        
        # Test 1: Health Check
        try:
            response = self.session.get(f"{API_BASE}/tiktok/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("TikTok Health Check", "PASS", data)
            else:
                self.log_result("TikTok Health Check", "FAIL", None, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("TikTok Health Check", "FAIL", None, str(e))
        
        # Test 2: Search Functionality
        try:
            response = self.session.get(
                f"{API_BASE}/tiktok/search",
                params={"query": "programming tutorial", "limit": 10},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("TikTok Search", "PASS", data)
            else:
                self.log_result("TikTok Search", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("TikTok Search", "FAIL", None, str(e))
        
        # Test 3: Video Upload
        try:
            upload_data = {
                "title": "Test Video Upload",
                "description": "Testing TikTok API integration",
                "video_url": "https://example.com/test-video.mp4",
                "hashtags": ["#test", "#api"]
            }
            response = self.session.post(
                f"{API_BASE}/tiktok/upload",
                json=upload_data,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("TikTok Video Upload", "PASS", data)
            else:
                self.log_result("TikTok Video Upload", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("TikTok Video Upload", "FAIL", None, str(e))
        
        # Test 4: Analytics
        try:
            response = self.session.get(f"{API_BASE}/tiktok/stats", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("TikTok Analytics", "PASS", data)
            else:
                self.log_result("TikTok Analytics", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("TikTok Analytics", "FAIL", None, str(e))
    
    def test_stripe_integration(self):
        """Test Stripe Integration - Real payment processing"""
        print(f"\n💳 TESTING STRIPE INTEGRATION...")
        
        # Test 1: Health Check
        try:
            response = self.session.get(f"{API_BASE}/stripe-integration/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Stripe Health Check", "PASS", data)
            else:
                self.log_result("Stripe Health Check", "FAIL", None, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Stripe Health Check", "FAIL", None, str(e))
        
        # Test 2: Create Payment Intent
        try:
            payment_data = {
                "amount": 2000,  # $20.00 in cents
                "currency": "usd",
                "description": "Test payment for Mewayz platform",
                "customer_email": ADMIN_EMAIL
            }
            response = self.session.post(
                f"{API_BASE}/stripe-integration/",
                json=payment_data,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Stripe Create Payment Intent", "PASS", data)
                return data.get("id")  # Return payment ID for further testing
            else:
                self.log_result("Stripe Create Payment Intent", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_result("Stripe Create Payment Intent", "FAIL", None, str(e))
            return None
        
        # Test 3: Payment Methods
        try:
            response = self.session.get(
                f"{API_BASE}/stripe-integration/payment-methods",
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Stripe Payment Methods", "PASS", data)
            else:
                self.log_result("Stripe Payment Methods", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Stripe Payment Methods", "FAIL", None, str(e))
        
        # Test 4: Create Customer
        try:
            customer_data = {
                "email": ADMIN_EMAIL,
                "name": "Test Customer",
                "description": "Test customer for Mewayz platform"
            }
            response = self.session.post(
                f"{API_BASE}/stripe-integration/customers",
                json=customer_data,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Stripe Create Customer", "PASS", data)
            else:
                self.log_result("Stripe Create Customer", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Stripe Create Customer", "FAIL", None, str(e))
    
    def test_authentication_system(self):
        """Test Authentication System - JWT token validation"""
        print(f"\n🔐 TESTING AUTHENTICATION SYSTEM...")
        
        # Test 1: Token Validation (Get Current User)
        try:
            response = self.session.get(f"{API_BASE}/auth/me", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("JWT Token Validation", "PASS", data)
            else:
                self.log_result("JWT Token Validation", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("JWT Token Validation", "FAIL", None, str(e))
        
        # Test 2: Profile Access
        try:
            response = self.session.get(f"{API_BASE}/auth/profile", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Authentication Profile Access", "PASS", data)
            else:
                self.log_result("Authentication Profile Access", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Authentication Profile Access", "FAIL", None, str(e))
        
        # Test 3: Admin Access (List Auth Records)
        try:
            response = self.session.get(
                f"{API_BASE}/auth/",
                params={"limit": 10, "offset": 0},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_result("Authentication Admin Access", "PASS", data)
            else:
                self.log_result("Authentication Admin Access", "FAIL", None, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Authentication Admin Access", "FAIL", None, str(e))
    
    def run_focused_tests(self):
        """Run all focused tests from review request"""
        print("🎯 FOCUSED REVIEW REQUEST BACKEND TESTING - JANUARY 2025")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Step 2: Test specific areas from review request
        self.test_authentication_system()
        self.test_twitter_api_integration()
        self.test_referral_system()
        self.test_tiktok_api()
        self.test_stripe_integration()
        
        # Step 3: Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 FOCUSED REVIEW REQUEST TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   • Total Tests: {self.total_tests}")
        print(f"   • Passed: {self.passed_tests}")
        print(f"   • Failed: {self.total_tests - self.passed_tests}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        
        # Categorize results by system
        systems = {
            "Authentication System": [r for r in self.test_results if "Authentication" in r["test"] or "JWT" in r["test"]],
            "Twitter API Integration": [r for r in self.test_results if "Twitter" in r["test"]],
            "Referral System": [r for r in self.test_results if "Referral" in r["test"]],
            "TikTok API": [r for r in self.test_results if "TikTok" in r["test"]],
            "Stripe Integration": [r for r in self.test_results if "Stripe" in r["test"]]
        }
        
        print(f"\n📋 SYSTEM-BY-SYSTEM RESULTS:")
        for system_name, results in systems.items():
            if results:
                passed = len([r for r in results if r["status"] == "PASS"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                status_emoji = "✅" if rate >= 75 else "⚠️" if rate >= 50 else "❌"
                print(f"   {status_emoji} {system_name}: {rate:.1f}% ({passed}/{total} tests passed)")
        
        # Improvement analysis
        print(f"\n📈 IMPROVEMENT ANALYSIS:")
        if success_rate >= 95:
            print("   🎉 EXCELLENT - Platform ready for production deployment")
        elif success_rate >= 75:
            print("   ✅ GOOD - Platform meets production readiness criteria")
        elif success_rate >= 50:
            print("   ⚠️ MIXED RESULTS - Some improvements needed")
        else:
            print("   ❌ CRITICAL ISSUES - Major fixes required")
        
        # Critical issues
        failed_tests = [r for r in self.test_results if r["status"] == "FAIL"]
        if failed_tests:
            print(f"\n🔴 CRITICAL ISSUES REQUIRING ATTENTION:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
        
        print(f"\n🎯 REVIEW REQUEST ASSESSMENT:")
        print(f"   • Previous Success Rate: 48% (mentioned in review request)")
        print(f"   • Current Success Rate: {success_rate:.1f}%")
        if success_rate > 48:
            print(f"   • Improvement: +{success_rate - 48:.1f}% ✅")
        else:
            print(f"   • Regression: {success_rate - 48:.1f}% ❌")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = FocusedReviewTester()
    tester.run_focused_tests()
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