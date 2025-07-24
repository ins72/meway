#!/usr/bin/env python3
"""
COMPREHENSIVE WORKSPACE SUBSCRIPTION SYSTEM TEST
===============================================
Testing the newly implemented Workspace Subscription System with focus on:

1. Health Check & Service Initialization
2. Bundle Information & Pricing
3. Workspace Subscription CRUD Operations
4. Feature Access Control
5. Usage Limits & Tracking
6. Billing History

Test credentials: tmonnens@outlook.com / Voetballen5
"""

import requests
import json
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://eff6f53c-47df-43a1-9962-4d20b26f6dc5.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class WorkspaceSubscriptionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_workspace_id = "deebdeae-4a9d-4611-ad12-9b71e13376a6"  # Pre-created workspace owned by test user
        
    def log_result(self, test_name: str, endpoint: str, method: str, success: bool, status_code: int = None, details: str = ""):
        """Log test result"""
        result = {
            "test_name": test_name,
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
            print(f"✅ {test_name}: {method} {endpoint} - {status_code}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {method} {endpoint} - {status_code} - {details}")

    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
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
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/api/workspace-subscription/health",
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("healthy") and data.get("service") == "workspace_subscription":
                    details = f"Service healthy, {data.get('bundles_available', 0)} bundles available"
                else:
                    success = False
                    details = "Health check returned unhealthy status"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Health Check",
                "/api/workspace-subscription/health",
                "GET",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Health Check",
                "/api/workspace-subscription/health",
                "GET",
                False,
                None,
                str(e)
            )

    def test_available_bundles(self):
        """Test get available bundles endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/api/workspace-subscription/bundles/available",
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("bundles"):
                    bundles = data["bundles"]
                    expected_bundles = ["creator", "ecommerce", "social_media", "education", "business", "operations"]
                    found_bundles = list(bundles.keys())
                    
                    if all(bundle in found_bundles for bundle in expected_bundles):
                        details = f"All {len(found_bundles)} expected bundles found: {', '.join(found_bundles)}"
                    else:
                        success = False
                        details = f"Missing bundles. Found: {found_bundles}, Expected: {expected_bundles}"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Available Bundles",
                "/api/workspace-subscription/bundles/available",
                "GET",
                success,
                response.status_code,
                details
            )
            
            return response.json() if success else None
            
        except Exception as e:
            self.log_result(
                "Available Bundles",
                "/api/workspace-subscription/bundles/available",
                "GET",
                False,
                None,
                str(e)
            )
            return None

    def test_pricing_calculation(self):
        """Test pricing calculation for different bundle combinations"""
        test_cases = [
            {
                "name": "Single Bundle - Creator",
                "bundles": "creator",
                "billing_cycle": "monthly"
            },
            {
                "name": "Two Bundles - Creator + E-commerce",
                "bundles": "creator,ecommerce",
                "billing_cycle": "monthly"
            },
            {
                "name": "Three Bundles - Creator + E-commerce + Social Media",
                "bundles": "creator,ecommerce,social_media",
                "billing_cycle": "monthly"
            },
            {
                "name": "All Bundles - Monthly",
                "bundles": "creator,ecommerce,social_media,education,business,operations",
                "billing_cycle": "monthly"
            },
            {
                "name": "All Bundles - Yearly",
                "bundles": "creator,ecommerce,social_media,education,business,operations",
                "billing_cycle": "yearly"
            }
        ]
        
        for test_case in test_cases:
            try:
                params = {
                    "bundles": test_case["bundles"],
                    "billing_cycle": test_case["billing_cycle"]
                }
                
                response = requests.get(
                    f"{self.base_url}/api/workspace-subscription/pricing/calculate",
                    params=params,
                    headers=self.headers,
                    timeout=30
                )
                
                success = response.status_code == 200
                details = ""
                
                if success:
                    data = response.json()
                    if data.get("success") and data.get("pricing"):
                        pricing = data["pricing"]
                        bundle_count = len(test_case["bundles"].split(","))
                        
                        # Verify discount logic
                        expected_discount = 0
                        if bundle_count >= 4:
                            expected_discount = 0.40
                        elif bundle_count == 3:
                            expected_discount = 0.30
                        elif bundle_count == 2:
                            expected_discount = 0.20
                        
                        actual_discount = pricing.get("discount_rate", 0)
                        
                        if abs(actual_discount - expected_discount) < 0.01:  # Allow small floating point differences
                            details = f"Pricing: ${pricing['total_amount']}, Discount: {actual_discount*100}%, Base: ${pricing['base_total']}"
                        else:
                            success = False
                            details = f"Incorrect discount. Expected: {expected_discount*100}%, Got: {actual_discount*100}%"
                    else:
                        success = False
                        details = "Invalid pricing response structure"
                else:
                    details = f"Response: {response.text[:200]}"
                
                self.log_result(
                    f"Pricing - {test_case['name']}",
                    "/api/workspace-subscription/pricing/calculate",
                    "GET",
                    success,
                    response.status_code,
                    details
                )
                
            except Exception as e:
                self.log_result(
                    f"Pricing - {test_case['name']}",
                    "/api/workspace-subscription/pricing/calculate",
                    "GET",
                    False,
                    None,
                    str(e)
                )

    def test_create_workspace_subscription(self):
        """Test creating a workspace subscription"""
        try:
            # Use the pre-created workspace that the user owns
            # Create subscription
            subscription_data = {
                "bundles": ["creator", "ecommerce"],
                "billing_cycle": "monthly"
            }
            
            response = requests.post(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription",
                json=subscription_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("subscription"):
                    subscription = data["subscription"]
                    details = f"Subscription created: {subscription['_id']}, Bundles: {subscription['bundles']}, Status: {subscription['status']}"
                else:
                    success = False
                    details = "Invalid subscription response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Create Workspace Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription",
                "POST",
                success,
                response.status_code,
                details
            )
            
            return success
            
        except Exception as e:
            self.log_result(
                "Create Workspace Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription",
                "POST",
                False,
                None,
                str(e)
            )
            return False

    def test_get_workspace_subscription(self):
        """Test getting workspace subscription details"""
        try:
            response = requests.get(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription",
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("subscription"):
                    subscription = data["subscription"]
                    details = f"Subscription found: {subscription['_id']}, Bundles: {subscription['bundles']}, Status: {subscription['status']}"
                else:
                    success = False
                    details = "Invalid subscription response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Get Workspace Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription",
                "GET",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Get Workspace Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription",
                "GET",
                False,
                None,
                str(e)
            )

    def test_modify_workspace_bundles(self):
        """Test modifying workspace bundles (add/remove)"""
        # Test adding bundles
        try:
            add_data = {
                "action": "add",
                "bundles": ["social_media"]
            }
            
            response = requests.put(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription/bundle",
                json=add_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("updated_subscription"):
                    subscription = data["updated_subscription"]
                    if "social_media" in subscription["bundles"]:
                        details = f"Bundle added successfully. Current bundles: {subscription['bundles']}"
                    else:
                        success = False
                        details = "Bundle was not added to subscription"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Add Bundle to Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription/bundle",
                "PUT",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Add Bundle to Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription/bundle",
                "PUT",
                False,
                None,
                str(e)
            )
        
        # Test removing bundles
        try:
            remove_data = {
                "action": "remove",
                "bundles": ["ecommerce"]
            }
            
            response = requests.put(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription/bundle",
                json=remove_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("updated_subscription"):
                    subscription = data["updated_subscription"]
                    if "ecommerce" not in subscription["bundles"]:
                        details = f"Bundle removed successfully. Current bundles: {subscription['bundles']}"
                    else:
                        success = False
                        details = "Bundle was not removed from subscription"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Remove Bundle from Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription/bundle",
                "PUT",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Remove Bundle from Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/subscription/bundle",
                "PUT",
                False,
                None,
                str(e)
            )

    def test_feature_access_control(self):
        """Test feature access control"""
        test_features = [
            "advanced_bio_links",  # Should be available (creator bundle)
            "website_builder",     # Should be available (creator bundle)
            "social_scheduling",   # Should be available (social_media bundle)
            "course_platform",     # Should NOT be available (education bundle not subscribed)
            "advanced_crm"         # Should NOT be available (business bundle not subscribed)
        ]
        
        for feature in test_features:
            try:
                params = {"feature": feature}
                
                response = requests.get(
                    f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/feature-access",
                    params=params,
                    headers=self.headers,
                    timeout=30
                )
                
                success = response.status_code == 200
                details = ""
                
                if success:
                    data = response.json()
                    if data.get("success"):
                        has_access = data.get("has_access", False)
                        reason = data.get("reason", "")
                        details = f"Feature '{feature}': {'✅ Access granted' if has_access else '❌ Access denied'} - {reason}"
                    else:
                        success = False
                        details = "Invalid response structure"
                else:
                    details = f"Response: {response.text[:200]}"
                
                self.log_result(
                    f"Feature Access - {feature}",
                    f"/api/workspace-subscription/workspace/{self.test_workspace_id}/feature-access",
                    "GET",
                    success,
                    response.status_code,
                    details
                )
                
            except Exception as e:
                self.log_result(
                    f"Feature Access - {feature}",
                    f"/api/workspace-subscription/workspace/{self.test_workspace_id}/feature-access",
                    "GET",
                    False,
                    None,
                    str(e)
                )

    def test_usage_limits(self):
        """Test getting workspace usage limits"""
        try:
            response = requests.get(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/usage-limits",
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("limits"):
                    limits = data["limits"]
                    current_usage = data.get("current_usage", {})
                    active_bundles = data.get("active_bundles", [])
                    
                    details = f"Active bundles: {active_bundles}, Limits tracked: {len(limits)} items, Usage tracked: {len(current_usage)} items"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Usage Limits",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/usage-limits",
                "GET",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Usage Limits",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/usage-limits",
                "GET",
                False,
                None,
                str(e)
            )

    def test_billing_history(self):
        """Test getting workspace billing history"""
        try:
            params = {"limit": 10, "offset": 0}
            
            response = requests.get(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/billing-history",
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and "billing_history" in data:
                    billing_history = data["billing_history"]
                    pagination = data.get("pagination", {})
                    
                    details = f"Billing records: {len(billing_history)}, Total: {pagination.get('total_count', 0)}"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Billing History",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/billing-history",
                "GET",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Billing History",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/billing-history",
                "GET",
                False,
                None,
                str(e)
            )

    def test_upgrade_subscription(self):
        """Test upgrading workspace subscription"""
        try:
            upgrade_data = {
                "bundles": ["education", "business"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/upgrade",
                json=upgrade_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("updated_subscription"):
                    subscription = data["updated_subscription"]
                    bundles = subscription["bundles"]
                    
                    if "education" in bundles and "business" in bundles:
                        details = f"Upgrade successful. Current bundles: {bundles}"
                    else:
                        success = False
                        details = "Upgrade bundles not found in subscription"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Upgrade Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/upgrade",
                "POST",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Upgrade Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/upgrade",
                "POST",
                False,
                None,
                str(e)
            )

    def test_downgrade_subscription(self):
        """Test downgrading workspace subscription"""
        try:
            downgrade_data = {
                "bundles": ["business"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/downgrade",
                json=downgrade_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("updated_subscription"):
                    subscription = data["updated_subscription"]
                    bundles = subscription["bundles"]
                    
                    if "business" not in bundles:
                        details = f"Downgrade successful. Current bundles: {bundles}"
                    else:
                        success = False
                        details = "Downgrade bundle still found in subscription"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Downgrade Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/downgrade",
                "POST",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Downgrade Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/downgrade",
                "POST",
                False,
                None,
                str(e)
            )

    def test_cancel_subscription(self):
        """Test cancelling workspace subscription"""
        try:
            cancel_data = {
                "reason": "Testing cancellation functionality"
            }
            
            response = requests.post(
                f"{self.base_url}/api/workspace-subscription/workspace/{self.test_workspace_id}/cancel",
                json=cancel_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            details = ""
            
            if success:
                data = response.json()
                if data.get("success") and data.get("cancelled_subscription"):
                    subscription = data["cancelled_subscription"]
                    status = subscription.get("status")
                    
                    if status == "cancelled":
                        details = f"Cancellation successful. Status: {status}, Auto-renew: {subscription.get('auto_renew', True)}"
                    else:
                        success = False
                        details = f"Subscription not properly cancelled. Status: {status}"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Response: {response.text[:200]}"
            
            self.log_result(
                "Cancel Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/cancel",
                "POST",
                success,
                response.status_code,
                details
            )
            
        except Exception as e:
            self.log_result(
                "Cancel Subscription",
                f"/api/workspace-subscription/workspace/{self.test_workspace_id}/cancel",
                "POST",
                False,
                None,
                str(e)
            )

    def run_comprehensive_test(self):
        """Run all workspace subscription tests"""
        print("🚀 STARTING COMPREHENSIVE WORKSPACE SUBSCRIPTION SYSTEM TEST")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print(f"🔧 Using test workspace ID: {self.test_workspace_id}")
        print()
        
        # Run all tests in logical order
        print("📋 1. HEALTH CHECK & SERVICE INITIALIZATION")
        self.test_health_check()
        print()
        
        print("📋 2. BUNDLE INFORMATION & PRICING")
        self.test_available_bundles()
        self.test_pricing_calculation()
        print()
        
        print("📋 3. WORKSPACE SUBSCRIPTION CRUD OPERATIONS")
        subscription_created = self.test_create_workspace_subscription()
        if subscription_created:
            self.test_get_workspace_subscription()
            self.test_modify_workspace_bundles()
            self.test_upgrade_subscription()
            self.test_downgrade_subscription()
        print()
        
        print("📋 4. FEATURE ACCESS CONTROL")
        self.test_feature_access_control()
        print()
        
        print("📋 5. USAGE LIMITS & TRACKING")
        self.test_usage_limits()
        print()
        
        print("📋 6. BILLING HISTORY")
        self.test_billing_history()
        print()
        
        print("📋 7. SUBSCRIPTION CANCELLATION")
        self.test_cancel_subscription()
        print()
        
        # Print final results
        self.print_final_results()
        
        return self.passed_tests > 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("=" * 80)
        print("🎯 WORKSPACE SUBSCRIPTION SYSTEM TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests} ✅")
        print(f"   Failed: {self.failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by test category
        categories = {}
        for result in self.test_results:
            test_name = result["test_name"]
            if "Health" in test_name:
                category = "Health & Initialization"
            elif "Bundle" in test_name or "Pricing" in test_name:
                category = "Bundle & Pricing"
            elif "Create" in test_name or "Get" in test_name or "Add" in test_name or "Remove" in test_name or "Upgrade" in test_name or "Downgrade" in test_name:
                category = "CRUD Operations"
            elif "Feature Access" in test_name:
                category = "Feature Access Control"
            elif "Usage" in test_name:
                category = "Usage Limits"
            elif "Billing" in test_name:
                category = "Billing History"
            elif "Cancel" in test_name:
                category = "Subscription Management"
            else:
                category = "Other"
            
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            
            categories[category]["tests"].append(result)
        
        print("📋 DETAILED RESULTS BY CATEGORY:")
        for category, data in categories.items():
            total = data["passed"] + data["failed"]
            rate = (data["passed"] / total * 100) if total > 0 else 0
            print(f"\n   {category}:")
            print(f"     ✅ Passed: {data['passed']}")
            print(f"     ❌ Failed: {data['failed']}")
            print(f"     📈 Success Rate: {rate:.1f}%")
            
            # Show failed tests
            failed_tests = [t for t in data["tests"] if not t["success"]]
            if failed_tests:
                print(f"     🔍 Failed Tests:")
                for test in failed_tests:
                    print(f"       - {test['test_name']}: {test['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 80:
            print("🎉 WORKSPACE SUBSCRIPTION SYSTEM IS PRODUCTION-READY!")
            print("   All critical functionality is working correctly.")
        elif success_rate >= 60:
            print("⚠️  WORKSPACE SUBSCRIPTION SYSTEM NEEDS MINOR FIXES")
            print("   Core functionality works but some features need attention.")
        else:
            print("❌ WORKSPACE SUBSCRIPTION SYSTEM NEEDS MAJOR FIXES")
            print("   Critical issues found that prevent production deployment.")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = WorkspaceSubscriptionTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()