#!/usr/bin/env python3
"""
COMPREHENSIVE NINTH WAVE TESTING - MEWAYZ PLATFORM
Testing Social Email Integration, Advanced Financial Analytics, and Enhanced E-commerce APIs
Testing Agent - December 2024
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

class NinthWaveTester:
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
                self.auth_token = auth_result.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("/auth/login", "POST", response.status_code, response_time, True, 
                            f"Authentication successful - Token: {self.auth_token[:20]}...")
                return True
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("/auth/login", "POST", 0, 0, False, f"Authentication error: {str(e)}")
            return False

    def test_social_email_integration(self):
        """Test Social Email Integration APIs"""
        print(f"\n🌊 TESTING SOCIAL EMAIL INTEGRATION SYSTEM...")
        
        endpoints = [
            ("/social-email/dashboard", "GET", "Social email dashboard"),
            ("/social-email/platforms/available", "GET", "Available social platforms"),
            ("/social-email/platforms/connected", "GET", "Connected platforms"),
            ("/social-email/posts", "GET", "Social media posts"),
            ("/social-email/email/campaigns", "GET", "Email campaigns"),
            ("/social-email/email/contacts", "GET", "Email contacts"),
            ("/social-email/automation/rules", "GET", "Automation rules"),
            ("/social-email/analytics/social", "GET", "Social analytics"),
            ("/social-email/analytics/email", "GET", "Email analytics"),
            ("/social-email/content/suggestions", "GET", "Content suggestions")
        ]
        
        for endpoint, method, description in endpoints:
            self.test_endpoint(endpoint, method, description)

    def test_advanced_financial_analytics(self):
        """Test Advanced Financial Analytics APIs"""
        print(f"\n💰 TESTING ADVANCED FINANCIAL ANALYTICS SYSTEM...")
        
        endpoints = [
            ("/advanced-financial/dashboard", "GET", "Advanced financial dashboard"),
            ("/advanced-financial/comprehensive-analysis", "GET", "Comprehensive financial analysis"),
            ("/advanced-financial/invoicing/advanced", "GET", "Advanced invoicing dashboard"),
            ("/advanced-financial/cash-flow/advanced", "GET", "Advanced cash flow analysis"),
            ("/advanced-financial/profitability-analysis", "GET", "Profitability analysis"),
            ("/advanced-financial/financial-forecasting", "GET", "Financial forecasting"),
            ("/advanced-financial/budget-analysis", "GET", "Budget analysis"),
            ("/advanced-financial/financial-kpis", "GET", "Financial KPIs"),
            ("/advanced-financial/investor-metrics", "GET", "Investor metrics")
        ]
        
        for endpoint, method, description in endpoints:
            self.test_endpoint(endpoint, method, description)

    def test_enhanced_ecommerce(self):
        """Test Enhanced E-commerce APIs"""
        print(f"\n🛒 TESTING ENHANCED E-COMMERCE SYSTEM...")
        
        endpoints = [
            ("/enhanced-ecommerce/inventory/overview", "GET", "Inventory management overview"),
            ("/enhanced-ecommerce/inventory/products", "GET", "Inventory products"),
            ("/enhanced-ecommerce/inventory/analytics", "GET", "Inventory analytics"),
            ("/enhanced-ecommerce/inventory/forecasting", "GET", "Demand forecasting"),
            ("/enhanced-ecommerce/dropshipping/suppliers", "GET", "Dropshipping suppliers"),
            ("/enhanced-ecommerce/dropshipping/connections", "GET", "Dropshipping connections"),
            ("/enhanced-ecommerce/dropshipping/products", "GET", "Dropshipping products"),
            ("/enhanced-ecommerce/marketplace/dashboard", "GET", "Marketplace dashboard"),
            ("/enhanced-ecommerce/payment/advanced-options", "GET", "Advanced payment options"),
            ("/enhanced-ecommerce/subscription/management", "GET", "Subscription management"),
            ("/enhanced-ecommerce/analytics/comprehensive", "GET", "Comprehensive e-commerce analytics")
        ]
        
        for endpoint, method, description in endpoints:
            self.test_endpoint(endpoint, method, description)

    def test_post_endpoints(self):
        """Test POST endpoints for data creation"""
        print(f"\n📝 TESTING POST ENDPOINTS FOR DATA CREATION...")
        
        # Test Social Email POST endpoints
        self.test_social_post_creation()
        self.test_email_campaign_creation()
        self.test_email_contact_creation()
        
        # Test Enhanced E-commerce POST endpoints
        self.test_inventory_product_creation()
        self.test_dropshipping_connection()

    def test_social_post_creation(self):
        """Test social media post creation"""
        endpoint = "/social-email/posts"
        url = f"{API_BASE}{endpoint}"
        
        post_data = {
            "platform": "twitter",
            "content": "Testing our new social media integration! 🚀 #innovation #business",
            "media_urls": [],
            "tags": ["innovation", "business", "testing"]
        }
        
        try:
            start_time = time.time()
            response = self.session.post(url, json=post_data)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 201]
            data_size = len(response.text) if response.text else 0
            
            details = f"Social post creation - {data_size} chars"
            if not success and response.text:
                details += f" - {response.text[:100]}"
                
            self.log_test(endpoint, "POST", response.status_code, response_time, success, details, data_size)
            
        except Exception as e:
            self.log_test(endpoint, "POST", 0, 0, False, f"Error: {str(e)}")

    def test_email_campaign_creation(self):
        """Test email campaign creation"""
        endpoint = "/social-email/email/campaigns"
        url = f"{API_BASE}{endpoint}"
        
        campaign_data = {
            "name": "Test Newsletter Campaign",
            "subject": "Welcome to our platform!",
            "content": "Thank you for joining us. Here's what you can expect...",
            "recipients": ["test@example.com", "demo@example.com"],
            "sender_name": "Mewayz Team"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(url, json=campaign_data)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 201]
            data_size = len(response.text) if response.text else 0
            
            details = f"Email campaign creation - {data_size} chars"
            if not success and response.text:
                details += f" - {response.text[:100]}"
                
            self.log_test(endpoint, "POST", response.status_code, response_time, success, details, data_size)
            
        except Exception as e:
            self.log_test(endpoint, "POST", 0, 0, False, f"Error: {str(e)}")

    def test_email_contact_creation(self):
        """Test email contact creation"""
        endpoint = "/social-email/email/contacts"
        url = f"{API_BASE}{endpoint}"
        
        contact_data = {
            "email": "newcontact@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "tags": ["prospect", "newsletter"],
            "custom_fields": {"company": "Test Corp", "role": "Manager"}
        }
        
        try:
            start_time = time.time()
            response = self.session.post(url, json=contact_data)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 201]
            data_size = len(response.text) if response.text else 0
            
            details = f"Email contact creation - {data_size} chars"
            if not success and response.text:
                details += f" - {response.text[:100]}"
                
            self.log_test(endpoint, "POST", response.status_code, response_time, success, details, data_size)
            
        except Exception as e:
            self.log_test(endpoint, "POST", 0, 0, False, f"Error: {str(e)}")

    def test_inventory_product_creation(self):
        """Test inventory product creation"""
        endpoint = "/enhanced-ecommerce/inventory/products/create"
        url = f"{API_BASE}{endpoint}"
        
        product_data = {
            "name": "Test Product",
            "sku": "TEST-001",
            "category": "Electronics",
            "cost_price": 50.00,
            "selling_price": 99.99,
            "initial_stock": 100,
            "reorder_point": 20,
            "supplier_info": json.dumps({"supplier": "Test Supplier", "contact": "supplier@test.com"})
        }
        
        try:
            start_time = time.time()
            response = self.session.post(url, data=product_data)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 201]
            data_size = len(response.text) if response.text else 0
            
            details = f"Inventory product creation - {data_size} chars"
            if not success and response.text:
                details += f" - {response.text[:100]}"
                
            self.log_test(endpoint, "POST", response.status_code, response_time, success, details, data_size)
            
        except Exception as e:
            self.log_test(endpoint, "POST", 0, 0, False, f"Error: {str(e)}")

    def test_dropshipping_connection(self):
        """Test dropshipping supplier connection"""
        endpoint = "/enhanced-ecommerce/dropshipping/connect"
        url = f"{API_BASE}{endpoint}"
        
        connection_data = {
            "supplier_id": "supplier_001",
            "api_credentials": json.dumps({"api_key": "test_key", "secret": "test_secret"}),
            "settings": json.dumps({"auto_sync": True, "markup_percentage": 50})
        }
        
        try:
            start_time = time.time()
            response = self.session.post(url, data=connection_data)
            response_time = time.time() - start_time
            
            success = response.status_code in [200, 201]
            data_size = len(response.text) if response.text else 0
            
            details = f"Dropshipping connection - {data_size} chars"
            if not success and response.text:
                details += f" - {response.text[:100]}"
                
            self.log_test(endpoint, "POST", response.status_code, response_time, success, details, data_size)
            
        except Exception as e:
            self.log_test(endpoint, "POST", 0, 0, False, f"Error: {str(e)}")

    def test_endpoint(self, endpoint, method, description):
        """Test a single endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url)
            else:
                response = self.session.request(method, url)
                
            response_time = time.time() - start_time
            
            # Consider 200, 201 as success
            success = response.status_code in [200, 201]
            data_size = len(response.text) if response.text else 0
            
            details = f"{description} - {data_size} chars"
            if not success and response.text:
                details += f" - {response.text[:100]}"
                
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size)
            
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"Error: {str(e)}")

    def print_summary(self):
        """Print comprehensive test summary"""
        print(f"\n" + "="*80)
        print(f"🌊 COMPREHENSIVE NINTH WAVE TESTING COMPLETED")
        print(f"="*80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Tests Passed: {self.passed_tests}/{self.total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Calculate total data processed
        total_data = sum(result['data_size'] for result in self.test_results if result['success'])
        print(f"📦 Total Data Processed: {total_data:,} bytes")
        
        # Calculate average response time
        successful_tests = [r for r in self.test_results if r['success']]
        if successful_tests:
            avg_time = sum(float(r['response_time'].replace('s', '')) for r in successful_tests) / len(successful_tests)
            print(f"⚡ Average Response Time: {avg_time:.3f}s")
        
        print(f"\n🌊 NINTH WAVE SYSTEMS TESTED:")
        
        # Social Email Integration results
        social_tests = [r for r in self.test_results if '/social-email/' in r['endpoint']]
        social_passed = len([r for r in social_tests if r['success']])
        print(f"📧 Social Email Integration: {social_passed}/{len(social_tests)} endpoints working")
        
        # Advanced Financial Analytics results  
        financial_tests = [r for r in self.test_results if '/advanced-financial/' in r['endpoint']]
        financial_passed = len([r for r in financial_tests if r['success']])
        print(f"💰 Advanced Financial Analytics: {financial_passed}/{len(financial_tests)} endpoints working")
        
        # Enhanced E-commerce results
        ecommerce_tests = [r for r in self.test_results if '/enhanced-ecommerce/' in r['endpoint']]
        ecommerce_passed = len([r for r in ecommerce_tests if r['success']])
        print(f"🛒 Enhanced E-commerce: {ecommerce_passed}/{len(ecommerce_tests)} endpoints working")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['method']} {result['endpoint']} - {result['status']} ({result['response_time']}) - {result['details']}")
        
        print(f"\n" + "="*80)
        
        if success_rate >= 90:
            print(f"🎉 EXCELLENT: Ninth Wave integration is working perfectly!")
        elif success_rate >= 75:
            print(f"✅ GOOD: Ninth Wave integration is mostly working with minor issues.")
        elif success_rate >= 50:
            print(f"⚠️  PARTIAL: Ninth Wave integration has significant issues that need attention.")
        else:
            print(f"❌ CRITICAL: Ninth Wave integration has major problems requiring immediate fixes.")

def main():
    """Main test execution"""
    print(f"🌊 COMPREHENSIVE NINTH WAVE TESTING - MEWAYZ PLATFORM")
    print(f"Testing Social Email Integration, Advanced Financial Analytics, and Enhanced E-commerce")
    print(f"Testing Agent - {datetime.now().strftime('%B %d, %Y')}")
    print(f"Backend URL: {BACKEND_URL}")
    
    tester = NinthWaveTester()
    
    # Authenticate first
    if not tester.authenticate():
        print("❌ Authentication failed. Cannot proceed with testing.")
        return
    
    # Test all Ninth Wave systems
    tester.test_social_email_integration()
    tester.test_advanced_financial_analytics()
    tester.test_enhanced_ecommerce()
    tester.test_post_endpoints()
    
    # Print comprehensive summary
    tester.print_summary()

if __name__ == "__main__":
    main()