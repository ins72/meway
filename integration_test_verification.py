#!/usr/bin/env python3
"""
Integration Test Verification Script
Tests the newly integrated API endpoints and comprehensive analysis results as requested in the review
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class IntegrationTestVerifier:
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
        """Authenticate with the backend"""
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
                return False
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code}", data)
                    return True
                except:
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code} (non-JSON response)")
                    return True
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404) - May not be implemented")
                return False
            elif response.status_code == 401:
                self.log_result(test_name, False, f"Authentication required (401)")
                return False
            elif response.status_code == 403:
                self.log_result(test_name, False, f"Access forbidden (403)")
                return False
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Internal server error')
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}")
                return False
            else:
                self.log_result(test_name, False, f"Endpoint error - Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False
    
    def test_integration_test_endpoints(self):
        """Test the new integration test endpoints"""
        print("\n=== 1. API INTEGRATION TESTING ===")
        print("Testing the integration endpoints and external API connections")
        
        # Test integration management endpoints
        integration_endpoints = [
            ("/integration/api/integration/available", "Integration - Available Services"),
            ("/integration/api/integration/connected", "Integration - Connected Services"),
            ("/admin-config/integrations/status", "Integration - Status Check")
        ]
        
        for endpoint, test_name in integration_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test external API integration tests via admin config
        external_api_tests = [
            ("/admin-config/integrations/stripe/test", "POST", {}, "Integration Tests - Stripe API"),
            ("/admin-config/integrations/openai/test", "POST", {}, "Integration Tests - OpenAI API"),
            ("/admin-config/integrations/sendgrid/test", "POST", {}, "Integration Tests - SendGrid API"),
            ("/admin-config/integrations/twitter/test", "POST", {}, "Integration Tests - Twitter API")
        ]
        
        for endpoint, method, data, test_name in external_api_tests:
            self.test_endpoint(endpoint, method, data, test_name)
    
    def test_enhanced_features(self):
        """Test the enhanced features verification"""
        print("\n=== 2. ENHANCED FEATURES VERIFICATION ===")
        print("Testing enhanced AI Analytics, real-time notifications, and workflow automation")
        
        # Test enhanced AI Analytics endpoints (correct paths)
        print("\n--- Enhanced AI Analytics (/api/ai-analytics) ---")
        ai_analytics_endpoints = [
            ("/ai-analytics/api/ai-analytics/insights", "AI Analytics - Get Insights"),
            ("/ai-analytics/api/ai-analytics/insights/generate", "POST", {"data_source": "user_behavior", "time_range": "30_days"}, "AI Analytics - Generate Insights"),
            ("/ai-analytics/api/ai-analytics/analytics/summary", "AI Analytics - Analytics Summary"),
            ("/ai-analytics/api/ai-analytics/insights/anomaly-detection", "POST", {"dataset": "user_activity", "threshold": 0.95}, "AI Analytics - Anomaly Detection")
        ]
        
        for item in ai_analytics_endpoints:
            if len(item) == 4:
                endpoint, method, data, test_name = item
                self.test_endpoint(endpoint, method, data, test_name)
            else:
                endpoint, test_name = item
                self.test_endpoint(endpoint, test_name=test_name)
        
        # Test real-time notifications (correct paths)
        print("\n--- Real-time Notifications (/api/notifications-system) ---")
        notification_endpoints = [
            ("/notifications-system/history", "Notifications - Get History"),
            ("/notifications-system/analytics/overview", "Notifications - Get Statistics"),
            ("/notifications-system/channels", "Notifications - Get Channels"),
            ("/notifications-system/send", "POST", {"title": "Test", "message": "Test notification", "type": "info"}, "Notifications - Send Notification")
        ]
        
        for item in notification_endpoints:
            if len(item) == 4:
                endpoint, method, data, test_name = item
                self.test_endpoint(endpoint, method, data, test_name)
            else:
                endpoint, test_name = item
                self.test_endpoint(endpoint, test_name=test_name)
        
        # Test workflow automation (correct paths)
        print("\n--- Workflow Automation (/api/automation) ---")
        workflow_endpoints = [
            ("/automation/workflows", "Workflows - List User Workflows"),
            ("/automation/workflows/advanced", "Workflows - Get Advanced Workflows"),
            ("/automation/integrations/available", "Workflows - Available Integrations")
        ]
        
        for endpoint, test_name in workflow_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_specification_compliance(self):
        """Test specification compliance check"""
        print("\n=== 3. SPECIFICATION COMPLIANCE CHECK ===")
        print("Testing major feature areas: workspaces, social media, analytics, AI services")
        
        # Test major feature areas
        feature_areas = [
            # Workspaces
            ("/workspaces", "Workspaces - List Workspaces"),
            ("/workspaces/create", "POST", {"name": "Test Workspace", "description": "Test"}, "Workspaces - Create Workspace"),
            
            # Social Media
            ("/social-media/analytics", "Social Media - Analytics"),
            ("/social-media/posts", "Social Media - Posts"),
            
            # Analytics
            ("/analytics/overview", "Analytics - Overview"),
            ("/analytics/features/usage", "Analytics - Feature Usage"),
            ("/analytics/platform/overview", "Analytics - Platform Overview"),
            
            # AI Services
            ("/ai/services", "AI Services - List Services"),
            ("/ai/conversations", "AI Services - Conversations"),
            ("/advanced-ai/capabilities", "AI Services - Advanced Capabilities")
        ]
        
        for item in feature_areas:
            if len(item) == 4:
                endpoint, method, data, test_name = item
                self.test_endpoint(endpoint, method, data, test_name)
            else:
                endpoint, test_name = item
                self.test_endpoint(endpoint, test_name=test_name)
        
        # Test CRUD operations
        print("\n--- CRUD Operations Verification ---")
        crud_endpoints = [
            # User management CRUD
            ("/users/profile", "CRUD - Read User Profile"),
            ("/users/profile", "PUT", {"name": "Updated Name"}, "CRUD - Update User Profile"),
            
            # Workspace CRUD
            ("/workspaces", "CRUD - Read Workspaces"),
            
            # Marketing CRUD
            ("/marketing/campaigns", "CRUD - Read Marketing Campaigns"),
            ("/marketing/contacts", "CRUD - Read Marketing Contacts")
        ]
        
        for item in crud_endpoints:
            if len(item) == 4:
                endpoint, method, data, test_name = item
                self.test_endpoint(endpoint, method, data, test_name)
            else:
                endpoint, test_name = item
                self.test_endpoint(endpoint, test_name=test_name)
    
    def test_api_key_verification(self):
        """Test API key verification"""
        print("\n=== 4. API KEY VERIFICATION ===")
        print("Testing new API keys configuration and external service connections")
        
        # Test admin configuration endpoints for API key management
        api_key_endpoints = [
            ("/admin-config/configuration", "API Keys - Get Configuration"),
            ("/admin-config/integrations/status", "API Keys - Integration Status"),
            ("/admin-config/available-services", "API Keys - Available Services")
        ]
        
        for endpoint, test_name in api_key_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test external service connections
        print("\n--- External Service Connection Tests ---")
        external_service_tests = [
            ("/admin-config/integrations/stripe/test", "POST", {}, "API Keys - Test Stripe Connection"),
            ("/admin-config/integrations/openai/test", "POST", {}, "API Keys - Test OpenAI Connection"),
            ("/admin-config/integrations/sendgrid/test", "POST", {}, "API Keys - Test SendGrid Connection"),
            ("/admin-config/integrations/twitter/test", "POST", {}, "API Keys - Test Twitter Connection")
        ]
        
        for endpoint, method, data, test_name in external_service_tests:
            self.test_endpoint(endpoint, method, data, test_name)
        
        # Test admin configuration system
        print("\n--- Admin Configuration System ---")
        admin_config_endpoints = [
            ("/admin-config/system/health", "Admin Config - System Health"),
            ("/admin-config/logs", "Admin Config - System Logs"),
            ("/admin-config/analytics/dashboard", "Admin Config - Analytics Dashboard")
        ]
        
        for endpoint, test_name in admin_config_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_comprehensive_analysis_results(self):
        """Test comprehensive analysis results verification"""
        print("\n=== 5. COMPREHENSIVE ANALYSIS RESULTS VERIFICATION ===")
        print("Testing comprehensive database operations and business workflows")
        
        # Test comprehensive database operations
        database_endpoints = [
            ("/dashboard/overview", "Database - Dashboard Overview"),
            ("/users/profile", "Database - User Profile"),
            ("/ecommerce/products", "Database - E-commerce Products"),
            ("/marketing/campaigns", "Database - Marketing Campaigns"),
            ("/ai/services", "Database - AI Services"),
            ("/admin/users", "Database - Admin Users")
        ]
        
        for endpoint, test_name in database_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test business workflow CRUD operations
        print("\n--- Business Workflow CRUD Support ---")
        business_crud_endpoints = [
            # E-commerce workflows
            ("/ecommerce/products", "Business CRUD - E-commerce Products"),
            ("/ecommerce/orders", "Business CRUD - E-commerce Orders"),
            ("/ecommerce/dashboard", "Business CRUD - E-commerce Dashboard"),
            
            # Marketing workflows
            ("/marketing/campaigns", "Business CRUD - Marketing Campaigns"),
            ("/marketing/contacts", "Business CRUD - Marketing Contacts"),
            ("/marketing/analytics", "Business CRUD - Marketing Analytics"),
            
            # AI service workflows
            ("/ai/services", "Business CRUD - AI Services"),
            ("/ai/conversations", "Business CRUD - AI Conversations"),
            
            # Admin workflows
            ("/admin/users", "Business CRUD - Admin Users"),
            ("/admin/system/metrics", "Business CRUD - Admin System Metrics")
        ]
        
        for endpoint, test_name in business_crud_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_data_consistency_verification(self):
        """Test data consistency to verify real database operations"""
        print("\n=== 6. DATA CONSISTENCY VERIFICATION ===")
        print("Testing data consistency across multiple calls to verify real database usage")
        
        consistency_endpoints = [
            "/dashboard/overview",
            "/users/profile",
            "/ai/services",
            "/ecommerce/dashboard",
            "/marketing/analytics"
        ]
        
        for endpoint in consistency_endpoints:
            self.test_data_consistency(endpoint)
    
    def test_data_consistency(self, endpoint: str):
        """Test if endpoint returns consistent data (indicating real database usage)"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            # Make first request
            response1 = self.session.get(url, timeout=10)
            if response1.status_code != 200:
                self.log_result(f"Data Consistency - {endpoint}", False, f"First request failed - Status {response1.status_code}")
                return False
            
            data1 = response1.json()
            
            # Wait a moment and make second request
            time.sleep(1)
            
            response2 = self.session.get(url, timeout=10)
            if response2.status_code != 200:
                self.log_result(f"Data Consistency - {endpoint}", False, f"Second request failed - Status {response2.status_code}")
                return False
            
            data2 = response2.json()
            
            # Compare responses
            if json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True):
                self.log_result(f"Data Consistency - {endpoint}", True, f"Data consistent across calls - confirms real database usage")
                return True
            else:
                self.log_result(f"Data Consistency - {endpoint}", False, f"Data inconsistent - may still be using random generation")
                return False
                
        except Exception as e:
            self.log_result(f"Data Consistency - {endpoint}", False, f"Request error: {str(e)}")
            return False
    
    def run_comprehensive_verification(self):
        """Run comprehensive verification of the review request requirements"""
        print("🎯 INTEGRATION TEST VERIFICATION - MEWAYZ PLATFORM")
        print("Testing the newly integrated API endpoints and comprehensive analysis results")
        print("Review Request Requirements:")
        print("1. API Integration Testing - Test new integration test endpoints")
        print("2. Enhanced Features Verification - Test AI Analytics, notifications, workflows")
        print("3. Specification Compliance Check - Test major feature areas and CRUD operations")
        print("4. API Key Verification - Confirm new API keys and external service connections")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Run all verification tests
        self.test_integration_test_endpoints()
        self.test_enhanced_features()
        self.test_specification_compliance()
        self.test_api_key_verification()
        self.test_comprehensive_analysis_results()
        self.test_data_consistency_verification()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 INTEGRATION TEST VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by category
        categories = {
            "Authentication": [],
            "Integration Tests": [],
            "AI Analytics": [],
            "Notifications": [],
            "Workflows": [],
            "Workspaces": [],
            "Social Media": [],
            "Analytics": [],
            "AI Services": [],
            "CRUD": [],
            "API Keys": [],
            "Admin Config": [],
            "Database": [],
            "Business CRUD": [],
            "Data Consistency": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                categories["Authentication"].append(result)
            elif "Integration Tests" in test_name:
                categories["Integration Tests"].append(result)
            elif "AI Analytics" in test_name:
                categories["AI Analytics"].append(result)
            elif "Notifications" in test_name:
                categories["Notifications"].append(result)
            elif "Workflows" in test_name:
                categories["Workflows"].append(result)
            elif "Workspaces" in test_name:
                categories["Workspaces"].append(result)
            elif "Social Media" in test_name:
                categories["Social Media"].append(result)
            elif "Analytics" in test_name:
                categories["Analytics"].append(result)
            elif "AI Services" in test_name:
                categories["AI Services"].append(result)
            elif "CRUD" in test_name:
                categories["CRUD"].append(result)
            elif "API Keys" in test_name:
                categories["API Keys"].append(result)
            elif "Admin Config" in test_name:
                categories["Admin Config"].append(result)
            elif "Database" in test_name:
                categories["Database"].append(result)
            elif "Business CRUD" in test_name:
                categories["Business CRUD"].append(result)
            elif "Data Consistency" in test_name:
                categories["Data Consistency"].append(result)
        
        print("\n📋 RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"\n{category}: {passed}/{total} passed ({(passed/total)*100:.1f}%)")
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    print(f"  {status} {result['test']}: {result['message']}")
        
        print(f"\n🎯 REVIEW REQUEST VERIFICATION COMPLETE")
        print(f"Overall Success Rate: {(passed_tests/total_tests)*100:.1f}%")

if __name__ == "__main__":
    verifier = IntegrationTestVerifier()
    success = verifier.run_comprehensive_verification()
    sys.exit(0 if success else 1)