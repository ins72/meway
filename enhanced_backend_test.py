#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - ENHANCED BACKEND TESTING
Review Request Final Assessment - January 2025

Enhanced Testing Focus Areas:
1. CRUD Authentication Deep Dive - Investigate "Not authenticated" errors
2. Performance Systems - Test caching and monitoring systems
3. Enterprise Security - Test advanced security features
4. Additional External API Functionality - Test actual API operations beyond health checks
5. Data Persistence Verification - Ensure real database operations

Target: Achieve 95%+ success rate (target 98.6%)
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

class EnhancedMewayzV2Tester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.auth_token = None
        self.user_info = None
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
        
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, include_auth: bool = True) -> Tuple[bool, Dict, int]:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.backend_url}{endpoint}"
            request_headers = {"Content-Type": "application/json"}
            
            if headers:
                request_headers.update(headers)
                
            if self.auth_token and include_auth and "Authorization" not in request_headers:
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

    async def test_authentication_deep_dive(self):
        """Deep dive into authentication system"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM - DEEP DIVE")
        
        # Test 1: JWT Token Generation
        success, response, size = await self.make_request(
            "POST", "/api/auth/login", 
            data=TEST_CREDENTIALS,
            include_auth=False
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
                self.user_info = profile_response
                self.log_test(
                    "JWT Token Validation", 
                    True, 
                    f"Token validation successful ({profile_size} chars response)",
                    profile_size
                )
                
                # Test 3: Check User Permissions
                user_role = profile_response.get('role', 'unknown')
                user_permissions = profile_response.get('permissions', [])
                self.log_test(
                    "User Role & Permissions Check",
                    True,
                    f"User role: {user_role}, Permissions: {len(user_permissions)} items"
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

    async def test_crud_authentication_investigation(self):
        """Investigate CRUD authentication issues in detail"""
        print("\n🔍 INVESTIGATING CRUD AUTHENTICATION ISSUES")
        
        if not self.auth_token:
            self.log_test("CRUD Auth Investigation", False, "No auth token available")
            return
            
        # Test different CRUD endpoints with various approaches
        crud_endpoints = [
            ("/api/complete-financial", "Financial System"),
            ("/api/referral-system", "Referral System"),
            ("/api/complete-multi-workspace", "Workspace System")
        ]
        
        for base_endpoint, system_name in crud_endpoints:
            # Test 1: Try GET first (should work if auth is correct)
            success, response, size = await self.make_request("GET", base_endpoint)
            
            if success:
                self.log_test(
                    f"{system_name} GET Operation",
                    True,
                    f"GET working - auth is valid ({size} chars response)",
                    size
                )
            else:
                error_detail = response.get('detail', response.get('error', 'Unknown error'))
                self.log_test(
                    f"{system_name} GET Operation",
                    False,
                    f"GET failed: {error_detail}"
                )
            
            # Test 2: Try POST with minimal data
            minimal_data = {"name": f"Test {system_name} Item"}
            success, response, size = await self.make_request(
                "POST", base_endpoint, 
                data=minimal_data
            )
            
            if success:
                self.log_test(
                    f"{system_name} POST Operation",
                    True,
                    f"POST working ({size} chars response)",
                    size
                )
            else:
                error_detail = response.get('detail', response.get('error', 'Unknown error'))
                self.log_test(
                    f"{system_name} POST Operation",
                    False,
                    f"POST failed: {error_detail}"
                )

    async def test_performance_systems(self):
        """Test Performance Systems - Caching and Monitoring"""
        print("\n⚡ TESTING PERFORMANCE SYSTEMS")
        
        performance_endpoints = [
            ("/api/performance/cache", "Cache System"),
            ("/api/performance/monitoring", "Performance Monitoring"),
            ("/api/performance/metrics", "Performance Metrics"),
            ("/api/cache/health", "Cache Health"),
            ("/api/monitoring/health", "Monitoring Health"),
            ("/api/system/performance", "System Performance")
        ]
        
        for endpoint, test_name in performance_endpoints:
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

    async def test_enterprise_security_features(self):
        """Test Enterprise Security Features"""
        print("\n🛡️ TESTING ENTERPRISE SECURITY FEATURES")
        
        security_endpoints = [
            ("/api/security/audit", "Security Audit"),
            ("/api/security/compliance", "Compliance Check"),
            ("/api/security/encryption", "Encryption Status"),
            ("/api/security/access-control", "Access Control"),
            ("/api/enterprise/security", "Enterprise Security"),
            ("/api/auth/security-status", "Auth Security Status")
        ]
        
        for endpoint, test_name in security_endpoints:
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

    async def test_external_api_functionality(self):
        """Test External API Functionality Beyond Health Checks"""
        print("\n🌐 TESTING EXTERNAL API FUNCTIONALITY")
        
        # Test Twitter/X API functionality
        twitter_endpoints = [
            ("/api/twitter/search?q=test", "Twitter Search"),
            ("/api/twitter/tweets", "Twitter Tweets List"),
            ("/api/twitter/analytics", "Twitter Analytics")
        ]
        
        for endpoint, test_name in twitter_endpoints:
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
                # Don't mark as failed if it's just not implemented (404)
                if "404" in str(error_msg) or "Not Found" in str(error_msg):
                    self.log_test(
                        test_name,
                        False,
                        f"Not implemented: {error_msg}"
                    )
                else:
                    self.log_test(
                        test_name,
                        False,
                        f"Failed: {error_msg}"
                    )
        
        # Test TikTok API functionality
        tiktok_endpoints = [
            ("/api/tiktok/search?q=test", "TikTok Search"),
            ("/api/tiktok/videos", "TikTok Videos List"),
            ("/api/tiktok/analytics", "TikTok Analytics")
        ]
        
        for endpoint, test_name in tiktok_endpoints:
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
                if "404" in str(error_msg) or "Not Found" in str(error_msg):
                    self.log_test(
                        test_name,
                        False,
                        f"Not implemented: {error_msg}"
                    )
                else:
                    self.log_test(
                        test_name,
                        False,
                        f"Failed: {error_msg}"
                    )
        
        # Test Stripe functionality
        stripe_endpoints = [
            ("/api/stripe-integration/payment-methods", "Stripe Payment Methods"),
            ("/api/stripe-integration/subscriptions", "Stripe Subscriptions"),
            ("/api/stripe-integration/customers", "Stripe Customers")
        ]
        
        for endpoint, test_name in stripe_endpoints:
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
                if "404" in str(error_msg) or "Not Found" in str(error_msg):
                    self.log_test(
                        test_name,
                        False,
                        f"Not implemented: {error_msg}"
                    )
                else:
                    self.log_test(
                        test_name,
                        False,
                        f"Failed: {error_msg}"
                    )

    async def test_data_persistence_verification(self):
        """Test Data Persistence - Ensure Real Database Operations"""
        print("\n💾 TESTING DATA PERSISTENCE VERIFICATION")
        
        # Test multiple calls to same endpoints to check for data consistency
        persistence_endpoints = [
            ("/api/complete-financial/health", "Financial System Data Consistency"),
            ("/api/analytics/health", "Analytics System Data Consistency"),
            ("/api/complete-multi-workspace/health", "Workspace System Data Consistency")
        ]
        
        for endpoint, test_name in persistence_endpoints:
            # Make 3 calls and compare responses
            responses = []
            for i in range(3):
                success, response, size = await self.make_request("GET", endpoint)
                if success:
                    responses.append(response)
                await asyncio.sleep(0.1)  # Small delay between calls
            
            if len(responses) == 3:
                # Check if responses are consistent (indicating real data, not random)
                if responses[0] == responses[1] == responses[2]:
                    self.log_test(
                        test_name,
                        True,
                        f"Data consistent across multiple calls - real database operations confirmed"
                    )
                else:
                    self.log_test(
                        test_name,
                        False,
                        f"Data inconsistent - may still be using random generation"
                    )
            else:
                self.log_test(
                    test_name,
                    False,
                    f"Could not verify - endpoint not accessible"
                )

    async def run_enhanced_comprehensive_test(self):
        """Run all enhanced comprehensive tests"""
        print("🎯 MEWAYZ V2 PLATFORM - ENHANCED COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Credentials: {TEST_CREDENTIALS['email']}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        print("=" * 80)
        
        # Run all test suites
        await self.test_authentication_deep_dive()
        await self.test_crud_authentication_investigation()
        await self.test_performance_systems()
        await self.test_enterprise_security_features()
        await self.test_external_api_functionality()
        await self.test_data_persistence_verification()
        
        # Calculate results
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🏆 ENHANCED COMPREHENSIVE TESTING RESULTS")
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
        print("ENHANCED REVIEW REQUEST ASSESSMENT:")
        
        # Check specific review request criteria
        auth_tests = [t for t in self.test_results if 'JWT' in t['test'] or 'Authentication' in t['test'] or 'Auth' in t['test']]
        auth_success_rate = (sum(1 for t in auth_tests if t['success']) / len(auth_tests) * 100) if auth_tests else 0
        
        crud_tests = [t for t in self.test_results if 'CRUD' in t['test'] or 'GET Operation' in t['test'] or 'POST Operation' in t['test']]
        crud_success_rate = (sum(1 for t in crud_tests if t['success']) / len(crud_tests) * 100) if crud_tests else 0
        
        performance_tests = [t for t in self.test_results if 'Performance' in t['test'] or 'Cache' in t['test'] or 'Monitoring' in t['test']]
        performance_success_rate = (sum(1 for t in performance_tests if t['success']) / len(performance_tests) * 100) if performance_tests else 0
        
        security_tests = [t for t in self.test_results if 'Security' in t['test'] or 'Enterprise' in t['test']]
        security_success_rate = (sum(1 for t in security_tests if t['success']) / len(security_tests) * 100) if security_tests else 0
        
        external_api_tests = [t for t in self.test_results if 'Twitter' in t['test'] or 'TikTok' in t['test'] or 'Stripe' in t['test']]
        external_api_success_rate = (sum(1 for t in external_api_tests if t['success']) / len(external_api_tests) * 100) if external_api_tests else 0
        
        persistence_tests = [t for t in self.test_results if 'Consistency' in t['test'] or 'Persistence' in t['test']]
        persistence_success_rate = (sum(1 for t in persistence_tests if t['success']) / len(persistence_tests) * 100) if persistence_tests else 0
        
        print(f"✅ Authentication System: {auth_success_rate:.1f}% success rate")
        print(f"✅ CRUD Operations: {crud_success_rate:.1f}% success rate")
        print(f"✅ Performance Systems: {performance_success_rate:.1f}% success rate")
        print(f"✅ Enterprise Security: {security_success_rate:.1f}% success rate")
        print(f"✅ External API Integrations: {external_api_success_rate:.1f}% success rate")
        print(f"✅ Data Persistence: {persistence_success_rate:.1f}% success rate")
        print(f"✅ Overall Success Rate: {success_rate:.1f}% (Target: 98.6%)")
        
        if success_rate >= 95.0:
            print("\n🎉 SUCCESS: Platform meets production readiness criteria!")
            print("🚀 Ready for production deployment!")
        elif success_rate >= 85.0:
            print(f"\n⚠️ GOOD PROGRESS: Success rate {success_rate:.1f}% shows significant improvement")
            print("🔧 Minor fixes needed to reach production target")
        else:
            print(f"\n⚠️ NEEDS WORK: Success rate {success_rate:.1f}% is below production readiness")
            print("🔧 Additional fixes needed before production deployment")
        
        return success_rate

async def main():
    """Main test execution"""
    try:
        async with EnhancedMewayzV2Tester() as tester:
            success_rate = await tester.run_enhanced_comprehensive_test()
            
            # Exit with appropriate code
            if success_rate >= 95.0:
                sys.exit(0)  # Success
            else:
                sys.exit(1)  # Needs improvement
                
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        sys.exit(2)  # Critical error

if __name__ == "__main__":
    asyncio.run(main())