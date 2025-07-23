#!/usr/bin/env python3
"""
Comprehensive Backend Testing for SEVENTEENTH WAVE - Advanced Webhook & Event Management System
Testing all webhook system functionality including registry, CRUD operations, event management, and analytics
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Add the backend directory to the Python path
sys.path.append('/app/backend')

class WebhookSystemTester:
    def __init__(self):
        # Get backend URL from environment
        self.base_url = "https://227a6971-09fc-47c6-b443-58c2c19d4c11.preview.emergentagent.com"
        self.api_base = f"{self.base_url}/api"
        self.headers = {"Content-Type": "application/json"}
        self.auth_token = None
        self.test_results = []
        self.webhook_id = None
        
    def log_result(self, test_name, success, details="", response_size=0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_size": response_size,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_size > 0:
            print(f"   Response size: {response_size} chars")
        print()

    def authenticate(self):
        """Authenticate with the backend"""
        print("🔐 Authenticating with backend...")
        
        auth_data = {
            "username": "tmonnens@outlook.com",
            "password": "Voetballen5"
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/auth/login",
                data=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.auth_token}"
                self.log_result("Authentication", True, f"Token obtained successfully")
                return True
            else:
                self.log_result("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False

    def test_webhook_registry(self):
        """Test GET /api/webhooks/registry - Webhook Registry & Event Catalog"""
        print("📋 Testing Webhook Registry & Event Catalog...")
        
        try:
            response = requests.get(
                f"{self.api_base}/webhooks/registry",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                # Verify registry structure
                if (data.get("success") and 
                    "data" in data and
                    "available_events" in data["data"] and
                    "webhook_endpoints" in data["data"] and
                    "delivery_stats" in data["data"]):
                    
                    registry_data = data["data"]
                    events = registry_data["available_events"]
                    
                    # Check event categories
                    expected_categories = ["user_events", "business_events", "system_events"]
                    categories_found = all(cat in events for cat in expected_categories)
                    
                    # Check delivery stats
                    stats = registry_data["delivery_stats"]
                    stats_complete = all(key in stats for key in [
                        "total_webhooks", "active_webhooks", "total_events_24h", 
                        "successful_deliveries_24h", "reliability_score"
                    ])
                    
                    if categories_found and stats_complete:
                        self.log_result(
                            "Webhook Registry & Event Catalog", 
                            True, 
                            f"Registry loaded with {len(events)} event categories, delivery stats included",
                            len(response_text)
                        )
                    else:
                        self.log_result(
                            "Webhook Registry & Event Catalog", 
                            False, 
                            "Registry structure incomplete - missing categories or stats"
                        )
                else:
                    self.log_result(
                        "Webhook Registry & Event Catalog", 
                        False, 
                        "Invalid registry response structure"
                    )
            else:
                self.log_result(
                    "Webhook Registry & Event Catalog", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Webhook Registry & Event Catalog", False, f"Exception: {str(e)}")

    def test_get_user_webhooks(self):
        """Test GET /api/webhooks - Get User Webhooks"""
        print("📝 Testing Get User Webhooks...")
        
        try:
            response = requests.get(
                f"{self.api_base}/webhooks",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data and
                    "webhooks" in data["data"]):
                    
                    webhooks_data = data["data"]
                    webhooks = webhooks_data["webhooks"]
                    
                    self.log_result(
                        "Get User Webhooks", 
                        True, 
                        f"Retrieved {len(webhooks)} webhooks with filtering support",
                        len(response_text)
                    )
                else:
                    self.log_result("Get User Webhooks", False, "Invalid webhooks response structure")
            else:
                self.log_result(
                    "Get User Webhooks", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get User Webhooks", False, f"Exception: {str(e)}")

    def test_create_webhook(self):
        """Test POST /api/webhooks - Create Webhook"""
        print("➕ Testing Create Webhook...")
        
        try:
            webhook_data = {
                "name": "Test Business Webhook",
                "url": "https://api.example.com/webhooks/test",
                "events": json.dumps(["user.created", "order.completed", "payment.failed"]),
                "retry_config": json.dumps({
                    "max_retries": 5,
                    "backoff_strategy": "exponential",
                    "timeout_seconds": 30
                }),
                "security_config": json.dumps({
                    "signature_verification": True,
                    "ip_whitelist": ["192.168.1.100"]
                }),
                "custom_headers": json.dumps({
                    "X-Custom-Header": "webhook-test",
                    "X-API-Version": "v1"
                }),
                "rate_limiting": json.dumps({
                    "enabled": True,
                    "requests_per_minute": 100
                })
            }
            
            response = requests.post(
                f"{self.api_base}/webhooks",
                data=webhook_data,
                headers={k: v for k, v in self.headers.items() if k != "Content-Type"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data and
                    "webhook_id" in data["data"]):
                    
                    webhook_info = data["data"]
                    self.webhook_id = webhook_info["webhook_id"]  # Store for later tests
                    
                    # Verify webhook creation details
                    required_fields = ["webhook_id", "name", "url", "events", "secret_key", "status"]
                    fields_present = all(field in webhook_info for field in required_fields)
                    
                    if fields_present:
                        self.log_result(
                            "Create Webhook", 
                            True, 
                            f"Webhook created successfully with ID: {self.webhook_id}",
                            len(response_text)
                        )
                    else:
                        self.log_result("Create Webhook", False, "Webhook creation response missing required fields")
                else:
                    self.log_result("Create Webhook", False, "Invalid webhook creation response")
            else:
                self.log_result(
                    "Create Webhook", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Create Webhook", False, f"Exception: {str(e)}")

    def test_get_webhook_details(self):
        """Test GET /api/webhooks/{webhook_id} - Get Webhook Details"""
        print("🔍 Testing Get Webhook Details...")
        
        if not self.webhook_id:
            self.log_result("Get Webhook Details", False, "No webhook ID available from creation test")
            return
        
        try:
            response = requests.get(
                f"{self.api_base}/webhooks/{self.webhook_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data):
                    
                    webhook_details = data["data"]
                    
                    # Verify detailed webhook information
                    required_fields = ["id", "name", "url", "events", "status", "retry_policy", 
                                     "security", "rate_limiting", "monitoring", "statistics"]
                    fields_present = all(field in webhook_details for field in required_fields)
                    
                    if fields_present:
                        self.log_result(
                            "Get Webhook Details", 
                            True, 
                            f"Retrieved detailed webhook information with comprehensive configuration",
                            len(response_text)
                        )
                    else:
                        self.log_result("Get Webhook Details", False, "Webhook details response missing required fields")
                else:
                    self.log_result("Get Webhook Details", False, "Invalid webhook details response")
            else:
                self.log_result(
                    "Get Webhook Details", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Webhook Details", False, f"Exception: {str(e)}")

    def test_update_webhook(self):
        """Test PUT /api/webhooks/{webhook_id} - Update Webhook"""
        print("✏️ Testing Update Webhook...")
        
        if not self.webhook_id:
            self.log_result("Update Webhook", False, "No webhook ID available from creation test")
            return
        
        try:
            update_data = {
                "name": "Updated Test Webhook",
                "status": "active",
                "events": json.dumps(["user.created", "order.completed"])
            }
            
            response = requests.put(
                f"{self.api_base}/webhooks/{self.webhook_id}",
                data=update_data,
                headers={k: v for k, v in self.headers.items() if k != "Content-Type"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data and
                    data["data"]["name"] == "Updated Test Webhook"):
                    
                    self.log_result(
                        "Update Webhook", 
                        True, 
                        "Webhook updated successfully with new configuration",
                        len(response_text)
                    )
                else:
                    self.log_result("Update Webhook", False, "Webhook update did not apply changes correctly")
            else:
                self.log_result(
                    "Update Webhook", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Update Webhook", False, f"Exception: {str(e)}")

    def test_webhook_test(self):
        """Test POST /api/webhooks/{webhook_id}/test - Test Webhook"""
        print("🧪 Testing Webhook Test Functionality...")
        
        if not self.webhook_id:
            self.log_result("Webhook Test", False, "No webhook ID available from creation test")
            return
        
        try:
            test_data = {
                "test_event": "user.created",
                "custom_payload": json.dumps({
                    "user_id": "test-user-123",
                    "email": "test@example.com",
                    "name": "Test User",
                    "subscription_tier": "professional"
                })
            }
            
            response = requests.post(
                f"{self.api_base}/webhooks/{self.webhook_id}/test",
                data=test_data,
                headers={k: v for k, v in self.headers.items() if k != "Content-Type"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data and
                    "delivery_id" in data["data"]):
                    
                    test_result = data["data"]
                    
                    self.log_result(
                        "Webhook Test", 
                        True, 
                        f"Webhook test initiated successfully with delivery ID: {test_result['delivery_id']}",
                        len(response_text)
                    )
                else:
                    self.log_result("Webhook Test", False, "Invalid webhook test response")
            else:
                self.log_result(
                    "Webhook Test", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Webhook Test", False, f"Exception: {str(e)}")

    def test_webhook_deliveries(self):
        """Test GET /api/webhooks/{webhook_id}/deliveries - Get Webhook Deliveries"""
        print("📦 Testing Get Webhook Deliveries...")
        
        if not self.webhook_id:
            self.log_result("Get Webhook Deliveries", False, "No webhook ID available from creation test")
            return
        
        try:
            response = requests.get(
                f"{self.api_base}/webhooks/{self.webhook_id}/deliveries?limit=20&status_filter=all",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data and
                    "deliveries" in data["data"]):
                    
                    deliveries_data = data["data"]
                    deliveries = deliveries_data["deliveries"]
                    
                    # Verify delivery history structure
                    required_fields = ["total_deliveries", "success_count", "failed_count", "success_rate"]
                    fields_present = all(field in deliveries_data for field in required_fields)
                    
                    if fields_present:
                        self.log_result(
                            "Get Webhook Deliveries", 
                            True, 
                            f"Retrieved {len(deliveries)} delivery records with analytics",
                            len(response_text)
                        )
                    else:
                        self.log_result("Get Webhook Deliveries", False, "Delivery history response missing required fields")
                else:
                    self.log_result("Get Webhook Deliveries", False, "Invalid webhook deliveries response")
            else:
                self.log_result(
                    "Get Webhook Deliveries", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Webhook Deliveries", False, f"Exception: {str(e)}")

    def test_webhook_analytics(self):
        """Test GET /api/webhooks/{webhook_id}/analytics - Get Webhook Analytics"""
        print("📊 Testing Get Webhook Analytics...")
        
        if not self.webhook_id:
            self.log_result("Get Webhook Analytics", False, "No webhook ID available from creation test")
            return
        
        try:
            response = requests.get(
                f"{self.api_base}/webhooks/{self.webhook_id}/analytics?timeframe=30d",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data):
                    
                    analytics = data["data"]
                    
                    # Verify analytics structure
                    required_sections = ["delivery_stats", "event_breakdown", "failure_analysis", 
                                       "performance_trends", "recommendations"]
                    sections_present = all(section in analytics for section in required_sections)
                    
                    if sections_present:
                        self.log_result(
                            "Get Webhook Analytics", 
                            True, 
                            f"Retrieved comprehensive analytics with performance metrics and recommendations",
                            len(response_text)
                        )
                    else:
                        self.log_result("Get Webhook Analytics", False, "Analytics response missing required sections")
                else:
                    self.log_result("Get Webhook Analytics", False, "Invalid webhook analytics response")
            else:
                self.log_result(
                    "Get Webhook Analytics", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Webhook Analytics", False, f"Exception: {str(e)}")

    def test_event_catalog(self):
        """Test GET /api/webhooks/events/catalog - Get Event Catalog"""
        print("📚 Testing Get Event Catalog...")
        
        try:
            response = requests.get(
                f"{self.api_base}/webhooks/events/catalog",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data and
                    "event_categories" in data["data"]):
                    
                    catalog = data["data"]
                    categories = catalog["event_categories"]
                    
                    # Verify event catalog structure
                    expected_categories = ["user_events", "business_events", "system_events"]
                    categories_found = all(cat in categories for cat in expected_categories)
                    
                    if categories_found and "total_events" in catalog:
                        self.log_result(
                            "Get Event Catalog", 
                            True, 
                            f"Retrieved event catalog with {catalog['total_events']} total events across categories",
                            len(response_text)
                        )
                    else:
                        self.log_result("Get Event Catalog", False, "Event catalog structure incomplete")
                else:
                    self.log_result("Get Event Catalog", False, "Invalid event catalog response")
            else:
                self.log_result(
                    "Get Event Catalog", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Event Catalog", False, f"Exception: {str(e)}")

    def test_validate_payload(self):
        """Test POST /api/webhooks/validate-payload - Validate Webhook Payload"""
        print("✅ Testing Validate Webhook Payload...")
        
        try:
            validation_data = {
                "event_type": "user.created",
                "payload": json.dumps({
                    "user_id": "test-user-123",
                    "email": "test@example.com",
                    "name": "Test User",
                    "subscription_tier": "professional",
                    "created_at": "2025-01-08T10:00:00Z"
                })
            }
            
            response = requests.post(
                f"{self.api_base}/webhooks/validate-payload",
                data=validation_data,
                headers={k: v for k, v in self.headers.items() if k != "Content-Type"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data and
                    "valid" in data["data"]):
                    
                    validation_result = data["data"]
                    
                    # Verify validation result structure
                    required_fields = ["valid", "event_type", "payload_size_bytes", "missing_fields", "invalid_fields"]
                    fields_present = all(field in validation_result for field in required_fields)
                    
                    if fields_present:
                        self.log_result(
                            "Validate Webhook Payload", 
                            True, 
                            f"Payload validation completed - Valid: {validation_result['valid']}",
                            len(response_text)
                        )
                    else:
                        self.log_result("Validate Webhook Payload", False, "Validation response missing required fields")
                else:
                    self.log_result("Validate Webhook Payload", False, "Invalid payload validation response")
            else:
                self.log_result(
                    "Validate Webhook Payload", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Validate Webhook Payload", False, f"Exception: {str(e)}")

    def test_system_health(self):
        """Test GET /api/webhooks/system/health - Get System Health"""
        print("🏥 Testing Get System Health...")
        
        try:
            response = requests.get(
                f"{self.api_base}/webhooks/system/health",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data):
                    
                    health = data["data"]
                    
                    # Verify health status structure
                    required_fields = ["status", "uptime", "active_webhooks", "system_load", "components"]
                    fields_present = all(field in health for field in required_fields)
                    
                    if fields_present and health["status"] == "healthy":
                        self.log_result(
                            "Get System Health", 
                            True, 
                            f"System health: {health['status']}, Uptime: {health['uptime']}",
                            len(response_text)
                        )
                    else:
                        self.log_result("Get System Health", False, "System health response incomplete or unhealthy")
                else:
                    self.log_result("Get System Health", False, "Invalid system health response")
            else:
                self.log_result(
                    "Get System Health", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get System Health", False, f"Exception: {str(e)}")

    def test_webhook_stats_overview(self):
        """Test GET /api/webhooks/stats/overview - Get Webhook Stats Overview"""
        print("📈 Testing Get Webhook Stats Overview...")
        
        try:
            response = requests.get(
                f"{self.api_base}/webhooks/stats/overview",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if (data.get("success") and 
                    "data" in data):
                    
                    stats = data["data"]
                    
                    # Verify stats overview structure
                    required_fields = ["total_webhooks", "active_webhooks", "deliveries_today", 
                                     "success_rate_today", "quota_usage"]
                    fields_present = all(field in stats for field in required_fields)
                    
                    if fields_present:
                        self.log_result(
                            "Get Webhook Stats Overview", 
                            True, 
                            f"Stats overview: {stats['total_webhooks']} webhooks, {stats['success_rate_today']}% success rate",
                            len(response_text)
                        )
                    else:
                        self.log_result("Get Webhook Stats Overview", False, "Stats overview response missing required fields")
                else:
                    self.log_result("Get Webhook Stats Overview", False, "Invalid webhook stats response")
            else:
                self.log_result(
                    "Get Webhook Stats Overview", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Get Webhook Stats Overview", False, f"Exception: {str(e)}")

    def test_delete_webhook(self):
        """Test DELETE /api/webhooks/{webhook_id} - Delete Webhook"""
        print("🗑️ Testing Delete Webhook...")
        
        if not self.webhook_id:
            self.log_result("Delete Webhook", False, "No webhook ID available from creation test")
            return
        
        try:
            response = requests.delete(
                f"{self.api_base}/webhooks/{self.webhook_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = response.text
                
                if data.get("success"):
                    self.log_result(
                        "Delete Webhook", 
                        True, 
                        f"Webhook {self.webhook_id} deleted successfully",
                        len(response_text)
                    )
                else:
                    self.log_result("Delete Webhook", False, "Webhook deletion response indicates failure")
            else:
                self.log_result(
                    "Delete Webhook", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Delete Webhook", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all webhook system tests"""
        print("🌊 SEVENTEENTH WAVE - ADVANCED WEBHOOK & EVENT MANAGEMENT SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"API Base: {self.api_base}")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        print("\n🔧 TESTING WEBHOOK SYSTEM FUNCTIONALITY")
        print("-" * 50)
        
        # Core webhook system tests
        self.test_webhook_registry()
        self.test_get_user_webhooks()
        self.test_create_webhook()
        self.test_get_webhook_details()
        self.test_update_webhook()
        self.test_webhook_test()
        self.test_webhook_deliveries()
        self.test_webhook_analytics()
        
        # Event management tests
        self.test_event_catalog()
        self.test_validate_payload()
        
        # System monitoring tests
        self.test_system_health()
        self.test_webhook_stats_overview()
        
        # Cleanup test
        self.test_delete_webhook()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🌊 SEVENTEENTH WAVE WEBHOOK SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show all results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print("🎉 WEBHOOK SYSTEM TESTING: EXCELLENT PERFORMANCE")
        elif success_rate >= 75:
            print("✅ WEBHOOK SYSTEM TESTING: GOOD PERFORMANCE")
        elif success_rate >= 50:
            print("⚠️ WEBHOOK SYSTEM TESTING: NEEDS IMPROVEMENT")
        else:
            print("❌ WEBHOOK SYSTEM TESTING: CRITICAL ISSUES FOUND")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = WebhookSystemTester()
    tester.run_all_tests()