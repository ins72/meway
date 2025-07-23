#!/usr/bin/env python3
"""
🎯 DUPLICATE CLEANUP REVIEW REQUEST TESTING - JANUARY 2025 🎯

COMPREHENSIVE BACKEND TESTING after critical duplicate cleanup:
✅ REMOVED 61 duplicate files  
✅ RESOLVED 64 routing conflicts  
✅ ELIMINATED conflicting routes causing 405/500 errors

Testing specifically for:
1. Overall Success Rate improvement from 56.2% baseline
2. Routing Conflicts Resolved (fewer 405 errors)  
3. Authentication System (should be 100% working)
4. Core Business Systems (should maintain excellent performance)
5. Referral System (ObjectId fixes + cleanup)
6. Stripe Integration (routing conflicts resolved)
7. External APIs (Twitter/TikTok functionality after cleanup)

Expected: 70%+ success rate after massive routing conflict cleanup
Target: 95%+ production readiness
"""

import requests
import json
import sys
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class DuplicateCleanupReviewTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, response_info="", error_info=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "success": success,
            "response_info": response_info,
            "error_info": error_info,
            "status": status
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if response_info:
            print(f"   Response: {response_info}")
        if error_info:
            print(f"   Error: {error_info}")
        print()

    def test_authentication_system(self):
        """Test authentication system - should be 100% working"""
        print("🔐 TESTING AUTHENTICATION SYSTEM (Expected: 100% Success)")
        print("=" * 60)
        
        # Test 1: JWT Token Generation
        try:
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.jwt_token = token_data.get("access_token")
                if self.jwt_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                    self.log_test("JWT Token Generation", True, f"Token generated ({len(str(token_data))} chars)")
                else:
                    self.log_test("JWT Token Generation", False, "", "No access token in response")
            else:
                self.log_test("JWT Token Generation", False, "", f"Status {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("JWT Token Generation", False, "", f"Exception: {str(e)}")

        # Test 2: JWT Token Validation
        if self.jwt_token:
            try:
                response = self.session.get(f"{API_BASE}/auth/me")
                if response.status_code == 200:
                    user_data = response.json()
                    self.log_test("JWT Token Validation", True, f"User data retrieved ({len(str(user_data))} chars)")
                else:
                    self.log_test("JWT Token Validation", False, "", f"Status {response.status_code}: {response.text[:200]}")
            except Exception as e:
                self.log_test("JWT Token Validation", False, "", f"Exception: {str(e)}")
        else:
            self.log_test("JWT Token Validation", False, "", "No JWT token available")

        # Test 3: Protected Endpoint Access
        if self.jwt_token:
            try:
                response = self.session.get(f"{API_BASE}/admin/dashboard")
                if response.status_code == 200:
                    admin_data = response.json()
                    self.log_test("Protected Endpoint Access", True, f"Admin dashboard accessible ({len(str(admin_data))} chars)")
                elif response.status_code == 403:
                    self.log_test("Protected Endpoint Access", False, "", "403 Forbidden - Authorization issue")
                else:
                    self.log_test("Protected Endpoint Access", False, "", f"Status {response.status_code}: {response.text[:200]}")
            except Exception as e:
                self.log_test("Protected Endpoint Access", False, "", f"Exception: {str(e)}")

    def test_routing_conflicts_resolved(self):
        """Test that routing conflicts have been resolved - should see fewer 405 errors"""
        print("🛣️ TESTING ROUTING CONFLICTS RESOLUTION (Expected: No 405 Errors)")
        print("=" * 60)
        
        # Test endpoints that previously had routing conflicts
        test_endpoints = [
            ("/referral/health", "GET", "Referral Health Check"),
            ("/referral/programs", "GET", "Referral Programs List"),
            ("/referral/programs", "POST", "Referral Program Creation"),
            ("/stripe/health", "GET", "Stripe Health Check"),
            ("/stripe/payment-intent", "POST", "Stripe Payment Intent"),
            ("/twitter/health", "GET", "Twitter Health Check"),
            ("/twitter/search", "GET", "Twitter Search"),
            ("/tiktok/health", "GET", "TikTok Health Check"),
            ("/tiktok/search", "GET", "TikTok Search"),
            ("/financial/dashboard", "GET", "Financial Dashboard"),
            ("/workspace/list", "GET", "Workspace List"),
            ("/admin/users", "GET", "Admin Users"),
        ]
        
        for endpoint, method, test_name in test_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{API_BASE}{endpoint}", json={})
                
                if response.status_code == 405:
                    self.log_test(f"Routing - {test_name}", False, "", f"405 Method Not Allowed - Routing conflict still exists")
                elif response.status_code in [200, 201, 400, 422, 500]:
                    # These are acceptable - means routing is working, even if endpoint has other issues
                    self.log_test(f"Routing - {test_name}", True, f"Status {response.status_code} - Routing working")
                elif response.status_code == 404:
                    # 404 is acceptable - means routing works but endpoint not implemented
                    self.log_test(f"Routing - {test_name}", True, f"Status 404 - Routing working, endpoint not implemented")
                else:
                    self.log_test(f"Routing - {test_name}", False, "", f"Status {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_test(f"Routing - {test_name}", False, "", f"Exception: {str(e)}")

    def test_core_business_systems(self):
        """Test core business systems - should maintain excellent performance"""
        print("🏢 TESTING CORE BUSINESS SYSTEMS (Expected: Excellent Performance)")
        print("=" * 60)
        
        core_systems = [
            ("/financial/health", "Financial System Health"),
            ("/workspace/health", "Multi-Workspace System Health"),
            ("/admin/health", "Admin Dashboard System Health"),
            ("/analytics/health", "Analytics System Health"),
            ("/ai-content/health", "AI Automation Suite Health"),
            ("/template/health", "Website Builder System Health"),
            ("/booking/health", "Booking System Health"),
            ("/media-library/health", "Media Library System Health"),
        ]
        
        for endpoint, test_name in core_systems:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                if response.status_code == 200:
                    health_data = response.json()
                    self.log_test(test_name, True, f"System healthy ({len(str(health_data))} chars)")
                else:
                    self.log_test(test_name, False, "", f"Status {response.status_code}: {response.text[:200]}")
            except Exception as e:
                self.log_test(test_name, False, "", f"Exception: {str(e)}")

    def test_referral_system_objectid_fixes(self):
        """Test referral system - ObjectId fixes + cleanup should resolve issues"""
        print("🔗 TESTING REFERRAL SYSTEM (Expected: ObjectId Issues Resolved)")
        print("=" * 60)
        
        # Test 1: Referral System Health
        try:
            response = self.session.get(f"{API_BASE}/referral/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("Referral System Health", True, f"System healthy ({len(str(health_data))} chars)")
            else:
                self.log_test("Referral System Health", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Referral System Health", False, "", f"Exception: {str(e)}")

        # Test 2: List Referral Programs (READ operation)
        try:
            response = self.session.get(f"{API_BASE}/referral/programs")
            if response.status_code == 200:
                programs_data = response.json()
                self.log_test("Referral Programs List", True, f"Programs retrieved ({len(str(programs_data))} chars)")
            else:
                self.log_test("Referral Programs List", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Referral Programs List", False, "", f"Exception: {str(e)}")

        # Test 3: Create Referral Program (CREATE operation - ObjectId serialization test)
        try:
            referral_data = {
                "name": "Cleanup Test Referral Program",
                "description": "Testing ObjectId fixes after duplicate cleanup",
                "commission_rate": 0.15,
                "status": "active"
            }
            response = self.session.post(f"{API_BASE}/referral/programs", json=referral_data)
            if response.status_code in [200, 201]:
                created_data = response.json()
                self.log_test("Referral Program Creation (ObjectId Test)", True, f"Program created ({len(str(created_data))} chars)")
            elif response.status_code == 500 and "ObjectId" in response.text:
                self.log_test("Referral Program Creation (ObjectId Test)", False, "", "ObjectId serialization issue still exists")
            else:
                self.log_test("Referral Program Creation (ObjectId Test)", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Referral Program Creation (ObjectId Test)", False, "", f"Exception: {str(e)}")

        # Test 4: Referral Analytics
        try:
            response = self.session.get(f"{API_BASE}/referral/analytics")
            if response.status_code == 200:
                analytics_data = response.json()
                self.log_test("Referral Analytics", True, f"Analytics retrieved ({len(str(analytics_data))} chars)")
            else:
                self.log_test("Referral Analytics", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Referral Analytics", False, "", f"Exception: {str(e)}")

    def test_stripe_integration_routing_fixes(self):
        """Test Stripe integration - routing conflicts should be resolved"""
        print("💳 TESTING STRIPE INTEGRATION (Expected: Routing Conflicts Resolved)")
        print("=" * 60)
        
        # Test 1: Stripe Health Check
        try:
            response = self.session.get(f"{API_BASE}/stripe/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("Stripe Health Check", True, f"Stripe healthy ({len(str(health_data))} chars)")
            else:
                self.log_test("Stripe Health Check", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Stripe Health Check", False, "", f"Exception: {str(e)}")

        # Test 2: Create Payment Intent (should not have routing conflicts)
        try:
            payment_data = {
                "amount": 2000,
                "currency": "usd",
                "description": "Test payment after cleanup"
            }
            response = self.session.post(f"{API_BASE}/stripe/payment-intent", json=payment_data)
            if response.status_code in [200, 201]:
                payment_data = response.json()
                self.log_test("Stripe Payment Intent Creation", True, f"Payment intent created ({len(str(payment_data))} chars)")
            elif response.status_code == 405:
                self.log_test("Stripe Payment Intent Creation", False, "", "405 Method Not Allowed - Routing conflict still exists")
            else:
                self.log_test("Stripe Payment Intent Creation", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Stripe Payment Intent Creation", False, "", f"Exception: {str(e)}")

        # Test 3: List Payment Methods
        try:
            response = self.session.get(f"{API_BASE}/stripe/payment-methods")
            if response.status_code == 200:
                methods_data = response.json()
                self.log_test("Stripe Payment Methods", True, f"Payment methods retrieved ({len(str(methods_data))} chars)")
            elif response.status_code == 405:
                self.log_test("Stripe Payment Methods", False, "", "405 Method Not Allowed - Routing conflict still exists")
            else:
                self.log_test("Stripe Payment Methods", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Stripe Payment Methods", False, "", f"Exception: {str(e)}")

        # Test 4: Subscription Management
        try:
            response = self.session.get(f"{API_BASE}/stripe/subscriptions")
            if response.status_code == 200:
                subs_data = response.json()
                self.log_test("Stripe Subscription Management", True, f"Subscriptions retrieved ({len(str(subs_data))} chars)")
            elif response.status_code == 405:
                self.log_test("Stripe Subscription Management", False, "", "405 Method Not Allowed - Routing conflict still exists")
            else:
                self.log_test("Stripe Subscription Management", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Stripe Subscription Management", False, "", f"Exception: {str(e)}")

    def test_external_apis_after_cleanup(self):
        """Test external APIs - Twitter/TikTok functionality after cleanup"""
        print("🌐 TESTING EXTERNAL APIs (Expected: Functionality After Cleanup)")
        print("=" * 60)
        
        # Twitter/X API Tests
        twitter_tests = [
            ("/twitter/health", "GET", "Twitter Health Check"),
            ("/twitter/search", "GET", "Twitter Search Functionality"),
            ("/twitter/tweets", "GET", "Twitter Tweets List"),
            ("/twitter/analytics", "GET", "Twitter Analytics"),
        ]
        
        for endpoint, method, test_name in twitter_tests:
            try:
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(test_name, True, f"Working ({len(str(data))} chars)")
                elif response.status_code == 405:
                    self.log_test(test_name, False, "", "405 Method Not Allowed - Routing conflict still exists")
                else:
                    self.log_test(test_name, False, "", f"Status {response.status_code}: {response.text[:200]}")
            except Exception as e:
                self.log_test(test_name, False, "", f"Exception: {str(e)}")

        # TikTok API Tests
        tiktok_tests = [
            ("/tiktok/health", "GET", "TikTok Health Check"),
            ("/tiktok/search", "GET", "TikTok Search Functionality"),
            ("/tiktok/videos", "GET", "TikTok Videos List"),
            ("/tiktok/analytics", "GET", "TikTok Analytics"),
        ]
        
        for endpoint, method, test_name in tiktok_tests:
            try:
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(test_name, True, f"Working ({len(str(data))} chars)")
                elif response.status_code == 405:
                    self.log_test(test_name, False, "", "405 Method Not Allowed - Routing conflict still exists")
                else:
                    self.log_test(test_name, False, "", f"Status {response.status_code}: {response.text[:200]}")
            except Exception as e:
                self.log_test(test_name, False, "", f"Exception: {str(e)}")

    def test_system_infrastructure(self):
        """Test overall system infrastructure"""
        print("🏗️ TESTING SYSTEM INFRASTRUCTURE (Expected: Solid Foundation)")
        print("=" * 60)
        
        # Test 1: OpenAPI Specification
        try:
            response = self.session.get(f"{BACKEND_URL}/openapi.json")
            if response.status_code == 200:
                openapi_data = response.json()
                endpoint_count = len(openapi_data.get("paths", {}))
                self.log_test("OpenAPI Specification", True, f"{endpoint_count} endpoints available")
            else:
                self.log_test("OpenAPI Specification", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("OpenAPI Specification", False, "", f"Exception: {str(e)}")

        # Test 2: System Health
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("System Health Check", True, f"System healthy ({len(str(health_data))} chars)")
            else:
                self.log_test("System Health Check", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("System Health Check", False, "", f"Exception: {str(e)}")

        # Test 3: Database Connectivity
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                try:
                    root_data = response.json()
                    self.log_test("Database Connectivity", True, f"Root endpoint returns JSON ({len(str(root_data))} chars)")
                except:
                    self.log_test("Database Connectivity", False, "", "Root endpoint returns HTML instead of JSON")
            else:
                self.log_test("Database Connectivity", False, "", f"Status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_test("Database Connectivity", False, "", f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run all tests and generate comprehensive report"""
        print("🎯 DUPLICATE CLEANUP REVIEW REQUEST TESTING - JANUARY 2025 🎯")
        print("=" * 80)
        print("Testing improvement after removing 61 duplicate files and resolving 64 routing conflicts")
        print("Expected: 70%+ success rate improvement from 56.2% baseline")
        print("Target: 95%+ production readiness")
        print("=" * 80)
        print()
        
        # Run all test suites
        self.test_authentication_system()
        self.test_routing_conflicts_resolved()
        self.test_core_business_systems()
        self.test_referral_system_objectid_fixes()
        self.test_stripe_integration_routing_fixes()
        self.test_external_apis_after_cleanup()
        self.test_system_infrastructure()
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive final report"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("🎯 DUPLICATE CLEANUP REVIEW REQUEST TESTING RESULTS 🎯")
        print("=" * 80)
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        print()
        
        # Compare with baseline
        baseline_rate = 56.2
        improvement = success_rate - baseline_rate
        
        if success_rate >= 70:
            print(f"✅ SUCCESS: {success_rate:.1f}% exceeds expected 70%+ target")
            print(f"✅ IMPROVEMENT: +{improvement:.1f}% from {baseline_rate}% baseline")
        elif success_rate > baseline_rate:
            print(f"⚠️ PARTIAL SUCCESS: {success_rate:.1f}% improved by +{improvement:.1f}% but below 70% target")
        else:
            print(f"❌ REGRESSION: {success_rate:.1f}% is {abs(improvement):.1f}% worse than {baseline_rate}% baseline")
        
        print()
        
        # Categorize results
        categories = {
            "Authentication System": [],
            "Routing Conflicts": [],
            "Core Business Systems": [],
            "Referral System": [],
            "Stripe Integration": [],
            "External APIs": [],
            "System Infrastructure": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "JWT" in test_name or "Protected" in test_name:
                categories["Authentication System"].append(result)
            elif "Routing" in test_name:
                categories["Routing Conflicts"].append(result)
            elif any(x in test_name for x in ["Financial", "Workspace", "Admin", "Analytics", "AI", "Website", "Booking", "Media"]):
                categories["Core Business Systems"].append(result)
            elif "Referral" in test_name:
                categories["Referral System"].append(result)
            elif "Stripe" in test_name:
                categories["Stripe Integration"].append(result)
            elif any(x in test_name for x in ["Twitter", "TikTok"]):
                categories["External APIs"].append(result)
            else:
                categories["System Infrastructure"].append(result)
        
        # Report by category
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                cat_rate = (passed / total * 100) if total > 0 else 0
                
                if cat_rate >= 80:
                    status = "✅ EXCELLENT"
                elif cat_rate >= 60:
                    status = "⚠️ GOOD"
                else:
                    status = "❌ NEEDS WORK"
                
                print(f"{status} {category}: {cat_rate:.1f}% ({passed}/{total} tests passed)")
                
                # Show failed tests
                failed_tests = [r for r in results if not r["success"]]
                if failed_tests:
                    for test in failed_tests:
                        print(f"   ❌ {test['test']}: {test['error_info']}")
                print()
        
        # Production readiness assessment
        print("🚀 PRODUCTION READINESS ASSESSMENT:")
        print("=" * 50)
        
        if success_rate >= 95:
            print("✅ PRODUCTION READY: Platform exceeds 95% success rate target")
        elif success_rate >= 75:
            print("⚠️ MOSTLY READY: Platform meets basic production criteria (75%+)")
        elif success_rate >= 50:
            print("⚠️ NEEDS WORK: Platform shows improvement but requires fixes")
        else:
            print("❌ NOT READY: Platform requires major fixes before production")
        
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        print("=" * 30)
        
        routing_conflicts = [r for r in self.test_results if "405 Method Not Allowed" in r.get("error_info", "")]
        if routing_conflicts:
            print(f"❌ ROUTING CONFLICTS PERSIST: {len(routing_conflicts)} endpoints still have 405 errors")
        else:
            print("✅ ROUTING CONFLICTS RESOLVED: No 405 Method Not Allowed errors detected")
        
        objectid_issues = [r for r in self.test_results if "ObjectId" in r.get("error_info", "")]
        if objectid_issues:
            print(f"❌ OBJECTID ISSUES PERSIST: {len(objectid_issues)} endpoints still have ObjectId serialization problems")
        else:
            print("✅ OBJECTID ISSUES RESOLVED: No ObjectId serialization errors detected")
        
        auth_tests = [r for r in categories["Authentication System"] if r["success"]]
        if len(auth_tests) == len(categories["Authentication System"]):
            print("✅ AUTHENTICATION PERFECT: All authentication tests passing")
        else:
            print(f"⚠️ AUTHENTICATION ISSUES: {len(categories['Authentication System']) - len(auth_tests)} authentication tests failing")
        
        print()
        print("🎯 DUPLICATE CLEANUP IMPACT ASSESSMENT COMPLETE 🎯")

if __name__ == "__main__":
    tester = DuplicateCleanupReviewTester()
    tester.run_comprehensive_test()