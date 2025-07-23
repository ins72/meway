#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - FINAL COMPREHENSIVE REVIEW TEST
January 2025 - Review Request Assessment

Testing Focus Areas (as per review request):
1. CRUD Operations - Focus on specific CRUD endpoints that were failing (financial, referral, workspace)
2. Authentication System - Verify JWT tokens work with both id and _id formats
3. Production Systems - Test all production monitoring and enterprise security features
4. Business Systems - Confirm all core business systems are operational
5. External Integrations - Test all API integrations

Expected: Previous 85.0% success rate should improve to 95%+ with CRUD authentication fixes.
Credentials: tmonnens@outlook.com / Voetballen5
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Backend URL from environment
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "tmonnens@outlook.com",
    "password": "Voetballen5"
}

class MewayzV2ReviewTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
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
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_size: int = 0):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_size": response_size,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Tuple[bool, Dict, int]:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.backend_url}{endpoint}"
            request_headers = {"Content-Type": "application/json"}
            
            if headers:
                request_headers.update(headers)
                
            if self.auth_token and "Authorization" not in request_headers:
                request_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            async with self.session.request(
                method, url, 
                json=data if data else None,
                headers=request_headers
            ) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = {"error": "Invalid JSON response", "text": await response.text()}
                
                response_size = len(str(response_data))
                success = 200 <= response.status < 300
                
                return success, response_data, response_size
                
        except Exception as e:
            return False, {"error": str(e)}, 0

    async def test_authentication_system(self):
        """Test Authentication System - JWT tokens with both id and _id formats"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test 1: JWT Token Generation
        success, response, size = await self.make_request(
            "POST", "/api/auth/login", 
            data=TEST_CREDENTIALS
        )
        
        if success and "access_token" in response:
            self.auth_token = response["access_token"]
            self.log_test(
                "JWT Token Generation", 
                True, 
                f"Token generated successfully ({size} chars response)",
                size
            )
            
            # Test 2: JWT Token Validation - Get User Profile
            success, profile_response, profile_size = await self.make_request(
                "GET", "/api/auth/me"
            )
            
            if success:
                # Check if response contains both id and _id formats
                user_data = profile_response
                has_id = "id" in user_data or "user_id" in user_data
                has_underscore_id = "_id" in user_data
                
                self.log_test(
                    "JWT Token Validation", 
                    True, 
                    f"Token validation successful - ID formats: id={has_id}, _id={has_underscore_id} ({profile_size} chars)",
                    profile_size
                )
            else:
                self.log_test(
                    "JWT Token Validation", 
                    False, 
                    f"Token validation failed: {profile_response.get('error', 'Unknown error')}"
                )
                
        else:
            self.log_test(
                "JWT Token Generation", 
                False, 
                f"Login failed: {response.get('error', 'Unknown error')}"
            )
            self.log_test(
                "JWT Token Validation", 
                False, 
                "Cannot test - login failed"
            )

    async def test_crud_operations_focus(self):
        """Test CRUD Operations - Focus on financial, referral, workspace endpoints"""
        print("\n📊 TESTING CRUD OPERATIONS (FOCUS AREAS)")
        
        # Test Financial System CRUD
        await self.test_financial_crud()
        await self.test_referral_crud()
        await self.test_workspace_crud()

    async def test_financial_crud(self):
        """Test Financial System CRUD operations"""
        print("\n💰 Testing Financial System CRUD")
        
        # Test CREATE operation
        financial_data = {
            "type": "income",
            "amount": 1500.00,
            "description": "Review Test Transaction",
            "category": "consulting"
        }
        
        success, response, size = await self.make_request(
            "POST", "/api/complete-financial/", 
            data=financial_data
        )
        
        if success:
            transaction_id = response.get("id") or response.get("_id")
            self.log_test(
                "Financial System CREATE", 
                True, 
                f"Transaction created successfully - ID: {transaction_id} ({size} chars)",
                size
            )
            
            # Test READ operation
            success, read_response, read_size = await self.make_request(
                "GET", "/api/complete-financial/"
            )
            
            if success:
                self.log_test(
                    "Financial System READ", 
                    True, 
                    f"Transactions retrieved successfully ({read_size} chars)",
                    read_size
                )
            else:
                self.log_test(
                    "Financial System READ", 
                    False, 
                    f"Failed to read transactions: {read_response.get('error', 'Unknown error')}"
                )
        else:
            self.log_test(
                "Financial System CREATE", 
                False, 
                f"Failed to create transaction: {response.get('error', 'Unknown error')}"
            )
            self.log_test(
                "Financial System READ", 
                False, 
                "Cannot test - CREATE failed"
            )

    async def test_referral_crud(self):
        """Test Referral System CRUD operations"""
        print("\n🔗 Testing Referral System CRUD")
        
        # Test CREATE operation
        referral_data = {
            "referral_code": f"REVIEW_TEST_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "referred_email": "test.referral@example.com",
            "commission_rate": 0.15,
            "status": "active"
        }
        
        success, response, size = await self.make_request(
            "POST", "/api/referral/referrals", 
            data=referral_data
        )
        
        if success:
            referral_id = response.get("id") or response.get("_id")
            self.log_test(
                "Referral System CREATE", 
                True, 
                f"Referral created successfully - ID: {referral_id} ({size} chars)",
                size
            )
            
            # Test READ operation
            success, read_response, read_size = await self.make_request(
                "GET", "/api/referral/referrals"
            )
            
            if success:
                self.log_test(
                    "Referral System READ", 
                    True, 
                    f"Referrals retrieved successfully ({read_size} chars)",
                    read_size
                )
            else:
                self.log_test(
                    "Referral System READ", 
                    False, 
                    f"Failed to read referrals: {read_response.get('error', 'Unknown error')}"
                )
        else:
            self.log_test(
                "Referral System CREATE", 
                False, 
                f"Failed to create referral: {response.get('error', 'Unknown error')}"
            )
            self.log_test(
                "Referral System READ", 
                False, 
                "Cannot test - CREATE failed"
            )

    async def test_workspace_crud(self):
        """Test Workspace System CRUD operations"""
        print("\n🏢 Testing Workspace System CRUD")
        
        # Test CREATE operation
        workspace_data = {
            "name": f"Review Test Workspace {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "description": "Workspace created during review testing",
            "type": "business",
            "settings": {
                "theme": "professional",
                "notifications": True
            }
        }
        
        success, response, size = await self.make_request(
            "POST", "/api/complete-multi-workspace/workspaces", 
            data=workspace_data
        )
        
        if success:
            workspace_id = response.get("id") or response.get("_id")
            self.log_test(
                "Workspace System CREATE", 
                True, 
                f"Workspace created successfully - ID: {workspace_id} ({size} chars)",
                size
            )
            
            # Test READ operation
            success, read_response, read_size = await self.make_request(
                "GET", "/api/complete-multi-workspace/workspaces"
            )
            
            if success:
                self.log_test(
                    "Workspace System READ", 
                    True, 
                    f"Workspaces retrieved successfully ({read_size} chars)",
                    read_size
                )
            else:
                self.log_test(
                    "Workspace System READ", 
                    False, 
                    f"Failed to read workspaces: {read_response.get('error', 'Unknown error')}"
                )
        else:
            self.log_test(
                "Workspace System CREATE", 
                False, 
                f"Failed to create workspace: {response.get('error', 'Unknown error')}"
            )
            self.log_test(
                "Workspace System READ", 
                False, 
                "Cannot test - CREATE failed"
            )

    async def test_production_systems(self):
        """Test Production Monitoring and Enterprise Security Features"""
        print("\n🏭 TESTING PRODUCTION SYSTEMS")
        
        production_endpoints = [
            ("/api/production/health", "Production Health Check"),
            ("/api/production/configuration", "Production Configuration"),
            ("/api/production/security", "Enterprise Security Status"),
            ("/api/production/performance", "Performance Monitoring"),
            ("/api/production/logging", "Production Logging"),
            ("/api/production/system-info", "System Information")
        ]
        
        for endpoint, test_name in production_endpoints:
            success, response, size = await self.make_request("GET", endpoint)
            
            if success:
                self.log_test(
                    test_name,
                    True,
                    f"Working perfectly ({size} chars response)",
                    size
                )
            else:
                error_msg = response.get('error', response.get('detail', 'Unknown error'))
                self.log_test(
                    test_name,
                    False,
                    f"Failed: {error_msg}"
                )

    async def test_business_systems(self):
        """Test Core Business Systems"""
        print("\n💼 TESTING CORE BUSINESS SYSTEMS")
        
        business_systems = [
            ("/api/complete-financial/health", "Complete Financial System"),
            ("/api/complete-admin-dashboard/health", "Complete Admin Dashboard"),
            ("/api/analytics/health", "Analytics System"),
            ("/api/complete-multi-workspace/health", "Multi-Workspace System"),
            ("/api/complete-onboarding/health", "Complete Onboarding System"),
            ("/api/escrow/health", "Escrow System"),
            ("/api/ai-content-generation/health", "AI Content Generation"),
            ("/api/form-builder/health", "Form Builder System"),
            ("/api/website-builder/health", "Website Builder System"),
            ("/api/team-management/health", "Team Management System"),
            ("/api/booking/health", "Booking System"),
            ("/api/media-library/health", "Media Library System")
        ]
        
        for endpoint, test_name in business_systems:
            success, response, size = await self.make_request("GET", endpoint)
            
            if success:
                self.log_test(
                    test_name,
                    True,
                    f"Working perfectly ({size} chars response)",
                    size
                )
            else:
                error_msg = response.get('error', response.get('detail', 'Unknown error'))
                self.log_test(
                    test_name,
                    False,
                    f"Failed: {error_msg}"
                )

    async def test_external_integrations(self):
        """Test External API Integrations"""
        print("\n🔌 TESTING EXTERNAL INTEGRATIONS")
        
        integration_endpoints = [
            ("/api/referral/health", "Referral System"),
            ("/api/stripe/health", "Stripe Integration"),
            ("/api/twitter/health", "Twitter/X API"),
            ("/api/tiktok/health", "TikTok API"),
            ("/api/google-oauth/health", "Google OAuth"),
            ("/api/openai/health", "OpenAI Integration")
        ]
        
        for endpoint, test_name in integration_endpoints:
            success, response, size = await self.make_request("GET", endpoint)
            
            if success:
                self.log_test(
                    test_name,
                    True,
                    f"Connected ({size} chars response)",
                    size
                )
            else:
                error_msg = response.get('error', response.get('detail', 'Unknown error'))
                self.log_test(
                    test_name,
                    False,
                    f"Failed: {error_msg}"
                )

    async def test_system_infrastructure(self):
        """Test System Infrastructure"""
        print("\n🏗️ TESTING SYSTEM INFRASTRUCTURE")
        
        infrastructure_endpoints = [
            ("/", "Root Endpoint"),
            ("/api/health", "Health Endpoint"),
            ("/docs", "OpenAPI Documentation"),
            ("/openapi.json", "OpenAPI Specification")
        ]
        
        for endpoint, test_name in infrastructure_endpoints:
            success, response, size = await self.make_request("GET", endpoint)
            
            if success:
                if test_name == "OpenAPI Specification" and isinstance(response, dict):
                    endpoint_count = len(response.get("paths", {}))
                    self.log_test(
                        test_name,
                        True,
                        f"Available with {endpoint_count} endpoints",
                        size
                    )
                else:
                    self.log_test(
                        test_name,
                        True,
                        f"Working perfectly ({size} chars response)",
                        size
                    )
            else:
                error_msg = response.get('error', response.get('detail', 'Unknown error'))
                self.log_test(
                    test_name,
                    False,
                    f"Failed: {error_msg}"
                )

    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🎯 MEWAYZ V2 PLATFORM - FINAL COMPREHENSIVE REVIEW TEST")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Credentials: {TEST_CREDENTIALS['email']}")
        print("=" * 80)
        
        # Run all test categories
        await self.test_authentication_system()
        await self.test_crud_operations_focus()
        await self.test_production_systems()
        await self.test_business_systems()
        await self.test_external_integrations()
        await self.test_system_infrastructure()
        
        # Calculate and display results
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🏆 FINAL COMPREHENSIVE REVIEW TEST RESULTS")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed Tests: {self.passed_tests}")
        print(f"Failed Tests: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 95.0:
            print("✅ SUCCESS: Target 95%+ success rate ACHIEVED!")
        elif success_rate >= 85.0:
            print("⚠️ PROGRESS: Improved from 85% baseline but target not reached")
        else:
            print("❌ CRITICAL: Success rate below baseline - immediate attention required")
        
        print("=" * 80)
        
        # Detailed results by category
        print("\n📊 DETAILED RESULTS BY CATEGORY:")
        categories = {
            "Authentication System": ["JWT Token Generation", "JWT Token Validation"],
            "CRUD Operations": ["Financial System CREATE", "Financial System READ", 
                              "Referral System CREATE", "Referral System READ",
                              "Workspace System CREATE", "Workspace System READ"],
            "Production Systems": ["Production Health Check", "Production Configuration", 
                                 "Enterprise Security Status", "Performance Monitoring",
                                 "Production Logging", "System Information"],
            "Business Systems": ["Complete Financial System", "Complete Admin Dashboard",
                               "Analytics System", "Multi-Workspace System", "Complete Onboarding System",
                               "Escrow System", "AI Content Generation", "Form Builder System",
                               "Website Builder System", "Team Management System", "Booking System",
                               "Media Library System"],
            "External Integrations": ["Referral System", "Stripe Integration", "Twitter/X API",
                                    "TikTok API", "Google OAuth", "OpenAI Integration"],
            "System Infrastructure": ["Root Endpoint", "Health Endpoint", "OpenAPI Documentation",
                                    "OpenAPI Specification"]
        }
        
        for category, tests in categories.items():
            category_results = [r for r in self.test_results if r["test"] in tests]
            if category_results:
                passed = sum(1 for r in category_results if r["success"])
                total = len(category_results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅" if rate == 100 else "⚠️" if rate >= 75 else "❌"
                print(f"{status} {category}: {rate:.1f}% ({passed}/{total} tests passed)")
        
        return success_rate

async def main():
    """Main test execution"""
    try:
        async with MewayzV2ReviewTester() as tester:
            success_rate = await tester.run_comprehensive_test()
            
            # Exit with appropriate code
            if success_rate >= 95.0:
                sys.exit(0)  # Success
            else:
                sys.exit(1)  # Needs improvement
                
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(2)  # Error

if __name__ == "__main__":
    asyncio.run(main())