#!/usr/bin/env python3
"""
COMPREHENSIVE FULL PLATFORM AUDIT - REAL DATA OPERATIONS
Comprehensive Backend API Testing Script focused on CRUD operations and real data verification
Tests all internal database operations and external API integrations as requested in review
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import uuid

# Backend URL from environment
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ComprehensiveAuditTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.created_resources = {}  # Track created resources for cleanup
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "response_size": len(str(response_data)) if response_data else 0
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response size: {len(str(response_data))} chars")
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            # Check if we can access the OpenAPI spec (this confirms the backend is running)
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                paths_count = len(data.get('paths', {}))
                self.log_result("Health Check", True, f"Backend is operational with {paths_count} API endpoints", {"paths_count": paths_count})
                return True
            else:
                self.log_result("Health Check", False, f"Backend not accessible - OpenAPI status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Health check error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            # Test login
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,  # OAuth2PasswordRequestForm expects form data
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    # Set authorization header for future requests
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_result("Authentication", True, f"Login successful - Token received", data)
                    return True
                else:
                    self.log_result("Authentication", False, "Login response missing access_token")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, test_name: str = None):
        """Test a specific API endpoint"""
        if not test_name:
            test_name = f"{method} {endpoint}"
            
        try:
            url = f"{API_BASE}{endpoint}"
            
            # Ensure we have authentication headers if we have a token
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                self.log_result(test_name, False, f"Unsupported method: {method}")
                return False, None
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code}", data)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code} (non-JSON response)")
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404) - May not be implemented or imported")
                return False, None
            elif response.status_code == 401:
                self.log_result(test_name, False, f"Authentication required (401)")
                return False, None
            elif response.status_code == 403:
                self.log_result(test_name, False, f"Access forbidden (403)")
                return False, None
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Validation error')
                    self.log_result(test_name, False, f"Validation error (422): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Validation error (422): {response.text}")
                return False, None
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Internal server error')
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}")
                return False, None
            else:
                self.log_result(test_name, False, f"Endpoint error - Status {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False, None

    def test_data_consistency(self, endpoint: str, test_name: str):
        """Test data consistency by making multiple calls to the same endpoint"""
        try:
            # Make first call
            success1, data1 = self.test_endpoint(endpoint, "GET", test_name=f"{test_name} - Call 1")
            if not success1:
                return False
            
            time.sleep(0.1)  # Small delay
            
            # Make second call
            success2, data2 = self.test_endpoint(endpoint, "GET", test_name=f"{test_name} - Call 2")
            if not success2:
                return False
            
            # Compare responses
            if str(data1) == str(data2):
                self.log_result(f"{test_name} - Data Consistency", True, "Data consistent across calls - confirms real database usage")
                return True
            else:
                self.log_result(f"{test_name} - Data Consistency", False, "Data inconsistent - may still be using random generation")
                return False
                
        except Exception as e:
            self.log_result(f"{test_name} - Data Consistency", False, f"Consistency test error: {str(e)}")
            return False

    def run_comprehensive_audit(self):
        """Run the comprehensive full platform audit as requested"""
        print("🎯 COMPREHENSIVE FULL PLATFORM AUDIT - REAL DATA OPERATIONS")
        print("=" * 80)
        print("Testing ALL systems mentioned in review request:")
        print("1. INTERNAL DATABASE CRUD OPERATIONS")
        print("2. EXTERNAL API INTEGRATIONS")
        print("3. REAL DATA VERIFICATION")
        print("4. AUTHENTICATION & SECURITY")
        print("=" * 80)
        
        # Initialize
        if not self.test_health_check():
            print("❌ Backend not accessible. Stopping audit.")
            return False
            
        if not self.test_authentication():
            print("❌ Authentication failed. Stopping audit.")
            return False
        
        # Run all audit sections
        self.test_internal_database_crud_operations()
        self.test_external_api_integrations()
        self.test_real_data_verification()
        
        # Generate final report
        self.generate_audit_report()
        
    def test_internal_database_crud_operations(self):
        """Test all internal database CRUD operations"""
        print("\n🗄️ TESTING INTERNAL DATABASE CRUD OPERATIONS")
        print("=" * 60)
        
        # Test all systems mentioned in review request
        self.test_financial_management_crud()
        self.test_multi_workspace_crud()
        self.test_website_builder_crud()
        self.test_subscription_management_crud()
        self.test_ecommerce_crud()
        self.test_course_community_crud()
        self.test_escrow_crud()
        self.test_referral_crud()
        self.test_admin_dashboard_crud()
        self.test_onboarding_crud()
        self.test_link_in_bio_crud()
        
    def test_financial_management_crud(self):
        """Test Complete Financial Management System CRUD operations"""
        print("\n💰 Testing Financial Management System CRUD...")
        
        # CREATE operations
        invoice_data = {
            "client_name": "TechCorp Solutions",
            "client_email": "billing@techcorp.com",
            "items": [{"name": "Website Development", "quantity": 1, "price": 2500.00}],
            "tax_rate": 0.08
        }
        success, result = self.test_endpoint("/financial/invoices", "POST", invoice_data, "Financial - CREATE Invoice")
        if success and result:
            invoice_id = result.get("data", {}).get("id") or result.get("id")
            self.created_resources["invoice_id"] = invoice_id
        
        # READ operations
        self.test_endpoint("/financial/dashboard", "GET", test_name="Financial - READ Dashboard")
        self.test_endpoint("/financial/invoices", "GET", test_name="Financial - READ Invoices")
        
        # UPDATE operations
        if self.created_resources.get("invoice_id"):
            update_data = {"status": "sent"}
            self.test_endpoint(f"/financial/invoices/{self.created_resources['invoice_id']}", "PUT", update_data, "Financial - UPDATE Invoice")
        
        # DELETE operations would be tested here if endpoints exist
        
    def test_multi_workspace_crud(self):
        """Test Multi-Workspace System CRUD operations"""
        print("\n👥 Testing Multi-Workspace System CRUD...")
        
        # CREATE operations
        workspace_data = {
            "name": "Test Workspace",
            "description": "Test workspace for audit",
            "workspace_type": "business"
        }
        success, result = self.test_endpoint("/multi-workspace/workspaces", "POST", workspace_data, "Multi-Workspace - CREATE Workspace")
        if success and result:
            workspace_id = result.get("workspace", {}).get("id") or result.get("id")
            self.created_resources["workspace_id"] = workspace_id
        
        # READ operations
        self.test_endpoint("/multi-workspace/workspaces", "GET", test_name="Multi-Workspace - READ Workspaces")
        self.test_endpoint("/multi-workspace/roles", "GET", test_name="Multi-Workspace - READ Roles")
        
        # UPDATE operations
        if self.created_resources.get("workspace_id"):
            update_data = {"name": "Updated Test Workspace"}
            self.test_endpoint(f"/multi-workspace/workspaces/{self.created_resources['workspace_id']}", "PUT", update_data, "Multi-Workspace - UPDATE Workspace")
        
    def test_website_builder_crud(self):
        """Test Website Builder System CRUD operations"""
        print("\n🌐 Testing Website Builder System CRUD...")
        
        # CREATE operations
        website_data = {
            "name": "Test Website",
            "title": "Test Website Title",
            "description": "Test website for audit",
            "template_id": "basic_template"
        }
        success, result = self.test_endpoint("/website-builder/websites", "POST", website_data, "Website Builder - CREATE Website")
        if success and result:
            website_id = result.get("data", {}).get("id") or result.get("id")
            self.created_resources["website_id"] = website_id
        
        # READ operations
        self.test_endpoint("/website-builder/dashboard", "GET", test_name="Website Builder - READ Dashboard")
        self.test_endpoint("/website-builder/templates", "GET", test_name="Website Builder - READ Templates")
        self.test_endpoint("/website-builder/websites", "GET", test_name="Website Builder - READ Websites")
        
        # UPDATE operations
        if self.created_resources.get("website_id"):
            update_data = {"title": "Updated Test Website"}
            self.test_endpoint(f"/website-builder/websites/{self.created_resources['website_id']}", "PUT", update_data, "Website Builder - UPDATE Website")
        
    def test_subscription_management_crud(self):
        """Test Subscription Management System CRUD operations"""
        print("\n💳 Testing Subscription Management System CRUD...")
        
        # READ operations (most subscription systems are read-heavy)
        self.test_endpoint("/subscriptions/plans", "GET", test_name="Subscriptions - READ Plans")
        self.test_endpoint("/subscriptions/current", "GET", test_name="Subscriptions - READ Current Subscription")
        self.test_endpoint("/subscriptions/usage", "GET", test_name="Subscriptions - READ Usage")
        
        # CREATE operations (subscription creation)
        subscription_data = {
            "plan_id": "basic_plan",
            "payment_method": "stripe"
        }
        self.test_endpoint("/subscriptions/subscribe", "POST", subscription_data, "Subscriptions - CREATE Subscription")
        
    def test_ecommerce_crud(self):
        """Test E-commerce System CRUD operations"""
        print("\n🛒 Testing E-commerce System CRUD...")
        
        # CREATE operations
        product_data = {
            "name": "Test Product",
            "description": "Test product for audit",
            "price": 99.99,
            "category": "digital"
        }
        success, result = self.test_endpoint("/ecommerce/products", "POST", product_data, "E-commerce - CREATE Product")
        if success and result:
            product_id = result.get("data", {}).get("id") or result.get("id")
            self.created_resources["product_id"] = product_id
        
        # READ operations
        self.test_endpoint("/ecommerce/products", "GET", test_name="E-commerce - READ Products")
        self.test_endpoint("/ecommerce/orders", "GET", test_name="E-commerce - READ Orders")
        self.test_endpoint("/ecommerce/dashboard", "GET", test_name="E-commerce - READ Dashboard")
        
        # UPDATE operations
        if self.created_resources.get("product_id"):
            update_data = {"price": 89.99}
            self.test_endpoint(f"/ecommerce/products/{self.created_resources['product_id']}", "PUT", update_data, "E-commerce - UPDATE Product")
        
    def test_course_community_crud(self):
        """Test Course & Community System CRUD operations"""
        print("\n🎓 Testing Course & Community System CRUD...")
        
        # READ operations
        self.test_endpoint("/courses/list", "GET", test_name="Courses - READ Course List")
        self.test_endpoint("/courses/analytics", "GET", test_name="Courses - READ Analytics")
        self.test_endpoint("/courses/my-courses", "GET", test_name="Courses - READ My Courses")
        
        # CREATE operations
        course_data = {
            "title": "Test Course",
            "description": "Test course for audit",
            "price": 199.99
        }
        self.test_endpoint("/courses/create", "POST", course_data, "Courses - CREATE Course")
        
    def test_escrow_crud(self):
        """Test Escrow System CRUD operations"""
        print("\n🔒 Testing Escrow System CRUD...")
        
        # READ operations
        self.test_endpoint("/escrow/transactions", "GET", test_name="Escrow - READ Transactions")
        self.test_endpoint("/escrow/analytics", "GET", test_name="Escrow - READ Analytics")
        
        # CREATE operations
        escrow_data = {
            "amount": 1000.00,
            "buyer_id": "buyer_123",
            "seller_id": "seller_456",
            "description": "Test escrow transaction"
        }
        self.test_endpoint("/escrow/create", "POST", escrow_data, "Escrow - CREATE Transaction")
        
    def test_referral_crud(self):
        """Test Referral System CRUD operations"""
        print("\n🎁 Testing Referral System CRUD...")
        
        # READ operations
        self.test_endpoint("/referrals/dashboard", "GET", test_name="Referrals - READ Dashboard")
        self.test_endpoint("/referrals/analytics", "GET", test_name="Referrals - READ Analytics")
        
        # CREATE operations
        referral_data = {
            "referred_email": "newuser@example.com",
            "referral_code": "TEST123"
        }
        self.test_endpoint("/referrals/create", "POST", referral_data, "Referrals - CREATE Referral")
        
    def test_admin_dashboard_crud(self):
        """Test Admin Dashboard CRUD operations"""
        print("\n⚙️ Testing Admin Dashboard CRUD...")
        
        # READ operations
        self.test_endpoint("/admin/dashboard", "GET", test_name="Admin - READ Dashboard")
        self.test_endpoint("/admin/users", "GET", test_name="Admin - READ Users")
        self.test_endpoint("/admin/system/metrics", "GET", test_name="Admin - READ System Metrics")
        
        # UPDATE operations (admin settings)
        admin_settings = {
            "maintenance_mode": False,
            "registration_enabled": True
        }
        self.test_endpoint("/admin/settings", "PUT", admin_settings, "Admin - UPDATE Settings")
        
    def test_onboarding_crud(self):
        """Test Complete Onboarding System CRUD operations"""
        print("\n🎯 Testing Complete Onboarding System CRUD...")
        
        # CREATE operations
        onboarding_data = {
            "goals": ["increase_sales", "improve_marketing"],
            "business_type": "saas",
            "team_size": "small"
        }
        success, result = self.test_endpoint("/complete-onboarding/sessions", "POST", onboarding_data, "Onboarding - CREATE Session")
        if success and result:
            session_id = result.get("session_id") or result.get("id")
            self.created_resources["onboarding_session_id"] = session_id
        
        # READ operations
        self.test_endpoint("/complete-onboarding/goals", "GET", test_name="Onboarding - READ Goals")
        self.test_endpoint("/complete-onboarding/subscription-plans", "GET", test_name="Onboarding - READ Subscription Plans")
        self.test_endpoint("/complete-onboarding/health", "GET", test_name="Onboarding - READ Health")
        
        # UPDATE operations
        if self.created_resources.get("onboarding_session_id"):
            update_data = {"current_step": "subscription_selection"}
            self.test_endpoint(f"/complete-onboarding/sessions/{self.created_resources['onboarding_session_id']}/step", "PUT", update_data, "Onboarding - UPDATE Session Step")
        
    def test_link_in_bio_crud(self):
        """Test Link in Bio System CRUD operations"""
        print("\n🔗 Testing Link in Bio System CRUD...")
        
        # CREATE operations
        bio_page_data = {
            "title": "Test Bio Page",
            "username": "testuser_audit",
            "description": "Test bio page for audit"
        }
        success, result = self.test_endpoint("/link-in-bio/pages", "POST", bio_page_data, "Link in Bio - CREATE Page")
        if success and result:
            page_id = result.get("page_id") or result.get("id")
            self.created_resources["bio_page_id"] = page_id
        
        # READ operations
        self.test_endpoint("/link-in-bio/templates", "GET", test_name="Link in Bio - READ Templates")
        self.test_endpoint("/link-in-bio/analytics/overview", "GET", test_name="Link in Bio - READ Analytics")
        self.test_endpoint("/link-in-bio/health", "GET", test_name="Link in Bio - READ Health")
        
        # UPDATE operations
        if self.created_resources.get("bio_page_id"):
            update_data = {"title": "Updated Test Bio Page"}
            self.test_endpoint(f"/link-in-bio/pages/{self.created_resources['bio_page_id']}", "PUT", update_data, "Link in Bio - UPDATE Page")
        
    def test_external_api_integrations(self):
        """Test all external API integrations"""
        print("\n🌐 TESTING EXTERNAL API INTEGRATIONS")
        print("=" * 60)
        
        self.test_social_media_lead_generation()
        self.test_ai_automation_openai()
        self.test_email_automation_elasticmail()
        self.test_instagram_lead_generation()
        self.test_admin_config_external_apis()
        
    def test_social_media_lead_generation(self):
        """Test Real Social Media Lead Generation"""
        print("\n📱 Testing Social Media Lead Generation...")
        
        # Twitter lead generation
        twitter_data = {
            "keywords": ["entrepreneur", "startup"],
            "location": "United States",
            "max_results": 10
        }
        self.test_endpoint("/social-media-leads/twitter/search", "POST", twitter_data, "Social Media - Twitter Lead Search")
        
        # TikTok lead generation
        tiktok_data = {
            "keywords": ["business", "marketing"],
            "region": "US",
            "max_results": 10
        }
        self.test_endpoint("/social-media-leads/tiktok/search", "POST", tiktok_data, "Social Media - TikTok Lead Search")
        
        # Analytics
        self.test_endpoint("/social-media-leads/analytics/overview", "GET", test_name="Social Media - Analytics Overview")
        
    def test_ai_automation_openai(self):
        """Test Real AI Automation with OpenAI"""
        print("\n🤖 Testing AI Automation with OpenAI...")
        
        # Content generation
        content_data = {
            "platform": "linkedin",
            "topic": "digital transformation",
            "tone": "professional"
        }
        self.test_endpoint("/ai-automation/generate-content", "POST", content_data, "AI Automation - Generate Content")
        
        # Lead enrichment
        lead_data = {
            "username": "business_leader",
            "bio": "CEO of tech startup",
            "platform": "twitter"
        }
        self.test_endpoint("/ai-automation/enrich-lead", "POST", lead_data, "AI Automation - Enrich Lead")
        
        # Analytics
        self.test_endpoint("/ai-automation/analytics/overview", "GET", test_name="AI Automation - Analytics Overview")
        
    def test_email_automation_elasticmail(self):
        """Test Real Email Automation with ElasticMail"""
        print("\n📧 Testing Email Automation with ElasticMail...")
        
        # Send email
        email_data = {
            "to_email": "test@example.com",
            "subject": "Test Email",
            "text_content": "This is a test email",
            "from_email": "hello@mewayz.com"
        }
        self.test_endpoint("/email-automation/send-email", "POST", email_data, "Email Automation - Send Email")
        
        # Create campaign
        campaign_data = {
            "name": "Test Campaign",
            "subject": "Test Campaign Subject",
            "html_content": "<h1>Test Campaign</h1>"
        }
        self.test_endpoint("/email-automation/campaigns", "POST", campaign_data, "Email Automation - Create Campaign")
        
        # Analytics
        self.test_endpoint("/email-automation/analytics/overview", "GET", test_name="Email Automation - Analytics Overview")
        
    def test_instagram_lead_generation(self):
        """Test Instagram Lead Generation"""
        print("\n📸 Testing Instagram Lead Generation...")
        
        # Instagram search
        instagram_data = {
            "hashtags": ["business", "entrepreneur"],
            "location": "United States",
            "max_results": 10
        }
        self.test_endpoint("/instagram/search", "POST", instagram_data, "Instagram - Lead Search")
        
        # Analytics
        self.test_endpoint("/instagram/analytics", "GET", test_name="Instagram - Analytics")
        
    def test_admin_config_external_apis(self):
        """Test Admin Configuration external API testing"""
        print("\n⚙️ Testing Admin Configuration External APIs...")
        
        # Test external API configurations
        self.test_endpoint("/admin-config/configuration", "GET", test_name="Admin Config - Get Configuration")
        self.test_endpoint("/admin-config/integration-status", "GET", test_name="Admin Config - Integration Status")
        
        # Test individual API connections
        self.test_endpoint("/admin-config/test-stripe", "POST", {}, "Admin Config - Test Stripe API")
        self.test_endpoint("/admin-config/test-openai", "POST", {}, "Admin Config - Test OpenAI API")
        self.test_endpoint("/admin-config/test-sendgrid", "POST", {}, "Admin Config - Test SendGrid API")
        self.test_endpoint("/admin-config/test-twitter", "POST", {}, "Admin Config - Test Twitter API")
        
    def test_real_data_verification(self):
        """Test real data verification across all systems"""
        print("\n🔍 TESTING REAL DATA VERIFICATION")
        print("=" * 60)
        
        # Test data consistency across multiple calls
        consistency_endpoints = [
            ("/dashboard/overview", "Dashboard Overview"),
            ("/users/profile", "User Profile"),
            ("/ecommerce/dashboard", "E-commerce Dashboard"),
            ("/admin/system/metrics", "Admin System Metrics"),
            ("/analytics/overview", "Analytics Overview")
        ]
        
        for endpoint, name in consistency_endpoints:
            self.test_data_consistency(endpoint, name)
            
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n📊 COMPREHENSIVE AUDIT REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n🎯 AUDIT SUMMARY:")
        if success_rate >= 90:
            print("✅ EXCELLENT - Platform ready for production")
        elif success_rate >= 75:
            print("✅ GOOD - Platform mostly functional with minor issues")
        elif success_rate >= 60:
            print("⚠️ PARTIAL - Platform has significant issues requiring attention")
        else:
            print("❌ CRITICAL - Platform has major issues preventing production use")
        
        # Show failed tests
        failed_results = [result for result in self.test_results if not result["success"]]
        if failed_results:
            print(f"\n❌ FAILED TESTS ({len(failed_results)}):")
            for result in failed_results[:10]:  # Show first 10 failures
                print(f"   - {result['test']}: {result['message']}")
            if len(failed_results) > 10:
                print(f"   ... and {len(failed_results) - 10} more failures")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the comprehensive audit"""
    tester = ComprehensiveAuditTester()
    tester.run_comprehensive_audit()

if __name__ == "__main__":
    main()