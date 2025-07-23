#!/usr/bin/env python3
"""
ACCURATE FOCUSED REVIEW REQUEST BACKEND TESTING - JANUARY 2025
Testing specific areas mentioned in the review request with proper error handling
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class AccurateFocusedTester:
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
    
    def make_request(self, method, url, **kwargs):
        """Make request with proper error handling"""
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            
            # Try to parse JSON response
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                else:
                    data = {"raw_response": response.text, "content_type": response.headers.get('content-type')}
            except:
                data = {"raw_response": response.text, "content_type": response.headers.get('content-type')}
            
            return response.status_code, data
        except Exception as e:
            return None, str(e)
            
    def authenticate(self):
        """Authenticate with admin credentials"""
        print(f"\n🔐 AUTHENTICATING with {ADMIN_EMAIL}...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        status_code, data = self.make_request("POST", f"{API_BASE}/auth/login", json=login_data)
        
        if status_code == 200 and isinstance(data, dict):
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
            self.log_result("Authentication", "FAIL", data, f"HTTP {status_code}")
            return False
    
    def test_twitter_api_integration(self):
        """Test Twitter API Integration"""
        print(f"\n🐦 TESTING TWITTER API INTEGRATION...")
        
        # Test 1: Health Check
        status_code, data = self.make_request("GET", f"{API_BASE}/twitter/health")
        if status_code == 200:
            self.log_result("Twitter Health Check", "PASS", data)
        else:
            self.log_result("Twitter Health Check", "FAIL", data, f"HTTP {status_code}")
        
        # Test 2: List Tweets
        status_code, data = self.make_request("GET", f"{API_BASE}/twitter/", params={"limit": 10})
        if status_code == 200:
            self.log_result("Twitter List Tweets", "PASS", data)
        else:
            self.log_result("Twitter List Tweets", "FAIL", data, f"HTTP {status_code}")
        
        # Test 3: Search Functionality
        status_code, data = self.make_request("GET", f"{API_BASE}/twitter/search", params={"query": "python", "limit": 10})
        if status_code == 200:
            self.log_result("Twitter Search", "PASS", data)
        else:
            self.log_result("Twitter Search", "FAIL", data, f"HTTP {status_code}")
        
        # Test 4: Tweet Creation (CRUD Operation)
        tweet_data = {"text": "Test tweet from Mewayz platform", "hashtags": ["#test"]}
        status_code, data = self.make_request("POST", f"{API_BASE}/twitter/", json=tweet_data)
        if status_code == 200:
            self.log_result("Twitter Tweet Creation", "PASS", data)
        else:
            self.log_result("Twitter Tweet Creation", "FAIL", data, f"HTTP {status_code}")
        
        # Test 5: Analytics/Stats
        status_code, data = self.make_request("GET", f"{API_BASE}/twitter/stats")
        if status_code == 200:
            self.log_result("Twitter Analytics", "PASS", data)
        else:
            self.log_result("Twitter Analytics", "FAIL", data, f"HTTP {status_code}")
    
    def test_referral_system(self):
        """Test Referral System"""
        print(f"\n🎯 TESTING REFERRAL SYSTEM...")
        
        # Test 1: Health Check
        status_code, data = self.make_request("GET", f"{API_BASE}/referral-system/health")
        if status_code == 200:
            self.log_result("Referral System Health Check", "PASS", data)
        else:
            self.log_result("Referral System Health Check", "FAIL", data, f"HTTP {status_code}")
        
        # Test 2: List Referral Programs
        status_code, data = self.make_request("GET", f"{API_BASE}/referral-system/", params={"limit": 20})
        if status_code == 200:
            self.log_result("Referral System List Programs", "PASS", data)
        else:
            self.log_result("Referral System List Programs", "FAIL", data, f"HTTP {status_code}")
        
        # Test 3: Create Referral Program (Test ObjectId serialization)
        program_data = {
            "name": "Test Referral Program",
            "description": "Testing ObjectId serialization fixes",
            "reward_type": "percentage",
            "reward_value": 10.0,
            "max_referrals": 100,
            "active": True
        }
        status_code, data = self.make_request("POST", f"{API_BASE}/referral-system/", json=program_data)
        if status_code == 200:
            self.log_result("Referral System Create Program", "PASS", data)
        else:
            self.log_result("Referral System Create Program", "FAIL", data, f"HTTP {status_code}")
        
        # Test 4: Analytics
        status_code, data = self.make_request("GET", f"{API_BASE}/referral-system/stats")
        if status_code == 200:
            self.log_result("Referral System Analytics", "PASS", data)
        else:
            self.log_result("Referral System Analytics", "FAIL", data, f"HTTP {status_code}")
    
    def test_tiktok_api(self):
        """Test TikTok API"""
        print(f"\n🎵 TESTING TIKTOK API...")
        
        # Test 1: Health Check
        status_code, data = self.make_request("GET", f"{API_BASE}/tiktok/health")
        if status_code == 200:
            self.log_result("TikTok Health Check", "PASS", data)
        else:
            self.log_result("TikTok Health Check", "FAIL", data, f"HTTP {status_code}")
        
        # Test 2: List Posts
        status_code, data = self.make_request("GET", f"{API_BASE}/tiktok/", params={"limit": 10})
        if status_code == 200:
            self.log_result("TikTok List Posts", "PASS", data)
        else:
            self.log_result("TikTok List Posts", "FAIL", data, f"HTTP {status_code}")
        
        # Test 3: Search Functionality
        status_code, data = self.make_request("GET", f"{API_BASE}/tiktok/search", params={"query": "programming", "limit": 10})
        if status_code == 200:
            self.log_result("TikTok Search", "PASS", data)
        else:
            self.log_result("TikTok Search", "FAIL", data, f"HTTP {status_code}")
        
        # Test 4: Video Upload
        upload_data = {
            "title": "Test Video Upload",
            "description": "Testing TikTok API integration",
            "video_url": "https://example.com/test-video.mp4",
            "hashtags": ["#test", "#api"]
        }
        status_code, data = self.make_request("POST", f"{API_BASE}/tiktok/upload", json=upload_data)
        if status_code == 200:
            self.log_result("TikTok Video Upload", "PASS", data)
        else:
            self.log_result("TikTok Video Upload", "FAIL", data, f"HTTP {status_code}")
        
        # Test 5: Analytics
        status_code, data = self.make_request("GET", f"{API_BASE}/tiktok/stats")
        if status_code == 200:
            self.log_result("TikTok Analytics", "PASS", data)
        else:
            self.log_result("TikTok Analytics", "FAIL", data, f"HTTP {status_code}")
    
    def test_stripe_integration(self):
        """Test Stripe Integration"""
        print(f"\n💳 TESTING STRIPE INTEGRATION...")
        
        # Test 1: Health Check
        status_code, data = self.make_request("GET", f"{API_BASE}/stripe-integration/health")
        if status_code == 200:
            self.log_result("Stripe Health Check", "PASS", data)
        else:
            self.log_result("Stripe Health Check", "FAIL", data, f"HTTP {status_code}")
        
        # Test 2: List Payments
        status_code, data = self.make_request("GET", f"{API_BASE}/stripe-integration/", params={"limit": 10})
        if status_code == 200:
            self.log_result("Stripe List Payments", "PASS", data)
        else:
            self.log_result("Stripe List Payments", "FAIL", data, f"HTTP {status_code}")
        
        # Test 3: Create Payment Intent
        payment_data = {
            "amount": 2000,  # $20.00 in cents
            "currency": "usd",
            "description": "Test payment for Mewayz platform",
            "customer_email": ADMIN_EMAIL
        }
        status_code, data = self.make_request("POST", f"{API_BASE}/stripe-integration/", json=payment_data)
        if status_code == 200:
            self.log_result("Stripe Create Payment Intent", "PASS", data)
        else:
            self.log_result("Stripe Create Payment Intent", "FAIL", data, f"HTTP {status_code}")
        
        # Test 4: Payment Methods
        status_code, data = self.make_request("GET", f"{API_BASE}/stripe-integration/payment-methods")
        if status_code == 200:
            self.log_result("Stripe Payment Methods", "PASS", data)
        else:
            self.log_result("Stripe Payment Methods", "FAIL", data, f"HTTP {status_code}")
        
        # Test 5: Create Customer
        customer_data = {
            "email": ADMIN_EMAIL,
            "name": "Test Customer",
            "description": "Test customer for Mewayz platform"
        }
        status_code, data = self.make_request("POST", f"{API_BASE}/stripe-integration/customers", json=customer_data)
        if status_code == 200:
            self.log_result("Stripe Create Customer", "PASS", data)
        else:
            self.log_result("Stripe Create Customer", "FAIL", data, f"HTTP {status_code}")
    
    def test_authentication_system(self):
        """Test Authentication System"""
        print(f"\n🔐 TESTING AUTHENTICATION SYSTEM...")
        
        # Test 1: Token Validation (Get Current User)
        status_code, data = self.make_request("GET", f"{API_BASE}/auth/me")
        if status_code == 200:
            self.log_result("JWT Token Validation", "PASS", data)
        else:
            self.log_result("JWT Token Validation", "FAIL", data, f"HTTP {status_code}")
        
        # Test 2: Profile Access
        status_code, data = self.make_request("GET", f"{API_BASE}/auth/profile")
        if status_code == 200:
            self.log_result("Authentication Profile Access", "PASS", data)
        else:
            self.log_result("Authentication Profile Access", "FAIL", data, f"HTTP {status_code}")
        
        # Test 3: Admin Access (List Auth Records)
        status_code, data = self.make_request("GET", f"{API_BASE}/auth/", params={"limit": 10})
        if status_code == 200:
            self.log_result("Authentication Admin Access", "PASS", data)
        else:
            self.log_result("Authentication Admin Access", "FAIL", data, f"HTTP {status_code}")
    
    def run_focused_tests(self):
        """Run all focused tests from review request"""
        print("🎯 ACCURATE FOCUSED REVIEW REQUEST BACKEND TESTING - JANUARY 2025")
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
        print("🎯 ACCURATE FOCUSED REVIEW REQUEST TESTING SUMMARY")
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
    tester = AccurateFocusedTester()
    tester.run_focused_tests()