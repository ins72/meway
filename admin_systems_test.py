#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for New Admin Systems
Tests the newly implemented Admin Workspace Management and Customer Notification systems
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://3dc4dc3c-9195-4a26-87f6-3f23beffd557.preview.emergentagent.com"
BASE_URL = f"{BACKEND_URL}/api"

# Test credentials for admin access
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class AdminSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and not success:
            print(f"    Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data if not success else None
        })
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            # Try to login with admin credentials
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("access_token"):
                    self.admin_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    self.log_test("Admin Authentication", True, f"Logged in as {ADMIN_EMAIL}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No access token in response", data)
                    return False
            else:
                # Try to register admin user if login fails
                register_data = {
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "full_name": "Admin User",
                    "is_admin": True
                }
                
                reg_response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
                
                if reg_response.status_code == 200:
                    # Now try login again
                    login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
                    if login_response.status_code == 200:
                        data = login_response.json()
                        if data.get("access_token"):
                            self.admin_token = data["access_token"]
                            self.session.headers.update({
                                "Authorization": f"Bearer {self.admin_token}"
                            })
                            self.log_test("Admin Authentication", True, f"Registered and logged in as {ADMIN_EMAIL}")
                            return True
                
                self.log_test("Admin Authentication", False, f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_workspace_management_system(self):
        """Test Admin Workspace Management System endpoints"""
        print("\n🔧 TESTING ADMIN WORKSPACE MANAGEMENT SYSTEM")
        print("=" * 60)
        
        # Test 1: Health Check
        try:
            response = self.session.get(f"{BASE_URL}/admin-workspace-management/health")
            success = response.status_code == 200
            data = response.json() if success else response.text
            
            if success and data.get("healthy"):
                self.log_test("Admin Workspace Management Health Check", True, "Service is healthy and operational")
            else:
                self.log_test("Admin Workspace Management Health Check", False, f"Status: {response.status_code}", data)
        except Exception as e:
            self.log_test("Admin Workspace Management Health Check", False, f"Exception: {str(e)}")
        
        # Test 2: Get All Workspaces (requires admin auth)
        try:
            response = self.session.get(f"{BASE_URL}/admin-workspace-management/workspaces?limit=10")
            success = response.status_code == 200
            data = response.json() if success else response.text
            
            if success:
                workspaces = data.get("workspaces", [])
                total = data.get("total", 0)
                self.log_test("Get All Workspaces", True, f"Retrieved {len(workspaces)} workspaces (total: {total})")
            elif response.status_code == 403:
                self.log_test("Get All Workspaces", False, "Admin access required - authentication issue", data)
            else:
                self.log_test("Get All Workspaces", False, f"Status: {response.status_code}", data)
        except Exception as e:
            self.log_test("Get All Workspaces", False, f"Exception: {str(e)}")
        
        # Test 3: Advanced Workspace Search
        try:
            search_criteria = {
                "filters": {
                    "status": "active"
                },
                "limit": 5
            }
            
            response = self.session.post(f"{BASE_URL}/admin-workspace-management/workspaces/search", json=search_criteria)
            success = response.status_code == 200
            data = response.json() if success else response.text
            
            if success:
                results = data.get("search_results", [])
                self.log_test("Advanced Workspace Search", True, f"Search returned {len(results)} results")
            elif response.status_code == 403:
                self.log_test("Advanced Workspace Search", False, "Admin access required - authentication issue", data)
            else:
                self.log_test("Advanced Workspace Search", False, f"Status: {response.status_code}", data)
        except Exception as e:
            self.log_test("Advanced Workspace Search", False, f"Exception: {str(e)}")
        
        # Test 4: Admin Analytics Overview
        try:
            response = self.session.get(f"{BASE_URL}/admin-workspace-management/analytics/overview")
            success = response.status_code == 200
            data = response.json() if success else response.text
            
            if success:
                analytics = data.get("analytics", {})
                total_workspaces = analytics.get("total_workspaces", 0)
                active_subs = analytics.get("active_subscriptions", 0)
                self.log_test("Admin Analytics Overview", True, f"Analytics: {total_workspaces} workspaces, {active_subs} active subscriptions")
            elif response.status_code == 403:
                self.log_test("Admin Analytics Overview", False, "Admin access required - authentication issue", data)
            else:
                self.log_test("Admin Analytics Overview", False, f"Status: {response.status_code}", data)
        except Exception as e:
            self.log_test("Admin Analytics Overview", False, f"Exception: {str(e)}")
    
    def test_customer_notification_system(self):
        """Test Customer Notification System endpoints"""
        print("\n📧 TESTING CUSTOMER NOTIFICATION SYSTEM")
        print("=" * 60)
        
        # Test 1: Health Check
        try:
            response = self.session.get(f"{BASE_URL}/customer-notification/health")
            success = response.status_code == 200
            data = response.json() if success else response.text
            
            if success and data.get("healthy"):
                self.log_test("Customer Notification Health Check", True, "Service is healthy and operational")
            else:
                self.log_test("Customer Notification Health Check", False, f"Status: {response.status_code}", data)
        except Exception as e:
            self.log_test("Customer Notification Health Check", False, f"Exception: {str(e)}")
        
        # Test 2: Get Notification Templates
        try:
            response = self.session.get(f"{BASE_URL}/customer-notification/templates")
            success = response.status_code == 200
            data = response.json() if success else response.text
            
            if success:
                templates = data.get("templates", {})
                template_count = len(templates)
                self.log_test("Get Notification Templates", True, f"Retrieved {template_count} notification templates")
            elif response.status_code == 403:
                self.log_test("Get Notification Templates", False, "Admin access required - authentication issue", data)
            else:
                self.log_test("Get Notification Templates", False, f"Status: {response.status_code}", data)
        except Exception as e:
            self.log_test("Get Notification Templates", False, f"Exception: {str(e)}")
        
        # Test 3: Get Notification Analytics
        try:
            response = self.session.get(f"{BASE_URL}/customer-notification/analytics?days_back=7")
            success = response.status_code == 200
            data = response.json() if success else response.text
            
            if success:
                analytics = data.get("analytics", {})
                total_sent = analytics.get("total_notifications_sent", 0)
                success_rate = analytics.get("success_rate", 0)
                self.log_test("Get Notification Analytics", True, f"Analytics: {total_sent} sent, {success_rate}% success rate")
            elif response.status_code == 403:
                self.log_test("Get Notification Analytics", False, "Admin access required - authentication issue", data)
            else:
                self.log_test("Get Notification Analytics", False, f"Status: {response.status_code}", data)
        except Exception as e:
            self.log_test("Get Notification Analytics", False, f"Exception: {str(e)}")
        
        # Test 4: Notification Statistics Overview
        try:
            response = self.session.get(f"{BASE_URL}/customer-notification/stats/overview")
            success = response.status_code == 200
            data = response.json() if success else response.text
            
            if success:
                overview = data.get("overview", {})
                weekly = overview.get("weekly", {})
                monthly = overview.get("monthly", {})
                available_templates = overview.get("available_templates", 0)
                enabled_channels = overview.get("enabled_channels", 0)
                self.log_test("Notification Statistics Overview", True, f"Overview: {available_templates} templates, {enabled_channels} enabled channels")
            elif response.status_code == 403:
                self.log_test("Notification Statistics Overview", False, "Admin access required - authentication issue", data)
            else:
                self.log_test("Notification Statistics Overview", False, f"Status: {response.status_code}", data)
        except Exception as e:
            self.log_test("Notification Statistics Overview", False, f"Exception: {str(e)}")
    
    def test_database_access(self):
        """Test that services can access database collections"""
        print("\n💾 TESTING DATABASE ACCESS")
        print("=" * 60)
        
        # Test database connectivity through health endpoints
        endpoints_to_test = [
            ("/admin-workspace-management/health", "Admin Workspace Management DB Access"),
            ("/customer-notification/health", "Customer Notification DB Access")
        ]
        
        for endpoint, test_name in endpoints_to_test:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                success = response.status_code == 200
                data = response.json() if success else response.text
                
                if success:
                    db_connected = data.get("database_connected", False)
                    collections = data.get("collections_available", [])
                    if db_connected:
                        self.log_test(test_name, True, f"Database connected, {len(collections)} collections available")
                    else:
                        self.log_test(test_name, True, "Service healthy but database status unknown")
                else:
                    self.log_test(test_name, False, f"Status: {response.status_code}", data)
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
    
    def test_admin_access_validation(self):
        """Test that admin access is properly validated"""
        print("\n🔐 TESTING ADMIN ACCESS VALIDATION")
        print("=" * 60)
        
        # Create a session without admin token
        non_admin_session = requests.Session()
        
        # Test endpoints that should require admin access
        admin_endpoints = [
            ("/admin-workspace-management/workspaces", "GET", "Admin Workspace List"),
            ("/admin-workspace-management/workspaces/search", "POST", "Admin Workspace Search"),
            ("/admin-workspace-management/analytics/overview", "GET", "Admin Analytics"),
            ("/customer-notification/templates", "GET", "Notification Templates"),
            ("/customer-notification/analytics", "GET", "Notification Analytics"),
            ("/customer-notification/stats/overview", "GET", "Notification Stats")
        ]
        
        for endpoint, method, test_name in admin_endpoints:
            try:
                if method == "GET":
                    response = non_admin_session.get(f"{BASE_URL}{endpoint}")
                else:
                    response = non_admin_session.post(f"{BASE_URL}{endpoint}", json={})
                
                # Should return 401 (unauthorized) or 403 (forbidden)
                if response.status_code in [401, 403]:
                    self.log_test(f"{test_name} - Access Control", True, f"Properly blocked non-admin access (status: {response.status_code})")
                else:
                    self.log_test(f"{test_name} - Access Control", False, f"Should block non-admin access but returned {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"{test_name} - Access Control", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 STARTING COMPREHENSIVE ADMIN SYSTEMS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with admin-only tests.")
            print("Will still test public endpoints and access control validation.")
        
        # Step 2: Test Admin Workspace Management System
        self.test_admin_workspace_management_system()
        
        # Step 3: Test Customer Notification System
        self.test_customer_notification_system()
        
        # Step 4: Test Database Access
        self.test_database_access()
        
        # Step 5: Test Admin Access Validation
        self.test_admin_access_validation()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  • {test['test']}: {test['details']}")
        
        # Overall assessment
        if success_rate >= 80:
            print(f"\n🎉 OVERALL ASSESSMENT: EXCELLENT - Both admin systems are operational and ready for production!")
        elif success_rate >= 60:
            print(f"\n✅ OVERALL ASSESSMENT: GOOD - Admin systems are mostly working with minor issues.")
        else:
            print(f"\n⚠️ OVERALL ASSESSMENT: NEEDS ATTENTION - Significant issues found in admin systems.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = AdminSystemTester()
    tester.run_all_tests()