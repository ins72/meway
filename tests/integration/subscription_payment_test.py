#!/usr/bin/env python3
"""
Comprehensive Subscription and Payment Management System Testing
Testing Phase 1 of the comprehensive subscription management system
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com"
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class SubscriptionPaymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                },
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.token = data["token"]
                    self.user_data = data.get("user", {})
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.token}"
                    })
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Successfully authenticated as {self.user_data.get('name', 'Admin')} ({self.user_data.get('role', 'unknown')})",
                        response_time
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_comprehensive_subscription_status(self):
        """Test GET /api/subscription/comprehensive-status"""
        print("\n📊 TESTING COMPREHENSIVE SUBSCRIPTION STATUS...")
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{BACKEND_URL}/api/subscription/comprehensive-status",
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    subscription_data = data["data"]
                    
                    # Validate comprehensive data structure
                    required_sections = [
                        "subscription_overview",
                        "payment_health", 
                        "usage_analytics",
                        "account_lifecycle"
                    ]
                    
                    missing_sections = [section for section in required_sections if section not in subscription_data]
                    
                    if not missing_sections:
                        overview = subscription_data["subscription_overview"]
                        payment_health = subscription_data["payment_health"]
                        usage = subscription_data["usage_analytics"]
                        lifecycle = subscription_data["account_lifecycle"]
                        
                        details = f"Comprehensive subscription data retrieved - Plan: {overview.get('plan_name')}, Health Score: {overview.get('health_score')}, Risk Level: {overview.get('risk_level')}, Engagement Score: {usage.get('engagement_score')}, Lifecycle Stage: {lifecycle.get('lifecycle_stage')}"
                        self.log_result("Comprehensive Subscription Status", True, details, response_time)
                        return True
                    else:
                        self.log_result("Comprehensive Subscription Status", False, f"Missing sections: {missing_sections}", response_time)
                        return False
                else:
                    self.log_result("Comprehensive Subscription Status", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Comprehensive Subscription Status", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Comprehensive Subscription Status", False, f"Exception: {str(e)}")
            return False
    
    def test_failed_payments(self):
        """Test GET /api/payment/failed-payments"""
        print("\n💳 TESTING FAILED PAYMENTS ENDPOINT...")
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{BACKEND_URL}/api/payment/failed-payments",
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    payment_data = data["data"]
                    
                    # Validate failed payments data structure
                    required_sections = [
                        "failed_payments_summary",
                        "payment_failures",
                        "recovery_options",
                        "prevention_tips"
                    ]
                    
                    missing_sections = [section for section in required_sections if section not in payment_data]
                    
                    if not missing_sections:
                        summary = payment_data["failed_payments_summary"]
                        recovery_options = payment_data["recovery_options"]
                        
                        details = f"Failed payments data retrieved - Total Failed: {summary.get('total_failed_attempts')}, Recovery Status: {summary.get('recovery_status')}, Recovery Options: {len(recovery_options)}"
                        self.log_result("Failed Payments Data", True, details, response_time)
                        return True
                    else:
                        self.log_result("Failed Payments Data", False, f"Missing sections: {missing_sections}", response_time)
                        return False
                else:
                    self.log_result("Failed Payments Data", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Failed Payments Data", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Failed Payments Data", False, f"Exception: {str(e)}")
            return False
    
    def test_payment_recovery_dashboard(self):
        """Test GET /api/payment/recovery-dashboard"""
        print("\n🔄 TESTING PAYMENT RECOVERY DASHBOARD...")
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{BACKEND_URL}/api/payment/recovery-dashboard",
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    recovery_data = data["data"]
                    
                    # Validate recovery dashboard data structure
                    required_sections = [
                        "account_status",
                        "payment_analytics",
                        "proactive_monitoring",
                        "recommendations"
                    ]
                    
                    missing_sections = [section for section in required_sections if section not in recovery_data]
                    
                    if not missing_sections:
                        account_status = recovery_data["account_status"]
                        analytics = recovery_data["payment_analytics"]
                        monitoring = recovery_data["proactive_monitoring"]
                        
                        details = f"Recovery dashboard data retrieved - Payment Health: {account_status.get('payment_health')}, Success Rate: {account_status.get('payment_success_rate')}%, Total Payments: {analytics.get('total_payments')}, Monitoring Features: {len([k for k, v in monitoring.items() if v])}"
                        self.log_result("Payment Recovery Dashboard", True, details, response_time)
                        return True
                    else:
                        self.log_result("Payment Recovery Dashboard", False, f"Missing sections: {missing_sections}", response_time)
                        return False
                else:
                    self.log_result("Payment Recovery Dashboard", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Payment Recovery Dashboard", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Payment Recovery Dashboard", False, f"Exception: {str(e)}")
            return False
    
    def test_retry_failed_payment(self):
        """Test POST /api/payment/retry-failed"""
        print("\n🔁 TESTING RETRY FAILED PAYMENT...")
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/api/payment/retry-failed",
                data={
                    "payment_intent_id": "pi_test_1234567890"
                },
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    retry_data = data["data"]
                    
                    # Validate retry response structure
                    required_fields = [
                        "payment_intent_id",
                        "status",
                        "client_secret",
                        "retry_attempt",
                        "next_action"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in retry_data]
                    
                    if not missing_fields:
                        details = f"Payment retry initiated - Intent ID: {retry_data.get('payment_intent_id')}, Status: {retry_data.get('status')}, Retry Attempt: {retry_data.get('retry_attempt')}, Next Action: {retry_data.get('next_action')}"
                        self.log_result("Retry Failed Payment", True, details, response_time)
                        return True
                    else:
                        self.log_result("Retry Failed Payment", False, f"Missing fields: {missing_fields}", response_time)
                        return False
                else:
                    self.log_result("Retry Failed Payment", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Retry Failed Payment", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Retry Failed Payment", False, f"Exception: {str(e)}")
            return False
    
    def test_cancellation_survey(self):
        """Test POST /api/subscription/cancellation/survey"""
        print("\n📝 TESTING CANCELLATION SURVEY...")
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/api/subscription/cancellation/survey",
                data={
                    "reason": "too_expensive",
                    "feedback": "The service is great but the pricing is too high for my current budget",
                    "satisfaction_score": 4,
                    "likelihood_to_return": 7,
                    "suggestions": "Consider offering more flexible pricing tiers"
                },
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    survey_data = data["data"]
                    
                    # Validate survey response structure
                    required_fields = [
                        "survey_id",
                        "retention_offers",
                        "contact_info"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in survey_data]
                    
                    if not missing_fields:
                        retention_offers = survey_data.get("retention_offers", [])
                        details = f"Cancellation survey submitted - Survey ID: {survey_data.get('survey_id')}, Retention Offers: {len(retention_offers)}, Contact Support Available: {survey_data.get('contact_info', {}).get('chat_available', False)}"
                        self.log_result("Cancellation Survey", True, details, response_time)
                        return True
                    else:
                        self.log_result("Cancellation Survey", False, f"Missing fields: {missing_fields}", response_time)
                        return False
                else:
                    self.log_result("Cancellation Survey", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Cancellation Survey", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Cancellation Survey", False, f"Exception: {str(e)}")
            return False
    
    def test_account_deletion_request(self):
        """Test POST /api/account/deletion/request"""
        print("\n🗑️ TESTING ACCOUNT DELETION REQUEST...")
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/api/account/deletion/request",
                data={
                    "password": ADMIN_PASSWORD,
                    "reason": "no_longer_needed",
                    "data_export_requested": True
                },
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    deletion_data = data["data"]
                    
                    # Validate deletion request response structure
                    required_fields = [
                        "deletion_request_id",
                        "scheduled_deletion_date",
                        "grace_period_days",
                        "data_retention_info",
                        "cancellation_info"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in deletion_data]
                    
                    if not missing_fields:
                        # Store deletion request ID for cancellation test
                        self.deletion_request_id = deletion_data.get("deletion_request_id")
                        
                        details = f"Account deletion requested - Request ID: {deletion_data.get('deletion_request_id')}, Grace Period: {deletion_data.get('grace_period_days')} days, Data Export: Requested, Cancellation Link Available: {bool(deletion_data.get('cancellation_info', {}).get('link'))}"
                        self.log_result("Account Deletion Request", True, details, response_time)
                        return True
                    else:
                        self.log_result("Account Deletion Request", False, f"Missing fields: {missing_fields}", response_time)
                        return False
                else:
                    self.log_result("Account Deletion Request", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Account Deletion Request", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Account Deletion Request", False, f"Exception: {str(e)}")
            return False
    
    def test_cancel_account_deletion(self):
        """Test POST /api/account/deletion/cancel/{deletion_request_id}"""
        print("\n↩️ TESTING CANCEL ACCOUNT DELETION...")
        
        if not hasattr(self, 'deletion_request_id') or not self.deletion_request_id:
            self.log_result("Cancel Account Deletion", False, "No deletion request ID available from previous test")
            return False
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/api/account/deletion/cancel/{self.deletion_request_id}",
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    cancellation_data = data["data"]
                    
                    # Validate cancellation response structure
                    required_fields = [
                        "deletion_request_id",
                        "status",
                        "account_restored",
                        "subscription_status",
                        "message"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in cancellation_data]
                    
                    if not missing_fields:
                        details = f"Account deletion cancelled - Request ID: {cancellation_data.get('deletion_request_id')}, Status: {cancellation_data.get('status')}, Account Restored: {cancellation_data.get('account_restored')}, Subscription: {cancellation_data.get('subscription_status')}"
                        self.log_result("Cancel Account Deletion", True, details, response_time)
                        return True
                    else:
                        self.log_result("Cancel Account Deletion", False, f"Missing fields: {missing_fields}", response_time)
                        return False
                else:
                    self.log_result("Cancel Account Deletion", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Cancel Account Deletion", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Cancel Account Deletion", False, f"Exception: {str(e)}")
            return False
    
    def test_retention_analysis(self):
        """Test GET /api/subscription/retention-analysis"""
        print("\n📈 TESTING RETENTION ANALYSIS...")
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{BACKEND_URL}/api/subscription/retention-analysis",
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    retention_data = data["data"]
                    
                    # Validate retention analysis data structure
                    required_sections = [
                        "account_health",
                        "usage_insights"
                    ]
                    
                    missing_sections = [section for section in required_sections if section not in retention_data]
                    
                    if not missing_sections:
                        health = retention_data["account_health"]
                        insights = retention_data["usage_insights"]
                        
                        details = f"Retention analysis retrieved - Retention Score: {health.get('retention_score')}, Churn Risk: {health.get('churn_risk')}, Engagement Trend: {health.get('engagement_trend')}, Most Used Features: {len(insights.get('most_used_features', []))}, Growth Opportunities: {len(insights.get('growth_opportunities', []))}"
                        self.log_result("Retention Analysis", True, details, response_time)
                        return True
                    else:
                        self.log_result("Retention Analysis", False, f"Missing sections: {missing_sections}", response_time)
                        return False
                else:
                    self.log_result("Retention Analysis", False, f"Invalid response format: {data}", response_time)
                    return False
            else:
                self.log_result("Retention Analysis", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Retention Analysis", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all subscription and payment management tests"""
        print("🚀 STARTING COMPREHENSIVE SUBSCRIPTION & PAYMENT MANAGEMENT TESTING")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate():
            print("\n❌ AUTHENTICATION FAILED - CANNOT PROCEED WITH TESTS")
            return False
        
        # Core Subscription Management Tests
        print("\n" + "=" * 50)
        print("📊 CORE SUBSCRIPTION MANAGEMENT TESTS")
        print("=" * 50)
        
        test_results = []
        test_results.append(self.test_comprehensive_subscription_status())
        test_results.append(self.test_failed_payments())
        test_results.append(self.test_payment_recovery_dashboard())
        
        # Payment Recovery Tests
        print("\n" + "=" * 50)
        print("🔄 PAYMENT RECOVERY TESTS")
        print("=" * 50)
        
        test_results.append(self.test_retry_failed_payment())
        
        # Account Lifecycle Management Tests
        print("\n" + "=" * 50)
        print("🔄 ACCOUNT LIFECYCLE MANAGEMENT TESTS")
        print("=" * 50)
        
        test_results.append(self.test_cancellation_survey())
        test_results.append(self.test_account_deletion_request())
        test_results.append(self.test_cancel_account_deletion())
        test_results.append(self.test_retention_analysis())
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE SUBSCRIPTION & PAYMENT MANAGEMENT TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in test_results if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n✅ PASSED: {passed_tests}/{total_tests} tests ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL SUBSCRIPTION & PAYMENT MANAGEMENT TESTS PASSED!")
            print("✅ Phase 1 of comprehensive subscription management system is working correctly")
        else:
            failed_tests = total_tests - passed_tests
            print(f"⚠️  {failed_tests} test(s) failed")
            
        # Performance Summary
        response_times = [result.get("response_time", 0) for result in self.test_results if result.get("response_time")]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"⚡ Average Response Time: {avg_response_time:.3f}s")
            print(f"⚡ Fastest Response: {min(response_times):.3f}s")
            print(f"⚡ Slowest Response: {max(response_times):.3f}s")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = SubscriptionPaymentTester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/subscription_payment_test_results.json', 'w') as f:
        json.dump({
            "test_results": tester.test_results,
            "summary": {
                "total_tests": len(tester.test_results),
                "passed_tests": sum(1 for r in tester.test_results if r["success"]),
                "success_rate": (sum(1 for r in tester.test_results if r["success"]) / len(tester.test_results)) * 100 if tester.test_results else 0,
                "test_completed_at": datetime.now().isoformat()
            }
        }, f, indent=2)
    
    return success

if __name__ == "__main__":
    main()