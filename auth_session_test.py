#!/usr/bin/env python3
"""
AUTHENTICATION SESSION PERSISTENCE TEST
======================================
Focused testing for session persistence and tab navigation issues.
Testing the specific user report: "getting logged out when navigating between tabs"

Test Plan:
1. Login flow with valid credentials (test@example.com / password123)
2. Test the /api/auth/me endpoint multiple times to check for consistency
3. Test token validation and see if there are any 401 responses happening unexpectedly
4. Check if the JWT tokens are valid and not expiring prematurely
5. Look for any authentication issues that could cause session drops
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import jwt as jwt_lib

# Configuration
BACKEND_URL = "https://b2614b52-973e-4c52-9dec-e3ec14470901.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class AuthSessionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, test_name: str, success: bool, status_code: int = None, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "status_code": status_code,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: {details}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {details}")
            
    def decode_jwt_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token without verification to inspect contents"""
        try:
            # Decode without verification to inspect token contents
            decoded = jwt_lib.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            return {"error": str(e)}
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        print(f"\n🔐 AUTHENTICATION TEST")
        print(f"Testing login with: {TEST_EMAIL}")
        
        try:
            # Try login first
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.token}"
                
                # Decode and inspect token
                token_info = self.decode_jwt_token(self.token)
                
                self.log_result(
                    "Login Authentication", 
                    True, 
                    200, 
                    f"Login successful - Token received (expires: {token_info.get('exp', 'unknown')})",
                    {
                        "token_length": len(self.token),
                        "token_info": token_info,
                        "user_data": data.get("user", {})
                    }
                )
                return True
            else:
                # Log the login failure details
                print(f"🔄 Login failed with status {response.status_code}: {response.text}")
                self.log_result("Login Authentication", False, response.status_code, f"Login failed: {response.text}")
                
                # Try registration if login fails
                print("🔄 Attempting registration...")
                register_data = {
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "full_name": "Test User"
                }
                
                reg_response = requests.post(
                    f"{self.base_url}/api/auth/register",
                    json=register_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if reg_response.status_code == 200:
                    data = reg_response.json()
                    self.token = data.get("access_token")
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    
                    # Decode and inspect token
                    token_info = self.decode_jwt_token(self.token)
                    
                    self.log_result(
                        "Registration Authentication", 
                        True, 
                        200, 
                        f"Registration successful - Token received (expires: {token_info.get('exp', 'unknown')})",
                        {
                            "token_length": len(self.token),
                            "token_info": token_info,
                            "user_data": data.get("user", {})
                        }
                    )
                    return True
                else:
                    self.log_result("Registration Authentication", False, reg_response.status_code, f"Registration failed: {reg_response.text}")
                    return False
        except Exception as e:
            self.log_result("Authentication", False, 0, f"Authentication error: {str(e)}")
            return False
    
    def test_auth_me_endpoint_consistency(self):
        """Test /api/auth/me endpoint multiple times for consistency"""
        print(f"\n🔍 TESTING /api/auth/me ENDPOINT CONSISTENCY")
        
        if not self.token:
            self.log_result("Auth Me Consistency", False, 0, "No token available for testing")
            return
        
        # Test the endpoint multiple times
        test_count = 5
        successful_calls = 0
        responses = []
        
        for i in range(test_count):
            try:
                response = requests.get(
                    f"{self.base_url}/api/auth/me",
                    headers=self.headers,
                    timeout=30
                )
                
                responses.append({
                    "attempt": i + 1,
                    "status_code": response.status_code,
                    "response_data": response.json() if response.status_code == 200 else response.text,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                if response.status_code == 200:
                    successful_calls += 1
                    print(f"  ✅ Attempt {i + 1}: Success (200)")
                else:
                    print(f"  ❌ Attempt {i + 1}: Failed ({response.status_code}) - {response.text}")
                
                # Small delay between calls to simulate tab switching
                time.sleep(0.5)
                
            except Exception as e:
                responses.append({
                    "attempt": i + 1,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                print(f"  ❌ Attempt {i + 1}: Exception - {str(e)}")
        
        success_rate = (successful_calls / test_count) * 100
        
        self.log_result(
            "Auth Me Endpoint Consistency",
            successful_calls == test_count,
            200 if successful_calls == test_count else 401,
            f"Success rate: {success_rate}% ({successful_calls}/{test_count})",
            responses
        )
    
    def test_token_validation_stress(self):
        """Test token validation under stress conditions"""
        print(f"\n⚡ TOKEN VALIDATION STRESS TEST")
        
        if not self.token:
            self.log_result("Token Validation Stress", False, 0, "No token available for testing")
            return
        
        # Test multiple endpoints rapidly to simulate tab switching
        endpoints = [
            "/api/auth/me",
            "/api/auth/profile",
            "/api/auth/health"
        ]
        
        total_calls = 0
        successful_calls = 0
        failed_calls = []
        
        for endpoint in endpoints:
            for i in range(3):  # 3 calls per endpoint
                try:
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        timeout=30
                    )
                    
                    total_calls += 1
                    
                    if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                        successful_calls += 1
                        print(f"  ✅ {endpoint} (attempt {i + 1}): {response.status_code}")
                    else:
                        failed_calls.append({
                            "endpoint": endpoint,
                            "attempt": i + 1,
                            "status_code": response.status_code,
                            "response": response.text
                        })
                        print(f"  ❌ {endpoint} (attempt {i + 1}): {response.status_code} - {response.text}")
                    
                    # Very short delay to simulate rapid tab switching
                    time.sleep(0.1)
                    
                except Exception as e:
                    total_calls += 1
                    failed_calls.append({
                        "endpoint": endpoint,
                        "attempt": i + 1,
                        "error": str(e)
                    })
                    print(f"  ❌ {endpoint} (attempt {i + 1}): Exception - {str(e)}")
        
        success_rate = (successful_calls / total_calls) * 100
        
        self.log_result(
            "Token Validation Stress Test",
            len(failed_calls) == 0,
            200 if len(failed_calls) == 0 else 401,
            f"Success rate: {success_rate}% ({successful_calls}/{total_calls})",
            {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls
            }
        )
    
    def test_token_expiration_check(self):
        """Check if JWT token has proper expiration settings"""
        print(f"\n⏰ TOKEN EXPIRATION CHECK")
        
        if not self.token:
            self.log_result("Token Expiration Check", False, 0, "No token available for testing")
            return
        
        try:
            # Decode token to check expiration
            token_info = self.decode_jwt_token(self.token)
            
            if "exp" in token_info:
                exp_timestamp = token_info["exp"]
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                current_time = datetime.utcnow()
                time_until_expiry = exp_datetime - current_time
                
                # Check if token expires in reasonable time (should be 24 hours = 1440 minutes)
                expected_expiry_hours = 24
                actual_expiry_hours = time_until_expiry.total_seconds() / 3600
                
                is_reasonable_expiry = 20 <= actual_expiry_hours <= 26  # Allow some variance
                
                self.log_result(
                    "Token Expiration Check",
                    is_reasonable_expiry,
                    200,
                    f"Token expires in {actual_expiry_hours:.2f} hours (expected ~{expected_expiry_hours}h)",
                    {
                        "exp_timestamp": exp_timestamp,
                        "exp_datetime": exp_datetime.isoformat(),
                        "current_time": current_time.isoformat(),
                        "hours_until_expiry": actual_expiry_hours,
                        "is_reasonable": is_reasonable_expiry
                    }
                )
            else:
                self.log_result("Token Expiration Check", False, 0, "No expiration field found in token", token_info)
                
        except Exception as e:
            self.log_result("Token Expiration Check", False, 0, f"Error checking token expiration: {str(e)}")
    
    def test_session_persistence_simulation(self):
        """Simulate tab navigation scenario"""
        print(f"\n🔄 SESSION PERSISTENCE SIMULATION (Tab Navigation)")
        
        if not self.token:
            self.log_result("Session Persistence Simulation", False, 0, "No token available for testing")
            return
        
        # Simulate user behavior: login, then navigate between different pages/tabs
        navigation_sequence = [
            ("Dashboard", "/api/auth/me"),
            ("User Info", "/api/auth/me"),  # Simulate checking user info again
            ("Back to Dashboard", "/api/auth/me"),
            ("Settings Check", "/api/auth/me"),  # Using /me as proxy for settings check
            ("Another Tab", "/api/auth/me"),
        ]
        
        successful_navigations = 0
        navigation_results = []
        
        for step, (page_name, endpoint) in enumerate(navigation_sequence):
            try:
                # Add delay to simulate user thinking/navigation time
                time.sleep(1)
                
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=30
                )
                
                navigation_result = {
                    "step": step + 1,
                    "page": page_name,
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                if response.status_code == 200:
                    successful_navigations += 1
                    print(f"  ✅ Step {step + 1}: {page_name} - Success")
                    navigation_result["user_data"] = response.json()
                else:
                    print(f"  ❌ Step {step + 1}: {page_name} - Failed ({response.status_code})")
                    navigation_result["error"] = response.text
                
                navigation_results.append(navigation_result)
                
            except Exception as e:
                navigation_result = {
                    "step": step + 1,
                    "page": page_name,
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False,
                    "timestamp": datetime.utcnow().isoformat()
                }
                navigation_results.append(navigation_result)
                print(f"  ❌ Step {step + 1}: {page_name} - Exception: {str(e)}")
        
        success_rate = (successful_navigations / len(navigation_sequence)) * 100
        
        self.log_result(
            "Session Persistence Simulation",
            successful_navigations == len(navigation_sequence),
            200 if successful_navigations == len(navigation_sequence) else 401,
            f"Navigation success rate: {success_rate}% ({successful_navigations}/{len(navigation_sequence)})",
            navigation_results
        )
    
    def run_comprehensive_auth_test(self):
        """Run all authentication session tests"""
        print("=" * 80)
        print("🔐 AUTHENTICATION SESSION PERSISTENCE TEST SUITE")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Test Time: {datetime.utcnow().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with session tests")
            return self.generate_report()
        
        # Step 2: Test /api/auth/me endpoint consistency
        self.test_auth_me_endpoint_consistency()
        
        # Step 3: Test token validation under stress
        self.test_token_validation_stress()
        
        # Step 4: Check token expiration settings
        self.test_token_expiration_check()
        
        # Step 5: Simulate tab navigation scenario
        self.test_session_persistence_simulation()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 AUTHENTICATION SESSION TEST REPORT")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test_name']}: {result['details']}")
        
        print("\n🔍 ANALYSIS:")
        
        # Check for specific session persistence issues
        auth_me_results = [r for r in self.test_results if "Auth Me" in r["test_name"]]
        if auth_me_results:
            auth_me_result = auth_me_results[0]
            if not auth_me_result["success"]:
                print("⚠️  CRITICAL ISSUE: /api/auth/me endpoint inconsistency detected")
                print("   This could cause users to appear logged out when switching tabs")
        
        # Check token validation issues
        token_stress_results = [r for r in self.test_results if "Token Validation Stress" in r["test_name"]]
        if token_stress_results:
            stress_result = token_stress_results[0]
            if not stress_result["success"]:
                print("⚠️  CRITICAL ISSUE: Token validation failures under stress")
                print("   This could cause authentication to fail during rapid tab switching")
        
        # Check session persistence simulation
        session_results = [r for r in self.test_results if "Session Persistence" in r["test_name"]]
        if session_results:
            session_result = session_results[0]
            if not session_result["success"]:
                print("⚠️  CRITICAL ISSUE: Session persistence failures detected")
                print("   This directly matches the user's reported issue with tab navigation")
        
        # Overall assessment
        if self.failed_tests == 0:
            print("\n✅ OVERALL ASSESSMENT: Authentication system appears stable for session persistence")
        elif self.failed_tests <= 2:
            print("\n⚠️  OVERALL ASSESSMENT: Minor authentication issues detected - investigate further")
        else:
            print("\n❌ OVERALL ASSESSMENT: Significant authentication issues - immediate attention required")
        
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0,
            "test_results": self.test_results
        }

if __name__ == "__main__":
    tester = AuthSessionTester()
    report = tester.run_comprehensive_auth_test()
    
    # Exit with appropriate code
    sys.exit(0 if report["failed_tests"] == 0 else 1)