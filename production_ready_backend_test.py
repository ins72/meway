#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - PRODUCTION READINESS BACKEND TESTING - JANUARY 2025
COMPREHENSIVE TESTING FOR REVIEW REQUEST VALIDATION

TESTING OBJECTIVES:
1. Complete CRUD Operations Assessment
2. Real Data Persistence Verification  
3. Critical Business Services Testing
4. External API Integration Testing
5. Production Deployment Readiness

CREDENTIALS: tmonnens@outlook.com/Voetballen5 (super_admin with full permissions)
BACKEND URL: https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional, List, Tuple
import uuid
from datetime import datetime, timedelta
import traceback

# Backend URL from environment
BACKEND_URL = "https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ProductionReadinessTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.working_endpoints = []
        self.failing_endpoints = []
        self.crud_results = {
            'CREATE': {'working': [], 'failing': []},
            'READ': {'working': [], 'failing': []},
            'UPDATE': {'working': [], 'failing': []},
            'DELETE': {'working': [], 'failing': []}
        }
        self.real_data_confirmed = []
        self.mock_data_detected = []
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None, status_code: int = None):
        """Log test result with comprehensive information"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "status_code": status_code,
            "response_size": len(str(response_data)) if response_data else 0,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response size: {len(str(response_data))} chars")
        if status_code:
            print(f"   Status code: {status_code}")
    
    def authenticate(self) -> bool:
        """Authenticate with the backend and get access token"""
        try:
            print("🔐 AUTHENTICATING WITH BACKEND...")
            
            # First check if backend is accessible
            health_response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if health_response.status_code == 200:
                self.log_result("Health Check", True, f"Backend operational with {health_response.text}", 
                              health_response.json() if health_response.headers.get('content-type', '').startswith('application/json') else health_response.text, 
                              health_response.status_code)
            else:
                self.log_result("Health Check", False, f"Backend not accessible - Status {health_response.status_code}", 
                              None, health_response.status_code)
                return False
            
            # Try to authenticate
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            auth_response = self.session.post(f"{API_BASE}/auth/login", json=auth_data, timeout=10)
            
            if auth_response.status_code == 200:
                auth_result = auth_response.json()
                if 'access_token' in auth_result:
                    self.access_token = auth_result['access_token']
                    self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                    self.log_result("Authentication", True, f"Login successful - JWT token obtained", 
                                  auth_result, auth_response.status_code)
                    return True
                else:
                    self.log_result("Authentication", False, "Login response missing access_token", 
                                  auth_result, auth_response.status_code)
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed - Status {auth_response.status_code}", 
                              auth_response.text, auth_response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Tuple[bool, Any, int]:
        """Test a single endpoint"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=10)
            else:
                return False, None, 0
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return success, response_data, response.status_code
            
        except Exception as e:
            return False, f"Error: {str(e)}", 0
    
    def test_crud_operations(self):
        """Test CRUD operations across critical business services"""
        print("\n🎯 TESTING CRUD OPERATIONS")
        print("=" * 80)
        
        # Test Financial Management CRUD
        print("\n📊 TESTING FINANCIAL MANAGEMENT CRUD")
        
        # CREATE - Invoice
        invoice_data = {
            "client_name": "Test Client",
            "amount": 1500.00,
            "description": "Test Invoice for CRUD Testing",
            "due_date": "2025-02-15"
        }
        success, response, status = self.test_endpoint('POST', '/financial/invoices', invoice_data, 201)
        if success:
            self.crud_results['CREATE']['working'].append('Financial Invoice Creation')
            self.log_result("Financial Invoice - CREATE", True, f"Invoice created successfully", response, status)
            invoice_id = response.get('id') if isinstance(response, dict) else None
        else:
            self.crud_results['CREATE']['failing'].append('Financial Invoice Creation')
            self.log_result("Financial Invoice - CREATE", False, f"Invoice creation failed", response, status)
            invoice_id = None
        
        # READ - Invoices List
        success, response, status = self.test_endpoint('GET', '/financial/invoices')
        if success:
            self.crud_results['READ']['working'].append('Financial Invoices List')
            self.log_result("Financial Invoices - READ", True, f"Invoices retrieved successfully", response, status)
        else:
            self.crud_results['READ']['failing'].append('Financial Invoices List')
            self.log_result("Financial Invoices - READ", False, f"Invoices retrieval failed", response, status)
        
        # UPDATE - Invoice (if we have an ID)
        if invoice_id:
            update_data = {"status": "paid"}
            success, response, status = self.test_endpoint('PUT', f'/financial/invoices/{invoice_id}', update_data)
            if success:
                self.crud_results['UPDATE']['working'].append('Financial Invoice Update')
                self.log_result("Financial Invoice - UPDATE", True, f"Invoice updated successfully", response, status)
            else:
                self.crud_results['UPDATE']['failing'].append('Financial Invoice Update')
                self.log_result("Financial Invoice - UPDATE", False, f"Invoice update failed", response, status)
        
        # Test Workspace Management CRUD
        print("\n🏢 TESTING WORKSPACE MANAGEMENT CRUD")
        
        # CREATE - Workspace
        workspace_data = {
            "name": "Test Workspace",
            "description": "Test workspace for CRUD testing",
            "plan": "professional"
        }
        success, response, status = self.test_endpoint('POST', '/workspace', workspace_data, 201)
        if success:
            self.crud_results['CREATE']['working'].append('Workspace Creation')
            self.log_result("Workspace - CREATE", True, f"Workspace created successfully", response, status)
            workspace_id = response.get('id') if isinstance(response, dict) else None
        else:
            self.crud_results['CREATE']['failing'].append('Workspace Creation')
            self.log_result("Workspace - CREATE", False, f"Workspace creation failed", response, status)
            workspace_id = None
        
        # READ - Workspaces List
        success, response, status = self.test_endpoint('GET', '/workspace')
        if success:
            self.crud_results['READ']['working'].append('Workspaces List')
            self.log_result("Workspaces - READ", True, f"Workspaces retrieved successfully", response, status)
        else:
            self.crud_results['READ']['failing'].append('Workspaces List')
            self.log_result("Workspaces - READ", False, f"Workspaces retrieval failed", response, status)
        
        # Test AI Content CRUD
        print("\n🤖 TESTING AI CONTENT CRUD")
        
        # CREATE - AI Content
        ai_content_data = {
            "prompt": "Generate a blog post about sustainable technology",
            "type": "blog_post",
            "tone": "professional"
        }
        success, response, status = self.test_endpoint('POST', '/ai-content/generate', ai_content_data, 201)
        if success:
            self.crud_results['CREATE']['working'].append('AI Content Generation')
            self.log_result("AI Content - CREATE", True, f"AI content generated successfully", response, status)
        else:
            self.crud_results['CREATE']['failing'].append('AI Content Generation')
            self.log_result("AI Content - CREATE", False, f"AI content generation failed", response, status)
        
        # READ - AI Content History
        success, response, status = self.test_endpoint('GET', '/ai-content/history')
        if success:
            self.crud_results['READ']['working'].append('AI Content History')
            self.log_result("AI Content - READ", True, f"AI content history retrieved successfully", response, status)
        else:
            self.crud_results['READ']['failing'].append('AI Content History')
            self.log_result("AI Content - READ", False, f"AI content history retrieval failed", response, status)
    
    def test_real_data_persistence(self):
        """Test real data persistence verification"""
        print("\n🗄️ TESTING REAL DATA PERSISTENCE")
        print("=" * 80)
        
        # Test multiple calls to same endpoint to verify data consistency
        endpoints_to_test = [
            '/dashboard/overview',
            '/user/profile',
            '/financial/dashboard',
            '/analytics/overview'
        ]
        
        for endpoint in endpoints_to_test:
            print(f"\n🔍 Testing data consistency for {endpoint}")
            
            # Make multiple calls
            responses = []
            for i in range(3):
                success, response, status = self.test_endpoint('GET', endpoint)
                if success:
                    responses.append(response)
                time.sleep(0.5)  # Small delay between calls
            
            if len(responses) >= 2:
                # Check if responses are consistent (indicating real data)
                if responses[0] == responses[1]:
                    self.real_data_confirmed.append(endpoint)
                    self.log_result(f"Data Consistency - {endpoint}", True, 
                                  f"Data consistent across calls - confirms real database usage", responses[0])
                else:
                    self.mock_data_detected.append(endpoint)
                    self.log_result(f"Data Consistency - {endpoint}", False, 
                                  f"Data inconsistent - may still be using random generation")
            else:
                self.log_result(f"Data Consistency - {endpoint}", False, 
                              f"Endpoint not accessible for consistency testing")
    
    def test_critical_business_services(self):
        """Test critical business services"""
        print("\n🏢 TESTING CRITICAL BUSINESS SERVICES")
        print("=" * 80)
        
        critical_services = [
            # Financial Management
            {'name': 'Financial Dashboard', 'endpoint': '/financial/dashboard', 'method': 'GET'},
            {'name': 'Invoice Management', 'endpoint': '/financial/invoices', 'method': 'GET'},
            {'name': 'Payment Processing', 'endpoint': '/financial/payments', 'method': 'GET'},
            
            # User Management
            {'name': 'User Profile', 'endpoint': '/user/profile', 'method': 'GET'},
            {'name': 'User Statistics', 'endpoint': '/user/stats', 'method': 'GET'},
            
            # Workspace Management
            {'name': 'Workspace Management', 'endpoint': '/workspace', 'method': 'GET'},
            {'name': 'Workspace Settings', 'endpoint': '/workspace/settings', 'method': 'GET'},
            
            # AI Automation Suite
            {'name': 'AI Services', 'endpoint': '/ai/services', 'method': 'GET'},
            {'name': 'AI Analytics', 'endpoint': '/ai/analytics', 'method': 'GET'},
            
            # Template Marketplace
            {'name': 'Template Marketplace', 'endpoint': '/template/marketplace', 'method': 'GET'},
            {'name': 'Template Categories', 'endpoint': '/template/categories', 'method': 'GET'},
            
            # Admin Dashboard
            {'name': 'Admin Dashboard', 'endpoint': '/admin/dashboard', 'method': 'GET'},
            {'name': 'System Metrics', 'endpoint': '/admin/metrics', 'method': 'GET'},
            
            # Analytics System
            {'name': 'Analytics Overview', 'endpoint': '/analytics/overview', 'method': 'GET'},
            {'name': 'Business Intelligence', 'endpoint': '/analytics/business-intelligence', 'method': 'GET'}
        ]
        
        for service in critical_services:
            success, response, status = self.test_endpoint(service['method'], service['endpoint'])
            if success:
                self.working_endpoints.append(service['name'])
                self.log_result(service['name'], True, f"Service operational", response, status)
            else:
                self.failing_endpoints.append(service['name'])
                self.log_result(service['name'], False, f"Service failed", response, status)
    
    def test_external_api_integrations(self):
        """Test external API integrations"""
        print("\n🌐 TESTING EXTERNAL API INTEGRATIONS")
        print("=" * 80)
        
        external_apis = [
            # OpenAI Integration
            {'name': 'OpenAI API Test', 'endpoint': '/integrations/openai/test', 'method': 'GET'},
            {'name': 'AI Content Generation', 'endpoint': '/ai/generate-content', 'method': 'POST', 
             'data': {'prompt': 'Test content generation', 'type': 'blog'}},
            
            # Twitter/X Integration
            {'name': 'Twitter API Test', 'endpoint': '/integrations/twitter/test', 'method': 'GET'},
            {'name': 'Twitter Lead Search', 'endpoint': '/social-media/twitter/search', 'method': 'POST',
             'data': {'keywords': ['tech', 'startup'], 'count': 10}},
            
            # TikTok Integration
            {'name': 'TikTok API Test', 'endpoint': '/integrations/tiktok/test', 'method': 'GET'},
            {'name': 'TikTok Content Discovery', 'endpoint': '/social-media/tiktok/discover', 'method': 'POST',
             'data': {'hashtags': ['technology'], 'count': 5}},
            
            # ElasticMail Integration
            {'name': 'ElasticMail API Test', 'endpoint': '/integrations/elasticmail/test', 'method': 'GET'},
            {'name': 'Email Campaign Creation', 'endpoint': '/email/campaigns', 'method': 'POST',
             'data': {'name': 'Test Campaign', 'subject': 'Test Email', 'content': 'Test content'}},
            
            # Stripe Integration
            {'name': 'Stripe API Test', 'endpoint': '/integrations/stripe/test', 'method': 'GET'},
            {'name': 'Payment Processing Test', 'endpoint': '/payments/test', 'method': 'POST',
             'data': {'amount': 1000, 'currency': 'usd', 'test': True}}
        ]
        
        for api in external_apis:
            data = api.get('data', None)
            success, response, status = self.test_endpoint(api['method'], api['endpoint'], data)
            if success:
                self.working_endpoints.append(api['name'])
                self.log_result(api['name'], True, f"External API integration working", response, status)
            else:
                self.failing_endpoints.append(api['name'])
                self.log_result(api['name'], False, f"External API integration failed", response, status)
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 100)
        print("🎯 MEWAYZ V2 PLATFORM - PRODUCTION READINESS ASSESSMENT - JANUARY 2025")
        print("=" * 100)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   Tests Passed: {passed_tests} ✅")
        print(f"   Tests Failed: {total_tests - passed_tests} ❌")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        # CRUD Operations Summary
        print(f"\n🔄 CRUD OPERATIONS ASSESSMENT:")
        for operation, results in self.crud_results.items():
            working_count = len(results['working'])
            failing_count = len(results['failing'])
            total_count = working_count + failing_count
            op_success_rate = (working_count / total_count * 100) if total_count > 0 else 0
            print(f"   {operation}: {working_count}/{total_count} ({op_success_rate:.1f}%) {'✅' if op_success_rate >= 75 else '❌'}")
        
        # Real Data Verification
        print(f"\n🗄️ REAL DATA PERSISTENCE VERIFICATION:")
        real_data_count = len(self.real_data_confirmed)
        mock_data_count = len(self.mock_data_detected)
        total_data_tests = real_data_count + mock_data_count
        real_data_percentage = (real_data_count / total_data_tests * 100) if total_data_tests > 0 else 0
        print(f"   Real Data Confirmed: {real_data_count} endpoints ✅")
        print(f"   Mock Data Detected: {mock_data_count} endpoints ❌")
        print(f"   Real Data Usage: {real_data_percentage:.1f}%")
        
        # Critical Business Services
        print(f"\n🏢 CRITICAL BUSINESS SERVICES:")
        working_services = len(self.working_endpoints)
        failing_services = len(self.failing_endpoints)
        total_services = working_services + failing_services
        services_success_rate = (working_services / total_services * 100) if total_services > 0 else 0
        print(f"   Working Services: {working_services}/{total_services} ({services_success_rate:.1f}%)")
        
        # Production Readiness Assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            readiness_status = "✅ PRODUCTION READY - EXCELLENT"
        elif success_rate >= 75:
            readiness_status = "✅ PRODUCTION READY - GOOD"
        elif success_rate >= 50:
            readiness_status = "⚠️ NEEDS IMPROVEMENT - PARTIAL"
        else:
            readiness_status = "❌ NOT PRODUCTION READY - CRITICAL ISSUES"
        
        print(f"   Status: {readiness_status}")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        # Key Achievements
        print(f"\n🎉 KEY ACHIEVEMENTS:")
        if self.access_token:
            print("   ✅ Authentication system working perfectly")
        if real_data_percentage >= 80:
            print("   ✅ Real data operations confirmed")
        if services_success_rate >= 75:
            print("   ✅ Critical business services operational")
        
        # Issues Requiring Attention
        print(f"\n🔧 ISSUES REQUIRING ATTENTION:")
        if success_rate < 90:
            print(f"   - Overall success rate needs improvement ({success_rate:.1f}%)")
        if real_data_percentage < 95:
            print(f"   - Some endpoints may still use mock data ({100-real_data_percentage:.1f}%)")
        if any(len(self.crud_results[op]['failing']) > 0 for op in self.crud_results):
            print("   - CRUD operations need fixes")
        
        return success_rate
    
    def run_comprehensive_test(self):
        """Run comprehensive production readiness test"""
        print("🎯 MEWAYZ V2 PLATFORM - PRODUCTION READINESS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: CRUD Operations Testing
        self.test_crud_operations()
        
        # Step 3: Real Data Persistence Testing
        self.test_real_data_persistence()
        
        # Step 4: Critical Business Services Testing
        self.test_critical_business_services()
        
        # Step 5: External API Integration Testing
        self.test_external_api_integrations()
        
        # Step 6: Generate Final Report
        success_rate = self.generate_final_report()
        
        return success_rate >= 75  # Production ready if 75%+ success rate

def main():
    """Main function to run the production readiness test"""
    tester = ProductionReadinessTester()
    
    try:
        production_ready = tester.run_comprehensive_test()
        
        if production_ready:
            print("\n🎉 FINAL CONCLUSION: MEWAYZ V2 PLATFORM IS PRODUCTION READY!")
            sys.exit(0)
        else:
            print("\n❌ FINAL CONCLUSION: PLATFORM NEEDS IMPROVEMENTS BEFORE PRODUCTION DEPLOYMENT")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()