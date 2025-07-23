#!/usr/bin/env python3
"""
SIXTH WAVE EMAIL MARKETING AND ADVANCED ANALYTICS TESTING - MEWAYZ PLATFORM
Re-testing after authentication fixes
Testing Agent - December 2024
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

class SixthWaveTester:
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
        print(f"\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Backend URL: {BACKEND_URL}")
        
        auth_url = f"{API_BASE}/auth/login"
        auth_data = {
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            start_time = time.time()
            response = self.session.post(auth_url, data=auth_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                auth_result = response.json()
                self.auth_token = auth_result.get('access_token')
                
                if self.auth_token:
                    # Set authorization header for all future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}',
                        'Content-Type': 'application/json'
                    })
                    
                    self.log_test(auth_url, "POST", response.status_code, response_time, True, 
                                f"Authentication successful - Token: {self.auth_token[:20]}...")
                    return True
                else:
                    self.log_test(auth_url, "POST", response.status_code, response_time, False, 
                                "No access token in response")
                    return False
            else:
                self.log_test(auth_url, "POST", response.status_code, response_time, False, 
                            f"Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(auth_url, "POST", 0, 0, False, f"Authentication error: {str(e)}")
            return False
    
    def test_get_endpoint(self, endpoint, expected_success=True):
        """Test GET endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            response = self.session.get(url)
            response_time = time.time() - start_time
            
            success = response.status_code == 200 if expected_success else response.status_code != 200
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    data_str = json.dumps(data, indent=2)
                    data_size = len(data_str)
                    details = f"Success - Data size: {data_size} chars"
                except:
                    data_size = len(response.text)
                    details = f"Success - Response size: {data_size} chars"
            else:
                details = f"Error: {response.text[:200]}"
                data_size = 0
            
            self.log_test(url, "GET", response.status_code, response_time, success, details, data_size)
            return success
            
        except Exception as e:
            self.log_test(url, "GET", 0, 0, False, f"Request error: {str(e)}")
            return False
    
    def test_post_endpoint(self, endpoint, data, expected_success=True):
        """Test POST endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            response = self.session.post(url, json=data)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 201] if expected_success else response.status_code not in [200, 201]
            
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    result_str = json.dumps(result, indent=2)
                    data_size = len(result_str)
                    details = f"Success - Created/Updated - Data size: {data_size} chars"
                except:
                    data_size = len(response.text)
                    details = f"Success - Response size: {data_size} chars"
            else:
                details = f"Error: {response.text[:200]}"
                data_size = 0
            
            self.log_test(url, "POST", response.status_code, response_time, success, details, data_size)
            return success
            
        except Exception as e:
            self.log_test(url, "POST", 0, 0, False, f"Request error: {str(e)}")
            return False

    def test_email_marketing_system(self):
        """Test Email Marketing System endpoints"""
        print(f"\n📧 TESTING EMAIL MARKETING SYSTEM")
        print("=" * 60)
        
        # Test previously failing endpoints
        print("\n🔍 Testing Previously Failing Endpoints:")
        self.test_get_endpoint("/email-marketing/campaigns")
        self.test_get_endpoint("/email-marketing/lists")
        self.test_get_endpoint("/email-marketing/contacts")
        self.test_get_endpoint("/email-marketing/templates")
        
        # Test POST endpoints
        print("\n📝 Testing POST Endpoints:")
        
        # Test campaign creation
        campaign_data = {
            "name": "Sixth Wave Test Campaign",
            "subject": "Testing Email Marketing System",
            "content": "This is a test campaign for the Sixth Wave migration",
            "recipient_list_id": "test-list-id",
            "schedule_type": "immediate"
        }
        self.test_post_endpoint("/email-marketing/campaigns", campaign_data)
        
        # Test email list creation
        list_data = {
            "name": "Sixth Wave Test List",
            "description": "Test email list for Sixth Wave migration",
            "tags": ["test", "sixth-wave"]
        }
        self.test_post_endpoint("/email-marketing/lists", list_data)
        
        # Test working endpoints to ensure no regressions
        print("\n✅ Testing Previously Working Endpoints (Regression Check):")
        self.test_get_endpoint("/email-marketing/dashboard")
        self.test_get_endpoint("/email-marketing/analytics")

    def test_advanced_analytics_system(self):
        """Test Advanced Analytics System endpoints"""
        print(f"\n📊 TESTING ADVANCED ANALYTICS SYSTEM")
        print("=" * 60)
        
        # Test previously failing endpoints
        print("\n🔍 Testing Previously Failing Endpoints:")
        self.test_get_endpoint("/advanced-analytics/overview")
        self.test_get_endpoint("/advanced-analytics/business-intelligence")
        self.test_get_endpoint("/advanced-analytics/reports")
        
        # Test working endpoints to ensure no regressions
        print("\n✅ Testing Previously Working Endpoints (Regression Check):")
        self.test_get_endpoint("/advanced-analytics/dashboard")
        self.test_get_endpoint("/advanced-analytics/real-time")
        self.test_get_endpoint("/advanced-analytics/customer-analytics")
        self.test_get_endpoint("/advanced-analytics/revenue-analytics")
        self.test_get_endpoint("/advanced-analytics/conversion-funnel")

    def run_comprehensive_test(self):
        """Run comprehensive Sixth Wave testing"""
        print("🌊 SIXTH WAVE EMAIL MARKETING AND ADVANCED ANALYTICS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with testing")
            return False
        
        # Step 2: Test Email Marketing System
        self.test_email_marketing_system()
        
        # Step 3: Test Advanced Analytics System
        self.test_advanced_analytics_system()
        
        # Step 4: Generate summary
        self.generate_summary()
        
        return True
    
    def generate_summary(self):
        """Generate test summary"""
        print(f"\n🎯 SIXTH WAVE TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed Tests: {self.passed_tests}")
        print(f"Failed Tests: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Calculate performance metrics
        response_times = []
        total_data_size = 0
        
        for result in self.test_results:
            if result['success'] and 'response_time' in result:
                try:
                    time_val = float(result['response_time'].replace('s', ''))
                    response_times.append(time_val)
                except:
                    pass
            total_data_size += result.get('data_size', 0)
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"Average Response Time: {avg_response_time:.3f}s")
            print(f"Total Data Processed: {total_data_size:,} bytes")
        
        print(f"\n📊 DETAILED RESULTS:")
        print("-" * 60)
        
        # Group results by system
        email_marketing_results = []
        advanced_analytics_results = []
        auth_results = []
        
        for result in self.test_results:
            if 'email-marketing' in result['endpoint']:
                email_marketing_results.append(result)
            elif 'advanced-analytics' in result['endpoint']:
                advanced_analytics_results.append(result)
            elif 'auth' in result['endpoint']:
                auth_results.append(result)
        
        # Authentication Results
        if auth_results:
            print(f"\n🔐 AUTHENTICATION SYSTEM:")
            for result in auth_results:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {result['method']} {result['endpoint']} - {result['status']} ({result['response_time']})")
        
        # Email Marketing Results
        if email_marketing_results:
            email_passed = sum(1 for r in email_marketing_results if r['success'])
            email_total = len(email_marketing_results)
            email_rate = (email_passed / email_total * 100) if email_total > 0 else 0
            
            print(f"\n📧 EMAIL MARKETING SYSTEM ({email_passed}/{email_total} - {email_rate:.1f}%):")
            for result in email_marketing_results:
                status = "✅" if result['success'] else "❌"
                endpoint_name = result['endpoint'].split('/')[-1]
                print(f"  {status} {result['method']} /{endpoint_name} - {result['status']} ({result['response_time']})")
        
        # Advanced Analytics Results
        if advanced_analytics_results:
            analytics_passed = sum(1 for r in advanced_analytics_results if r['success'])
            analytics_total = len(advanced_analytics_results)
            analytics_rate = (analytics_passed / analytics_total * 100) if analytics_total > 0 else 0
            
            print(f"\n📊 ADVANCED ANALYTICS SYSTEM ({analytics_passed}/{analytics_total} - {analytics_rate:.1f}%):")
            for result in advanced_analytics_results:
                status = "✅" if result['success'] else "❌"
                endpoint_name = result['endpoint'].split('/')[-1]
                print(f"  {status} {result['method']} /{endpoint_name} - {result['status']} ({result['response_time']})")
        
        # Overall Assessment
        print(f"\n🎯 SIXTH WAVE MIGRATION ASSESSMENT:")
        if success_rate >= 90:
            print("✅ EXCELLENT - Sixth Wave migration highly successful")
        elif success_rate >= 75:
            print("✅ GOOD - Sixth Wave migration mostly successful")
        elif success_rate >= 50:
            print("⚠️ PARTIAL - Sixth Wave migration partially successful")
        else:
            print("❌ NEEDS WORK - Sixth Wave migration needs significant fixes")
        
        print(f"\n🚀 PRODUCTION READINESS:")
        if success_rate >= 85:
            print("✅ Ready for production deployment")
        else:
            print("⚠️ Needs fixes before production deployment")

if __name__ == "__main__":
    tester = SixthWaveTester()
    tester.run_comprehensive_test()
"""
SIXTH WAVE EMAIL MARKETING & ADVANCED ANALYTICS TEST - MEWAYZ PLATFORM
Testing newly integrated Sixth Wave systems
Testing Agent - December 2024
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

class SixthWaveTester:
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
        
        login_data = {
            "username": ADMIN_EMAIL,  # FastAPI OAuth2PasswordRequestForm uses 'username'
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

    def test_email_marketing_system(self):
        """Test Email Marketing System endpoints"""
        print(f"\n📧 TESTING EMAIL MARKETING SYSTEM")
        
        # Test GET endpoints
        self.test_endpoint("/email-marketing/dashboard", "GET", description="Email marketing dashboard with comprehensive metrics")
        self.test_endpoint("/email-marketing/campaigns", "GET", description="User's email campaigns")
        self.test_endpoint("/email-marketing/lists", "GET", description="Email lists")
        self.test_endpoint("/email-marketing/contacts", "GET", description="Email contacts")
        self.test_endpoint("/email-marketing/templates", "GET", description="Email templates")
        self.test_endpoint("/email-marketing/analytics", "GET", description="Email marketing analytics")
        
        # Test POST endpoints with realistic data
        print(f"\n📧 Testing Email Marketing POST endpoints...")
        
        # Create email campaign
        campaign_data = {
            "name": "Holiday Newsletter 2024",
            "subject": "🎄 Special Holiday Offers Just for You!",
            "content": "<html><body><h1>Holiday Greetings!</h1><p>Check out our amazing holiday deals...</p></body></html>",
            "recipient_list_id": "test-list-123",
            "campaign_type": "regular"
        }
        self.test_endpoint("/email-marketing/campaigns", "POST", data=campaign_data, description="Create email campaign")
        
        # Create email list
        list_data = {
            "name": "Holiday Subscribers 2024",
            "description": "Subscribers interested in holiday promotions",
            "tags": ["holiday", "newsletter", "promotions"]
        }
        self.test_endpoint("/email-marketing/lists", "POST", data=list_data, description="Create email list")

    def test_advanced_analytics_system(self):
        """Test Advanced Analytics System endpoints"""
        print(f"\n📊 TESTING ADVANCED ANALYTICS SYSTEM")
        
        # Test all GET endpoints
        self.test_endpoint("/advanced-analytics/dashboard", "GET", description="Comprehensive analytics dashboard")
        self.test_endpoint("/advanced-analytics/overview", "GET", description="Analytics overview")
        self.test_endpoint("/advanced-analytics/real-time", "GET", description="Real-time analytics")
        self.test_endpoint("/advanced-analytics/business-intelligence", "GET", description="Business intelligence insights")
        self.test_endpoint("/advanced-analytics/customer-analytics", "GET", description="Customer analytics")
        self.test_endpoint("/advanced-analytics/revenue-analytics", "GET", description="Revenue analytics")
        self.test_endpoint("/advanced-analytics/conversion-funnel", "GET", description="Conversion funnel analysis")
        self.test_endpoint("/advanced-analytics/reports", "GET", description="Available reports")

    def run_comprehensive_test(self):
        """Run comprehensive test of Sixth Wave systems"""
        print("=" * 80)
        print("🌊 SIXTH WAVE EMAIL MARKETING & ADVANCED ANALYTICS TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Test Email Marketing System
        self.test_email_marketing_system()
        
        # Test Advanced Analytics System  
        self.test_advanced_analytics_system()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 SIXTH WAVE TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Calculate average response time
        total_time = 0
        valid_times = 0
        total_data = 0
        
        for result in self.test_results:
            if result['success']:
                try:
                    time_val = float(result['response_time'].replace('s', ''))
                    total_time += time_val
                    valid_times += 1
                    total_data += result['data_size']
                except:
                    pass
        
        if valid_times > 0:
            avg_time = total_time / valid_times
            print(f"Average Response Time: {avg_time:.3f}s")
            print(f"Total Data Processed: {total_data:,} bytes")
        
        print("\n🌊 SIXTH WAVE SYSTEMS STATUS:")
        
        # Email Marketing System Status
        email_tests = [r for r in self.test_results if '/email-marketing/' in r['endpoint']]
        email_passed = len([r for r in email_tests if r['success']])
        email_total = len(email_tests)
        email_rate = (email_passed / email_total * 100) if email_total > 0 else 0
        
        print(f"📧 Email Marketing System: {email_passed}/{email_total} ({email_rate:.1f}%) {'✅ WORKING' if email_rate >= 80 else '⚠️ PARTIAL' if email_rate >= 50 else '❌ BROKEN'}")
        
        # Advanced Analytics System Status
        analytics_tests = [r for r in self.test_results if '/advanced-analytics/' in r['endpoint']]
        analytics_passed = len([r for r in analytics_tests if r['success']])
        analytics_total = len(analytics_tests)
        analytics_rate = (analytics_passed / analytics_total * 100) if analytics_total > 0 else 0
        
        print(f"📊 Advanced Analytics System: {analytics_passed}/{analytics_total} ({analytics_rate:.1f}%) {'✅ WORKING' if analytics_rate >= 80 else '⚠️ PARTIAL' if analytics_rate >= 50 else '❌ BROKEN'}")
        
        print(f"\n🎯 SIXTH WAVE MIGRATION STATUS:")
        if success_rate >= 90:
            print("✅ EXCELLENT - Sixth Wave migration successful with outstanding performance")
        elif success_rate >= 80:
            print("✅ GOOD - Sixth Wave migration successful with good performance")
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE - Sixth Wave migration mostly successful with minor issues")
        elif success_rate >= 50:
            print("⚠️ PARTIAL - Sixth Wave migration partially successful, needs attention")
        else:
            print("❌ CRITICAL - Sixth Wave migration has significant issues requiring immediate attention")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

if __name__ == "__main__":
    tester = SixthWaveTester()
    tester.run_comprehensive_test()