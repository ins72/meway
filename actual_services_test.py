#!/usr/bin/env python3
"""
FOCUSED VERIFICATION FOR ACTUAL WORKING SERVICES - MEWAYZ V2 PLATFORM
Testing the actual available services based on the OpenAPI specification
"""

import requests
import json
import sys
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = "https://d70b9379-58ef-4e6d-9a10-f0eebb21d382.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ActualServiceTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
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
    
    def authenticate(self):
        """Authenticate and get access token"""
        try:
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_result("Authentication", True, "Login successful - Token received", data)
                    return True
                else:
                    self.log_result("Authentication", False, "Login response missing access_token")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, test_name: str = None):
        """Make authenticated API request"""
        if not test_name:
            test_name = f"{method} {endpoint}"
            
        try:
            url = f"{API_BASE}{endpoint}"
            headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
            
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
                    return True, data
                except:
                    return True, response.text
            else:
                error_msg = f"Status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', response.text)}"
                except:
                    error_msg += f": {response.text}"
                return False, error_msg
                
        except Exception as e:
            return False, f"Request error: {str(e)}"
    
    def check_for_mock_data(self, data: Any, service_name: str) -> bool:
        """Check if response contains mock/hardcoded data"""
        data_str = str(data).lower()
        mock_indicators = [
            "sample", "mock", "test", "dummy", "fake", "example",
            "lorem ipsum", "placeholder", "default", "hardcoded"
        ]
        
        for indicator in mock_indicators:
            if indicator in data_str:
                self.log_result(f"{service_name} - Mock Data Check", False, f"MOCK DATA DETECTED: Contains '{indicator}'")
                return True
        
        self.log_result(f"{service_name} - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        return False
    
    def test_email_marketing_service(self):
        """Test actual email marketing service"""
        print("\n📧 TESTING EMAIL MARKETING SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # READ - Get campaigns list
        print("\n📋 Testing Email Marketing Campaigns (READ)...")
        success, response = self.make_request("GET", "/email-marketing/campaigns", test_name="Email Marketing - Get Campaigns")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Email Marketing READ")
            self.log_result("Email Marketing - Get Campaigns", True, f"Successfully retrieved campaigns - {len(str(response))} chars")
        else:
            self.log_result("Email Marketing - Get Campaigns", False, f"Failed to get campaigns: {response}")
        
        # CREATE - Create new campaign
        print("\n📮 Testing Email Marketing Campaign Creation (CREATE)...")
        campaign_data = {
            "name": "Q1 2025 Product Launch Campaign",
            "subject": "Introducing Our Revolutionary Business Platform",
            "content": "Discover our new platform features that will transform your business operations.",
            "sender_name": "Mewayz Team",
            "sender_email": "hello@mewayz.com",
            "campaign_type": "promotional"
        }
        
        success, response = self.make_request("POST", "/email-marketing/campaigns", campaign_data, "Email Marketing - Create Campaign")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Email Marketing CREATE")
            self.log_result("Email Marketing - Create Campaign", True, f"Successfully created campaign - {len(str(response))} chars")
        else:
            self.log_result("Email Marketing - Create Campaign", False, f"Failed to create campaign: {response}")
        
        # Test other endpoints
        success, response = self.make_request("GET", "/email-marketing/contacts", test_name="Email Marketing - Get Contacts")
        if success:
            self.check_for_mock_data(response, "Email Marketing Contacts")
        
        success, response = self.make_request("GET", "/email-marketing/dashboard", test_name="Email Marketing - Dashboard")
        if success:
            self.check_for_mock_data(response, "Email Marketing Dashboard")
        
        return service_results
    
    def test_ai_automation_service(self):
        """Test AI automation service"""
        print("\n🤖 TESTING AI AUTOMATION SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # READ - Get workflows
        print("\n📋 Testing AI Workflows (READ)...")
        success, response = self.make_request("GET", "/ai-automation/workflows", test_name="AI Automation - Get Workflows")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "AI Automation READ")
            self.log_result("AI Automation - Get Workflows", True, f"Successfully retrieved workflows - {len(str(response))} chars")
        else:
            self.log_result("AI Automation - Get Workflows", False, f"Failed to get workflows: {response}")
        
        # CREATE - Create workflow
        print("\n🔧 Testing AI Workflow Creation (CREATE)...")
        workflow_data = {
            "name": "Content Generation Workflow",
            "description": "Automated content creation and social media posting",
            "triggers": [{"type": "schedule", "cron": "0 9 * * 1"}],
            "actions": [{"type": "generate_content", "template": "social_post"}]
        }
        
        success, response = self.make_request("POST", "/ai-automation/create-workflow", workflow_data, "AI Automation - Create Workflow")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "AI Automation CREATE")
            self.log_result("AI Automation - Create Workflow", True, f"Successfully created workflow - {len(str(response))} chars")
        else:
            self.log_result("AI Automation - Create Workflow", False, f"Failed to create workflow: {response}")
        
        # Test content generation
        content_data = {
            "type": "social_media_post",
            "topic": "business automation",
            "tone": "professional",
            "length": "medium"
        }
        
        success, response = self.make_request("POST", "/ai-automation/generate-content", content_data, "AI Automation - Generate Content")
        if success:
            self.check_for_mock_data(response, "AI Automation Content Generation")
        
        # Test analytics
        success, response = self.make_request("GET", "/ai-automation/analytics/overview", test_name="AI Automation - Analytics Overview")
        if success:
            self.check_for_mock_data(response, "AI Automation Analytics")
        
        return service_results
    
    def test_crm_management_service(self):
        """Test CRM management service"""
        print("\n👥 TESTING CRM MANAGEMENT SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # READ - Get contacts
        print("\n📋 Testing CRM Contacts (READ)...")
        success, response = self.make_request("GET", "/crm/contacts", test_name="CRM - Get Contacts")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "CRM READ")
            self.log_result("CRM - Get Contacts", True, f"Successfully retrieved contacts - {len(str(response))} chars")
        else:
            self.log_result("CRM - Get Contacts", False, f"Failed to get contacts: {response}")
        
        # CREATE - Create contact
        print("\n👤 Testing CRM Contact Creation (CREATE)...")
        contact_data = {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@techstartup.com",
            "phone": "+1-555-0123",
            "company": "TechStartup Inc.",
            "position": "Marketing Director",
            "source": "website",
            "notes": "Interested in our business automation platform"
        }
        
        success, response = self.make_request("POST", "/crm/contacts", contact_data, "CRM - Create Contact")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "CRM CREATE")
            self.log_result("CRM - Create Contact", True, f"Successfully created contact - {len(str(response))} chars")
        else:
            self.log_result("CRM - Create Contact", False, f"Failed to create contact: {response}")
        
        # Test dashboard
        success, response = self.make_request("GET", "/crm/dashboard", test_name="CRM - Dashboard")
        if success:
            self.check_for_mock_data(response, "CRM Dashboard")
        
        # Test deals
        success, response = self.make_request("GET", "/crm/deals", test_name="CRM - Get Deals")
        if success:
            self.check_for_mock_data(response, "CRM Deals")
        
        return service_results
    
    def test_blog_service(self):
        """Test blog service"""
        print("\n📝 TESTING BLOG SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # READ - Get posts
        print("\n📋 Testing Blog Posts (READ)...")
        success, response = self.make_request("GET", "/blog/posts", test_name="Blog - Get Posts")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Blog READ")
            self.log_result("Blog - Get Posts", True, f"Successfully retrieved posts - {len(str(response))} chars")
        else:
            self.log_result("Blog - Get Posts", False, f"Failed to get posts: {response}")
        
        # CREATE - Create post
        print("\n📄 Testing Blog Post Creation (CREATE)...")
        post_data = {
            "title": "The Future of Business Automation",
            "content": "In today's rapidly evolving business landscape, automation has become a critical factor for success...",
            "excerpt": "Discover how business automation is transforming industries and driving growth.",
            "author": "Mewayz Team",
            "category": "business",
            "tags": ["automation", "business", "technology"],
            "status": "published"
        }
        
        success, response = self.make_request("POST", "/blog/posts", post_data, "Blog - Create Post")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Blog CREATE")
            self.log_result("Blog - Create Post", True, f"Successfully created post - {len(str(response))} chars")
        else:
            self.log_result("Blog - Create Post", False, f"Failed to create post: {response}")
        
        # Test analytics
        success, response = self.make_request("GET", "/blog/analytics", test_name="Blog - Analytics")
        if success:
            self.check_for_mock_data(response, "Blog Analytics")
        
        return service_results
    
    def test_forms_service(self):
        """Test forms service"""
        print("\n📋 TESTING FORMS SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # READ - Get forms
        print("\n📋 Testing Forms (READ)...")
        success, response = self.make_request("GET", "/forms/forms", test_name="Forms - Get Forms")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Forms READ")
            self.log_result("Forms - Get Forms", True, f"Successfully retrieved forms - {len(str(response))} chars")
        else:
            self.log_result("Forms - Get Forms", False, f"Failed to get forms: {response}")
        
        # CREATE - Create form
        print("\n📝 Testing Form Creation (CREATE)...")
        form_data = {
            "title": "Contact Us Form",
            "description": "Get in touch with our team",
            "fields": [
                {"name": "name", "type": "text", "label": "Full Name", "required": True},
                {"name": "email", "type": "email", "label": "Email Address", "required": True},
                {"name": "message", "type": "textarea", "label": "Message", "required": True}
            ],
            "settings": {
                "submit_button_text": "Send Message",
                "success_message": "Thank you for your message!",
                "redirect_url": "/thank-you"
            }
        }
        
        success, response = self.make_request("POST", "/forms/create", form_data, "Forms - Create Form")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Forms CREATE")
            self.log_result("Forms - Create Form", True, f"Successfully created form - {len(str(response))} chars")
        else:
            self.log_result("Forms - Create Form", False, f"Failed to create form: {response}")
        
        # Test dashboard
        success, response = self.make_request("GET", "/forms/dashboard", test_name="Forms - Dashboard")
        if success:
            self.check_for_mock_data(response, "Forms Dashboard")
        
        return service_results
    
    def test_integrations_service(self):
        """Test integrations service"""
        print("\n🔗 TESTING INTEGRATIONS SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # READ - Get available integrations
        print("\n📋 Testing Available Integrations (READ)...")
        success, response = self.make_request("GET", "/integrations/available", test_name="Integrations - Get Available")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Integrations READ")
            self.log_result("Integrations - Get Available", True, f"Successfully retrieved integrations - {len(str(response))} chars")
        else:
            self.log_result("Integrations - Get Available", False, f"Failed to get integrations: {response}")
        
        # READ - Get connected integrations
        success, response = self.make_request("GET", "/integrations/connected", test_name="Integrations - Get Connected")
        if success:
            self.check_for_mock_data(response, "Integrations Connected")
        
        # Test logs
        success, response = self.make_request("GET", "/integrations/logs", test_name="Integrations - Get Logs")
        if success:
            self.check_for_mock_data(response, "Integrations Logs")
        
        return service_results
    
    def test_analytics_system_service(self):
        """Test analytics system service"""
        print("\n📊 TESTING ANALYTICS SYSTEM SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # READ - Get dashboard
        print("\n📋 Testing Analytics Dashboard (READ)...")
        success, response = self.make_request("GET", "/analytics-system/dashboard", test_name="Analytics - Dashboard")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Analytics READ")
            self.log_result("Analytics - Dashboard", True, f"Successfully retrieved dashboard - {len(str(response))} chars")
        else:
            self.log_result("Analytics - Dashboard", False, f"Failed to get dashboard: {response}")
        
        # READ - Get overview
        success, response = self.make_request("GET", "/analytics-system/overview", test_name="Analytics - Overview")
        if success:
            self.check_for_mock_data(response, "Analytics Overview")
        
        # CREATE - Track event
        print("\n📝 Testing Analytics Event Tracking (CREATE)...")
        event_data = {
            "event_type": "page_view",
            "event_name": "dashboard_viewed",
            "user_id": "user_12345",
            "properties": {
                "page": "/dashboard",
                "source": "direct",
                "device": "desktop"
            }
        }
        
        success, response = self.make_request("POST", "/analytics-system/track", event_data, "Analytics - Track Event")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Analytics CREATE")
            self.log_result("Analytics - Track Event", True, f"Successfully tracked event - {len(str(response))} chars")
        else:
            self.log_result("Analytics - Track Event", False, f"Failed to track event: {response}")
        
        # Test reports
        success, response = self.make_request("GET", "/analytics-system/reports", test_name="Analytics - Reports")
        if success:
            self.check_for_mock_data(response, "Analytics Reports")
        
        return service_results
    
    def test_ai_tokens_service(self):
        """Test AI tokens service"""
        print("\n🪙 TESTING AI TOKENS SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # READ - Get dashboard
        print("\n📋 Testing AI Tokens Dashboard (READ)...")
        success, response = self.make_request("GET", "/ai-tokens/dashboard", test_name="AI Tokens - Dashboard")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "AI Tokens READ")
            self.log_result("AI Tokens - Dashboard", True, f"Successfully retrieved dashboard - {len(str(response))} chars")
        else:
            self.log_result("AI Tokens - Dashboard", False, f"Failed to get dashboard: {response}")
        
        # READ - Get packages
        success, response = self.make_request("GET", "/ai-tokens/packages", test_name="AI Tokens - Packages")
        if success:
            self.check_for_mock_data(response, "AI Tokens Packages")
        
        return service_results
    
    def run_actual_services_test(self):
        """Run test for actual available services"""
        print("🎯 FOCUSED VERIFICATION FOR ACTUAL WORKING SERVICES - MEWAYZ V2 PLATFORM")
        print("=" * 80)
        print("Testing the actual available services based on the OpenAPI specification")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Stopping tests.")
            return False
        
        print(f"\n✅ Authentication successful. Token: {self.access_token[:20]}...")
        
        # Test actual available services
        all_results = {}
        
        print("\n🎯 TESTING ACTUAL AVAILABLE SERVICES")
        print("=" * 80)
        
        # Test services that actually exist
        all_results["email_marketing"] = self.test_email_marketing_service()
        all_results["ai_automation"] = self.test_ai_automation_service()
        all_results["crm_management"] = self.test_crm_management_service()
        all_results["blog"] = self.test_blog_service()
        all_results["forms"] = self.test_forms_service()
        all_results["integrations"] = self.test_integrations_service()
        all_results["analytics_system"] = self.test_analytics_system_service()
        all_results["ai_tokens"] = self.test_ai_tokens_service()
        
        # Print comprehensive summary
        self.print_actual_services_summary(all_results)
        
        return True
    
    def print_actual_services_summary(self, all_results):
        """Print summary of actual services test"""
        print("\n" + "=" * 80)
        print("🎯 ACTUAL SERVICES VERIFICATION SUMMARY - MEWAYZ V2 PLATFORM")
        print("=" * 80)
        
        total_services = len(all_results)
        successful_services = 0
        
        service_names = {
            "email_marketing": "Email Marketing Service",
            "ai_automation": "AI Automation Service",
            "crm_management": "CRM Management Service",
            "blog": "Blog Service",
            "forms": "Forms Service",
            "integrations": "Integrations Service",
            "analytics_system": "Analytics System Service",
            "ai_tokens": "AI Tokens Service"
        }
        
        print(f"📊 ACTUAL SERVICES RESULTS:")
        print("-" * 80)
        
        for service_key, results in all_results.items():
            service_name = service_names.get(service_key, service_key.title())
            operations_passed = sum(1 for success in results.values() if success)
            operations_total = len(results)
            success_rate = (operations_passed / operations_total * 100) if operations_total > 0 else 0
            
            if operations_passed > 0:
                successful_services += 1
            
            status_icon = "✅" if success_rate >= 50 else "❌"
            print(f"{status_icon} {service_name}")
            print(f"   Operations Working: {operations_passed}/{operations_total} ({success_rate:.1f}%)")
            
            # Show individual operation results
            for operation, success in results.items():
                op_icon = "✅" if success else "❌"
                print(f"   • {operation.upper()}: {op_icon}")
            print()
        
        service_success_rate = (successful_services / total_services * 100) if total_services > 0 else 0
        
        print(f"📈 OVERALL ACTUAL SERVICES RESULTS:")
        print(f"   Total Services Tested: {total_services}")
        print(f"   Services with Working Operations: {successful_services}")
        print(f"   Services Success Rate: {service_success_rate:.1f}%")
        
        # Count total test results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   Passed Tests: {passed_tests}")
        print(f"   Failed Tests: {total_tests - passed_tests}")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Production readiness assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if overall_success_rate >= 75:
            print("   🟢 GOOD - Most actual services are working properly")
            print("   ✅ Platform has functional services with real data operations")
        elif overall_success_rate >= 50:
            print("   🟡 PARTIAL - Some actual services are working")
            print("   ⚠️ Platform has basic functionality but needs improvements")
        else:
            print("   🔴 NEEDS WORK - Most services need attention")
            print("   ❌ Platform requires development work")
        
        # Data quality assessment
        mock_data_count = len([r for r in self.test_results if "Mock Data Check" in r["test"] and not r["success"]])
        real_data_count = len([r for r in self.test_results if "Mock Data Check" in r["test"] and r["success"]])
        
        if real_data_count > mock_data_count:
            print(f"\n✅ DATA QUALITY VERIFICATION: GOOD")
            print(f"   ✅ {real_data_count} services using real data")
            print(f"   ❌ {mock_data_count} services using mock/hardcoded data")
        else:
            print(f"\n⚠️ DATA QUALITY VERIFICATION: MIXED")
            print(f"   ✅ {real_data_count} services using real data")
            print(f"   ❌ {mock_data_count} services using mock/hardcoded data")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = ActualServiceTester()
    tester.run_actual_services_test()