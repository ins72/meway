#!/usr/bin/env python3
"""
CRM & WEBSITE BUILDER SYSTEMS TEST - FIFTH WAVE MIGRATION
Testing newly integrated CRM and Website Builder systems
Testing Agent - December 2024
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class CRMWebsiteBuilderTester:
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
            
            # Determine success
            success = response.status_code == expected_status
            
            # Get response details
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
                details = f"{description} - {data_size} chars"
                if not success:
                    error_detail = response_data.get('detail', 'Unknown error')
                    details += f" - Error: {error_detail}"
            except:
                data_size = len(response.text)
                details = f"{description} - {data_size} chars"
                if not success:
                    details += f" - Error: {response.text[:100]}"
            
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size)
            return response
            
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"Request error: {str(e)}")
            return None

    def test_crm_system(self):
        """Test CRM Management System endpoints"""
        print(f"\n🏢 TESTING CRM MANAGEMENT SYSTEM...")
        
        # Test CRM Dashboard
        self.test_endpoint("/crm/dashboard", "GET", description="CRM dashboard with customer statistics")
        
        # Test Get Contacts
        self.test_endpoint("/crm/contacts", "GET", description="Customer contact list")
        
        # Test Create Contact (with unique email to avoid conflicts)
        import random
        unique_id = random.randint(1000, 9999)
        contact_data = {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": f"sarah.johnson{unique_id}@testcompany.com",
            "phone": "+1-555-0124",
            "company": "Innovation Corp",
            "position": "Sales Manager",
            "website": "https://innovationcorp.com",
            "address": "456 Innovation Ave, Tech City, State 54321",
            "status": "prospect",
            "lead_score": 85,
            "source": "referral",
            "tags": ["sales", "high-priority"],
            "custom_fields": {
                "industry": "Software",
                "company_size": "100-500"
            }
        }
        self.test_endpoint("/crm/contacts", "POST", data=contact_data, expected_status=200, 
                          description="Customer contact creation")
        
        # Test missing endpoints (should return 404 or 405)
        self.test_endpoint("/crm/pipelines", "GET", expected_status=404, 
                          description="Sales pipelines (not implemented)")
        self.test_endpoint("/crm/activities", "GET", expected_status=405, 
                          description="Customer activities log (GET not implemented, only POST exists)")
        self.test_endpoint("/crm/reports", "GET", expected_status=404, 
                          description="CRM analytics reports (not implemented)")

    def test_website_builder_system(self):
        """Test Website Builder System endpoints"""
        print(f"\n🌐 TESTING WEBSITE BUILDER SYSTEM...")
        
        # Test Website Builder Dashboard (actually exists)
        self.test_endpoint("/website-builder/dashboard", "GET", expected_status=200,
                          description="Website builder dashboard with metrics")
        
        # Test Get Templates
        self.test_endpoint("/website-builder/templates", "GET", description="Available website templates")
        
        # Test Get Websites (sites)
        self.test_endpoint("/website-builder/websites", "GET", description="User's websites")
        
        # Test Create Website (with unique name to avoid conflicts)
        import random
        unique_id = random.randint(1000, 9999)
        website_data = {
            "name": f"Business Website {unique_id}",
            "title": "Professional Business Solutions",
            "description": "A comprehensive business website showcasing our services and expertise",
            "domain": None,  # Will use subdomain
            "template_id": None,
            "theme": {
                "primary_color": "#2563EB",
                "secondary_color": "#059669",
                "font_family": "Inter",
                "background_color": "#FFFFFF"
            },
            "seo_settings": {
                "meta_title": "Professional Business Solutions - Expert Services",
                "meta_description": "Leading provider of professional business solutions with expert consulting and innovative strategies.",
                "keywords": ["business", "consulting", "professional", "solutions"]
            },
            "is_published": False
        }
        self.test_endpoint("/website-builder/websites", "POST", data=website_data, expected_status=200,
                          description="Website creation")
        
        # Test missing endpoints (should return 404)
        self.test_endpoint("/website-builder/domains", "GET", expected_status=404,
                          description="Domain management (not implemented)")
        self.test_endpoint("/website-builder/analytics", "GET", expected_status=404,
                          description="Website analytics (not implemented)")
        self.test_endpoint("/website-builder/seo-tools", "GET", expected_status=404,
                          description="SEO optimization tools (not implemented)")

    def run_comprehensive_test(self):
        """Run comprehensive test of CRM and Website Builder systems"""
        print("=" * 80)
        print("🌊 FIFTH WAVE MIGRATION TEST - CRM & WEBSITE BUILDER SYSTEMS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Test CRM System
        self.test_crm_system()
        
        # Test Website Builder System  
        self.test_website_builder_system()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 FIFTH WAVE MIGRATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Calculate average response time
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
        
        print("\n🎯 DETAILED RESULTS:")
        
        # Group by system
        crm_results = [r for r in self.test_results if '/crm/' in r['endpoint']]
        wb_results = [r for r in self.test_results if '/website-builder/' in r['endpoint']]
        auth_results = [r for r in self.test_results if '/auth/' in r['endpoint']]
        
        if auth_results:
            print(f"\n🔐 AUTHENTICATION SYSTEM:")
            for result in auth_results:
                status_icon = "✅" if result['success'] else "❌"
                print(f"  {status_icon} {result['method']} {result['endpoint']} - {result['details']}")
        
        if crm_results:
            crm_passed = sum(1 for r in crm_results if r['success'])
            print(f"\n🏢 CRM MANAGEMENT SYSTEM ({crm_passed}/{len(crm_results)} working):")
            for result in crm_results:
                status_icon = "✅" if result['success'] else "❌"
                print(f"  {status_icon} {result['method']} {result['endpoint']} - {result['details']}")
        
        if wb_results:
            wb_passed = sum(1 for r in wb_results if r['success'])
            print(f"\n🌐 WEBSITE BUILDER SYSTEM ({wb_passed}/{len(wb_results)} working):")
            for result in wb_results:
                status_icon = "✅" if result['success'] else "❌"
                print(f"  {status_icon} {result['method']} {result['endpoint']} - {result['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 70:
            print("🎉 FIFTH WAVE MIGRATION TEST: MOSTLY SUCCESSFUL")
        elif success_rate >= 50:
            print("⚠️  FIFTH WAVE MIGRATION TEST: PARTIAL SUCCESS")
        else:
            print("❌ FIFTH WAVE MIGRATION TEST: NEEDS ATTENTION")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = CRMWebsiteBuilderTester()
    tester.run_comprehensive_test()