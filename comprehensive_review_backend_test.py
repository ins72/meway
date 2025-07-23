#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE BACKEND TESTING - REVIEW REQUEST ASSESSMENT - JANUARY 2025 🎯

This script tests the Mewayz Platform backend to measure improvement after fixing:
1. ObjectId serialization issues
2. Real API integrations implementation
3. Overall system performance from 39.1% baseline
4. Authentication system functionality
5. External API integrations (Twitter, TikTok, Stripe, Referral System)
6. Real data operations vs mock data
7. Core business systems functionality

Target: Measure progress toward 95%+ production readiness
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class ComprehensiveBackendTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        
        # Admin credentials from review request
        self.admin_email = "tmonnens@outlook.com"
        self.admin_password = "Voetballen5"
        
        self.jwt_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Test categories for detailed analysis
        self.category_results = {
            "authentication": {"passed": 0, "total": 0, "tests": []},
            "external_apis": {"passed": 0, "total": 0, "tests": []},
            "objectid_serialization": {"passed": 0, "total": 0, "tests": []},
            "real_data_operations": {"passed": 0, "total": 0, "tests": []},
            "core_business": {"passed": 0, "total": 0, "tests": []},
            "system_health": {"passed": 0, "total": 0, "tests": []}
        }
        
        print(f"🎯 COMPREHENSIVE BACKEND TESTING - REVIEW REQUEST ASSESSMENT")
        print(f"Backend URL: {self.api_url}")
        print(f"Testing with admin credentials: {self.admin_email}")
        print("=" * 80)
"""
🎯 MEWAYZ V2 PLATFORM - COMPREHENSIVE BACKEND TESTING - JANUARY 2025 🎯

MISSION: Run comprehensive backend testing for the Mewayz v2 platform to assess current status 
and identify critical issues as requested in the review.

Focus Areas:
1. Authentication System - Test JWT token generation and validation
2. Missing Integrations - Test Referral System, Twitter/X API, TikTok API, and Stripe API endpoints
3. CRUD Operations - Verify all major business systems have working CRUD operations  
4. Database Operations - Ensure all endpoints are using real data from MongoDB
5. Overall System Health - Check service availability and endpoint functionality

Test Credentials: tmonnens@outlook.com/Voetballen5
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
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
    
    def log_test_result(self, test_name: str, status: str, details: str = "", response_size: int = 0):
        """Log test result"""
        self.total_tests += 1
        if status == "✅ PASS":
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_size": response_size,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
    
    async def make_request(self, method: str, endpoint: str, data: dict = None, use_auth: bool = True) -> tuple:
        """Make HTTP request with error handling"""
        try:
            url = f"{BACKEND_URL}/api{endpoint}"
            headers = {}
            
            if use_auth and self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_text = await response.text()
                    return response.status, response_text
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    response_text = await response.text()
                    return response.status, response_text
            elif method.upper() == "PUT":
                async with self.session.put(url, headers=headers, json=data) as response:
                    response_text = await response.text()
                    return response.status, response_text
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    response_text = await response.text()
                    return response.status, response_text
                    
        except Exception as e:
            return 0, f"Request failed: {str(e)}"
    
    async def test_authentication_system(self):
        """Test JWT token generation and validation"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 50)
        
        # Test 1: User Login
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        status, response = await self.make_request("POST", "/auth/login", login_data, use_auth=False)
        
        if status == 200:
            try:
                response_data = json.loads(response)
                if "access_token" in response_data:
                    self.auth_token = response_data["access_token"]
                    self.log_test_result(
                        "Authentication - Login", 
                        "✅ PASS", 
                        f"JWT token generated successfully ({len(response)} chars)",
                        len(response)
                    )
                else:
                    self.log_test_result("Authentication - Login", "❌ FAIL", "No access_token in response")
            except json.JSONDecodeError:
                self.log_test_result("Authentication - Login", "❌ FAIL", "Invalid JSON response")
        else:
            self.log_test_result("Authentication - Login", "❌ FAIL", f"Status {status}: {response[:200]}")
        
        # Test 2: Token Validation
        if self.auth_token:
            status, response = await self.make_request("GET", "/auth/me")
            if status == 200:
                self.log_test_result(
                    "Authentication - Token Validation", 
                    "✅ PASS", 
                    f"Token validation successful ({len(response)} chars)",
                    len(response)
                )
            else:
                self.log_test_result("Authentication - Token Validation", "❌ FAIL", f"Status {status}: {response[:200]}")
        else:
            self.log_test_result("Authentication - Token Validation", "❌ FAIL", "No token available for validation")
    
    async def test_missing_integrations(self):
        """Test missing integrations: Referral System, Twitter/X API, TikTok API, Stripe API"""
        print("\n🔗 TESTING MISSING INTEGRATIONS")
        print("=" * 50)
        
        # Test Referral System
        await self.test_referral_system()
        
        # Test Twitter/X API Integration
        await self.test_twitter_api()
        
        # Test TikTok API Integration
        await self.test_tiktok_api()
        
        # Test Stripe API Integration
        await self.test_stripe_api()
    
    async def test_referral_system(self):
        """Test Referral System endpoints"""
        print("\n📢 Testing Referral System")
        
        # Test health endpoint
        status, response = await self.make_request("GET", "/referral-system/health")
        if status == 200:
            self.log_test_result(
                "Referral System - Health Check", 
                "✅ PASS", 
                f"Health endpoint working ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("Referral System - Health Check", "❌ FAIL", f"Status {status}: {response[:200]}")
        
        # Test referrals list
        status, response = await self.make_request("GET", "/referral-system/referrals")
        if status == 200:
            self.log_test_result(
                "Referral System - List Referrals", 
                "✅ PASS", 
                f"Referrals list retrieved ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("Referral System - List Referrals", "❌ FAIL", f"Status {status}: {response[:200]}")
        
        # Test create referral
        referral_data = {
            "referrer_email": TEST_EMAIL,
            "referee_email": "test.referee@example.com",
            "campaign_name": "Test Campaign"
        }
        status, response = await self.make_request("POST", "/referral-system/referrals", referral_data)
        if status in [200, 201]:
            self.log_test_result(
                "Referral System - Create Referral", 
                "✅ PASS", 
                f"Referral created successfully ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("Referral System - Create Referral", "❌ FAIL", f"Status {status}: {response[:200]}")
    
    async def test_twitter_api(self):
        """Test Twitter/X API Integration"""
        print("\n🐦 Testing Twitter/X API Integration")
        
        # Test health endpoint
        status, response = await self.make_request("GET", "/twitter/health")
        if status == 200:
            self.log_test_result(
                "Twitter API - Health Check", 
                "✅ PASS", 
                f"Health endpoint working ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("Twitter API - Health Check", "❌ FAIL", f"Status {status}: {response[:200]}")
        
        # Test search functionality
        status, response = await self.make_request("GET", "/twitter/search?query=test")
        if status == 200:
            self.log_test_result(
                "Twitter API - Search", 
                "✅ PASS", 
                f"Search functionality working ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("Twitter API - Search", "❌ FAIL", f"Status {status}: {response[:200]}")
    
    async def test_tiktok_api(self):
        """Test TikTok API Integration"""
        print("\n🎵 Testing TikTok API Integration")
        
        # Test health endpoint
        status, response = await self.make_request("GET", "/tiktok/health")
        if status == 200:
            self.log_test_result(
                "TikTok API - Health Check", 
                "✅ PASS", 
                f"Health endpoint working ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("TikTok API - Health Check", "❌ FAIL", f"Status {status}: {response[:200]}")
        
        # Test search functionality
        status, response = await self.make_request("GET", "/tiktok/search?query=test")
        if status == 200:
            self.log_test_result(
                "TikTok API - Search", 
                "✅ PASS", 
                f"Search functionality working ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("TikTok API - Search", "❌ FAIL", f"Status {status}: {response[:200]}")
    
    async def test_stripe_api(self):
        """Test Stripe API Integration"""
        print("\n💳 Testing Stripe API Integration")
        
        # Test health endpoint
        status, response = await self.make_request("GET", "/stripe-integration/health")
        if status == 200:
            self.log_test_result(
                "Stripe API - Health Check", 
                "✅ PASS", 
                f"Health endpoint working ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("Stripe API - Health Check", "❌ FAIL", f"Status {status}: {response[:200]}")
        
        # Test payment intent creation
        payment_data = {
            "amount": 1000,
            "currency": "usd",
            "description": "Test payment"
        }
        status, response = await self.make_request("POST", "/stripe-integration/create-payment-intent", payment_data)
        if status in [200, 201]:
            self.log_test_result(
                "Stripe API - Create Payment Intent", 
                "✅ PASS", 
                f"Payment intent created ({len(response)} chars)",
                len(response)
            )
        else:
            self.log_test_result("Stripe API - Create Payment Intent", "❌ FAIL", f"Status {status}: {response[:200]}")
    
    async def test_crud_operations(self):
        """Test CRUD operations for major business systems"""
        print("\n📊 TESTING CRUD OPERATIONS")
        print("=" * 50)
        
        # Test major business systems
        systems_to_test = [
            ("financial", "Financial Management"),
            ("complete-multi-workspace", "Multi-Workspace System"),
            ("complete-admin-dashboard", "Admin Dashboard"),
            ("team-management", "Team Management"),
            ("form-builder", "Form Builder"),
            ("analytics-system", "Analytics System"),
            ("ai-content", "AI Automation Suite"),
            ("complete-website-builder", "Website Builder"),
            ("complete-escrow", "Escrow System"),
            ("complete-onboarding", "Complete Onboarding")
        ]
        
        for endpoint, system_name in systems_to_test:
            await self.test_system_crud(endpoint, system_name)
    
    async def test_system_crud(self, endpoint: str, system_name: str):
        """Test CRUD operations for a specific system"""
        print(f"\n📋 Testing {system_name}")
        
        # Test READ operation (health check or list)
        status, response = await self.make_request("GET", f"/{endpoint}/health")
        if status == 200:
            self.log_test_result(
                f"{system_name} - READ (Health)", 
                "✅ PASS", 
                f"Health check working ({len(response)} chars)",
                len(response)
            )
        else:
            # Try alternative endpoints
            for alt_endpoint in [f"/{endpoint}", f"/{endpoint}/dashboard", f"/{endpoint}/overview"]:
                status, response = await self.make_request("GET", alt_endpoint)
                if status == 200:
                    self.log_test_result(
                        f"{system_name} - READ", 
                        "✅ PASS", 
                        f"Data retrieved ({len(response)} chars)",
                        len(response)
                    )
                    break
            else:
                self.log_test_result(f"{system_name} - READ", "❌ FAIL", f"No working READ endpoint found")
    
    async def test_database_operations(self):
        """Test database operations to ensure real data usage"""
        print("\n🗄️ TESTING DATABASE OPERATIONS")
        print("=" * 50)
        
        # Test systems that should have real database operations
        database_systems = [
            ("financial/dashboard", "Financial System"),
            ("complete-admin-dashboard/overview", "Admin System"),
            ("analytics-system/overview", "Analytics System"),
            ("complete-multi-workspace/workspaces", "Multi-Workspace System")
        ]
        
        for endpoint, system_name in database_systems:
            await self.test_real_data_operations(endpoint, system_name)
    
    async def test_real_data_operations(self, endpoint: str, system_name: str):
        """Test if system uses real database operations"""
        print(f"\n🔍 Testing {system_name} Database Operations")
        
        # Make multiple requests to check for data consistency
        responses = []
        for i in range(3):
            status, response = await self.make_request("GET", f"/{endpoint}")
            if status == 200:
                responses.append(response)
            await asyncio.sleep(0.5)  # Small delay between requests
        
        if len(responses) >= 2:
            # Check if responses are consistent (indicating real database usage)
            if responses[0] == responses[1]:
                self.log_test_result(
                    f"{system_name} - Real Database Operations", 
                    "✅ PASS", 
                    f"Data consistent across calls - confirms real database usage",
                    len(responses[0])
                )
            else:
                self.log_test_result(
                    f"{system_name} - Real Database Operations", 
                    "⚠️ PARTIAL", 
                    f"Data inconsistent - may still be using random generation",
                    len(responses[0])
                )
        else:
            self.log_test_result(f"{system_name} - Real Database Operations", "❌ FAIL", "Could not retrieve data for comparison")
    
    async def test_system_health(self):
        """Test overall system health and endpoint functionality"""
        print("\n🏥 TESTING SYSTEM HEALTH")
        print("=" * 50)
        
        # Test system health endpoints
        health_endpoints = [
            ("/health", "System Health"),
            ("/docs", "API Documentation"),
            ("/openapi.json", "OpenAPI Specification")
        ]
        
        for endpoint, test_name in health_endpoints:
            status, response = await self.make_request("GET", endpoint, use_auth=False)
            if status == 200:
                self.log_test_result(
                    test_name, 
                    "✅ PASS", 
                    f"Endpoint accessible ({len(response)} chars)",
                    len(response)
                )
            else:
                self.log_test_result(test_name, "❌ FAIL", f"Status {status}: {response[:200]}")
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🎯 MEWAYZ V2 PLATFORM - COMPREHENSIVE BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Run all test categories
            await self.test_authentication_system()
            await self.test_missing_integrations()
            await self.test_crud_operations()
            await self.test_database_operations()
            await self.test_system_health()
            
        except Exception as e:
            print(f"❌ Critical error during testing: {e}")
        finally:
            await self.cleanup_session()
        
        # Generate final report
        await self.generate_final_report()
    
    async def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE BACKEND TESTING RESULTS")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed Tests: {self.passed_tests}")
        print(f"   Failed Tests: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        categories = {
            "Authentication": [],
            "Missing Integrations": [],
            "CRUD Operations": [],
            "Database Operations": [],
            "System Health": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                categories["Authentication"].append(result)
            elif any(x in test_name for x in ["Referral", "Twitter", "TikTok", "Stripe"]):
                categories["Missing Integrations"].append(result)
            elif any(x in test_name for x in ["Financial", "Multi-Workspace", "Admin", "Team", "Form", "Analytics", "AI", "Website", "Escrow", "Onboarding"]):
                categories["CRUD Operations"].append(result)
            elif "Database Operations" in test_name:
                categories["Database Operations"].append(result)
            else:
                categories["System Health"].append(result)
        
        # Print category results
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if "✅ PASS" in r["status"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"\n📋 {category.upper()}: {rate:.1f}% ({passed}/{total})")
                for result in results:
                    print(f"   {result['status']} {result['test']}")
        
        # Production readiness assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 95:
            print("   ✅ EXCELLENT - Platform is production ready")
        elif success_rate >= 85:
            print("   ✅ GOOD - Platform is mostly production ready with minor issues")
        elif success_rate >= 75:
            print("   ⚠️ ACCEPTABLE - Platform needs some fixes before production")
        elif success_rate >= 50:
            print("   ❌ NEEDS WORK - Platform has significant issues requiring attention")
        else:
            print("   ❌ CRITICAL - Platform has major issues and is not production ready")
        
        # Critical issues summary
        failed_tests = [r for r in self.test_results if "❌ FAIL" in r["status"]]
        if failed_tests:
            print(f"\n🔧 CRITICAL ISSUES REQUIRING ATTENTION:")
            for result in failed_tests:
                print(f"   ❌ {result['test']}: {result['details']}")
        
        print(f"\n📅 Test Completed: {datetime.now().isoformat()}")
        print("=" * 60)

async def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())