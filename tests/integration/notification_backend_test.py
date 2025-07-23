#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for Mewayz Platform
Focus: Advanced Notification & Communication System (Thirteenth Wave)
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com/api"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class NotificationSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.created_template_id = None
        self.created_notification_id = None
        
    def log_test(self, test_name, success, response_data=None, error=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response_size": len(str(response_data)) if response_data else 0,
            "error": str(error) if error else None
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")
        if response_data and success:
            print(f"   Response size: {result['response_size']} chars")
    
    def authenticate(self):
        """Authenticate with the backend"""
        try:
            auth_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_test("Authentication", True, token_data)
                return True
            else:
                self.log_test("Authentication", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, error=str(e))
            return False
    
    def test_get_notification_channels(self):
        """Test GET /notifications/channels"""
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications/channels")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /notifications/channels", True, data)
                return True
            else:
                self.log_test("GET /notifications/channels", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /notifications/channels", False, error=str(e))
            return False
    
    def test_send_notification(self):
        """Test POST /notifications/send"""
        try:
            notification_data = {
                "title": "Test Notification",
                "message": "This is a test notification from the Mewayz platform notification system.",
                "channels": json.dumps(["email", "push"]),
                "recipients": json.dumps(["test@example.com", "user@mewayz.com"]),
                "category": "system",
                "priority": "normal"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/notifications/send",
                data=notification_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data", {}).get("notification_id"):
                    self.created_notification_id = data["data"]["notification_id"]
                self.log_test("POST /notifications/send", True, data)
                return True
            else:
                self.log_test("POST /notifications/send", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /notifications/send", False, error=str(e))
            return False
    
    def test_get_notification_history(self):
        """Test GET /notifications/history"""
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications/history?limit=20&category=all&status=all")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /notifications/history", True, data)
                return True
            else:
                self.log_test("GET /notifications/history", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /notifications/history", False, error=str(e))
            return False
    
    def test_get_notification_analytics(self):
        """Test GET /notifications/analytics/overview"""
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications/analytics/overview?timeframe=30d")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /notifications/analytics/overview", True, data)
                return True
            else:
                self.log_test("GET /notifications/analytics/overview", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /notifications/analytics/overview", False, error=str(e))
            return False
    
    def test_create_notification_template(self):
        """Test POST /notifications/templates"""
        try:
            template_data = {
                "name": "Welcome Template",
                "title": "Welcome to {company_name}!",
                "message": "Hello {user_name}, welcome to {company_name}! We're excited to have you on board. Your account is now active and ready to use.",
                "category": "business",
                "default_channels": json.dumps(["email", "push"]),
                "variables": json.dumps(["user_name", "company_name"])
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/notifications/templates",
                data=template_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data", {}).get("template_id"):
                    self.created_template_id = data["data"]["template_id"]
                self.log_test("POST /notifications/templates", True, data)
                return True
            else:
                self.log_test("POST /notifications/templates", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /notifications/templates", False, error=str(e))
            return False
    
    def test_get_notification_templates(self):
        """Test GET /notifications/templates"""
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications/templates")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /notifications/templates", True, data)
                return True
            else:
                self.log_test("GET /notifications/templates", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /notifications/templates", False, error=str(e))
            return False
    
    def test_send_template_notification(self):
        """Test POST /notifications/templates/{template_id}/send"""
        if not self.created_template_id:
            self.log_test("POST /notifications/templates/{template_id}/send", False, error="No template ID available")
            return False
            
        try:
            template_send_data = {
                "recipients": json.dumps(["john.doe@example.com", "jane.smith@mewayz.com"]),
                "variables": json.dumps({
                    "user_name": "John Doe",
                    "company_name": "Mewayz Platform"
                })
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/notifications/templates/{self.created_template_id}/send",
                data=template_send_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("POST /notifications/templates/{template_id}/send", True, data)
                return True
            else:
                self.log_test("POST /notifications/templates/{template_id}/send", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /notifications/templates/{template_id}/send", False, error=str(e))
            return False
    
    def test_get_notification_preferences(self):
        """Test GET /notifications/preferences"""
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications/preferences")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /notifications/preferences", True, data)
                return True
            else:
                self.log_test("GET /notifications/preferences", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /notifications/preferences", False, error=str(e))
            return False
    
    def test_update_notification_preferences(self):
        """Test POST /notifications/preferences"""
        try:
            preferences_data = {
                "email_enabled": "true",
                "sms_enabled": "true", 
                "push_enabled": "true",
                "categories": json.dumps(["system", "business", "security"]),
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/notifications/preferences",
                data=preferences_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("POST /notifications/preferences", True, data)
                return True
            else:
                self.log_test("POST /notifications/preferences", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /notifications/preferences", False, error=str(e))
            return False
    
    def test_get_notification_details(self):
        """Test GET /notifications/{notification_id}"""
        if not self.created_notification_id:
            self.log_test("GET /notifications/{notification_id}", False, error="No notification ID available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications/{self.created_notification_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("GET /notifications/{notification_id}", True, data)
                return True
            else:
                self.log_test("GET /notifications/{notification_id}", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /notifications/{notification_id}", False, error=str(e))
            return False
    
    def test_configure_notification_channel(self):
        """Test POST /notifications/channels/configure"""
        try:
            channel_config_data = {
                "channel_id": "email",
                "enabled": "true",
                "settings": json.dumps({
                    "frequency": "instant",
                    "categories": ["system", "business"]
                })
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/notifications/channels/configure",
                data=channel_config_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("POST /notifications/channels/configure", True, data)
                return True
            else:
                self.log_test("POST /notifications/channels/configure", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /notifications/channels/configure", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all notification system tests"""
        print("🌊 THIRTEENTH WAVE - ADVANCED NOTIFICATION & COMMUNICATION SYSTEM TESTING")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n📋 CORE NOTIFICATION ENDPOINTS:")
        print("-" * 40)
        
        # Core notification functionality tests
        tests = [
            self.test_get_notification_channels,
            self.test_send_notification,
            self.test_get_notification_history,
            self.test_get_notification_analytics,
            self.test_create_notification_template,
            self.test_get_notification_templates,
            self.test_send_template_notification,
            self.test_get_notification_preferences,
            self.test_update_notification_preferences,
            self.test_get_notification_details,
            self.test_configure_notification_channel
        ]
        
        # Run tests
        for test in tests:
            test()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = len([r for r in self.test_results if r["success"]])
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL NOTIFICATION SYSTEM TESTS PASSED!")
            print("🌊 Advanced Notification & Communication System is fully operational!")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Review the errors above.")
        
        # Performance metrics
        total_data = sum(r["response_size"] for r in self.test_results if r["success"])
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Total data processed: {total_data:,} bytes")
        print(f"   Average response size: {total_data // max(passed, 1):,} bytes")
        
        return passed == total

def main():
    """Main test execution"""
    tester = NotificationSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ NOTIFICATION SYSTEM TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n❌ NOTIFICATION SYSTEM TESTING COMPLETED WITH FAILURES")
        sys.exit(1)

if __name__ == "__main__":
    main()