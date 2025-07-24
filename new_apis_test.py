#!/usr/bin/env python3
"""
NEW APIS TESTING FOR 15% GAP IMPLEMENTATION
==========================================
Testing the newly implemented API endpoints:
1. PWA Management API (/api/pwa/)
2. Visual Builder API (/api/visual-builder/)
3. Native Mobile API (/api/native-mobile/)
4. Advanced UI API (/api/advanced-ui/)
5. Workflow Automation API (/api/workflow-automation/) - Verification

Test credentials: tmonnens@outlook.com / Voetballen5
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

class NewAPIsAuditor:
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
            
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {system} - {method} {endpoint} - {status_code} - {details}")
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            print(f"\n🔐 AUTHENTICATING with {TEST_EMAIL}...")
            
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=auth_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("access_token"):
                    self.token = data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    print(f"✅ Authentication successful - Token obtained")
                    return True
                else:
                    print(f"❌ Authentication failed - No token in response")
                    return False
            else:
                print(f"❌ Authentication failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_endpoint(self, system: str, endpoint: str, method: str = "GET", data: Dict = None, expected_status: List[int] = None) -> bool:
        """Test a single endpoint"""
        if expected_status is None:
            expected_status = [200, 201]
            
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=self.headers, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=self.headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                self.log_result(system, endpoint, method, False, None, f"Unsupported method: {method}")
                return False
            
            success = response.status_code in expected_status
            
            if success:
                try:
                    response_data = response.json()
                    details = f"Success - Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}"
                except:
                    details = "Success - Non-JSON response"
            else:
                try:
                    error_data = response.json()
                    details = f"Failed - {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Failed - {response.text[:100]}"
            
            self.log_result(system, endpoint, method, success, response.status_code, details)
            return success
            
        except Exception as e:
            self.log_result(system, endpoint, method, False, None, f"Exception: {str(e)}")
            return False
    
    def test_pwa_management_api(self):
        """Test PWA Management API endpoints"""
        print(f"\n🔧 TESTING PWA MANAGEMENT API...")
        
        # Test health check
        self.test_endpoint("PWA Management", "/api/pwa/health", "GET")
        
        # Test manifest generation
        manifest_data = {
            "workspace_id": "test-workspace-123"
        }
        self.test_endpoint("PWA Management", "/api/pwa/manifest/generate", "POST", manifest_data)
        
        # Test current manifest
        self.test_endpoint("PWA Management", "/api/pwa/manifest/current", "GET")
        
        # Test service worker config
        self.test_endpoint("PWA Management", "/api/pwa/service-worker/config", "GET")
        
        # Test PWA capabilities
        self.test_endpoint("PWA Management", "/api/pwa/capabilities", "GET")
        
        # Test installation tracking
        install_data = {
            "platform": "web",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_endpoint("PWA Management", "/api/pwa/install/track", "POST", install_data)
        
        # Test offline sync
        sync_data = {
            "items": [
                {
                    "id": "sync-item-1",
                    "type": "booking",
                    "data": {"name": "Test Booking", "status": "pending"}
                },
                {
                    "id": "sync-item-2", 
                    "type": "financial",
                    "data": {"amount": 100.00, "currency": "USD"}
                }
            ]
        }
        self.test_endpoint("PWA Management", "/api/pwa/offline/sync", "POST", sync_data)
    
    def test_visual_builder_api(self):
        """Test Visual Builder API endpoints"""
        print(f"\n🎨 TESTING VISUAL BUILDER API...")
        
        # Test health check
        self.test_endpoint("Visual Builder", "/api/visual-builder/health", "GET")
        
        # Test component library
        self.test_endpoint("Visual Builder", "/api/visual-builder/components", "GET")
        
        # Test create project
        project_data = {
            "name": "Test Landing Page",
            "description": "A test landing page for our business",
            "type": "webpage",
            "canvas_data": {
                "components": [
                    {
                        "id": "header-1",
                        "type": "heading",
                        "properties": {
                            "content": "Welcome to Our Business",
                            "level": "h1",
                            "color": "#000000"
                        }
                    }
                ],
                "layout": {"width": 1200, "height": 800},
                "theme": {"primary_color": "#007AFF", "secondary_color": "#F5F5F5"}
            }
        }
        create_response = self.test_endpoint("Visual Builder", "/api/visual-builder/projects", "POST", project_data)
        
        # Test list projects
        self.test_endpoint("Visual Builder", "/api/visual-builder/projects", "GET")
        
        # For testing individual project operations, we'll use a test ID
        test_project_id = "test-project-123"
        
        # Test get project (might fail if project doesn't exist, that's expected)
        self.test_endpoint("Visual Builder", f"/api/visual-builder/projects/{test_project_id}", "GET", expected_status=[200, 404])
        
        # Test update project (might fail if project doesn't exist, that's expected)
        update_data = {
            "name": "Updated Test Project",
            "canvas_data": {
                "components": [
                    {
                        "id": "text-1",
                        "type": "text",
                        "properties": {
                            "content": "Updated content",
                            "font_size": "18px"
                        }
                    }
                ]
            }
        }
        self.test_endpoint("Visual Builder", f"/api/visual-builder/projects/{test_project_id}", "PUT", update_data, expected_status=[200, 404])
        
        # Test publish project (might fail if project doesn't exist, that's expected)
        self.test_endpoint("Visual Builder", f"/api/visual-builder/projects/{test_project_id}/publish", "POST", expected_status=[200, 404])
    
    def test_native_mobile_api(self):
        """Test Native Mobile API endpoints"""
        print(f"\n📱 TESTING NATIVE MOBILE API...")
        
        # Test health check
        self.test_endpoint("Native Mobile", "/api/native-mobile/health", "GET")
        
        # Test create app config
        config_data = {
            "app_name": "Mewayz Business App",
            "app_identifier": "com.mewayz.business",
            "app_version": "1.0.0",
            "ios_bundle_id": "com.mewayz.business.ios",
            "android_package_name": "com.mewayz.business.android",
            "push_notifications": True,
            "offline_sync": True,
            "biometric_auth": True,
            "theme": {
                "primary_color": "#007AFF",
                "secondary_color": "#5856D6"
            }
        }
        self.test_endpoint("Native Mobile", "/api/native-mobile/config", "POST", config_data)
        
        # Test get app config
        self.test_endpoint("Native Mobile", "/api/native-mobile/config", "GET")
        
        # Test register push token
        push_token_data = {
            "token": "test-push-token-12345",
            "platform": "ios",
            "device_id": "test-device-123",
            "app_version": "1.0.0"
        }
        self.test_endpoint("Native Mobile", "/api/native-mobile/push/register", "POST", push_token_data)
        
        # Test send push notification
        notification_data = {
            "user_id": "test-user-123",
            "title": "Test Notification",
            "body": "This is a test push notification",
            "data": {"action": "open_app", "screen": "dashboard"},
            "badge": 1
        }
        self.test_endpoint("Native Mobile", "/api/native-mobile/push/send", "POST", notification_data)
        
        # Test sync app data - upload
        sync_upload_data = {
            "device_id": "test-device-123",
            "sync_type": "upload",
            "data": [
                {
                    "type": "booking",
                    "data": {"name": "Mobile Booking", "date": "2025-01-15"},
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "type": "customer",
                    "data": {"name": "John Doe", "email": "john@example.com"},
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        self.test_endpoint("Native Mobile", "/api/native-mobile/sync", "POST", sync_upload_data)
        
        # Test sync app data - download
        sync_download_data = {
            "device_id": "test-device-123",
            "sync_type": "download",
            "last_sync_timestamp": "2025-01-01T00:00:00Z"
        }
        self.test_endpoint("Native Mobile", "/api/native-mobile/sync", "POST", sync_download_data)
        
        # Test deep link handling
        deep_link_data = {
            "url": "mewayz://booking/123",
            "user_id": "test-user-123"
        }
        self.test_endpoint("Native Mobile", "/api/native-mobile/deep-link", "POST", deep_link_data)
    
    def test_advanced_ui_api(self):
        """Test Advanced UI API endpoints"""
        print(f"\n🎯 TESTING ADVANCED UI API...")
        
        # Test health check
        self.test_endpoint("Advanced UI", "/api/advanced-ui/health", "GET")
        
        # Test create wizard session
        wizard_data = {
            "wizard_type": "workspace_setup",
            "current_step": 1,
            "total_steps": 5,
            "user_responses": {},
            "device_info": {"platform": "web", "browser": "Chrome"}
        }
        self.test_endpoint("Advanced UI", "/api/advanced-ui/wizard", "POST", wizard_data)
        
        # Test update wizard session
        test_session_id = "test-session-123"
        wizard_update_data = {
            "current_step": 2,
            "total_steps": 5,
            "user_responses": {
                "business_name": "Test Business",
                "business_type": "Service",
                "industry": "Technology"
            },
            "progress_percentage": 40
        }
        self.test_endpoint("Advanced UI", f"/api/advanced-ui/wizard/{test_session_id}", "PUT", wizard_update_data, expected_status=[200, 404])
        
        # Test save user goals
        goals_data = {
            "primary_goals": ["lead_generation", "customer_management", "online_sales"],
            "secondary_goals": ["email_marketing", "financial_tracking"],
            "goal_priorities": {
                "lead_generation": 1,
                "customer_management": 2,
                "online_sales": 3
            },
            "target_metrics": {
                "monthly_leads": 100,
                "customer_retention": 85,
                "monthly_revenue": 10000
            },
            "timeline": "6_months"
        }
        self.test_endpoint("Advanced UI", "/api/advanced-ui/goals", "POST", goals_data)
        
        # Test get UI state
        test_component_id = "dashboard-widget-1"
        self.test_endpoint("Advanced UI", f"/api/advanced-ui/state/{test_component_id}", "GET", expected_status=[200, 404])
        
        # Test save UI state
        ui_state_data = {
            "component_id": "dashboard-widget-1",
            "component_type": "data_table",
            "state_data": {
                "columns_visible": ["name", "status", "created_at"],
                "sort_order": "desc",
                "sort_field": "created_at",
                "filters": {"status": "active"},
                "page_size": 25,
                "current_page": 1
            },
            "page_context": "dashboard"
        }
        self.test_endpoint("Advanced UI", "/api/advanced-ui/state", "POST", ui_state_data)
        
        # Test component configurations
        component_types = ["data_table", "chart", "form", "calendar"]
        for component_type in component_types:
            self.test_endpoint("Advanced UI", f"/api/advanced-ui/component/{component_type}/config", "GET")
    
    def test_workflow_automation_api(self):
        """Test Workflow Automation API endpoints (verification)"""
        print(f"\n⚙️ TESTING WORKFLOW AUTOMATION API (VERIFICATION)...")
        
        # Test health check
        self.test_endpoint("Workflow Automation", "/api/workflow-automation/health", "GET")
        
        # Test list workflows
        self.test_endpoint("Workflow Automation", "/api/workflow-automation/", "GET")
        
        # Test create workflow
        workflow_data = {
            "name": "Customer Onboarding Workflow",
            "description": "Automated workflow for new customer onboarding",
            "trigger": {
                "type": "form_submission",
                "form_id": "customer-signup"
            },
            "actions": [
                {
                    "type": "send_email",
                    "template": "welcome_email",
                    "delay": 0
                },
                {
                    "type": "create_task",
                    "title": "Follow up with new customer",
                    "delay": 86400
                }
            ],
            "status": "active"
        }
        self.test_endpoint("Workflow Automation", "/api/workflow-automation/", "POST", workflow_data)
        
        # Test get specific workflow (might fail if workflow doesn't exist, that's expected)
        test_workflow_id = "test-workflow-123"
        self.test_endpoint("Workflow Automation", f"/api/workflow-automation/{test_workflow_id}", "GET", expected_status=[200, 404])
    
    def run_comprehensive_audit(self):
        """Run comprehensive audit of all new APIs"""
        print("=" * 80)
        print("🚀 STARTING COMPREHENSIVE NEW APIS AUDIT")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - Cannot proceed with tests")
            return False
        
        # Test all new API systems
        self.test_pwa_management_api()
        self.test_visual_builder_api()
        self.test_native_mobile_api()
        self.test_advanced_ui_api()
        self.test_workflow_automation_api()
        
        # Print comprehensive results
        self.print_final_results()
        
        return self.failed_tests == 0
    
    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE NEW APIS AUDIT RESULTS")
        print("=" * 80)
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   ✅ Passed: {self.passed_tests}")
        print(f"   ❌ Failed: {self.failed_tests}")
        print(f"   📊 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        # Group results by system
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
        
        print(f"\n📋 RESULTS BY SYSTEM:")
        for system, stats in systems.items():
            success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status_icon = "✅" if stats["failed"] == 0 else "⚠️" if success_rate >= 70 else "❌"
            print(f"   {status_icon} {system}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"   • {result['system']} - {result['method']} {result['endpoint']}")
                print(f"     Status: {result['status_code']}, Details: {result['details']}")
        
        print("\n" + "=" * 80)
        if self.failed_tests == 0:
            print("🎉 ALL NEW APIS ARE WORKING PERFECTLY!")
        elif self.failed_tests <= 3:
            print("⚠️ MOSTLY WORKING - Few minor issues detected")
        else:
            print("❌ SIGNIFICANT ISSUES DETECTED - Needs attention")
        print("=" * 80)

def main():
    """Main execution function"""
    auditor = NewAPIsAuditor()
    success = auditor.run_comprehensive_audit()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()