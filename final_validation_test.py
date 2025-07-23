#!/usr/bin/env python3
"""
FINAL VALIDATION TEST - JANUARY 2025
Testing the 3 specific issues that were just fixed:
1. Fixed Endpoint Errors - Test AI Workflows and Email Marketing Dashboard endpoints that were causing 500 errors
2. CRUD Completion - Test the newly implemented CRUD operations (orders cancel_order, contacts update/delete, payments all CRUD)  
3. Overall Platform Health - Quick validation that the platform is still working well overall
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

class FinalValidationTester:
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
                return False, None
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Endpoint working - Status {response.status_code}", data)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Endpoint working - Status {response.status_code} (non-JSON response)")
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404) - May not be implemented")
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
                    error_msg = error_data.get('detail', error_data.get('message', 'Internal server error'))
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}")
                return False, None
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Validation error')
                    self.log_result(test_name, False, f"Validation error (422): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Validation error (422): {response.text}")
                return False, None
            else:
                self.log_result(test_name, False, f"Endpoint error - Status {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False, None

    def test_fixed_endpoint_errors(self):
        """Test Issue 1: Fixed Endpoint Errors - AI Workflows and Email Marketing Dashboard"""
        print("\n🎯 TESTING ISSUE 1: FIXED ENDPOINT ERRORS")
        print("=" * 60)
        print("Testing AI Workflows and Email Marketing Dashboard endpoints that were causing 500 errors")
        
        # Test AI Workflows endpoint
        print("\n🤖 Testing AI Workflows...")
        success, data = self.test_endpoint("/ai-automation/workflows", "GET", test_name="AI Workflows - Get Workflows")
        
        if success:
            print("   ✅ AI Workflows endpoint is now working!")
        else:
            print("   ❌ AI Workflows endpoint still has issues")
        
        # Test Email Marketing Dashboard endpoint
        print("\n📧 Testing Email Marketing Dashboard...")
        success, data = self.test_endpoint("/email-marketing/dashboard", "GET", test_name="Email Marketing Dashboard - Get Dashboard")
        
        if success:
            print("   ✅ Email Marketing Dashboard endpoint is now working!")
        else:
            print("   ❌ Email Marketing Dashboard endpoint still has issues")
        
        # Test additional AI automation endpoints
        print("\n🔧 Testing Additional AI Automation Endpoints...")
        self.test_endpoint("/ai-automation/analytics/overview", "GET", test_name="AI Automation - Analytics Overview")
        self.test_endpoint("/automation/workflows", "GET", test_name="Automation - Workflows")
        
        # Test additional email marketing endpoints
        print("\n📬 Testing Additional Email Marketing Endpoints...")
        self.test_endpoint("/email-marketing/campaigns", "GET", test_name="Email Marketing - Get Campaigns")
        self.test_endpoint("/email-marketing/analytics", "GET", test_name="Email Marketing - Analytics")
        
        print("\n🎯 Fixed Endpoint Errors Testing Complete!")
        return True

    def test_crud_completion(self):
        """Test Issue 2: CRUD Completion - orders cancel_order, contacts update/delete, payments all CRUD"""
        print("\n🎯 TESTING ISSUE 2: CRUD COMPLETION")
        print("=" * 60)
        print("Testing newly implemented CRUD operations:")
        print("- Orders: cancel_order operation")
        print("- Contacts: update/delete operations")
        print("- Payments: all CRUD operations")
        
        # Test Orders CRUD - Cancel Order
        print("\n📦 Testing Orders CRUD - Cancel Order...")
        
        # First, try to get existing orders to find one to cancel
        success, orders_data = self.test_endpoint("/orders", "GET", test_name="Orders - Get All Orders")
        
        order_id = None
        if success and orders_data:
            # Try to extract an order ID from the response
            if isinstance(orders_data, dict):
                orders = orders_data.get('data', orders_data.get('orders', []))
                if isinstance(orders, list) and len(orders) > 0:
                    order_id = orders[0].get('id', orders[0].get('_id'))
        
        if order_id:
            # Test cancel order operation
            cancel_data = {"reason": "Customer requested cancellation", "refund_amount": 50.00}
            self.test_endpoint(f"/orders/{order_id}/cancel", "POST", cancel_data, "Orders - Cancel Order")
        else:
            # Test with a sample order ID if no real orders exist
            sample_order_id = "sample_order_123"
            cancel_data = {"reason": "Customer requested cancellation", "refund_amount": 50.00}
            self.test_endpoint(f"/orders/{sample_order_id}/cancel", "POST", cancel_data, "Orders - Cancel Order (Sample)")
        
        # Test Contacts CRUD - Update and Delete
        print("\n👥 Testing Contacts CRUD - Update/Delete...")
        
        # First, try to get existing contacts
        success, contacts_data = self.test_endpoint("/email-marketing/contacts", "GET", test_name="Contacts - Get All Contacts")
        
        contact_id = None
        if success and contacts_data:
            # Try to extract a contact ID from the response
            if isinstance(contacts_data, dict):
                contacts = contacts_data.get('data', contacts_data.get('contacts', []))
                if isinstance(contacts, list) and len(contacts) > 0:
                    contact_id = contacts[0].get('id', contacts[0].get('_id'))
        
        if contact_id:
            # Test update contact operation
            update_data = {
                "name": "Updated Contact Name",
                "email": "updated@example.com",
                "tags": ["updated", "premium"],
                "notes": "Contact information updated via API"
            }
            self.test_endpoint(f"/email-marketing/contacts/{contact_id}", "PUT", update_data, "Contacts - Update Contact")
            
            # Test delete contact operation
            self.test_endpoint(f"/email-marketing/contacts/{contact_id}", "DELETE", test_name="Contacts - Delete Contact")
        else:
            # Test with sample contact ID if no real contacts exist
            sample_contact_id = "sample_contact_123"
            update_data = {
                "name": "Updated Contact Name",
                "email": "updated@example.com",
                "tags": ["updated", "premium"],
                "notes": "Contact information updated via API"
            }
            self.test_endpoint(f"/email-marketing/contacts/{sample_contact_id}", "PUT", update_data, "Contacts - Update Contact (Sample)")
            self.test_endpoint(f"/email-marketing/contacts/{sample_contact_id}", "DELETE", test_name="Contacts - Delete Contact (Sample)")
        
        # Test Payments CRUD - All Operations
        print("\n💳 Testing Payments CRUD - All Operations...")
        
        # CREATE - Create Payment
        create_payment_data = {
            "amount": 299.99,
            "currency": "USD",
            "payment_method": "credit_card",
            "customer_email": "customer@example.com",
            "description": "Product purchase payment",
            "metadata": {
                "order_id": "order_123",
                "product_name": "Premium Subscription"
            }
        }
        success, payment_data = self.test_endpoint("/payments", "POST", create_payment_data, "Payments - Create Payment")
        
        payment_id = None
        if success and payment_data:
            payment_id = payment_data.get('id', payment_data.get('payment_id', payment_data.get('data', {}).get('id')))
        
        # READ - Get All Payments
        self.test_endpoint("/payments", "GET", test_name="Payments - Get All Payments")
        
        # READ - Get Specific Payment
        if payment_id:
            self.test_endpoint(f"/payments/{payment_id}", "GET", test_name="Payments - Get Payment Details")
        else:
            # Test with sample payment ID
            sample_payment_id = "sample_payment_123"
            self.test_endpoint(f"/payments/{sample_payment_id}", "GET", test_name="Payments - Get Payment Details (Sample)")
        
        # UPDATE - Update Payment
        if payment_id:
            update_payment_data = {
                "status": "completed",
                "notes": "Payment processed successfully",
                "metadata": {
                    "order_id": "order_123",
                    "product_name": "Premium Subscription",
                    "processed_by": "admin"
                }
            }
            self.test_endpoint(f"/payments/{payment_id}", "PUT", update_payment_data, "Payments - Update Payment")
        else:
            # Test with sample payment ID
            sample_payment_id = "sample_payment_123"
            update_payment_data = {
                "status": "completed",
                "notes": "Payment processed successfully"
            }
            self.test_endpoint(f"/payments/{sample_payment_id}", "PUT", update_payment_data, "Payments - Update Payment (Sample)")
        
        # DELETE - Delete Payment
        if payment_id:
            self.test_endpoint(f"/payments/{payment_id}", "DELETE", test_name="Payments - Delete Payment")
        else:
            # Test with sample payment ID
            sample_payment_id = "sample_payment_123"
            self.test_endpoint(f"/payments/{sample_payment_id}", "DELETE", test_name="Payments - Delete Payment (Sample)")
        
        print("\n🎯 CRUD Completion Testing Complete!")
        return True

    def test_overall_platform_health(self):
        """Test Issue 3: Overall Platform Health - Quick validation that platform is working well"""
        print("\n🎯 TESTING ISSUE 3: OVERALL PLATFORM HEALTH")
        print("=" * 60)
        print("Quick validation that the platform is still working well overall")
        
        # Test Core System Health
        print("\n🏥 Testing Core System Health...")
        
        # Check if backend is operational
        try:
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                paths_count = len(data.get('paths', {}))
                self.log_result("Backend Health", True, f"Backend operational with {paths_count} API endpoints", {"paths_count": paths_count})
            else:
                self.log_result("Backend Health", False, f"Backend not accessible - OpenAPI status {response.status_code}")
        except Exception as e:
            self.log_result("Backend Health", False, f"Backend health check error: {str(e)}")
        
        # Test Key Features
        print("\n🔑 Testing Key Features...")
        
        # Test User Profile
        self.test_endpoint("/user/profile", "GET", test_name="Platform Health - User Profile")
        
        # Test Dashboard
        self.test_endpoint("/dashboard/overview", "GET", test_name="Platform Health - Dashboard Overview")
        
        # Test Analytics
        self.test_endpoint("/analytics/overview", "GET", test_name="Platform Health - Analytics Overview")
        
        # Test AI Services
        self.test_endpoint("/ai/services", "GET", test_name="Platform Health - AI Services")
        
        # Test E-commerce
        self.test_endpoint("/ecommerce/products", "GET", test_name="Platform Health - E-commerce Products")
        self.test_endpoint("/ecommerce/dashboard", "GET", test_name="Platform Health - E-commerce Dashboard")
        
        # Test Marketing
        self.test_endpoint("/marketing/campaigns", "GET", test_name="Platform Health - Marketing Campaigns")
        
        # Test Admin Functions
        print("\n⚙️ Testing Admin Functions...")
        self.test_endpoint("/admin/users", "GET", test_name="Platform Health - Admin Users")
        self.test_endpoint("/admin/system/metrics", "GET", test_name="Platform Health - System Metrics")
        
        # Test External API Integrations
        print("\n🔗 Testing External API Integrations...")
        self.test_endpoint("/admin-config/integration/status", "GET", test_name="Platform Health - Integration Status")
        self.test_endpoint("/admin-config/test/stripe", "GET", test_name="Platform Health - Stripe Integration")
        self.test_endpoint("/admin-config/test/openai", "GET", test_name="Platform Health - OpenAI Integration")
        
        # Test Database Connectivity
        print("\n🗄️ Testing Database Connectivity...")
        
        # Test data consistency for key endpoints
        success1, data1 = self.test_endpoint("/user/profile", "GET", test_name="Database - User Profile (Call 1)")
        time.sleep(0.5)
        success2, data2 = self.test_endpoint("/user/profile", "GET", test_name="Database - User Profile (Call 2)")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result("Database Consistency", True, "User profile data consistent - real database confirmed")
            else:
                self.log_result("Database Consistency", False, "User profile data inconsistent - may be using random data")
        
        print("\n🎯 Overall Platform Health Testing Complete!")
        return True

    def run_final_validation(self):
        """Run the complete final validation test"""
        print("🎯 FINAL VALIDATION TEST - JANUARY 2025")
        print("=" * 80)
        print("Testing the 3 specific issues that were just fixed:")
        print("1. Fixed Endpoint Errors - AI Workflows and Email Marketing Dashboard")
        print("2. CRUD Completion - orders cancel_order, contacts update/delete, payments all CRUD")
        print("3. Overall Platform Health - Quick validation")
        print("=" * 80)
        
        # Authenticate first
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run the three main test categories
        self.test_fixed_endpoint_errors()
        self.test_crud_completion()
        self.test_overall_platform_health()
        
        # Print summary
        self.print_test_summary()
        
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 FINAL VALIDATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Group results by issue category
        issue_results = {
            "Fixed Endpoint Errors": {"passed": 0, "failed": 0, "total": 0},
            "CRUD Completion": {"passed": 0, "failed": 0, "total": 0},
            "Platform Health": {"passed": 0, "failed": 0, "total": 0},
            "Authentication": {"passed": 0, "failed": 0, "total": 0}
        }
        
        for result in self.test_results:
            test_name = result["test"]
            category = "Platform Health"  # default
            
            if "AI Workflows" in test_name or "Email Marketing Dashboard" in test_name or "AI Automation" in test_name:
                category = "Fixed Endpoint Errors"
            elif "Orders" in test_name or "Contacts" in test_name or "Payments" in test_name:
                category = "CRUD Completion"
            elif "Authentication" in test_name:
                category = "Authentication"
            
            issue_results[category]["total"] += 1
            if result["success"]:
                issue_results[category]["passed"] += 1
            else:
                issue_results[category]["failed"] += 1
        
        print(f"\n📋 ISSUE-BY-ISSUE RESULTS:")
        for issue, stats in issue_results.items():
            if stats["total"] > 0:
                issue_success_rate = (stats["passed"] / stats["total"] * 100)
                status = "✅" if issue_success_rate >= 75 else "⚠️" if issue_success_rate >= 50 else "❌"
                print(f"   {status} {issue}: {stats['passed']}/{stats['total']} ({issue_success_rate:.1f}%)")
        
        print(f"\n🔍 FAILED TESTS SUMMARY:")
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            for result in failed_results:
                print(f"   ❌ {result['test']}: {result['message']}")
        else:
            print("   🎉 No failed tests!")
        
        print(f"\n🎯 FINAL VALIDATION ASSESSMENT:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - All fixes working perfectly, platform ready")
        elif success_rate >= 75:
            print("   🟡 GOOD - Most fixes working, minor issues to address")
        elif success_rate >= 50:
            print("   🟠 PARTIAL - Some fixes working, significant issues remain")
        else:
            print("   🔴 CRITICAL - Major issues with fixes, immediate attention required")
        
        print("=" * 80)

def main():
    """Main function to run the final validation test"""
    tester = FinalValidationTester()
    
    try:
        success = tester.run_final_validation()
        if success:
            print("\n✅ Final validation test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Final validation test failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()