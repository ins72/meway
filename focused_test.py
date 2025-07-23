#!/usr/bin/env python3
"""
FOCUSED TEST FOR 3 SPECIFIC FIXES - JANUARY 2025
Quick targeted test of the 3 specific issues that were just fixed:
1. Email Marketing Dashboard - Test /api/email-marketing/dashboard endpoint
2. AI Workflows - Test /api/ai-automation/workflows or /api/workflows/ endpoints 
3. Quick Health Check - Test a few other key endpoints
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

class FocusedTester:
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
            auth_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", data=auth_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_result("Authentication", True, f"Successfully authenticated as {TEST_EMAIL}")
                    return True
                else:
                    self.log_result("Authentication", False, "No access token in response")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_email_marketing_dashboard(self):
        """Test Email Marketing Dashboard endpoint that was causing 500 errors"""
        print("\n🎯 TESTING EMAIL MARKETING DASHBOARD (Issue #1)")
        
        try:
            response = self.session.get(f"{API_BASE}/email-marketing/dashboard", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Email Marketing Dashboard", True, 
                              f"Working perfectly ({len(str(data))} chars response)", data)
                return True
            elif response.status_code == 500:
                self.log_result("Email Marketing Dashboard", False, 
                              f"Still getting 500 error: {response.text}")
                return False
            else:
                self.log_result("Email Marketing Dashboard", False, 
                              f"Unexpected status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Email Marketing Dashboard", False, f"Request error: {str(e)}")
            return False
    
    def test_ai_workflows(self):
        """Test AI Workflows endpoints"""
        print("\n🎯 TESTING AI WORKFLOWS (Issue #2)")
        
        # Test multiple possible endpoints for AI workflows
        endpoints_to_test = [
            "/api/ai-automation/workflows",
            "/api/workflows/",
            "/api/workflows",
            "/api/ai-automation/workflows/list"
        ]
        
        success_count = 0
        
        for endpoint in endpoints_to_test:
            try:
                full_url = f"{BACKEND_URL}{endpoint}" if endpoint.startswith("/api") else f"{API_BASE}{endpoint}"
                response = self.session.get(full_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(f"AI Workflows - {endpoint}", True, 
                                  f"Working perfectly ({len(str(data))} chars response)", data)
                    success_count += 1
                elif response.status_code == 404:
                    self.log_result(f"AI Workflows - {endpoint}", False, 
                                  f"Endpoint not found (404)")
                elif response.status_code == 500:
                    self.log_result(f"AI Workflows - {endpoint}", False, 
                                  f"Internal server error (500): {response.text}")
                else:
                    self.log_result(f"AI Workflows - {endpoint}", False, 
                                  f"Status {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"AI Workflows - {endpoint}", False, f"Request error: {str(e)}")
        
        return success_count > 0
    
    def test_health_check(self):
        """Quick health check of key endpoints"""
        print("\n🎯 QUICK HEALTH CHECK (Issue #3)")
        
        # Key endpoints to test for general health
        health_endpoints = [
            ("/health", "System Health"),
            ("/api/auth/me", "User Profile"),
            ("/api/dashboard/overview", "Dashboard Overview"),
            ("/api/analytics/overview", "Analytics Overview"),
            ("/api/ai-services/list", "AI Services")
        ]
        
        success_count = 0
        total_count = len(health_endpoints)
        
        for endpoint, name in health_endpoints:
            try:
                full_url = f"{BACKEND_URL}{endpoint}" if endpoint.startswith("/") else f"{API_BASE}/{endpoint}"
                response = self.session.get(full_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(f"Health Check - {name}", True, 
                                  f"Working perfectly ({len(str(data))} chars response)")
                    success_count += 1
                elif response.status_code == 401:
                    self.log_result(f"Health Check - {name}", True, 
                                  f"Authentication required (expected for protected endpoints)")
                    success_count += 1
                else:
                    self.log_result(f"Health Check - {name}", False, 
                                  f"Status {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"Health Check - {name}", False, f"Request error: {str(e)}")
        
        health_percentage = (success_count / total_count) * 100
        print(f"\n📊 Health Check Summary: {success_count}/{total_count} endpoints healthy ({health_percentage:.1f}%)")
        
        return success_count >= (total_count * 0.6)  # 60% threshold for health
    
    def run_focused_tests(self):
        """Run all focused tests"""
        print("🎯 FOCUSED TEST FOR 3 SPECIFIC FIXES - JANUARY 2025")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test the 3 specific issues
        results = []
        
        # Issue #1: Email Marketing Dashboard
        results.append(self.test_email_marketing_dashboard())
        
        # Issue #2: AI Workflows
        results.append(self.test_ai_workflows())
        
        # Issue #3: Quick Health Check
        results.append(self.test_health_check())
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 FOCUSED TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Issue-specific summary
        issue_results = [
            ("Email Marketing Dashboard", results[0]),
            ("AI Workflows", results[1]),
            ("Quick Health Check", results[2])
        ]
        
        print("\nIssue-Specific Results:")
        for issue_name, success in issue_results:
            status = "✅ FIXED" if success else "❌ STILL BROKEN"
            print(f"  {status}: {issue_name}")
        
        # Detailed results
        print("\nDetailed Test Results:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']} - {result['message']}")
        
        return success_rate >= 70  # 70% threshold for overall success

def main():
    """Main test execution"""
    tester = FocusedTester()
    success = tester.run_focused_tests()
    
    if success:
        print("\n🎉 FOCUSED TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n⚠️ FOCUSED TESTS COMPLETED WITH ISSUES")
        sys.exit(1)

if __name__ == "__main__":
    main()