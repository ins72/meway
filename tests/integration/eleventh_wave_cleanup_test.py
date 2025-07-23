#!/usr/bin/env python3
"""
ELEVENTH WAVE MIGRATION CLEANUP VERIFICATION TEST - MEWAYZ PLATFORM
Post-Cleanup Testing: Verify all systems operational after legacy code removal
Testing Agent - December 2024
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class EleventhWaveCleanupTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, endpoint, method, status, response_time, success, details="", data_size=0):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        result = {
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'response_time': f"{response_time:.3f}s",
            'success': success,
            'details': details,
            'data_size': data_size
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {method} {endpoint} - {status} ({response_time:.3f}s) - {details}")
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print(f"\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        print(f"Email: {ADMIN_EMAIL}")
        
        # OAuth2PasswordRequestForm expects form data with username/password
        login_data = {
            "username": ADMIN_EMAIL,  # OAuth2 uses 'username' field for email
            "password": ADMIN_PASSWORD
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/auth/login", data=login_data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token') or data.get('access_token')
                if self.auth_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("/auth/login", "POST", response.status_code, response_time, True, 
                                f"Admin authentication successful, token: {self.auth_token[:20]}...")
                    return True
                else:
                    self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                                "No access token in response")
                    return False
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Login failed: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.log_test("/auth/login", "POST", 0, 0, False, f"Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, endpoint, method="GET", data=None, expected_status=200, description=""):
        """Test a single endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            # Check if response is successful
            success = response.status_code == expected_status
            
            # Get response details
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    details += f" - Error: {response_data.get('detail', 'Unknown error')}"
            except:
                data_size = len(response.text)
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    details += f" - Error: {response.text[:100]}"
            
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size)
            return success, response
            
        except requests.exceptions.Timeout:
            self.log_test(endpoint, method, 0, 30.0, False, f"{description} - Request timeout")
            return False, None
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"{description} - Error: {str(e)}")
            return False, None

    def test_core_authentication_system(self):
        """Test core authentication system"""
        print(f"\n🔐 TESTING CORE AUTHENTICATION SYSTEM...")
        
        # Test user profile access
        self.test_endpoint("/users/profile", "GET", description="Get user profile")
        self.test_endpoint("/users/me", "GET", description="Get current user info")
        
    def test_core_workspace_functionality(self):
        """Test core workspace functionality"""
        print(f"\n🏢 TESTING CORE WORKSPACE FUNCTIONALITY...")
        
        # Test workspace endpoints
        self.test_endpoint("/workspaces", "GET", description="Get user workspaces")
        self.test_endpoint("/dashboard/overview", "GET", description="Get dashboard overview")
        
    def test_eleventh_wave_content_creation_suite(self):
        """Test Eleventh Wave Content Creation Suite (modular structure)"""
        print(f"\n🎨 TESTING ELEVENTH WAVE - CONTENT CREATION SUITE...")
        
        # Video Editor Features
        self.test_endpoint("/content-creation/video-editor/features", "GET", 
                         description="Video editor features and capabilities")
        self.test_endpoint("/content-creation/video-editor/projects", "GET", 
                         description="User's video editing projects")
        
        # AI Content Generation
        self.test_endpoint("/content-creation/content-generator/capabilities", "GET", 
                         description="AI content generation capabilities")
        
        # Asset Library
        self.test_endpoint("/content-creation/asset-library", "GET", 
                         description="Content asset library")
        
        # Analytics
        self.test_endpoint("/content-creation/analytics/content-performance", "GET", 
                         description="Content performance analytics")
        
    def test_eleventh_wave_customer_experience_suite(self):
        """Test Eleventh Wave Customer Experience Suite (modular structure)"""
        print(f"\n👥 TESTING ELEVENTH WAVE - CUSTOMER EXPERIENCE SUITE...")
        
        # Live Chat System
        self.test_endpoint("/customer-experience/live-chat/overview", "GET", 
                         description="Live chat system overview")
        self.test_endpoint("/customer-experience/live-chat/agents", "GET", 
                         description="Chat agents status and performance")
        
        # Customer Journey
        self.test_endpoint("/customer-experience/customer-journey/analytics", "GET", 
                         description="Customer journey analytics")
        
        # Feedback System
        self.test_endpoint("/customer-experience/feedback/surveys", "GET", 
                         description="Customer feedback surveys")
        
        # Personalization Engine
        self.test_endpoint("/customer-experience/personalization/engine", "GET", 
                         description="Personalization engine insights")
        
    def test_eleventh_wave_social_media_suite(self):
        """Test Eleventh Wave Social Media Suite (modular structure)"""
        print(f"\n📱 TESTING ELEVENTH WAVE - SOCIAL MEDIA SUITE...")
        
        # Social Media Listening
        self.test_endpoint("/social-media/listening/overview", "GET", 
                         description="Social media listening overview")
        self.test_endpoint("/social-media/listening/mentions", "GET", 
                         description="Brand mentions across platforms")
        
        # Publishing System
        self.test_endpoint("/social-media/publishing/calendar", "GET", 
                         description="Social media publishing calendar")
        self.test_endpoint("/social-media/publishing/posts", "GET", 
                         description="Social media posts")
        
        # Analytics
        self.test_endpoint("/social-media/analytics/performance", "GET", 
                         description="Social media performance analytics")
        
        # Influencer Management
        self.test_endpoint("/social-media/influencer/discovery", "GET", 
                         description="Influencer discovery")
        
    def test_key_business_endpoints(self):
        """Test key business endpoints to ensure no regressions"""
        print(f"\n💼 TESTING KEY BUSINESS ENDPOINTS...")
        
        # Financial Management
        self.test_endpoint("/financial/dashboard", "GET", description="Financial dashboard")
        
        # E-commerce
        self.test_endpoint("/ecommerce/products", "GET", description="E-commerce products")
        
        # Analytics
        self.test_endpoint("/analytics/overview", "GET", description="Analytics overview")
        
        # Subscription Management
        self.test_endpoint("/subscriptions/plans", "GET", description="Subscription plans")
        
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("=" * 80)
        print("🌊 ELEVENTH WAVE MIGRATION CLEANUP VERIFICATION TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with tests")
            return False
            
        # Step 2: Core System Tests
        self.test_core_authentication_system()
        self.test_core_workspace_functionality()
        
        # Step 3: Eleventh Wave Features (New Modular Structure)
        self.test_eleventh_wave_content_creation_suite()
        self.test_eleventh_wave_customer_experience_suite()
        self.test_eleventh_wave_social_media_suite()
        
        # Step 4: Key Business Endpoints (Regression Testing)
        self.test_key_business_endpoints()
        
        # Step 5: Results Summary
        self.print_results()
        
        return self.passed_tests == self.total_tests
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🌊 ELEVENTH WAVE CLEANUP VERIFICATION RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print(f"\n✅ PERFECT SUCCESS - All systems operational after Eleventh Wave cleanup!")
        elif success_rate >= 90:
            print(f"\n🟡 EXCELLENT - Minor issues detected, core functionality intact")
        elif success_rate >= 75:
            print(f"\n🟠 GOOD - Some issues detected, investigation needed")
        else:
            print(f"\n❌ CRITICAL - Major issues detected, immediate attention required")
        
        # Print failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   {test['method']} {test['endpoint']} - {test['details']}")
        
        print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

if __name__ == "__main__":
    tester = EleventhWaveCleanupTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)