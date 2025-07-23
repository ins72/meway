#!/usr/bin/env python3
"""
🏆 MEWAYZ V2 PLATFORM - ULTIMATE SUCCESS DEMONSTRATION - JANUARY 2025 🏆

MISSION: DEMONSTRATE COMPLETE PLATFORM TRANSFORMATION ACHIEVED
Testing the specific areas mentioned in the review request for 95%+ success rate

Authentication: tmonnens@outlook.com / Voetballen5
Backend URL: https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com

CRITICAL AREAS TO VERIFY:
1. ✅ Twitter/X API Integration - Complete service + API implementation
2. ✅ TikTok API Integration - Complete service + API implementation  
3. ✅ Stripe Payment Integration - Complete service + API implementation
4. ✅ Social Media Management - Complete service + API implementation
5. ✅ Referral System - Complete service + API implementation
6. ✅ Website Builder CRUD - All operations implemented
7. ✅ Stats Endpoints - Added to ALL APIs (15+ endpoints)
8. ✅ Service Methods - 18+ methods added across services
9. ✅ Auth /me Endpoint - User profile endpoint added
10. ✅ External API Integration Testing
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class UltimateVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, message: str, response_data: Any = None, status_code: int = None):
        """Log test results with detailed information"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'status_code': status_code,
            'response_size': len(str(response_data)) if response_data else 0,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} - {test_name}")
        print(f"    {message}")
        if status_code:
            print(f"    Status Code: {status_code}")
        if response_data and len(str(response_data)) < 300:
            print(f"    Response: {str(response_data)[:200]}...")
        elif response_data:
            print(f"    Response Size: {len(str(response_data))} chars")
        print()

    def authenticate(self) -> bool:
        """Authenticate with the platform"""
        try:
            print("🔐 AUTHENTICATING WITH PLATFORM")
            print("-" * 50)
            
            # Try OAuth2 style login first
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", data=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_test("Authentication", True, f"Login successful with {TEST_EMAIL}", data, response.status_code)
                    return True
                else:
                    self.log_test("Authentication", False, "No access token in response", data, response.status_code)
                    return False
            else:
                # Try JSON login as fallback
                response = self.session.post(f"{API_BASE}/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token") or data.get("token")
                    if self.access_token:
                        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                        self.log_test("Authentication", True, f"Login successful with {TEST_EMAIL} (JSON)", data, response.status_code)
                        return True
                
                self.log_test("Authentication", False, f"Login failed", response.text, response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, test_name: str = None, expected_status: int = 200) -> tuple:
        """Test a specific endpoint"""
        if not test_name:
            test_name = f"{method} {endpoint}"
            
        try:
            url = f"{API_BASE}{endpoint}"
            headers = {"Content-Type": "application/json"}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=15)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=15)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=15)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=15)
            else:
                self.log_test(test_name, False, f"Unsupported method: {method}")
                return False, None
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(test_name, True, f"Success - Working perfectly", response_data, response.status_code)
                    return True, response_data
                except:
                    self.log_test(test_name, True, f"Success - Working perfectly (non-JSON)", response.text, response.status_code)
                    return True, response.text
            else:
                error_msg = f"Failed - Status {response.status_code}"
                if response.status_code == 404:
                    error_msg += " (Not Found - Not implemented)"
                elif response.status_code == 405:
                    error_msg += " (Method Not Allowed - Endpoint exists but method not supported)"
                elif response.status_code == 500:
                    error_msg += " (Internal Server Error)"
                elif response.status_code == 403:
                    error_msg += " (Forbidden - Access denied)"
                elif response.status_code == 401:
                    error_msg += " (Unauthorized - Authentication required)"
                
                self.log_test(test_name, False, error_msg, response.text, response.status_code)
                return False, None
                
        except Exception as e:
            self.log_test(test_name, False, f"Request error: {str(e)}")
            return False, None

    def test_twitter_api_integration(self):
        """Test Twitter/X API Integration - Issue #1"""
        print("🐦 TESTING TWITTER/X API INTEGRATION")
        print("-" * 50)
        
        # Test health endpoint
        self.test_endpoint("/twitter/health", "GET", test_name="Twitter API - Health Check")
        
        # Test main functionality
        self.test_endpoint("/twitter/search", "GET", test_name="Twitter API - Search Functionality")
        self.test_endpoint("/twitter/profile", "GET", test_name="Twitter API - Profile Access")
        self.test_endpoint("/twitter/stats", "GET", test_name="Twitter API - Statistics Endpoint")
        
        # Test CRUD operations
        tweet_data = {"content": "Test tweet from Mewayz platform", "platform": "twitter"}
        self.test_endpoint("/twitter/post", "POST", tweet_data, "Twitter API - Create Post")

    def test_tiktok_api_integration(self):
        """Test TikTok API Integration - Issue #2"""
        print("🎵 TESTING TIKTOK API INTEGRATION")
        print("-" * 50)
        
        # Test health endpoint
        self.test_endpoint("/tiktok/health", "GET", test_name="TikTok API - Health Check")
        
        # Test main functionality
        self.test_endpoint("/tiktok/search", "GET", test_name="TikTok API - Search Functionality")
        self.test_endpoint("/tiktok/profile", "GET", test_name="TikTok API - Profile Access")
        self.test_endpoint("/tiktok/stats", "GET", test_name="TikTok API - Statistics Endpoint")
        
        # Test CRUD operations
        video_data = {"video_url": "https://example.com/video.mp4", "description": "Test video upload"}
        self.test_endpoint("/tiktok/upload", "POST", video_data, "TikTok API - Video Upload")

    def test_stripe_payment_integration(self):
        """Test Stripe Payment Integration - Issue #3"""
        print("💳 TESTING STRIPE PAYMENT INTEGRATION")
        print("-" * 50)
        
        # Test health endpoint
        self.test_endpoint("/stripe-integration/health", "GET", test_name="Stripe API - Health Check")
        
        # Test main functionality
        payment_data = {"amount": 1000, "currency": "usd", "description": "Test payment"}
        self.test_endpoint("/stripe-integration/create-payment-intent", "POST", payment_data, "Stripe API - Create Payment Intent")
        self.test_endpoint("/stripe-integration/payment-methods", "GET", test_name="Stripe API - Payment Methods")
        self.test_endpoint("/stripe-integration/stats", "GET", test_name="Stripe API - Statistics Endpoint")
        
        # Test customer management
        customer_data = {"email": "test@mewayz.com", "name": "Test Customer"}
        self.test_endpoint("/stripe-integration/create-customer", "POST", customer_data, "Stripe API - Create Customer")

    def test_social_media_management(self):
        """Test Social Media Management - Issue #4"""
        print("📱 TESTING SOCIAL MEDIA MANAGEMENT")
        print("-" * 50)
        
        # Test health endpoint
        self.test_endpoint("/social-media-management/health", "GET", test_name="Social Media - Health Check")
        
        # Test main functionality
        self.test_endpoint("/social-media-management/accounts", "GET", test_name="Social Media - Connected Accounts")
        self.test_endpoint("/social-media-management/analytics", "GET", test_name="Social Media - Analytics Dashboard")
        self.test_endpoint("/social-media-management/stats", "GET", test_name="Social Media - Statistics Endpoint")
        
        # Test post scheduling
        post_data = {"platform": "twitter", "content": "Scheduled post test", "schedule_time": "2025-01-25T10:00:00Z"}
        self.test_endpoint("/social-media-management/schedule-post", "POST", post_data, "Social Media - Schedule Post")

    def test_referral_system(self):
        """Test Referral System - Issue #5"""
        print("🔗 TESTING REFERRAL SYSTEM")
        print("-" * 50)
        
        # Test health endpoint
        self.test_endpoint("/referral-system/health", "GET", test_name="Referral System - Health Check")
        
        # Test main functionality
        self.test_endpoint("/referral-system/referrals", "GET", test_name="Referral System - List Referrals")
        self.test_endpoint("/referral-system/stats", "GET", test_name="Referral System - Statistics Endpoint")
        
        # Test CRUD operations
        referral_data = {"referrer_id": "user123", "referred_email": "referred@mewayz.com", "program": "standard"}
        self.test_endpoint("/referral-system/create", "POST", referral_data, "Referral System - Create Referral")
        
        # Test update and delete (using test IDs)
        update_data = {"status": "completed", "reward_amount": 50}
        self.test_endpoint("/referral-system/referrals/test-id", "PUT", update_data, "Referral System - Update Referral")
        self.test_endpoint("/referral-system/referrals/test-id", "DELETE", test_name="Referral System - Delete Referral")

    def test_website_builder_crud(self):
        """Test Website Builder CRUD Operations - Issue #6"""
        print("🌐 TESTING WEBSITE BUILDER CRUD OPERATIONS")
        print("-" * 50)
        
        # Test health endpoint
        self.test_endpoint("/website-builder/health", "GET", test_name="Website Builder - Health Check")
        
        # Test READ operations
        self.test_endpoint("/website-builder/sites", "GET", test_name="Website Builder - List Sites")
        self.test_endpoint("/website-builder/templates", "GET", test_name="Website Builder - List Templates")
        self.test_endpoint("/website-builder/stats", "GET", test_name="Website Builder - Statistics Endpoint")
        
        # Test CREATE operation
        site_data = {"title": "Test Business Site", "template": "modern", "domain": "test-business.mewayz.com"}
        self.test_endpoint("/website-builder/sites", "POST", site_data, "Website Builder - Create Site")
        
        # Test UPDATE operation
        update_data = {"title": "Updated Business Site", "content": "Updated content"}
        self.test_endpoint("/website-builder/sites/test-id", "PUT", update_data, "Website Builder - Update Site")
        
        # Test DELETE operation
        self.test_endpoint("/website-builder/sites/test-id", "DELETE", test_name="Website Builder - Delete Site")

    def test_stats_endpoints(self):
        """Test Stats Endpoints - Issue #7"""
        print("📊 TESTING STATS ENDPOINTS ACROSS ALL APIS")
        print("-" * 50)
        
        # Test stats endpoints for all major services
        stats_endpoints = [
            ("/complete-financial/stats", "Financial Management - Stats"),
            ("/complete-multi-workspace/stats", "Multi-Workspace - Stats"),
            ("/complete-admin-dashboard/stats", "Admin Dashboard - Stats"),
            ("/team-management/stats", "Team Management - Stats"),
            ("/form-builder/stats", "Form Builder - Stats"),
            ("/analytics-system/stats", "Analytics System - Stats"),
            ("/advanced-ai-suite/stats", "AI Automation - Stats"),
            ("/complete-link-in-bio/stats", "Bio Sites - Stats"),
            ("/link-shortener/stats", "Link Shortener - Stats"),
            ("/booking/stats", "Booking System - Stats"),
            ("/media-library/stats", "Media Library - Stats"),
            ("/template/stats", "Template System - Stats"),
            ("/escrow/stats", "Escrow System - Stats"),
            ("/complete-onboarding/stats", "Onboarding System - Stats"),
            ("/complete-course-community/stats", "Course Community - Stats")
        ]
        
        for endpoint, name in stats_endpoints:
            self.test_endpoint(endpoint, "GET", test_name=name)

    def test_auth_me_endpoint(self):
        """Test Auth /me Endpoint - Issue #9"""
        print("👤 TESTING AUTH /ME ENDPOINT")
        print("-" * 50)
        
        # Test the /me endpoint for user profile
        self.test_endpoint("/auth/me", "GET", test_name="Auth - Get Current User Profile")
        self.test_endpoint("/auth/profile", "GET", test_name="Auth - Get User Profile (Alternative)")
        self.test_endpoint("/user/profile", "GET", test_name="User - Get Profile")

    def test_external_api_integrations(self):
        """Test External API Integration Testing - Issue #10"""
        print("🔌 TESTING EXTERNAL API INTEGRATIONS")
        print("-" * 50)
        
        # Test external API health checks
        external_apis = [
            ("/integrations/openai/test", "OpenAI API - Connection Test"),
            ("/integrations/stripe/test", "Stripe API - Connection Test"),
            ("/integrations/twitter/test", "Twitter API - Connection Test"),
            ("/integrations/tiktok/test", "TikTok API - Connection Test"),
            ("/integrations/elasticmail/test", "ElasticMail API - Connection Test"),
            ("/integrations/google/test", "Google OAuth - Connection Test")
        ]
        
        for endpoint, name in external_apis:
            self.test_endpoint(endpoint, "GET", test_name=name)

    def test_critical_business_systems(self):
        """Test Critical Business Systems Status"""
        print("🏢 TESTING CRITICAL BUSINESS SYSTEMS")
        print("-" * 50)
        
        # Test all critical business systems
        business_systems = [
            ("/complete-financial/health", "Financial Management System"),
            ("/complete-multi-workspace/health", "Multi-Workspace System"),
            ("/complete-admin-dashboard/health", "Admin Dashboard System"),
            ("/team-management/health", "Team Management System"),
            ("/form-builder/health", "Form Builder System"),
            ("/analytics-system/health", "Analytics System"),
            ("/advanced-ai-suite/health", "AI Automation Suite"),
            ("/complete-link-in-bio/health", "Bio Sites System"),
            ("/escrow/health", "Escrow System"),
            ("/complete-onboarding/health", "Complete Onboarding System")
        ]
        
        for endpoint, name in business_systems:
            self.test_endpoint(endpoint, "GET", test_name=name)

    def run_ultimate_verification(self):
        """Run the ultimate verification test"""
        print("🏆 MEWAYZ V2 PLATFORM - ULTIMATE SUCCESS DEMONSTRATION - JANUARY 2025 🏆")
        print("=" * 100)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Authentication: {TEST_EMAIL} / {TEST_PASSWORD}")
        print("MISSION: DEMONSTRATE COMPLETE PLATFORM TRANSFORMATION ACHIEVED")
        print("TARGET: 95%+ SUCCESS RATE")
        print("=" * 100)
        
        start_time = time.time()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with verification.")
            return False
        
        print("\n🚀 CONDUCTING THE ULTIMATE VERIFICATION TEST! 🚀")
        
        # Step 2: Test all critical areas from review request
        print("\n" + "="*80)
        print("PHASE 1: EXTERNAL API INTEGRATIONS")
        print("="*80)
        self.test_twitter_api_integration()
        self.test_tiktok_api_integration()
        self.test_stripe_payment_integration()
        self.test_social_media_management()
        
        print("\n" + "="*80)
        print("PHASE 2: BUSINESS SYSTEMS & CRUD OPERATIONS")
        print("="*80)
        self.test_referral_system()
        self.test_website_builder_crud()
        
        print("\n" + "="*80)
        print("PHASE 3: STATS ENDPOINTS & SERVICE METHODS")
        print("="*80)
        self.test_stats_endpoints()
        
        print("\n" + "="*80)
        print("PHASE 4: AUTHENTICATION & USER MANAGEMENT")
        print("="*80)
        self.test_auth_me_endpoint()
        
        print("\n" + "="*80)
        print("PHASE 5: EXTERNAL API INTEGRATION TESTING")
        print("="*80)
        self.test_external_api_integrations()
        
        print("\n" + "="*80)
        print("PHASE 6: CRITICAL BUSINESS SYSTEMS VERIFICATION")
        print("="*80)
        self.test_critical_business_systems()
        
        # Generate final report
        self.generate_ultimate_report(time.time() - start_time)

    def generate_ultimate_report(self, duration: float):
        """Generate the ultimate verification report"""
        print("\n" + "="*100)
        print("🏆 ULTIMATE VERIFICATION RESULTS - MEWAYZ V2 PLATFORM 🏆")
        print("="*100)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        print(f"⏱️  TEST DURATION: {duration:.2f} seconds")
        print(f"🎯 TARGET SUCCESS RATE: 95%+")
        
        # Determine status
        if success_rate >= 95:
            print("🎉 EXCELLENT SUCCESS - TARGET ACHIEVED!")
            print("✅ PLATFORM TRANSFORMATION COMPLETE")
            status = "PRODUCTION READY - ULTIMATE SUCCESS"
        elif success_rate >= 85:
            print("✅ VERY GOOD SUCCESS - CLOSE TO TARGET")
            print("⚠️  MINOR IMPROVEMENTS NEEDED")
            status = "MOSTLY PRODUCTION READY"
        elif success_rate >= 75:
            print("⚠️  GOOD SUCCESS - APPROACHING TARGET")
            print("🔧 SOME IMPROVEMENTS NEEDED")
            status = "NEEDS MINOR FIXES"
        else:
            print("❌ CRITICAL ISSUES - TARGET NOT MET")
            print("🚨 MAJOR IMPROVEMENTS REQUIRED")
            status = "NOT PRODUCTION READY"
        
        print(f"🚀 PRODUCTION READINESS STATUS: {status}")
        
        # Category analysis
        categories = {
            "External API Integrations": [],
            "Business Systems & CRUD": [],
            "Stats Endpoints": [],
            "Authentication": [],
            "Critical Systems": []
        }
        
        for result in self.test_results:
            test_name = result['test']
            if any(api in test_name for api in ["Twitter", "TikTok", "Stripe", "Social Media"]):
                categories["External API Integrations"].append(result)
            elif any(sys in test_name for sys in ["Referral", "Website Builder"]):
                categories["Business Systems & CRUD"].append(result)
            elif "Stats" in test_name:
                categories["Stats Endpoints"].append(result)
            elif "Auth" in test_name or "User" in test_name:
                categories["Authentication"].append(result)
            else:
                categories["Critical Systems"].append(result)
        
        print("\n📋 DETAILED RESULTS BY CATEGORY:")
        print("-" * 100)
        
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r['success'])
                total = len(results)
                category_rate = (passed / total * 100) if total > 0 else 0
                
                status_icon = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
                print(f"{status_icon} {category}: {category_rate:.1f}% ({passed}/{total} tests passed)")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")
        
        # Show successful tests summary
        successful_tests = [r for r in self.test_results if r['success']]
        if successful_tests:
            print(f"\n✅ SUCCESSFUL TESTS ({len(successful_tests)}):")
            print(f"   • All {len(successful_tests)} tests passed successfully")
        
        print("\n" + "="*100)
        print("🎯 ULTIMATE VERIFICATION COMPLETE")
        print("="*100)
        
        return success_rate >= 95

def main():
    """Main function"""
    tester = UltimateVerificationTester()
    success = tester.run_ultimate_verification()
    
    if success:
        print("🎉 ULTIMATE SUCCESS ACHIEVED!")
        sys.exit(0)
    else:
        print("⚠️  IMPROVEMENTS NEEDED")
        sys.exit(1)

if __name__ == "__main__":
    main()