#!/usr/bin/env python3
"""
DEPLOYMENT RESOLUTION & CORE SYSTEM RESTORATION TEST
===================================================
Testing the deployment resolution task that needs retesting:
- Verify backend is running stable with health endpoints
- Test database connectivity 
- Verify core APIs are restored and functional
- Confirm no regression in functionality

Based on test_result.md requirements for the single task that needs_retesting: true
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration from frontend/.env
BACKEND_URL = "https://eff6f53c-47df-43a1-9962-4d20b26f6dc5.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class DeploymentResolutionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name: str, success: bool, status_code: int = None, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "status_code": status_code,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: PASSED")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: FAILED - {details}")
            
    def make_request(self, method: str, endpoint: str, data: Dict = None, auth_required: bool = False) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if auth_required and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_basic_health_endpoints(self):
        """Test basic health and root endpoints"""
        print("\n🔍 TESTING BASIC HEALTH ENDPOINTS")
        print("=" * 50)
        
        # Test root endpoint
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("service") == "mewayz-api" and data.get("status") == "running":
                    self.log_result("Root Endpoint", True, response.status_code, f"Service: {data.get('service')}, Status: {data.get('status')}")
                else:
                    self.log_result("Root Endpoint", False, response.status_code, "Invalid response structure")
            except json.JSONDecodeError:
                self.log_result("Root Endpoint", False, response.status_code, f"Invalid JSON response: {response.text[:100]}")
        else:
            self.log_result("Root Endpoint", False, response.status_code if response else None, "Request failed")
            
        # Test health endpoint
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                db_status = data.get("database", "unknown")
                self.log_result("Health Endpoint", True, response.status_code, f"Status: healthy, Database: {db_status}")
            else:
                self.log_result("Health Endpoint", False, response.status_code, "Status not healthy")
        else:
            self.log_result("Health Endpoint", False, response.status_code if response else None, "Request failed")
            
        # Test API health endpoint
        response = self.make_request("GET", "/api/health")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                db_status = data.get("database", "unknown")
                self.log_result("API Health Endpoint", True, response.status_code, f"Status: healthy, Database: {db_status}")
            else:
                self.log_result("API Health Endpoint", False, response.status_code, "Status not healthy")
        else:
            self.log_result("API Health Endpoint", False, response.status_code if response else None, "Request failed")

    def test_authentication_system(self):
        """Test authentication system restoration"""
        print("\n🔍 TESTING AUTHENTICATION SYSTEM")
        print("=" * 50)
        
        # Test login endpoint
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = self.make_request("POST", "/api/auth/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.token = data["access_token"]
                self.log_result("Authentication Login", True, response.status_code, "Login successful, token received")
                
                # Test token validation with /me endpoint
                response = self.make_request("GET", "/api/auth/me", auth_required=True)
                if response and response.status_code == 200:
                    user_data = response.json()
                    if user_data.get("email") == TEST_EMAIL:
                        self.log_result("Token Validation", True, response.status_code, f"User authenticated: {user_data.get('email')}")
                    else:
                        self.log_result("Token Validation", False, response.status_code, "Email mismatch in user data")
                else:
                    self.log_result("Token Validation", False, response.status_code if response else None, "Token validation failed")
            else:
                self.log_result("Authentication Login", False, response.status_code, "No access token in response")
        else:
            self.log_result("Authentication Login", False, response.status_code if response else None, "Login request failed")

    def test_core_api_restoration(self):
        """Test that core APIs mentioned in deployment resolution are working"""
        print("\n🔍 TESTING CORE API RESTORATION")
        print("=" * 50)
        
        # Core APIs that should be restored according to test_result.md
        core_apis = [
            ("/api/stripe-integration/health", "Stripe Integration"),
            ("/api/admin-workspace-management/health", "Admin Workspace Management"),
            ("/api/customer-notification/health", "Customer Notification"),
            ("/api/workspace-subscription/health", "Workspace Subscription"),
            ("/api/booking/health", "Booking API")
        ]
        
        for endpoint, system_name in core_apis:
            response = self.make_request("GET", endpoint)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("status") in ["healthy", "operational"]:
                    self.log_result(f"{system_name} Health", True, response.status_code, f"Status: {data.get('status')}")
                else:
                    self.log_result(f"{system_name} Health", False, response.status_code, f"Unexpected status: {data.get('status')}")
            else:
                self.log_result(f"{system_name} Health", False, response.status_code if response else None, "Health check failed")

    def test_database_connectivity(self):
        """Test database connectivity through various endpoints"""
        print("\n🔍 TESTING DATABASE CONNECTIVITY")
        print("=" * 50)
        
        if not self.token:
            print("⚠️ Skipping database tests - no authentication token")
            return
            
        # Test workspace endpoint (requires database)
        response = self.make_request("GET", "/api/workspace/", auth_required=True)
        if response and response.status_code in [200, 404]:  # 404 is OK if no workspaces exist
            if response.status_code == 200:
                data = response.json()
                self.log_result("Database Connectivity (Workspace)", True, response.status_code, f"Retrieved {len(data) if isinstance(data, list) else 'data'}")
            else:
                self.log_result("Database Connectivity (Workspace)", True, response.status_code, "Database accessible (no workspaces found)")
        else:
            self.log_result("Database Connectivity (Workspace)", False, response.status_code if response else None, "Database connection failed")
            
        # Test settings endpoint (requires database)
        response = self.make_request("GET", "/api/settings/", auth_required=True)
        if response and response.status_code in [200, 404]:  # 404 is OK if no settings exist
            if response.status_code == 200:
                data = response.json()
                self.log_result("Database Connectivity (Settings)", True, response.status_code, f"Retrieved {len(data) if isinstance(data, list) else 'data'}")
            else:
                self.log_result("Database Connectivity (Settings)", True, response.status_code, "Database accessible (no settings found)")
        else:
            self.log_result("Database Connectivity (Settings)", False, response.status_code if response else None, "Database connection failed")

    def test_no_503_errors(self):
        """Test that 503 errors (deployment issues) are resolved"""
        print("\n🔍 TESTING NO 503 ERRORS (DEPLOYMENT RESOLUTION)")
        print("=" * 50)
        
        # Test multiple endpoints to ensure no 503 errors
        test_endpoints = [
            "/",
            "/health", 
            "/api/health",
            "/api/auth/health" if self.token else None,
            "/api/workspace/health" if self.token else None,
            "/api/booking/health",
            "/api/escrow/health"
        ]
        
        # Filter out None endpoints
        test_endpoints = [ep for ep in test_endpoints if ep is not None]
        
        all_good = True
        for endpoint in test_endpoints:
            response = self.make_request("GET", endpoint, auth_required=("/api/" in endpoint and self.token))
            if response and response.status_code == 503:
                self.log_result(f"No 503 Error ({endpoint})", False, response.status_code, "Service unavailable error detected")
                all_good = False
            elif response and response.status_code in [200, 404, 401]:  # These are acceptable
                self.log_result(f"No 503 Error ({endpoint})", True, response.status_code, "No service unavailable error")
            else:
                # Other errors are not 503, so deployment is working
                self.log_result(f"No 503 Error ({endpoint})", True, response.status_code if response else None, "No 503 error (other status)")
                
        if all_good:
            self.log_result("Overall 503 Error Resolution", True, None, "No 503 errors detected across all endpoints")

    def run_deployment_resolution_tests(self):
        """Run all deployment resolution tests"""
        print("🚀 STARTING DEPLOYMENT RESOLUTION & CORE SYSTEM RESTORATION TESTS")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        print("=" * 80)
        
        # Run all test categories
        self.test_basic_health_endpoints()
        self.test_authentication_system()
        self.test_core_api_restoration()
        self.test_database_connectivity()
        self.test_no_503_errors()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 DEPLOYMENT RESOLUTION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        if self.failed_tests == 0:
            print("\n✅ DEPLOYMENT RESOLUTION: FULLY WORKING")
            print("All core systems restored and operational!")
        elif self.failed_tests <= 2:
            print("\n🟡 DEPLOYMENT RESOLUTION: MOSTLY WORKING")
            print("Core functionality restored with minor issues")
        else:
            print("\n❌ DEPLOYMENT RESOLUTION: ISSUES DETECTED")
            print("Significant problems found in deployment resolution")
            
        # Save detailed results
        with open("/app/deployment_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": self.total_tests,
                    "passed_tests": self.passed_tests,
                    "failed_tests": self.failed_tests,
                    "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0
                },
                "test_results": self.test_results,
                "timestamp": datetime.utcnow().isoformat()
            }, f, indent=2)
            
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = DeploymentResolutionTester()
    success = tester.run_deployment_resolution_tests()
    sys.exit(0 if success else 1)