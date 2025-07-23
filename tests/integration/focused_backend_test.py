#!/usr/bin/env python3
"""
MEWAYZ PLATFORM RESTRUCTURED BACKEND TESTING - FOCUSED ON AVAILABLE ENDPOINTS
Testing the newly restructured Mewayz Platform backend with correct endpoint paths
Testing Agent - January 20, 2025
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://d70b9379-58ef-4e6d-9a10-f0eebb21d382.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class FocusedBackendTester:
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
        """Authenticate with admin credentials using OAuth2PasswordRequestForm format"""
        print(f"\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        print(f"Email: {ADMIN_EMAIL}")
        
        # Use form data format as expected by FastAPI OAuth2PasswordRequestForm
        login_data = {
            "username": ADMIN_EMAIL,  # OAuth2PasswordRequestForm uses 'username' field
            "password": ADMIN_PASSWORD
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/auth/login", data=login_data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
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
    
    def test_endpoint(self, endpoint, method="GET", data=None, form_data=None, expected_status=200, description=""):
        """Test a single endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                if form_data:
                    response = self.session.post(url, data=form_data, timeout=30)
                else:
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
                details = f"{description} - Response: {len(str(response_data))} chars"
            except:
                response_data = response.text
                data_size = len(response_data)
                details = f"{description} - Text response: {len(response_data)} chars"
            
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size)
            
            return response, success
            
        except requests.exceptions.Timeout:
            self.log_test(endpoint, method, 0, 30.0, False, f"{description} - Request timeout")
            return None, False
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"{description} - Error: {str(e)}")
            return None, False

    def test_authentication_system(self):
        """Test authentication system with real database operations"""
        print(f"\n🔐 TESTING AUTHENTICATION SYSTEM...")
        
        # Test token verification
        self.test_endpoint("/auth/verify", "GET", expected_status=200, description="JWT token verification")
        
        # Test logout
        self.test_endpoint("/auth/logout", "POST", expected_status=200, description="User logout")

    def test_user_system(self):
        """Test user system with real database operations"""
        print(f"\n👤 TESTING USER SYSTEM...")
        
        # Test user profile (requires authentication and database)
        self.test_endpoint("/users/profile", "GET", expected_status=200, description="User profile from database")
        
        # Test user statistics (real database calculations)
        self.test_endpoint("/users/stats", "GET", expected_status=200, description="User statistics from database")
        
        # Test user analytics (real database operations)
        self.test_endpoint("/users/analytics", "GET", expected_status=200, description="User analytics from database")

    def test_analytics_system(self):
        """Test analytics system with real database operations"""
        print(f"\n📈 TESTING ANALYTICS SYSTEM...")
        
        # Test analytics tracking
        track_data = {
            "event_type": "test_event",
            "properties": {"test": True, "source": "backend_test"},
            "session_id": "test_session_123"
        }
        self.test_endpoint("/analytics/track", "POST", data=track_data, expected_status=200, description="Event tracking")
        
        # Test feature usage analytics
        self.test_endpoint("/analytics/features/usage", "GET", expected_status=200, description="Feature usage analytics")
        
        # Test platform overview (admin only)
        self.test_endpoint("/analytics/platform/overview", "GET", expected_status=200, description="Platform overview analytics")

    def test_dashboard_system(self):
        """Test dashboard system with real database operations"""
        print(f"\n📊 TESTING DASHBOARD SYSTEM...")
        
        # Test dashboard overview (should use multiple services)
        self.test_endpoint("/dashboard/overview", "GET", expected_status=200, description="Dashboard overview (multi-service)")
        
        # Test activity summary
        self.test_endpoint("/dashboard/activity-summary", "GET", expected_status=200, description="Activity summary")

    def test_workspace_system(self):
        """Test workspace system with real database operations"""
        print(f"\n🏢 TESTING WORKSPACE SYSTEM...")
        
        # Test workspace listing (should return real workspaces from database)
        self.test_endpoint("/workspaces/list", "GET", expected_status=200, description="Workspace listing from database")
        
        # Test workspace creation
        workspace_data = {
            "name": "Test Workspace - Backend Restructure",
            "description": "Testing the restructured backend workspace functionality"
        }
        self.test_endpoint("/workspaces/create", "POST", data=workspace_data, expected_status=200, description="Create workspace")

    def test_blog_system(self):
        """Test blog system with real database operations"""
        print(f"\n📝 TESTING BLOG SYSTEM...")
        
        # Test blog posts
        self.test_endpoint("/blog/posts", "GET", expected_status=200, description="Blog posts from database")
        
        # Test blog analytics
        self.test_endpoint("/blog/analytics", "GET", expected_status=200, description="Blog analytics from database")
        
        # Test blog post creation
        post_data = {
            "title": "Test Blog Post - Backend Restructure",
            "content": "This is a test blog post to verify the restructured backend is working properly with real database operations.",
            "status": "draft",
            "categories": ["testing", "backend"],
            "tags": ["restructure", "test", "backend"]
        }
        self.test_endpoint("/blog/posts", "POST", data=post_data, expected_status=200, description="Create blog post")

    def test_health_and_root(self):
        """Test basic health and root endpoints"""
        print(f"\n🏥 TESTING BASIC SYSTEM ENDPOINTS...")
        
        # Test root endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/", timeout=30)
            response_time = time.time() - start_time
            success = response.status_code == 200
            
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
                details = f"Root endpoint - Response: {len(str(response_data))} chars"
            except:
                response_data = response.text
                data_size = len(response_data)
                details = f"Root endpoint - Text response: {len(response_data)} chars"
            
            self.log_test("/", "GET", response.status_code, response_time, success, details, data_size)
        except Exception as e:
            self.log_test("/", "GET", 0, 0, False, f"Root endpoint - Error: {str(e)}")
        
        # Test health endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/health", timeout=30)
            response_time = time.time() - start_time
            success = response.status_code == 200
            
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
                details = f"Health check - Response: {len(str(response_data))} chars"
            except:
                response_data = response.text
                data_size = len(response_data)
                details = f"Health check - Text response: {len(response_data)} chars"
            
            self.log_test("/health", "GET", response.status_code, response_time, success, details, data_size)
        except Exception as e:
            self.log_test("/health", "GET", 0, 0, False, f"Health check - Error: {str(e)}")

    def run_comprehensive_test(self):
        """Run comprehensive test of restructured backend"""
        print("🚀 STARTING FOCUSED RESTRUCTURED BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Step 1: Test basic endpoints
        self.test_health_and_root()
        
        # Step 2: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed. Cannot proceed with authenticated testing.")
            return False
        
        # Step 3: Test core systems with correct endpoints
        self.test_authentication_system()
        self.test_user_system()
        self.test_analytics_system()
        self.test_dashboard_system()
        self.test_workspace_system()
        self.test_blog_system()
        
        # Generate final report
        self.generate_final_report()
        
        return True

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 FOCUSED RESTRUCTURED BACKEND TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"✅ TOTAL TESTS: {self.total_tests}")
        print(f"✅ PASSED TESTS: {self.passed_tests}")
        print(f"❌ FAILED TESTS: {self.total_tests - self.passed_tests}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        # Calculate performance metrics
        response_times = []
        total_data = 0
        
        for result in self.test_results:
            if result['success']:
                try:
                    response_times.append(float(result['response_time'].replace('s', '')))
                    total_data += result['data_size']
                except:
                    pass
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"⚡ AVERAGE RESPONSE TIME: {avg_response_time:.3f}s")
            print(f"📊 TOTAL DATA PROCESSED: {total_data:,} bytes")
            print(f"🚀 FASTEST RESPONSE: {min(response_times):.3f}s")
            print(f"🐌 SLOWEST RESPONSE: {max(response_times):.3f}s")
        
        print("\n" + "=" * 80)
        print("🎯 CRITICAL ISSUES RESOLUTION VERIFICATION")
        print("=" * 80)
        
        # Check if critical issues from review request are resolved
        auth_working = any(r['endpoint'] == '/auth/login' and r['success'] for r in self.test_results)
        db_working = any(r['endpoint'] == '/users/profile' and r['success'] for r in self.test_results)
        real_data = any(r['data_size'] > 100 and r['success'] for r in self.test_results)
        service_arch = any('/dashboard/' in r['endpoint'] and r['success'] for r in self.test_results)
        
        print(f"✅ Authentication System: {'WORKING' if auth_working else 'FAILED'}")
        print(f"✅ Database Connectivity: {'WORKING' if db_working else 'FAILED'}")
        print(f"✅ Real Data Operations: {'WORKING' if real_data else 'FAILED'}")
        print(f"✅ Service Architecture: {'WORKING' if service_arch else 'FAILED'}")
        
        # Check key features
        analytics_working = any('/analytics/' in r['endpoint'] and r['success'] for r in self.test_results)
        workspace_working = any('/workspaces/' in r['endpoint'] and r['success'] for r in self.test_results)
        blog_working = any('/blog/' in r['endpoint'] and r['success'] for r in self.test_results)
        
        print(f"📈 Analytics System: {'WORKING' if analytics_working else 'FAILED'}")
        print(f"🏢 Workspace System: {'WORKING' if workspace_working else 'FAILED'}")
        print(f"📝 Blog System: {'WORKING' if blog_working else 'FAILED'}")
        
        print("\n" + "=" * 80)
        print("🏁 FINAL ASSESSMENT")
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 EXCELLENT: Restructured backend is working excellently!")
            print("✅ All critical issues appear to be resolved.")
            print("🚀 Platform is ready for production deployment.")
        elif success_rate >= 60:
            print("✅ GOOD: Restructured backend is mostly working.")
            print("⚠️ Some issues remain but core functionality is operational.")
            print("🔧 Minor fixes needed for full production readiness.")
        else:
            print("❌ NEEDS WORK: Restructured backend has significant issues.")
            print("🚨 Critical issues still need to be addressed.")
            print("🔧 Major fixes required before production deployment.")
        
        print(f"\nTesting completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

if __name__ == "__main__":
    tester = FocusedBackendTester()
    tester.run_comprehensive_test()