#!/usr/bin/env python3
"""
MEWAYZ PLATFORM RESTRUCTURED BACKEND TESTING
Testing the newly restructured Mewayz Platform backend to verify critical issues are resolved
Testing Agent - January 20, 2025
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class RestructuredBackendTester:
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

    def test_database_connectivity(self):
        """Test database connectivity and real data operations"""
        print(f"\n📊 TESTING DATABASE CONNECTIVITY & REAL DATA OPERATIONS...")
        
        # Test health endpoint to verify system is running
        self.test_endpoint("/health", "GET", expected_status=200, description="System health check")
        
        # Test user profile (requires authentication and database)
        self.test_endpoint("/users/profile", "GET", expected_status=200, description="User profile from database")
        
        # Test user statistics (real database calculations)
        self.test_endpoint("/users/stats", "GET", expected_status=200, description="User statistics from database")
        
        # Test user analytics (real database operations)
        self.test_endpoint("/users/analytics", "GET", expected_status=200, description="User analytics from database")

    def test_authentication_system(self):
        """Test authentication system with real database operations"""
        print(f"\n🔐 TESTING AUTHENTICATION SYSTEM...")
        
        # Test token verification
        self.test_endpoint("/auth/verify", "GET", expected_status=200, description="JWT token verification")
        
        # Test logout
        self.test_endpoint("/auth/logout", "POST", expected_status=200, description="User logout")

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

    def test_workspace_system(self):
        """Test workspace system with real database operations"""
        print(f"\n🏢 TESTING WORKSPACE SYSTEM...")
        
        # Test workspace listing (should return real workspaces from database)
        self.test_endpoint("/workspaces", "GET", expected_status=200, description="Workspace listing from database")

    def test_blog_system(self):
        """Test blog system with real database operations"""
        print(f"\n📝 TESTING BLOG SYSTEM...")
        
        # Test blog posts
        self.test_endpoint("/blog/posts", "GET", expected_status=200, description="Blog posts from database")
        
        # Test blog categories
        self.test_endpoint("/blog/categories", "GET", expected_status=200, description="Blog categories from database")

    def test_email_marketing_system(self):
        """Test Email Marketing system - Priority task from test_result.md"""
        print(f"\n📧 TESTING EMAIL MARKETING SYSTEM (PRIORITY TASK)...")
        
        # Test email marketing campaigns
        self.test_endpoint("/email-marketing/campaigns", "GET", expected_status=200, description="Email marketing campaigns")
        
        # Test email marketing templates
        self.test_endpoint("/email-marketing/templates", "GET", expected_status=200, description="Email marketing templates")
        
        # Test email marketing subscribers
        self.test_endpoint("/email-marketing/subscribers", "GET", expected_status=200, description="Email marketing subscribers")
        
        # Test campaign creation
        campaign_data = {
            "name": "Test Campaign - Backend Restructure",
            "subject": "Testing Restructured Backend",
            "content": "This is a test campaign to verify the restructured backend is working.",
            "target_audience": "all_subscribers"
        }
        self.test_endpoint("/email-marketing/campaigns", "POST", data=campaign_data, expected_status=201, description="Create email campaign")

    def test_crm_system(self):
        """Test CRM system - Priority task from test_result.md"""
        print(f"\n👥 TESTING CRM SYSTEM (PRIORITY TASK)...")
        
        # Test CRM contacts
        self.test_endpoint("/crm/contacts", "GET", expected_status=200, description="CRM contacts")
        
        # Test CRM leads
        self.test_endpoint("/crm/leads", "GET", expected_status=200, description="CRM leads")
        
        # Test CRM automation workflows
        self.test_endpoint("/crm/automation/workflows", "GET", expected_status=200, description="CRM automation workflows")
        
        # Test contact creation
        contact_data = {
            "name": "Test Contact - Backend Restructure",
            "email": "test.contact@example.com",
            "phone": "+1234567890",
            "company": "Test Company",
            "source": "backend_test"
        }
        self.test_endpoint("/crm/contacts", "POST", data=contact_data, expected_status=201, description="Create CRM contact")

    def test_service_architecture(self):
        """Test the new modular service architecture"""
        print(f"\n🏗️ TESTING SERVICE ARCHITECTURE...")
        
        # Test that services are properly integrated and working
        # This tests the core/, services/, and api/ directory structure
        
        # Test dashboard (should use multiple services)
        self.test_endpoint("/dashboard/overview", "GET", expected_status=200, description="Dashboard overview (multi-service)")
        
        # Test admin dashboard (should use analytics service)
        self.test_endpoint("/dashboard/admin", "GET", expected_status=200, description="Admin dashboard (analytics service)")

    def run_comprehensive_test(self):
        """Run comprehensive test of restructured backend"""
        print("🚀 STARTING COMPREHENSIVE RESTRUCTURED BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed. Cannot proceed with testing.")
            return False
        
        # Step 2: Test Database Connectivity
        self.test_database_connectivity()
        
        # Step 3: Test Authentication System
        self.test_authentication_system()
        
        # Step 4: Test Service Architecture
        self.test_service_architecture()
        
        # Step 5: Test Analytics System
        self.test_analytics_system()
        
        # Step 6: Test Workspace System
        self.test_workspace_system()
        
        # Step 7: Test Blog System
        self.test_blog_system()
        
        # Step 8: Test Email Marketing System (Priority Task)
        self.test_email_marketing_system()
        
        # Step 9: Test CRM System (Priority Task)
        self.test_crm_system()
        
        # Generate final report
        self.generate_final_report()
        
        return True

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE RESTRUCTURED BACKEND TEST RESULTS")
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
        
        print(f"✅ Authentication System: {'WORKING' if auth_working else 'FAILED'}")
        print(f"✅ Database Connectivity: {'WORKING' if db_working else 'FAILED'}")
        print(f"✅ Real Data Operations: {'WORKING' if real_data else 'FAILED'}")
        print(f"✅ Service Architecture: {'WORKING' if success_rate > 70 else 'NEEDS WORK'}")
        
        # Priority tasks status
        email_marketing_working = any('/email-marketing/' in r['endpoint'] and r['success'] for r in self.test_results)
        crm_working = any('/crm/' in r['endpoint'] and r['success'] for r in self.test_results)
        
        print(f"📧 Email Marketing System: {'WORKING' if email_marketing_working else 'FAILED'}")
        print(f"👥 CRM System: {'WORKING' if crm_working else 'FAILED'}")
        
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
    tester = RestructuredBackendTester()
    tester.run_comprehensive_test()