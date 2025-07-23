#!/usr/bin/env python3
"""
Service Fixes Testing Script
Tests the specific endpoints mentioned in the review request that were previously failing
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://227a6971-09fc-47c6-b443-58c2c19d4c11.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ServiceFixesTester:
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
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
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
            
            if method.upper() == "GET":
                response = self.session.get(url, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
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
                self.log_result(test_name, False, f"Internal server error (500): {response.text}")
                return False
            else:
                self.log_result(test_name, False, f"Endpoint error - Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False
    
    def test_previously_failing_endpoints(self):
        """Test the endpoints that were previously failing with 500 errors due to service method mapping issues"""
        print("\n=== Testing Previously Failing Endpoints (Service Method Mapping Issues) ===")
        
        # Based on the backend startup logs, these modules had syntax issues:
        # - customer_experience: cannot import (still failing)
        # - social_email: unexpected indent (still failing) 
        # - advanced_ai: f-string unmatched '(' (still failing)
        # - content_creation: working now
        # - email_marketing: working now
        
        # Content Creation API - Should be working now (module loaded successfully)
        print("\n--- Content Creation API (Should be working) ---")
        self.test_endpoint("/content-creation/projects", test_name="Content Creation - Projects")
        self.test_endpoint("/content-creation/templates", test_name="Content Creation - Templates")
        self.test_endpoint("/content-creation/assets", test_name="Content Creation - Assets")
        
        # Email Marketing API - Should be working now (module loaded successfully)
        print("\n--- Email Marketing API (Should be working) ---")
        self.test_endpoint("/email-marketing/campaigns", test_name="Email Marketing - Campaigns")
        self.test_endpoint("/email-marketing/analytics", test_name="Email Marketing - Analytics")
        self.test_endpoint("/email-marketing/contacts", test_name="Email Marketing - Contacts")
        
        # Customer Experience API - Still has import issues (module failed to load)
        print("\n--- Customer Experience API (Still has issues) ---")
        self.test_endpoint("/customer-experience/dashboard", test_name="Customer Experience - Dashboard")
        self.test_endpoint("/customer-experience/journey-mapping", test_name="Customer Experience - Journey Mapping")
        self.test_endpoint("/customer-experience/feedback", test_name="Customer Experience - Feedback")
        
        # Social Email API - Still has syntax issues (module failed to load)
        print("\n--- Social Email API (Still has issues) ---")
        self.test_endpoint("/social-email/campaigns", test_name="Social Email - Campaigns")
        self.test_endpoint("/social-email/templates", test_name="Social Email - Templates")
    
    def test_database_integration_services(self):
        """Test services that should now be using real database operations"""
        print("\n=== Testing Database Integration Services ===")
        
        # Test services that are actually loaded and should have database integration
        database_services = [
            # Working services with database integration
            ("/social-media/analytics", "Social Media Service"),
            ("/automation/workflows", "Automation Service"),
            ("/support/tickets", "Support Service"),
            ("/monitoring/system-health", "Monitoring Service"),
            ("/backup/comprehensive-status", "Backup Service"),
            ("/business-intelligence/metrics", "Business Intelligence Service"),
            ("/enhanced-ecommerce/products", "Enhanced E-commerce Service"),
            ("/financial/dashboard", "Financial Management Service"),
            ("/crm/contacts", "CRM Management Service"),
            ("/content-creation/projects", "Content Creation Service")
        ]
        
        for endpoint, service_name in database_services:
            self.test_endpoint(endpoint, test_name=f"{service_name} Database Integration")
    
    def test_performance_and_stability(self):
        """Test performance and stability of the platform"""
        print("\n=== Testing Performance & Stability ===")
        
        # Test core endpoints multiple times to check stability
        stable_endpoints = [
            "/dashboard/overview",
            "/analytics/overview", 
            "/users/profile",
            "/workspaces",
            "/ai/services",
            "/ecommerce/products",
            "/marketing/campaigns"
        ]
        
        for endpoint in stable_endpoints:
            # Test endpoint 3 times to check for stability
            success_count = 0
            for i in range(3):
                try:
                    url = f"{API_BASE}{endpoint}"
                    start_time = time.time()
                    response = self.session.get(url, timeout=10)
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    if response.status_code == 200:
                        success_count += 1
                        if i == 0:  # Only log first success
                            self.log_result(f"Stability Test - {endpoint}", True, f"Stable endpoint - Response time: {response_time:.1f}ms")
                    else:
                        if i == 0:  # Only log first failure
                            self.log_result(f"Stability Test - {endpoint}", False, f"Unstable endpoint - Status {response.status_code}")
                        break
                        
                except Exception as e:
                    if i == 0:  # Only log first error
                        self.log_result(f"Stability Test - {endpoint}", False, f"Stability test error: {str(e)}")
                    break
            
            # Overall stability result
            if success_count == 3:
                self.log_result(f"Overall Stability - {endpoint}", True, f"100% stable (3/3 requests successful)")
            else:
                self.log_result(f"Overall Stability - {endpoint}", False, f"Unstable ({success_count}/3 requests successful)")
    
    def run_service_fixes_test(self):
        """Run comprehensive testing focused on the service fixes mentioned in the review request"""
        print("🔧 Starting Service Fixes Verification Testing")
        print("Testing the specific fixes mentioned in the review request:")
        print("- ✅ Fixed async/await syntax issues in customer_experience, email_marketing, social_email, and content_creation services")
        print("- ✅ Eliminated 32 additional random data calls (97 → 65 remaining)")
        print("- ✅ Applied database integration improvements to priority services")
        print("- ✅ Backend was restarted with all improvements applied")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test authentication first
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with service testing.")
            return False
        
        # Test the previously failing endpoints
        self.test_previously_failing_endpoints()
        
        # Test database integration services
        self.test_database_integration_services()
        
        # Test performance and stability
        self.test_performance_and_stability()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 SERVICE FIXES TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        previously_failing = [r for r in self.test_results if any(x in r['test'] for x in ['Customer Experience', 'Content Creation', 'Social Email', 'Email Marketing'])]
        database_integration = [r for r in self.test_results if 'Database Integration' in r['test']]
        stability_tests = [r for r in self.test_results if 'Stability' in r['test']]
        
        print(f"\n🔧 PREVIOUSLY FAILING ENDPOINTS:")
        prev_passed = sum(1 for r in previously_failing if r['success'])
        prev_total = len(previously_failing)
        print(f"   Success Rate: {(prev_passed/prev_total)*100:.1f}% ({prev_passed}/{prev_total})")
        
        print(f"\n💾 DATABASE INTEGRATION SERVICES:")
        db_passed = sum(1 for r in database_integration if r['success'])
        db_total = len(database_integration)
        if db_total > 0:
            print(f"   Success Rate: {(db_passed/db_total)*100:.1f}% ({db_passed}/{db_total})")
        
        print(f"\n⚡ STABILITY & PERFORMANCE:")
        stab_passed = sum(1 for r in stability_tests if r['success'])
        stab_total = len(stability_tests)
        if stab_total > 0:
            print(f"   Success Rate: {(stab_passed/stab_total)*100:.1f}% ({stab_passed}/{stab_total})")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")

if __name__ == "__main__":
    tester = ServiceFixesTester()
    success = tester.run_service_fixes_test()
    sys.exit(0 if success else 1)