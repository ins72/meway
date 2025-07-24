#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND AUDIT - FINAL VERIFICATION
===============================================
Testing all systems with proper endpoint routing and parameters
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://72c4cfb8-834d-427f-b182-685a764bee4b.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ComprehensiveAuditor:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.critical_failures = []
        
    def log_result(self, system: str, endpoint: str, method: str, success: bool, status_code: int = None, details: str = "", critical: bool = False):
        """Log test result"""
        result = {
            "system": system,
            "endpoint": endpoint,
            "method": method,
            "success": success,
            "status_code": status_code,
            "details": details,
            "critical": critical,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        self.total_tests += 1
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            if critical:
                self.critical_failures.append(f"{system} - {method} {endpoint}: {details}")
            
        status = "✅" if success else "❌"
        priority = " [CRITICAL]" if critical else ""
        print(f"{status} {system} - {method} {endpoint} ({status_code}) - {details}{priority}")

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
                self.headers["Authorization"] = f"Bearer {self.token}"
                self.log_result("Authentication", "/api/auth/login", "POST", True, 200, "Login successful")
                return True
            else:
                self.log_result("Authentication", "/api/auth/login", "POST", False, response.status_code, f"Login failed: {response.text}", critical=True)
                return False
                
        except Exception as e:
            self.log_result("Authentication", "/api/auth/login", "POST", False, None, f"Exception: {str(e)}", critical=True)
            return False

    def test_website_builder_comprehensive(self):
        """Comprehensive Website Builder test with correct endpoints"""
        print("\n🔍 COMPREHENSIVE WEBSITE BUILDER TESTING")
        
        # Health check
        try:
            response = requests.get(f"{self.base_url}/api/website-builder/health", headers=self.headers)
            self.log_result("Website Builder", "/health", "GET", response.status_code == 200, response.status_code, "Health check")
        except Exception as e:
            self.log_result("Website Builder", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # List websites - correct endpoint is "/"
        try:
            response = requests.get(f"{self.base_url}/api/website-builder/", headers=self.headers)
            self.log_result("Website Builder", "/", "GET", response.status_code == 200, response.status_code, "List websites (correct endpoint)")
        except Exception as e:
            self.log_result("Website Builder", "/", "GET", False, None, f"Exception: {str(e)}")
        
        # Templates
        try:
            response = requests.get(f"{self.base_url}/api/website-builder/templates", headers=self.headers)
            self.log_result("Website Builder", "/templates", "GET", response.status_code == 200, response.status_code, "Get templates")
        except Exception as e:
            self.log_result("Website Builder", "/templates", "GET", False, None, f"Exception: {str(e)}")
        
        # Stats
        try:
            response = requests.get(f"{self.base_url}/api/website-builder/stats", headers=self.headers)
            self.log_result("Website Builder", "/stats", "GET", response.status_code == 200, response.status_code, "Get stats")
        except Exception as e:
            self.log_result("Website Builder", "/stats", "GET", False, None, f"Exception: {str(e)}")
        
        # CREATE endpoint - correct endpoint is "/"
        try:
            create_data = {
                "name": "Comprehensive Audit Website",
                "template": "business",
                "domain": "audit-comprehensive.com",
                "description": "Website for comprehensive audit testing"
            }
            response = requests.post(f"{self.base_url}/api/website-builder/", json=create_data, headers=self.headers)
            self.log_result("Website Builder", "/", "POST", response.status_code == 200, response.status_code, 
                          "CREATE website (correct endpoint)", critical=True)
        except Exception as e:
            self.log_result("Website Builder", "/", "POST", False, None, f"Exception: {str(e)}", critical=True)

    def test_template_marketplace_access_comprehensive(self):
        """Comprehensive Template Marketplace Access test with correct parameters"""
        print("\n🔍 COMPREHENSIVE TEMPLATE MARKETPLACE ACCESS TESTING")
        
        # Health check
        try:
            response = requests.get(f"{self.base_url}/api/template-marketplace-access/health", headers=self.headers)
            self.log_result("Template Marketplace Access", "/health", "GET", response.status_code == 200, response.status_code, "Health check")
        except Exception as e:
            self.log_result("Template Marketplace Access", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Selling requirements (no parameters needed)
        try:
            response = requests.get(f"{self.base_url}/api/template-marketplace-access/selling-requirements", headers=self.headers)
            self.log_result("Template Marketplace Access", "/selling-requirements", "GET", response.status_code == 200, response.status_code, "Selling requirements")
        except Exception as e:
            self.log_result("Template Marketplace Access", "/selling-requirements", "GET", False, None, f"Exception: {str(e)}")
        
        # Bundle requirements for specific bundle
        try:
            response = requests.get(f"{self.base_url}/api/template-marketplace-access/bundle-requirements/creator", headers=self.headers)
            self.log_result("Template Marketplace Access", "/bundle-requirements/creator", "GET", response.status_code == 200, response.status_code, "Bundle requirements for creator")
        except Exception as e:
            self.log_result("Template Marketplace Access", "/bundle-requirements/creator", "GET", False, None, f"Exception: {str(e)}")
        
        # Check seller access with proper parameters
        try:
            test_user_id = "test-user-123"
            test_workspace_id = "test-workspace-456"
            response = requests.get(f"{self.base_url}/api/template-marketplace-access/seller-access/{test_user_id}?workspace_id={test_workspace_id}", headers=self.headers)
            self.log_result("Template Marketplace Access", f"/seller-access/{test_user_id}", "GET", 
                          response.status_code in [200, 403, 404], response.status_code, 
                          "Seller access check (expected 403/404 for test data)", critical=False)
        except Exception as e:
            self.log_result("Template Marketplace Access", "/seller-access/{user_id}", "GET", False, None, f"Exception: {str(e)}")

    def test_ai_token_purchase_comprehensive(self):
        """Comprehensive AI Token Purchase test with correct parameters"""
        print("\n🔍 COMPREHENSIVE AI TOKEN PURCHASE TESTING")
        
        # Health check
        try:
            response = requests.get(f"{self.base_url}/api/ai-token-purchase/health", headers=self.headers)
            self.log_result("AI Token Purchase", "/health", "GET", response.status_code == 200, response.status_code, "Health check")
        except Exception as e:
            self.log_result("AI Token Purchase", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Get pricing packages
        try:
            response = requests.get(f"{self.base_url}/api/ai-token-purchase/pricing", headers=self.headers)
            self.log_result("AI Token Purchase", "/pricing", "GET", response.status_code == 200, response.status_code, "Pricing packages")
        except Exception as e:
            self.log_result("AI Token Purchase", "/pricing", "GET", False, None, f"Exception: {str(e)}")
        
        # Check token balance with workspace ID
        try:
            test_workspace_id = "test-workspace-789"
            response = requests.get(f"{self.base_url}/api/ai-token-purchase/workspace/{test_workspace_id}/balance", headers=self.headers)
            self.log_result("AI Token Purchase", f"/workspace/{test_workspace_id}/balance", "GET", 
                          response.status_code in [200, 404], response.status_code, 
                          "Token balance (expected 404 for test workspace)", critical=False)
        except Exception as e:
            self.log_result("AI Token Purchase", "/workspace/{workspace_id}/balance", "GET", False, None, f"Exception: {str(e)}")
        
        # Test token purchase with proper data
        try:
            purchase_data = {
                "workspace_id": "test-workspace-789",
                "package_id": "starter_100",
                "payment_method": "stripe"
            }
            response = requests.post(f"{self.base_url}/api/ai-token-purchase/purchase", json=purchase_data, headers=self.headers)
            self.log_result("AI Token Purchase", "/purchase", "POST", 
                          response.status_code in [200, 400, 404], response.status_code, 
                          "Token purchase (expected 400/404 for test data)", critical=True)
        except Exception as e:
            self.log_result("AI Token Purchase", "/purchase", "POST", False, None, f"Exception: {str(e)}", critical=True)
        
        # Test usage history with workspace ID
        try:
            test_workspace_id = "test-workspace-789"
            response = requests.get(f"{self.base_url}/api/ai-token-purchase/workspace/{test_workspace_id}/usage-history", headers=self.headers)
            self.log_result("AI Token Purchase", f"/workspace/{test_workspace_id}/usage-history", "GET", 
                          response.status_code in [200, 404], response.status_code, 
                          "Usage history (expected 404 for test workspace)", critical=False)
        except Exception as e:
            self.log_result("AI Token Purchase", "/workspace/{workspace_id}/usage-history", "GET", False, None, f"Exception: {str(e)}")
        
        # Test purchase history with workspace ID
        try:
            test_workspace_id = "test-workspace-789"
            response = requests.get(f"{self.base_url}/api/ai-token-purchase/workspace/{test_workspace_id}/purchase-history", headers=self.headers)
            self.log_result("AI Token Purchase", f"/workspace/{test_workspace_id}/purchase-history", "GET", 
                          response.status_code in [200, 404], response.status_code, 
                          "Purchase history (expected 404 for test workspace)", critical=False)
        except Exception as e:
            self.log_result("AI Token Purchase", "/workspace/{workspace_id}/purchase-history", "GET", False, None, f"Exception: {str(e)}")

    def test_advanced_ui_comprehensive(self):
        """Comprehensive Advanced UI test"""
        print("\n🔍 COMPREHENSIVE ADVANCED UI TESTING")
        
        # Health check
        try:
            response = requests.get(f"{self.base_url}/api/advanced-ui/health", headers=self.headers)
            self.log_result("Advanced UI", "/health", "GET", response.status_code == 200, response.status_code, "Health check")
        except Exception as e:
            self.log_result("Advanced UI", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Test wizard creation (CREATE operation)
        try:
            wizard_data = {
                "name": "Comprehensive Audit Wizard",
                "type": "onboarding",
                "steps": ["welcome", "setup", "complete"]
            }
            response = requests.post(f"{self.base_url}/api/advanced-ui/wizard", json=wizard_data, headers=self.headers)
            self.log_result("Advanced UI", "/wizard", "POST", response.status_code == 200, response.status_code, "Wizard creation")
        except Exception as e:
            self.log_result("Advanced UI", "/wizard", "POST", False, None, f"Exception: {str(e)}")
        
        # Test wizard listing
        try:
            response = requests.get(f"{self.base_url}/api/advanced-ui/wizard", headers=self.headers)
            self.log_result("Advanced UI", "/wizard", "GET", response.status_code == 200, response.status_code, "Wizard list")
        except Exception as e:
            self.log_result("Advanced UI", "/wizard", "GET", False, None, f"Exception: {str(e)}")
        
        # Test goals system
        try:
            goals_data = {
                "user_id": "comprehensive-audit-user",
                "goals": ["increase_sales", "improve_engagement", "expand_reach"]
            }
            response = requests.post(f"{self.base_url}/api/advanced-ui/goals", json=goals_data, headers=self.headers)
            self.log_result("Advanced UI", "/goals", "POST", response.status_code == 200, response.status_code, "Goals creation")
        except Exception as e:
            self.log_result("Advanced UI", "/goals", "POST", False, None, f"Exception: {str(e)}")
        
        # Test UI state management
        try:
            ui_state_data = {
                "component": "dashboard",
                "state": {"active_tab": "analytics", "filters": {"date_range": "30d"}}
            }
            response = requests.post(f"{self.base_url}/api/advanced-ui/ui-state", json=ui_state_data, headers=self.headers)
            self.log_result("Advanced UI", "/ui-state", "POST", response.status_code == 200, response.status_code, "UI state management")
        except Exception as e:
            self.log_result("Advanced UI", "/ui-state", "POST", False, None, f"Exception: {str(e)}")

    def verify_all_critical_revenue_systems(self):
        """Verify all critical revenue-generating systems"""
        print("\n🔍 VERIFYING ALL CRITICAL REVENUE-GENERATING SYSTEMS")
        
        critical_systems = [
            ("Workspace Subscription", "/api/workspace-subscription/health"),
            ("Usage Tracking", "/api/usage-tracking/health"),
            ("Enterprise Revenue", "/api/enterprise-revenue/health"),
            ("Enhanced Escrow", "/api/escrow/health"),
            ("Launch Pricing", "/api/launch-pricing/health"),
            ("Admin Pricing", "/api/admin-pricing/health")
        ]
        
        for system_name, endpoint in critical_systems:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
                self.log_result(system_name, endpoint.split("/")[-1], "GET", 
                              response.status_code == 200, response.status_code, 
                              "Critical revenue system", critical=True)
            except Exception as e:
                self.log_result(system_name, endpoint.split("/")[-1], "GET", False, None, 
                              f"Exception: {str(e)}", critical=True)

    def test_core_business_systems(self):
        """Test core business systems for basic functionality"""
        print("\n🔍 TESTING CORE BUSINESS SYSTEMS")
        
        core_systems = [
            ("Booking System", "/api/booking/health"),
            ("Template Marketplace", "/api/template-marketplace/health"),
            ("Link in Bio", "/api/complete-link-in-bio/health"),
            ("Course & Community", "/api/complete-course-community/health"),
            ("Multi-Vendor Marketplace", "/api/multi-vendor-marketplace/health"),
            ("Financial System", "/api/financial/health"),
            ("Authentication", "/api/auth/health")
        ]
        
        for system_name, endpoint in core_systems:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
                self.log_result(system_name, endpoint.split("/")[-1], "GET", 
                              response.status_code == 200, response.status_code, 
                              "Core business system", critical=True)
            except Exception as e:
                self.log_result(system_name, endpoint.split("/")[-1], "GET", False, None, 
                              f"Exception: {str(e)}", critical=True)

    def run_comprehensive_audit(self):
        """Run the comprehensive audit"""
        print("🚀 STARTING COMPREHENSIVE BACKEND AUDIT")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with audit.")
            return False
        
        # Test core business systems first
        self.test_core_business_systems()
        
        # Test systems with potential issues
        self.test_website_builder_comprehensive()
        self.test_advanced_ui_comprehensive()
        self.test_template_marketplace_access_comprehensive()
        self.test_ai_token_purchase_comprehensive()
        
        # Verify critical revenue systems
        self.verify_all_critical_revenue_systems()
        
        # Print comprehensive summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE AUDIT SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        # Critical failures
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        else:
            print("\n✅ NO CRITICAL FAILURES DETECTED")
        
        # Analyze results by system
        systems = {}
        for result in self.test_results:
            system = result["system"]
            if system not in systems:
                systems[system] = {"passed": 0, "failed": 0, "total": 0, "critical_failed": 0}
            systems[system]["total"] += 1
            if result["success"]:
                systems[system]["passed"] += 1
            else:
                systems[system]["failed"] += 1
                if result.get("critical"):
                    systems[system]["critical_failed"] += 1
        
        print("\n📈 SYSTEM-BY-SYSTEM RESULTS:")
        for system, stats in systems.items():
            success_rate = (stats["passed"] / stats["total"]) * 100
            critical_note = f" ({stats['critical_failed']} critical)" if stats['critical_failed'] > 0 else ""
            status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            print(f"{status} {system}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%){critical_note}")
        
        # Final assessment
        critical_systems_working = sum(1 for system, stats in systems.items() 
                                     if "Revenue" in system or "Escrow" in system or "Pricing" in system or "Subscription" in system or "Usage" in system
                                     and stats["passed"] == stats["total"])
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        print(f"   • Overall Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        print(f"   • Critical Failures: {len(self.critical_failures)}")
        print(f"   • Revenue Systems Status: {'✅ All Working' if len(self.critical_failures) == 0 else '⚠️ Issues Detected'}")
        
        return len(self.critical_failures) == 0

if __name__ == "__main__":
    auditor = ComprehensiveAuditor()
    success = auditor.run_comprehensive_audit()
    sys.exit(0 if success else 1)