#!/usr/bin/env python3
"""
ONBOARDING AND WORKSPACE CREATION API TESTING
==============================================
Testing backend onboarding and workspace creation APIs to understand how they work 
with the new frontend onboarding wizard.

Key areas to test:
1. Check if there are existing user-accessible endpoints for onboarding/workspace creation
2. Test the workspace creation endpoint to see the expected data format
3. Check if there's a subscription creation workflow that matches our bundle selection
4. Verify authentication requirements for onboarding-related endpoints

Testing focus:
- POST /api/workspace (workspace creation)
- POST /api/complete_onboarding (onboarding completion)
- Any subscription-related endpoints that could handle bundle selection
- Authentication requirements for these endpoints
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://b2614b52-973e-4c52-9dec-e3ec14470901.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class OnboardingWorkspaceAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, system: str, endpoint: str, method: str, success: bool, status_code: int = None, details: str = ""):
        """Log test result"""
        result = {
            "system": system,
            "endpoint": endpoint,
            "method": method,
            "success": success,
            "status_code": status_code,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        self.total_tests += 1
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {system} | {method} {endpoint} | {status_code} | {details}")
    
    def authenticate(self):
        """Authenticate and get token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    self.log_result("Authentication", "/api/auth/login", "POST", True, 200, "Successfully authenticated")
                    return True
                else:
                    self.log_result("Authentication", "/api/auth/login", "POST", False, 200, "No token in response")
                    return False
            else:
                self.log_result("Authentication", "/api/auth/login", "POST", False, response.status_code, f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", "/api/auth/login", "POST", False, None, f"Exception: {str(e)}")
            return False

    def test_workspace_creation_endpoint(self):
        """Test POST /api/workspace endpoint"""
        print("\n=== TESTING WORKSPACE CREATION ENDPOINT ===")
        
        # Test 1: Health check
        try:
            response = requests.get(f"{self.base_url}/api/workspace/health", headers=self.headers)
            success = response.status_code == 200
            details = f"Health check response: {response.text[:200]}"
            self.log_result("Workspace API", "/api/workspace/health", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Workspace API", "/api/workspace/health", "GET", False, None, f"Exception: {str(e)}")

        # Test 2: Create workspace with onboarding data structure
        workspace_data = {
            "name": "My Business Workspace",
            "industry": "technology",
            "team_size": "1-5",
            "description": "A workspace for my tech startup",
            "business_type": "startup",
            "goals": ["increase_sales", "improve_marketing", "automate_workflows"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/workspace/", json=workspace_data, headers=self.headers)
            success = response.status_code in [200, 201]
            details = f"Workspace creation response: {response.text[:300]}"
            self.log_result("Workspace API", "/api/workspace/", "POST", success, response.status_code, details)
            
            if success:
                workspace_response = response.json()
                print(f"✅ Workspace created successfully: {json.dumps(workspace_response, indent=2)}")
                return workspace_response.get("data", {}).get("workspace_id")
            else:
                print(f"❌ Workspace creation failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Workspace API", "/api/workspace/", "POST", False, None, f"Exception: {str(e)}")
            return None

    def test_complete_onboarding_endpoint(self):
        """Test POST /api/complete_onboarding endpoint"""
        print("\n=== TESTING COMPLETE ONBOARDING ENDPOINT ===")
        
        # Test 1: Health check
        try:
            response = requests.get(f"{self.base_url}/api/complete-onboarding/health", headers=self.headers)
            success = response.status_code == 200
            details = f"Health check response: {response.text[:200]}"
            self.log_result("Complete Onboarding API", "/api/complete-onboarding/health", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Complete Onboarding API", "/api/complete-onboarding/health", "GET", False, None, f"Exception: {str(e)}")

        # Test 2: Complete onboarding with full data structure
        onboarding_data = {
            "workspace": {
                "name": "Complete Business Setup",
                "industry": "ecommerce",
                "team_size": "6-20"
            },
            "business_goals": ["increase_sales", "improve_customer_service", "expand_online_presence"],
            "selected_bundles": ["creator", "ecommerce"],
            "payment_method": "monthly",
            "user_preferences": {
                "notifications": True,
                "marketing_emails": True,
                "analytics_tracking": True
            },
            "onboarding_step": "completed"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/complete-onboarding/", json=onboarding_data, headers=self.headers)
            success = response.status_code in [200, 201]
            details = f"Onboarding completion response: {response.text[:300]}"
            self.log_result("Complete Onboarding API", "/api/complete-onboarding/", "POST", success, response.status_code, details)
            
            if success:
                onboarding_response = response.json()
                print(f"✅ Onboarding completed successfully: {json.dumps(onboarding_response, indent=2)}")
                return onboarding_response
            else:
                print(f"❌ Onboarding completion failed: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Complete Onboarding API", "/api/complete-onboarding/", "POST", False, None, f"Exception: {str(e)}")
            return None

    def test_workspace_subscription_endpoints(self):
        """Test workspace subscription endpoints for bundle selection"""
        print("\n=== TESTING WORKSPACE SUBSCRIPTION ENDPOINTS ===")
        
        # Test 1: Health check
        try:
            response = requests.get(f"{self.base_url}/api/workspace-subscription/health", headers=self.headers)
            success = response.status_code == 200
            details = f"Health check response: {response.text[:200]}"
            self.log_result("Workspace Subscription API", "/api/workspace-subscription/health", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Workspace Subscription API", "/api/workspace-subscription/health", "GET", False, None, f"Exception: {str(e)}")

        # Test 2: Get bundle information
        try:
            response = requests.get(f"{self.base_url}/api/workspace-subscription/bundles", headers=self.headers)
            success = response.status_code == 200
            details = f"Bundle info response: {response.text[:300]}"
            self.log_result("Workspace Subscription API", "/api/workspace-subscription/bundles", "GET", success, response.status_code, details)
            
            if success:
                bundles_response = response.json()
                print(f"✅ Available bundles: {json.dumps(bundles_response, indent=2)}")
        except Exception as e:
            self.log_result("Workspace Subscription API", "/api/workspace-subscription/bundles", "GET", False, None, f"Exception: {str(e)}")

        # Test 3: Get pricing information
        try:
            response = requests.get(f"{self.base_url}/api/workspace-subscription/pricing", headers=self.headers)
            success = response.status_code == 200
            details = f"Pricing info response: {response.text[:300]}"
            self.log_result("Workspace Subscription API", "/api/workspace-subscription/pricing", "GET", success, response.status_code, details)
            
            if success:
                pricing_response = response.json()
                print(f"✅ Pricing information: {json.dumps(pricing_response, indent=2)}")
        except Exception as e:
            self.log_result("Workspace Subscription API", "/api/workspace-subscription/pricing", "GET", False, None, f"Exception: {str(e)}")

        # Test 4: Create workspace subscription with bundle selection
        workspace_id = "test-workspace-123"  # Using test ID
        subscription_data = {
            "selected_bundles": ["creator", "social_media"],
            "billing_cycle": "monthly",
            "payment_method": "stripe",
            "auto_renew": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/workspace-subscription/workspace/{workspace_id}/subscription",
                json=subscription_data,
                headers=self.headers
            )
            success = response.status_code in [200, 201]
            details = f"Subscription creation response: {response.text[:300]}"
            self.log_result("Workspace Subscription API", f"/api/workspace-subscription/workspace/{workspace_id}/subscription", "POST", success, response.status_code, details)
            
            if success:
                subscription_response = response.json()
                print(f"✅ Workspace subscription created: {json.dumps(subscription_response, indent=2)}")
        except Exception as e:
            self.log_result("Workspace Subscription API", f"/api/workspace-subscription/workspace/{workspace_id}/subscription", "POST", False, None, f"Exception: {str(e)}")

    def test_authentication_requirements(self):
        """Test authentication requirements for onboarding endpoints"""
        print("\n=== TESTING AUTHENTICATION REQUIREMENTS ===")
        
        # Save current auth headers
        original_headers = self.headers.copy()
        
        # Test without authentication
        no_auth_headers = {"Content-Type": "application/json"}
        
        endpoints_to_test = [
            ("/api/workspace/", "POST"),
            ("/api/complete-onboarding/", "POST"),
            ("/api/workspace-subscription/health", "GET"),
            ("/api/workspace-subscription/bundles", "GET"),
            ("/api/workspace-subscription/pricing", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=no_auth_headers)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json={}, headers=no_auth_headers)
                
                # Check if endpoint requires authentication (401/403) or is public (200)
                requires_auth = response.status_code in [401, 403]
                is_public = response.status_code == 200
                
                if requires_auth:
                    details = f"Endpoint requires authentication (status: {response.status_code})"
                    self.log_result("Auth Requirements", endpoint, method, True, response.status_code, details)
                elif is_public:
                    details = f"Endpoint is publicly accessible (status: {response.status_code})"
                    self.log_result("Auth Requirements", endpoint, method, True, response.status_code, details)
                else:
                    details = f"Unexpected response (status: {response.status_code}): {response.text[:200]}"
                    self.log_result("Auth Requirements", endpoint, method, False, response.status_code, details)
                    
            except Exception as e:
                self.log_result("Auth Requirements", endpoint, method, False, None, f"Exception: {str(e)}")
        
        # Restore auth headers
        self.headers = original_headers

    def test_data_format_validation(self):
        """Test expected data formats for successful integration"""
        print("\n=== TESTING DATA FORMAT VALIDATION ===")
        
        # Test workspace creation with various data formats
        test_cases = [
            {
                "name": "minimal_data",
                "data": {"name": "Test Workspace"},
                "expected": "Should work with minimal data"
            },
            {
                "name": "complete_onboarding_format",
                "data": {
                    "name": "Complete Workspace",
                    "industry": "technology",
                    "team_size": "1-5",
                    "business_goals": ["increase_sales", "improve_marketing"],
                    "selected_bundles": ["creator", "business"],
                    "payment_method": "monthly"
                },
                "expected": "Should work with complete onboarding data"
            },
            {
                "name": "invalid_data",
                "data": {"invalid_field": "test"},
                "expected": "Should handle invalid data gracefully"
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/workspace/",
                    json=test_case["data"],
                    headers=self.headers
                )
                
                success = response.status_code in [200, 201, 400]  # 400 is acceptable for invalid data
                details = f"{test_case['expected']} - Status: {response.status_code}, Response: {response.text[:200]}"
                self.log_result("Data Format Validation", "/api/workspace/", "POST", success, response.status_code, details)
                
            except Exception as e:
                self.log_result("Data Format Validation", "/api/workspace/", "POST", False, None, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run all onboarding and workspace creation tests"""
        print("🚀 STARTING ONBOARDING AND WORKSPACE CREATION API TESTING")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Step 2: Test workspace creation endpoint
        workspace_id = self.test_workspace_creation_endpoint()
        
        # Step 3: Test complete onboarding endpoint
        self.test_complete_onboarding_endpoint()
        
        # Step 4: Test workspace subscription endpoints
        self.test_workspace_subscription_endpoints()
        
        # Step 5: Test authentication requirements
        self.test_authentication_requirements()
        
        # Step 6: Test data format validation
        self.test_data_format_validation()
        
        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 80)
        print("📊 ONBOARDING AND WORKSPACE CREATION API TEST SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        print("\n📋 DETAILED FINDINGS:")
        print("-" * 40)
        
        # Group results by system
        systems = {}
        for result in self.test_results:
            system = result["system"]
            if system not in systems:
                systems[system] = {"passed": 0, "failed": 0, "details": []}
            
            if result["success"]:
                systems[system]["passed"] += 1
            else:
                systems[system]["failed"] += 1
            
            systems[system]["details"].append({
                "endpoint": result["endpoint"],
                "method": result["method"],
                "success": result["success"],
                "status_code": result["status_code"],
                "details": result["details"]
            })
        
        for system, data in systems.items():
            total = data["passed"] + data["failed"]
            success_rate = (data["passed"] / total * 100) if total > 0 else 0
            print(f"\n🔧 {system}: {data['passed']}/{total} ({success_rate:.1f}%)")
            
            for detail in data["details"]:
                status = "✅" if detail["success"] else "❌"
                print(f"  {status} {detail['method']} {detail['endpoint']} ({detail['status_code']}) - {detail['details'][:100]}")
        
        print("\n🎯 KEY FINDINGS FOR FRONTEND INTEGRATION:")
        print("-" * 50)
        
        # Analyze authentication requirements
        auth_results = [r for r in self.test_results if r["system"] == "Auth Requirements"]
        public_endpoints = [r for r in auth_results if "publicly accessible" in r["details"]]
        protected_endpoints = [r for r in auth_results if "requires authentication" in r["details"]]
        
        print(f"📝 Authentication Analysis:")
        print(f"  - Public endpoints: {len(public_endpoints)}")
        print(f"  - Protected endpoints: {len(protected_endpoints)}")
        
        # Analyze workspace creation
        workspace_results = [r for r in self.test_results if r["system"] == "Workspace API" and r["method"] == "POST"]
        workspace_success = any(r["success"] for r in workspace_results)
        print(f"🏢 Workspace Creation: {'✅ Working' if workspace_success else '❌ Issues detected'}")
        
        # Analyze onboarding completion
        onboarding_results = [r for r in self.test_results if r["system"] == "Complete Onboarding API" and r["method"] == "POST"]
        onboarding_success = any(r["success"] for r in onboarding_results)
        print(f"🎯 Onboarding Completion: {'✅ Working' if onboarding_success else '❌ Issues detected'}")
        
        # Analyze subscription system
        subscription_results = [r for r in self.test_results if r["system"] == "Workspace Subscription API"]
        subscription_health = any(r["success"] for r in subscription_results if "health" in r["endpoint"])
        print(f"💳 Subscription System: {'✅ Available' if subscription_health else '❌ Issues detected'}")
        
        print("\n📋 RECOMMENDATIONS FOR FRONTEND DEVELOPMENT:")
        print("-" * 55)
        print("1. Use authenticated requests for workspace creation and onboarding")
        print("2. Include complete data structure with workspace, goals, and bundles")
        print("3. Handle both success and error responses appropriately")
        print("4. Implement proper error handling for authentication failures")
        print("5. Test with various data formats to ensure robustness")

if __name__ == "__main__":
    tester = OnboardingWorkspaceAPITester()
    tester.run_comprehensive_test()