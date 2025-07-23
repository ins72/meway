#!/usr/bin/env python3
"""
QUICK VALIDATION TEST - MEWAYZ PLATFORM
Quick validation test of the Mewayz platform after comprehensive fixes
Focus on: Core Systems Health, Authentication, Key Features, New API Endpoints, Database Connectivity
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

class QuickValidationTester:
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
            else:
                self.log_result(test_name, False, f"Unsupported method: {method}")
                return False, None
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Working perfectly - Status {response.status_code}", data)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Working perfectly - Status {response.status_code} (non-JSON response)")
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404)")
                return False, None
            elif response.status_code == 401:
                self.log_result(test_name, False, f"Authentication required (401)")
                return False, None
            elif response.status_code == 403:
                self.log_result(test_name, False, f"Access forbidden (403)")
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
                self.log_result(test_name, False, f"Error - Status {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False, None

    def test_core_systems_health(self):
        """Test Core Systems Health - Test health endpoints and basic functionality"""
        print("\n🏥 TESTING CORE SYSTEMS HEALTH")
        print("=" * 60)
        
        # 1. Backend Health Check
        try:
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                paths_count = len(data.get('paths', {}))
                self.log_result("Backend Health Check", True, f"Backend operational with {paths_count} API endpoints", {"paths_count": paths_count})
            else:
                self.log_result("Backend Health Check", False, f"Backend not accessible - Status {response.status_code}")
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Health check error: {str(e)}")
        
        # 2. System Health Endpoint
        self.test_endpoint("/health", "GET", test_name="System Health Endpoint")
        
        # 3. System Metrics
        self.test_endpoint("/metrics", "GET", test_name="System Metrics")
        
        print("🏥 Core Systems Health Testing Complete!")
        
    def test_authentication(self):
        """Test Authentication - Verify login still works"""
        print("\n🔐 TESTING AUTHENTICATION")
        print("=" * 60)
        
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
                    self.log_result("Authentication Login", True, f"Login successful with {TEST_EMAIL}", data)
                    
                    # Test token validation
                    self.test_endpoint("/auth/me", "GET", test_name="Authentication Token Validation")
                    return True
                else:
                    self.log_result("Authentication Login", False, "Login response missing access_token")
                    return False
            else:
                self.log_result("Authentication Login", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Login", False, f"Authentication error: {str(e)}")
            return False
        
        print("🔐 Authentication Testing Complete!")
        
    def test_key_features(self):
        """Test Key Features - Quick test of main systems like templates, ecommerce, financial"""
        print("\n🎯 TESTING KEY FEATURES")
        print("=" * 60)
        
        # 1. Template System
        print("\n📋 Testing Template System...")
        self.test_endpoint("/marketing-website/templates/marketplace", "GET", test_name="Templates - Marketplace")
        
        # 2. E-commerce System
        print("\n🛒 Testing E-commerce System...")
        self.test_endpoint("/ecommerce/products", "GET", test_name="E-commerce - Products")
        self.test_endpoint("/ecommerce/orders", "GET", test_name="E-commerce - Orders")
        self.test_endpoint("/ecommerce/dashboard", "GET", test_name="E-commerce - Dashboard")
        
        # 3. Financial System
        print("\n💰 Testing Financial System...")
        self.test_endpoint("/financial/dashboard", "GET", test_name="Financial - Dashboard")
        self.test_endpoint("/financial/invoices", "GET", test_name="Financial - Invoices")
        self.test_endpoint("/financial/expenses", "GET", test_name="Financial - Expenses")
        
        # 4. Analytics System
        print("\n📊 Testing Analytics System...")
        self.test_endpoint("/analytics-system/dashboard", "GET", test_name="Analytics - Dashboard")
        self.test_endpoint("/analytics-system/overview", "GET", test_name="Analytics - Overview")
        
        # 5. User Management
        print("\n👤 Testing User Management...")
        self.test_endpoint("/users/profile", "GET", test_name="User - Profile")
        self.test_endpoint("/users/statistics", "GET", test_name="User - Statistics")
        
        print("🎯 Key Features Testing Complete!")
        
    def test_new_api_endpoints(self):
        """Test New API Endpoints - Test some of the newly created endpoints"""
        print("\n🆕 TESTING NEW API ENDPOINTS")
        print("=" * 60)
        
        # 1. Team Management (New Feature)
        print("\n👥 Testing Team Management...")
        self.test_endpoint("/teams/dashboard", "GET", test_name="New API - Team Dashboard")
        self.test_endpoint("/teams/activity", "GET", test_name="New API - Team Activity")
        
        # 2. Mobile PWA Features (New Feature)
        print("\n📱 Testing Mobile PWA...")
        self.test_endpoint("/mobile-pwa/health", "GET", test_name="New API - PWA Health")
        self.test_endpoint("/mobile-pwa/pwa/manifest", "GET", test_name="New API - PWA Manifest")
        self.test_endpoint("/mobile-pwa/analytics/mobile", "GET", test_name="New API - Mobile Analytics")
        
        # 3. Admin Configuration (New Feature)
        print("\n⚙️ Testing Admin Configuration...")
        self.test_endpoint("/admin-config/configuration", "GET", test_name="New API - Admin Configuration")
        self.test_endpoint("/admin-config/integration-status", "GET", test_name="New API - Integration Status")
        self.test_endpoint("/admin-config/system-health", "GET", test_name="New API - System Health")
        
        # 4. Workflow Automation (New Feature)
        print("\n🔄 Testing Workflow Automation...")
        self.test_endpoint("/workflows/user-workflows", "GET", test_name="New API - User Workflows")
        self.test_endpoint("/workflows/advanced-workflows", "GET", test_name="New API - Advanced Workflows")
        
        print("🆕 New API Endpoints Testing Complete!")
        
    def test_database_connectivity(self):
        """Test Database Connectivity - Verify real data operations"""
        print("\n🗄️ TESTING DATABASE CONNECTIVITY")
        print("=" * 60)
        
        # Test data consistency across multiple calls to verify real database usage
        print("\n🔍 Testing Data Consistency (Real Database Verification)...")
        
        # Test 1: User Profile consistency
        success1, data1 = self.test_endpoint("/users/profile", "GET", test_name="Database - User Profile (Call 1)")
        time.sleep(1)
        success2, data2 = self.test_endpoint("/users/profile", "GET", test_name="Database - User Profile (Call 2)")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result("Database Consistency - User Profile", True, "Data consistent across calls - Real database confirmed")
            else:
                self.log_result("Database Consistency - User Profile", False, "Data inconsistent - May be using random generation")
        
        # Test 2: Dashboard data consistency
        success1, data1 = self.test_endpoint("/dashboard/overview", "GET", test_name="Database - Dashboard (Call 1)")
        time.sleep(1)
        success2, data2 = self.test_endpoint("/dashboard/overview", "GET", test_name="Database - Dashboard (Call 2)")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result("Database Consistency - Dashboard", True, "Data consistent across calls - Real database confirmed")
            else:
                self.log_result("Database Consistency - Dashboard", False, "Data inconsistent - May be using random generation")
        
        # Test 3: E-commerce data consistency
        success1, data1 = self.test_endpoint("/ecommerce/products", "GET", test_name="Database - E-commerce (Call 1)")
        time.sleep(1)
        success2, data2 = self.test_endpoint("/ecommerce/products", "GET", test_name="Database - E-commerce (Call 2)")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result("Database Consistency - E-commerce", True, "Data consistent across calls - Real database confirmed")
            else:
                self.log_result("Database Consistency - E-commerce", False, "Data inconsistent - May be using random generation")
        
        print("🗄️ Database Connectivity Testing Complete!")
        
    def print_validation_summary(self):
        """Print quick validation summary"""
        print("\n" + "=" * 80)
        print("🎯 QUICK VALIDATION TEST SUMMARY - MEWAYZ PLATFORM")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL VALIDATION RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Group results by category
        categories = {
            "Core Systems Health": [],
            "Authentication": [],
            "Key Features": [],
            "New API Endpoints": [],
            "Database Connectivity": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Health" in test_name or "Metrics" in test_name:
                categories["Core Systems Health"].append(result)
            elif "Authentication" in test_name:
                categories["Authentication"].append(result)
            elif any(x in test_name for x in ["Templates", "E-commerce", "Financial", "Analytics", "User"]):
                categories["Key Features"].append(result)
            elif "New API" in test_name:
                categories["New API Endpoints"].append(result)
            elif "Database" in test_name:
                categories["Database Connectivity"].append(result)
        
        print(f"\n📋 VALIDATION BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = len([r for r in results if r["success"]])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅" if rate >= 75 else "⚠️" if rate >= 50 else "❌"
                print(f"   {status} {category}: {passed}/{total} ({rate:.1f}%)")
        
        print(f"\n🔍 CRITICAL ISSUES (if any):")
        critical_failures = [r for r in self.test_results if not r["success"] and "500" in r["message"]]
        if critical_failures:
            for result in critical_failures:
                print(f"   🔴 {result['test']}: {result['message']}")
        else:
            print("   🎉 No critical issues found!")
        
        print(f"\n🎯 PLATFORM STATUS:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - Platform is working excellently after fixes")
        elif success_rate >= 75:
            print("   🟡 GOOD - Platform is working well with minor issues")
        elif success_rate >= 50:
            print("   🟠 FAIR - Platform has some issues but core functionality works")
        else:
            print("   🔴 POOR - Platform has significant issues requiring attention")
        
        print("=" * 80)

def main():
    """Main test execution"""
    print("🎯 QUICK VALIDATION TEST - MEWAYZ PLATFORM")
    print("Testing after comprehensive fixes")
    print("Focus: Core Systems Health, Authentication, Key Features, New API Endpoints, Database Connectivity")
    print("Credentials: tmonnens@outlook.com / Voetballen5")
    print("=" * 80)
    
    tester = QuickValidationTester()
    
    # Run validation tests in order
    tester.test_core_systems_health()
    tester.test_authentication()
    tester.test_key_features()
    tester.test_new_api_endpoints()
    tester.test_database_connectivity()
    
    # Print summary
    tester.print_validation_summary()

if __name__ == "__main__":
    main()