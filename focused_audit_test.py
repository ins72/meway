#!/usr/bin/env python3
"""
FOCUSED BACKEND AUDIT FOR SYSTEMS WITH POTENTIAL ISSUES
======================================================
Testing systems mentioned in review request that might need attention:
1. Website Builder (had CREATE endpoint issues)
2. Advanced UI System (had routing conflicts) 
3. Template Marketplace Access (had validation issues)
4. AI Token Purchase System (had some functionality issues)

Plus verification of all critical revenue-generating systems.
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

class FocusedAuditor:
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
            
        status = "✅" if success else "❌"
        print(f"{status} {system} - {method} {endpoint} ({status_code}) - {details}")

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
                self.log_result("Authentication", "/api/auth/login", "POST", False, response.status_code, f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", "/api/auth/login", "POST", False, None, f"Exception: {str(e)}")
            return False

    def test_website_builder(self):
        """Test Website Builder system - focus on CREATE endpoint issue"""
        print("\n🔍 TESTING WEBSITE BUILDER SYSTEM")
        
        # Health check
        try:
            response = requests.get(f"{self.base_url}/api/website-builder/health", headers=self.headers)
            self.log_result("Website Builder", "/health", "GET", response.status_code == 200, response.status_code, "Health check")
        except Exception as e:
            self.log_result("Website Builder", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # List websites
        try:
            response = requests.get(f"{self.base_url}/api/website-builder/list", headers=self.headers)
            self.log_result("Website Builder", "/list", "GET", response.status_code == 200, response.status_code, "List websites")
        except Exception as e:
            self.log_result("Website Builder", "/list", "GET", False, None, f"Exception: {str(e)}")
        
        # Templates
        try:
            response = requests.get(f"{self.base_url}/api/website-builder/templates", headers=self.headers)
            self.log_result("Website Builder", "/templates", "GET", response.status_code == 200, response.status_code, "Get templates")
        except Exception as e:
            self.log_result("Website Builder", "/templates", "GET", False, None, f"Exception: {str(e)}")
        
        # CREATE endpoint - the problematic one
        try:
            create_data = {
                "name": "Test Website Audit",
                "template": "business",
                "domain": "test-audit-site.com",
                "description": "Test website for audit"
            }
            response = requests.post(f"{self.base_url}/api/website-builder/create", json=create_data, headers=self.headers)
            self.log_result("Website Builder", "/create", "POST", response.status_code == 200, response.status_code, 
                          "CREATE endpoint - previously had 500 errors" if response.status_code != 200 else "CREATE working")
        except Exception as e:
            self.log_result("Website Builder", "/create", "POST", False, None, f"Exception: {str(e)}")

    def test_advanced_ui_system(self):
        """Test Advanced UI System - focus on routing conflicts"""
        print("\n🔍 TESTING ADVANCED UI SYSTEM")
        
        # Health check
        try:
            response = requests.get(f"{self.base_url}/api/advanced-ui/health", headers=self.headers)
            self.log_result("Advanced UI", "/health", "GET", response.status_code == 200, response.status_code, "Health check")
        except Exception as e:
            self.log_result("Advanced UI", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Test wizard creation (CREATE operation)
        try:
            wizard_data = {
                "name": "Audit Test Wizard",
                "type": "onboarding",
                "steps": ["welcome", "setup", "complete"]
            }
            response = requests.post(f"{self.base_url}/api/advanced-ui/wizard", json=wizard_data, headers=self.headers)
            self.log_result("Advanced UI", "/wizard", "POST", response.status_code == 200, response.status_code, "Wizard creation")
        except Exception as e:
            self.log_result("Advanced UI", "/wizard", "POST", False, None, f"Exception: {str(e)}")
        
        # Test wizard listing (potential routing conflict)
        try:
            response = requests.get(f"{self.base_url}/api/advanced-ui/wizard", headers=self.headers)
            self.log_result("Advanced UI", "/wizard", "GET", response.status_code == 200, response.status_code, 
                          "Wizard list - checking for routing conflicts" if response.status_code != 200 else "Wizard list working")
        except Exception as e:
            self.log_result("Advanced UI", "/wizard", "GET", False, None, f"Exception: {str(e)}")
        
        # Test goals system
        try:
            goals_data = {
                "user_id": "audit-test-user",
                "goals": ["increase_sales", "improve_engagement"]
            }
            response = requests.post(f"{self.base_url}/api/advanced-ui/goals", json=goals_data, headers=self.headers)
            self.log_result("Advanced UI", "/goals", "POST", response.status_code == 200, response.status_code, "Goals creation")
        except Exception as e:
            self.log_result("Advanced UI", "/goals", "POST", False, None, f"Exception: {str(e)}")

    def test_template_marketplace_access(self):
        """Test Template Marketplace Access - focus on validation issues"""
        print("\n🔍 TESTING TEMPLATE MARKETPLACE ACCESS CONTROL")
        
        # Health check
        try:
            response = requests.get(f"{self.base_url}/api/template-marketplace-access/health", headers=self.headers)
            self.log_result("Template Marketplace Access", "/health", "GET", response.status_code == 200, response.status_code, "Health check")
        except Exception as e:
            self.log_result("Template Marketplace Access", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Check seller access (validation issue area)
        try:
            response = requests.get(f"{self.base_url}/api/template-marketplace-access/seller-access", headers=self.headers)
            self.log_result("Template Marketplace Access", "/seller-access", "GET", response.status_code == 200, response.status_code, 
                          "Seller access validation - previously had issues" if response.status_code != 200 else "Seller access working")
        except Exception as e:
            self.log_result("Template Marketplace Access", "/seller-access", "GET", False, None, f"Exception: {str(e)}")
        
        # Check selling requirements
        try:
            response = requests.get(f"{self.base_url}/api/template-marketplace-access/selling-requirements", headers=self.headers)
            self.log_result("Template Marketplace Access", "/selling-requirements", "GET", response.status_code == 200, response.status_code, "Selling requirements")
        except Exception as e:
            self.log_result("Template Marketplace Access", "/selling-requirements", "GET", False, None, f"Exception: {str(e)}")
        
        # Check bundle requirements
        try:
            response = requests.get(f"{self.base_url}/api/template-marketplace-access/bundle-requirements", headers=self.headers)
            self.log_result("Template Marketplace Access", "/bundle-requirements", "GET", response.status_code == 200, response.status_code, "Bundle requirements")
        except Exception as e:
            self.log_result("Template Marketplace Access", "/bundle-requirements", "GET", False, None, f"Exception: {str(e)}")

    def test_ai_token_purchase_system(self):
        """Test AI Token Purchase System - focus on functionality issues"""
        print("\n🔍 TESTING AI TOKEN PURCHASE SYSTEM")
        
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
        
        # Check token balance
        try:
            response = requests.get(f"{self.base_url}/api/ai-token-purchase/balance", headers=self.headers)
            self.log_result("AI Token Purchase", "/balance", "GET", response.status_code == 200, response.status_code, "Token balance")
        except Exception as e:
            self.log_result("AI Token Purchase", "/balance", "GET", False, None, f"Exception: {str(e)}")
        
        # Test token purchase (core functionality)
        try:
            purchase_data = {
                "package": "starter_100",
                "payment_method": "test"
            }
            response = requests.post(f"{self.base_url}/api/ai-token-purchase/purchase", json=purchase_data, headers=self.headers)
            self.log_result("AI Token Purchase", "/purchase", "POST", response.status_code == 200, response.status_code, 
                          "Token purchase - previously had functionality issues" if response.status_code != 200 else "Token purchase working")
        except Exception as e:
            self.log_result("AI Token Purchase", "/purchase", "POST", False, None, f"Exception: {str(e)}")
        
        # Test usage history
        try:
            response = requests.get(f"{self.base_url}/api/ai-token-purchase/usage-history", headers=self.headers)
            self.log_result("AI Token Purchase", "/usage-history", "GET", response.status_code == 200, response.status_code, "Usage history")
        except Exception as e:
            self.log_result("AI Token Purchase", "/usage-history", "GET", False, None, f"Exception: {str(e)}")

    def verify_critical_revenue_systems(self):
        """Verify all critical revenue-generating systems are still working"""
        print("\n🔍 VERIFYING CRITICAL REVENUE-GENERATING SYSTEMS")
        
        # Workspace Subscription System
        try:
            response = requests.get(f"{self.base_url}/api/workspace-subscription/health", headers=self.headers)
            self.log_result("Workspace Subscription", "/health", "GET", response.status_code == 200, response.status_code, "Critical revenue system")
        except Exception as e:
            self.log_result("Workspace Subscription", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Usage Tracking System
        try:
            response = requests.get(f"{self.base_url}/api/usage-tracking/health", headers=self.headers)
            self.log_result("Usage Tracking", "/health", "GET", response.status_code == 200, response.status_code, "Critical revenue system")
        except Exception as e:
            self.log_result("Usage Tracking", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Enterprise Revenue Tracking
        try:
            response = requests.get(f"{self.base_url}/api/enterprise-revenue/health", headers=self.headers)
            self.log_result("Enterprise Revenue", "/health", "GET", response.status_code == 200, response.status_code, "Critical revenue system")
        except Exception as e:
            self.log_result("Enterprise Revenue", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Enhanced Escrow with Transaction Fees
        try:
            response = requests.get(f"{self.base_url}/api/escrow/health", headers=self.headers)
            self.log_result("Enhanced Escrow", "/health", "GET", response.status_code == 200, response.status_code, "Critical revenue system")
        except Exception as e:
            self.log_result("Enhanced Escrow", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Launch Pricing System
        try:
            response = requests.get(f"{self.base_url}/api/launch-pricing/health", headers=self.headers)
            self.log_result("Launch Pricing", "/health", "GET", response.status_code == 200, response.status_code, "Critical revenue system")
        except Exception as e:
            self.log_result("Launch Pricing", "/health", "GET", False, None, f"Exception: {str(e)}")
        
        # Admin Pricing Management System
        try:
            response = requests.get(f"{self.base_url}/api/admin-pricing/health", headers=self.headers)
            self.log_result("Admin Pricing", "/health", "GET", response.status_code == 200, response.status_code, "Critical revenue system")
        except Exception as e:
            self.log_result("Admin Pricing", "/health", "GET", False, None, f"Exception: {str(e)}")

    def run_focused_audit(self):
        """Run the focused audit"""
        print("🚀 STARTING FOCUSED BACKEND AUDIT")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with audit.")
            return False
        
        # Test systems with potential issues
        self.test_website_builder()
        self.test_advanced_ui_system()
        self.test_template_marketplace_access()
        self.test_ai_token_purchase_system()
        
        # Verify critical revenue systems are still working
        self.verify_critical_revenue_systems()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FOCUSED AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        # Analyze results by system
        systems = {}
        for result in self.test_results:
            system = result["system"]
            if system not in systems:
                systems[system] = {"passed": 0, "failed": 0, "total": 0}
            systems[system]["total"] += 1
            if result["success"]:
                systems[system]["passed"] += 1
            else:
                systems[system]["failed"] += 1
        
        print("\n📈 SYSTEM-BY-SYSTEM RESULTS:")
        for system, stats in systems.items():
            success_rate = (stats["passed"] / stats["total"]) * 100
            status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            print(f"{status} {system}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        return True

if __name__ == "__main__":
    auditor = FocusedAuditor()
    auditor.run_focused_audit()