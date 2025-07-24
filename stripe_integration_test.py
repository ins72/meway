#!/usr/bin/env python3
"""
STRIPE INTEGRATION BACKEND TESTING
==================================
Testing Stripe integration backend to diagnose 400 error reported by user.
Specific focus on:
1. Health check endpoint
2. Checkout session creation
3. Payment confirmation
4. Error diagnosis

Test credentials: tmonnens@outlook.com / Voetballen5
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://3dc4dc3c-9195-4a26-87f6-3f23beffd557.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class StripeIntegrationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_result(self, system: str, endpoint: str, method: str, success: bool, status_code: int = None, details: str = "", response_data: dict = None):
        """Log test result with detailed information"""
        result = {
            "system": system,
            "endpoint": endpoint,
            "method": method,
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
            print(f"✅ {system} - {method} {endpoint} - Status {status_code}")
            if details:
                print(f"   📝 {details}")
        else:
            self.failed_tests += 1
            print(f"❌ {system} - {method} {endpoint} - Status {status_code} - {details}")
            if response_data:
                print(f"   📄 Response: {json.dumps(response_data, indent=2)}")
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            print(f"\n🔐 AUTHENTICATING WITH {TEST_EMAIL}")
            print("=" * 60)
            
            # Try login first
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✅ Login successful - Token received")
                self.log_result("Authentication", "/api/auth/login", "POST", True, 200, "Login successful")
                return True
            elif response.status_code == 401:
                # Try registration if login fails
                print("🔄 Login failed, attempting registration...")
                register_data = {
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "full_name": "Test User"
                }
                
                reg_response = requests.post(
                    f"{self.base_url}/api/auth/register",
                    json=register_data,
                    headers=self.headers,
                    timeout=30
                )
                
                if reg_response.status_code == 200:
                    data = reg_response.json()
                    self.token = data.get("access_token")
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    print(f"✅ Registration successful - Token received")
                    self.log_result("Authentication", "/api/auth/register", "POST", True, 200, "Registration successful")
                    return True
                else:
                    print(f"❌ Registration failed - Status {reg_response.status_code}")
                    self.log_result("Authentication", "/api/auth/register", "POST", False, reg_response.status_code, "Registration failed", reg_response.json() if reg_response.content else None)
                    return False
            else:
                print(f"❌ Authentication failed - Status {response.status_code}")
                self.log_result("Authentication", "/api/auth/login", "POST", False, response.status_code, "Authentication failed", response.json() if response.content else None)
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            self.log_result("Authentication", "/api/auth/login", "POST", False, 0, str(e))
            return False
    
    def test_stripe_health_check(self):
        """Test Stripe integration health check"""
        print(f"\n🏥 TESTING STRIPE INTEGRATION HEALTH CHECK")
        print("=" * 60)
        
        try:
            response = requests.get(f"{self.base_url}/api/stripe-integration/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                details = f"Healthy: {data.get('healthy', False)}, Stripe Connected: {data.get('stripe_connected', False)}"
                self.log_result("Stripe Integration", "/api/stripe-integration/health", "GET", True, 200, details, data)
            else:
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text}
                self.log_result("Stripe Integration", "/api/stripe-integration/health", "GET", False, response.status_code, "Health check failed", error_data)
                
        except Exception as e:
            self.log_result("Stripe Integration", "/api/stripe-integration/health", "GET", False, 0, str(e))
    
    def test_stripe_checkout_session_creation(self):
        """Test Stripe checkout session creation with the exact data from review request"""
        print(f"\n💳 TESTING STRIPE CHECKOUT SESSION CREATION")
        print("=" * 60)
        
        # Test data from review request
        test_data = {
            "bundles": ["creator", "ecommerce"],
            "workspace_name": "Test Workspace",
            "payment_method": "monthly"
        }
        
        try:
            print(f"📤 Sending request with data: {json.dumps(test_data, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/api/stripe-integration/create-checkout-session",
                json=test_data,
                headers=self.headers,
                timeout=30
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                details = f"Session created successfully. Session ID: {data.get('session_id', 'N/A')}"
                self.log_result("Stripe Integration", "/api/stripe-integration/create-checkout-session", "POST", True, 200, details, data)
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    details = f"400 ERROR IDENTIFIED: {error_data.get('detail', 'Unknown error')}"
                    self.log_result("Stripe Integration", "/api/stripe-integration/create-checkout-session", "POST", False, 400, details, error_data)
                    print(f"🚨 400 ERROR DETAILS: {json.dumps(error_data, indent=2)}")
                except:
                    error_text = response.text
                    details = f"400 ERROR: {error_text}"
                    self.log_result("Stripe Integration", "/api/stripe-integration/create-checkout-session", "POST", False, 400, details, {"raw_response": error_text})
                    print(f"🚨 400 ERROR RAW RESPONSE: {error_text}")
            else:
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text}
                details = f"Checkout session creation failed with status {response.status_code}"
                self.log_result("Stripe Integration", "/api/stripe-integration/create-checkout-session", "POST", False, response.status_code, details, error_data)
                
        except Exception as e:
            self.log_result("Stripe Integration", "/api/stripe-integration/create-checkout-session", "POST", False, 0, str(e))
    
    def test_stripe_payment_confirmation(self):
        """Test Stripe payment confirmation"""
        print(f"\n✅ TESTING STRIPE PAYMENT CONFIRMATION")
        print("=" * 60)
        
        # Test payment confirmation data
        test_data = {
            "paymentMethodId": "pm_test_1234567890",
            "workspace_name": "Test Workspace",
            "bundles": ["creator", "ecommerce"]
        }
        
        try:
            print(f"📤 Sending payment confirmation with data: {json.dumps(test_data, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/api/stripe-integration/confirm-payment",
                json=test_data,
                headers=self.headers,
                timeout=30
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                details = f"Payment confirmed successfully"
                self.log_result("Stripe Integration", "/api/stripe-integration/confirm-payment", "POST", True, 200, details, data)
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    details = f"400 ERROR: {error_data.get('detail', 'Unknown error')}"
                    self.log_result("Stripe Integration", "/api/stripe-integration/confirm-payment", "POST", False, 400, details, error_data)
                    print(f"🚨 400 ERROR DETAILS: {json.dumps(error_data, indent=2)}")
                except:
                    error_text = response.text
                    details = f"400 ERROR: {error_text}"
                    self.log_result("Stripe Integration", "/api/stripe-integration/confirm-payment", "POST", False, 400, details, {"raw_response": error_text})
            else:
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text}
                details = f"Payment confirmation failed with status {response.status_code}"
                self.log_result("Stripe Integration", "/api/stripe-integration/confirm-payment", "POST", False, response.status_code, details, error_data)
                
        except Exception as e:
            self.log_result("Stripe Integration", "/api/stripe-integration/confirm-payment", "POST", False, 0, str(e))
    
    def test_stripe_direct_api(self):
        """Test direct Stripe API connectivity"""
        print(f"\n🔗 TESTING DIRECT STRIPE API CONNECTIVITY")
        print("=" * 60)
        
        try:
            # Test creating a simple Stripe customer using the test keys
            stripe_secret_key = "sk_test_51RHeZMPTey8qEzxZn2t4XbP6CATdXVbcgbzvSjdVIsijehuscfcSOVQ016bUXsVaBV9MyoI8EThIBTgmXSjDUs6n00ipAjYRXZ"
            
            headers = {
                'Authorization': f'Bearer {stripe_secret_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Test data for Stripe customer creation
            stripe_data = {
                'email': 'test@example.com',
                'name': 'Test Customer',
                'description': 'Test customer for Stripe API verification'
            }
            
            print(f"📤 Testing direct Stripe API call...")
            
            response = requests.post(
                'https://api.stripe.com/v1/customers',
                headers=headers,
                data=stripe_data,
                timeout=30
            )
            
            print(f"📥 Stripe API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                details = f"Stripe API working. Customer ID: {data.get('id', 'N/A')}"
                self.log_result("Direct Stripe API", "https://api.stripe.com/v1/customers", "POST", True, 200, details, {"customer_id": data.get('id')})
            else:
                try:
                    error_data = response.json()
                    details = f"Stripe API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    self.log_result("Direct Stripe API", "https://api.stripe.com/v1/customers", "POST", False, response.status_code, details, error_data)
                    print(f"🚨 STRIPE API ERROR: {json.dumps(error_data, indent=2)}")
                except:
                    error_text = response.text
                    details = f"Stripe API error: {error_text}"
                    self.log_result("Direct Stripe API", "https://api.stripe.com/v1/customers", "POST", False, response.status_code, details, {"raw_response": error_text})
                
        except Exception as e:
            self.log_result("Direct Stripe API", "https://api.stripe.com/v1/customers", "POST", False, 0, str(e))
    
    def test_backend_logs_analysis(self):
        """Analyze backend logs for Stripe-related errors"""
        print(f"\n📋 ANALYZING BACKEND LOGS FOR STRIPE ERRORS")
        print("=" * 60)
        
        try:
            # Check if we can access any log endpoints
            log_endpoints = [
                "/api/logs",
                "/api/system/logs", 
                "/api/admin/logs"
            ]
            
            for endpoint in log_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        print(f"✅ Found log endpoint: {endpoint}")
                        # Look for Stripe-related errors in logs
                        data = response.json()
                        # This would need to be implemented based on actual log structure
                        break
                except:
                    continue
            else:
                print("ℹ️  No accessible log endpoints found - this is expected")
                
        except Exception as e:
            print(f"ℹ️  Log analysis not available: {e}")
    
    def run_comprehensive_test(self):
        """Run all Stripe integration tests"""
        print("🚀 STARTING COMPREHENSIVE STRIPE INTEGRATION TEST")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test Stripe health check
        self.test_stripe_health_check()
        
        # Step 3: Test checkout session creation (main focus)
        self.test_stripe_checkout_session_creation()
        
        # Step 4: Test payment confirmation
        self.test_stripe_payment_confirmation()
        
        # Step 5: Test direct Stripe API
        self.test_stripe_direct_api()
        
        # Step 6: Analyze logs
        self.test_backend_logs_analysis()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 STRIPE INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        print(f"📊 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/max(self.total_tests,1)*100):.1f}%")
        
        print("\n🔍 DETAILED RESULTS:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['system']} - {result['method']} {result['endpoint']}")
            if result["details"]:
                print(f"   📝 {result['details']}")
            if not result["success"] and result["response_data"]:
                print(f"   📄 Error Data: {json.dumps(result['response_data'], indent=6)}")
        
        # Specific 400 error analysis
        print("\n🚨 400 ERROR ANALYSIS:")
        print("-" * 40)
        
        error_400_found = False
        for result in self.test_results:
            if result["status_code"] == 400:
                error_400_found = True
                print(f"❌ 400 Error in {result['system']} - {result['endpoint']}")
                print(f"   📝 Details: {result['details']}")
                if result["response_data"]:
                    print(f"   📄 Response: {json.dumps(result['response_data'], indent=6)}")
        
        if not error_400_found:
            print("ℹ️  No 400 errors detected in this test run")
        
        print("\n🎯 RECOMMENDATIONS:")
        print("-" * 40)
        
        if self.failed_tests == 0:
            print("✅ All tests passed - Stripe integration appears to be working correctly")
        else:
            print("❌ Issues detected - see detailed results above for specific problems")
            print("🔧 Recommended actions:")
            print("   1. Check Stripe API key configuration")
            print("   2. Verify request data format matches expected schema")
            print("   3. Check authentication token validity")
            print("   4. Review backend logs for detailed error messages")

if __name__ == "__main__":
    tester = StripeIntegrationTester()
    tester.run_comprehensive_test()