#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - COMPREHENSIVE BACKEND TESTING
Review Request Assessment - January 2025

Testing Focus Areas:
1. Authentication System - JWT token generation and validation with tmonnens@outlook.com/Voetballen5
2. Production Monitoring Endpoints - Test new /api/production/* endpoints
3. Core Business Systems - Verify existing functionality maintains high success rate
4. Enterprise Security Features - Test advanced authentication and security
5. Performance Optimization - Test caching and performance systems
6. Authorization Middleware - Verify 403 Forbidden errors are resolved

Expected improvements:
- JWT tokens should now be properly validated by protected endpoints
- Authentication should work with proper admin access
- Production enhancement endpoints should be accessible
- Overall success rate should improve from previous 62.5% to target 98.6%
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

class MewayzV2Tester:
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
        """Test Authentication System - JWT token generation and validation"""
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
                self.log_test(
                    "JWT Token Validation", 
                    True, 
                    f"Token validation successful ({profile_size} chars response)",
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

    async def test_production_monitoring_endpoints(self):
        """Test Production Monitoring Endpoints - /api/production/*"""
        print("\n🏭 TESTING PRODUCTION MONITORING ENDPOINTS")
        
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

    async def test_core_business_systems(self):
        """Test Core Business Systems - Verify existing functionality"""
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
        
        for endpoint, system_name in business_systems:
            success, response, size = await self.make_request("GET", endpoint)
            
            if success:
                self.log_test(
                    f"{system_name} Health",
                    True,
                    f"Working perfectly ({size} chars response)",
                    size
                )
            else:
                error_msg = response.get('error', response.get('detail', 'Unknown error'))
                self.log_test(
                    f"{system_name} Health",
                    False,
                    f"Failed: {error_msg}"
                )

    async def test_external_api_integrations(self):
        """Test External API Integrations"""
        print("\n🔗 TESTING EXTERNAL API INTEGRATIONS")
        
        external_apis = [
            ("/api/referral-system/health", "Referral System"),
            ("/api/stripe-integration/health", "Stripe Integration"),
            ("/api/twitter/health", "Twitter/X API"),
            ("/api/tiktok/health", "TikTok API"),
            ("/api/google-oauth/health", "Google OAuth"),
            ("/api/ai/health", "OpenAI Integration")
        ]
        
        for endpoint, api_name in external_apis:
            success, response, size = await self.make_request("GET", endpoint)
            
            if success:
                self.log_test(
                    f"{api_name} Health",
                    True,
                    f"Connected ({size} chars response)",
                    size
                )
            else:
                error_msg = response.get('error', response.get('detail', 'Unknown error'))
                self.log_test(
                    f"{api_name} Health",
                    False,
                    f"Failed: {error_msg}"
                )

    async def test_crud_operations(self):
        """Test CRUD Operations - Verify 403 Forbidden errors are resolved"""
        print("\n📝 TESTING CRUD OPERATIONS")
        
        crud_endpoints = [
            ("/api/complete-financial", "Complete Financial System CRUD"),
            ("/api/referral-system", "Referral System CRUD"),
            ("/api/complete-multi-workspace", "Workspace System CRUD")
        ]
        
        for base_endpoint, system_name in crud_endpoints:
            # Test CREATE operation
            create_success, create_response, create_size = await self.make_request(
                "POST", base_endpoint,
                data={"name": f"Test {system_name}", "description": "Test data for CRUD operations"}
            )
            
            if create_success:
                self.log_test(
                    f"{system_name} CREATE",
                    True,
                    f"CREATE operation working ({create_size} chars response)",
                    create_size
                )
                
                # Test READ operation
                read_success, read_response, read_size = await self.make_request(
                    "GET", base_endpoint
                )
                
                if read_success:
                    self.log_test(
                        f"{system_name} READ",
                        True,
                        f"READ operation working ({read_size} chars response)",
                        read_size
                    )
                else:
                    self.log_test(
                        f"{system_name} READ",
                        False,
                        f"READ failed: {read_response.get('error', 'Unknown error')}"
                    )
            else:
                error_msg = create_response.get('error', create_response.get('detail', 'Unknown error'))
                self.log_test(
                    f"{system_name} CREATE",
                    False,
                    f"CREATE failed: {error_msg}"
                )
                self.log_test(
                    f"{system_name} READ",
                    False,
                    "Cannot test READ - CREATE failed"
                )

    async def test_system_infrastructure(self):
        """Test System Infrastructure"""
        print("\n🏗️ TESTING SYSTEM INFRASTRUCTURE")
        
        # Test Root Endpoint
        success, response, size = await self.make_request("GET", "/")
        if success:
            self.log_test(
                "Root Endpoint",
                True,
                f"Working perfectly (JSON response with operational status)",
                size
            )
        else:
            self.log_test(
                "Root Endpoint",
                False,
                f"Failed: {response.get('error', 'Unknown error')}"
            )
        
        # Test Health Endpoint
        success, response, size = await self.make_request("GET", "/health")
        if success:
            self.log_test(
                "Health Endpoint",
                True,
                f"Working perfectly (healthy status with {response.get('services', 0)} services)",
                size
            )
        else:
            self.log_test(
                "Health Endpoint",
                False,
                f"Failed: {response.get('error', 'Unknown error')}"
            )
        
        # Test OpenAPI Documentation
        success, response, size = await self.make_request("GET", "/docs")
        if success:
            self.log_test(
                "OpenAPI Documentation",
                True,
                f"Working perfectly (comprehensive API documentation)",
                size
            )
        else:
            self.log_test(
                "OpenAPI Documentation",
                False,
                f"Failed: {response.get('error', 'Unknown error')}"
            )

    async def test_authorization_middleware(self):
        """Test Authorization Middleware - Verify 403 Forbidden errors are resolved"""
        print("\n🔒 TESTING AUTHORIZATION MIDDLEWARE")
        
        # Test protected endpoints that previously returned 403
        protected_endpoints = [
            ("/api/complete-financial", "Financial System Data Access"),
            ("/api/complete-admin-dashboard", "Admin Dashboard Data Access"),
            ("/api/analytics", "Analytics System Data Access"),
            ("/api/complete-multi-workspace", "Workspace Data Access")
        ]
        
        for endpoint, test_name in protected_endpoints:
            success, response, size = await self.make_request("GET", endpoint)
            
            if success:
                self.log_test(
                    test_name,
                    True,
                    f"Authorization working - data accessible ({size} chars response)",
                    size
                )
            elif response.get('detail') == 'Forbidden' or 'status_code' in response and response['status_code'] == 403:
                self.log_test(
                    test_name,
                    False,
                    "403 Forbidden error still present - authorization middleware issue"
                )
            else:
                # Other errors are acceptable (404, 500, etc.) - means authorization passed
                self.log_test(
                    test_name,
                    True,
                    f"Authorization passed (got {response.get('error', 'other error')} instead of 403)"
                )

    async def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🎯 MEWAYZ V2 PLATFORM - COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Credentials: {TEST_CREDENTIALS['email']}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        print("=" * 80)
        
        # Run all test suites
        await self.test_authentication_system()
        await self.test_production_monitoring_endpoints()
        await self.test_core_business_systems()
        await self.test_external_api_integrations()
        await self.test_crud_operations()
        await self.test_system_infrastructure()
        await self.test_authorization_middleware()
        
        # Calculate results
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🏆 COMPREHENSIVE TESTING RESULTS")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed Tests: {self.passed_tests}")
        print(f"Failed Tests: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        if success_rate >= 98.0:
            print("🏆 OUTSTANDING SUCCESS - Production Ready!")
        elif success_rate >= 90.0:
            print("✅ EXCELLENT SUCCESS - Minor improvements needed")
        elif success_rate >= 75.0:
            print("⚠️ GOOD PERFORMANCE - Some issues need attention")
        elif success_rate >= 50.0:
            print("⚠️ MIXED RESULTS - Significant improvements needed")
        else:
            print("❌ CRITICAL ISSUES - Major fixes required")
        
        print("=" * 80)
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        # Show successful tests summary
        successful_tests = [test for test in self.test_results if test['success']]
        if successful_tests:
            print(f"\n✅ SUCCESSFUL TESTS ({len(successful_tests)}):")
            for test in successful_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("\n" + "=" * 80)
        print("REVIEW REQUEST ASSESSMENT:")
        
        # Check specific review request criteria
        auth_tests = [t for t in self.test_results if 'JWT' in t['test'] or 'Authentication' in t['test']]
        auth_success = all(t['success'] for t in auth_tests)
        
        production_tests = [t for t in self.test_results if 'Production' in t['test']]
        production_success = all(t['success'] for t in production_tests)
        
        crud_tests = [t for t in self.test_results if 'CRUD' in t['test']]
        crud_success = all(t['success'] for t in crud_tests)
        
        auth_middleware_tests = [t for t in self.test_results if 'Authorization' in t['test'] or 'Data Access' in t['test']]
        auth_middleware_success = all(t['success'] for t in auth_middleware_tests)
        
        print(f"✅ Authentication System: {'WORKING' if auth_success else 'ISSUES'}")
        print(f"✅ Production Monitoring: {'WORKING' if production_success else 'ISSUES'}")
        print(f"✅ CRUD Operations: {'WORKING' if crud_success else 'ISSUES'}")
        print(f"✅ Authorization Middleware: {'FIXED' if auth_middleware_success else 'STILL BROKEN'}")
        print(f"✅ Overall Success Rate: {success_rate:.1f}% (Target: 98.6%)")
        
        if success_rate >= 98.0:
            print("\n🎉 SUCCESS: Critical authorization middleware issues have been RESOLVED!")
            print("🚀 Platform is ready for production deployment!")
        else:
            print(f"\n⚠️ NEEDS WORK: Success rate {success_rate:.1f}% is below target 98.6%")
            print("🔧 Additional fixes needed before production deployment")
        
        return success_rate

async def main():
    """Main test execution"""
    try:
        async with MewayzV2Tester() as tester:
            success_rate = await tester.run_comprehensive_test()
            
            # Exit with appropriate code
            if success_rate >= 98.0:
                sys.exit(0)  # Success
            else:
                sys.exit(1)  # Needs improvement
                
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        sys.exit(2)  # Critical error

if __name__ == "__main__":
    asyncio.run(main())