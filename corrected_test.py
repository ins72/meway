#!/usr/bin/env python3
"""
CORRECTED REVIEW REQUEST TESTING - JANUARY 2025
Testing with the ACTUAL endpoint paths found in OpenAPI spec
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import uuid

# Backend URL from environment
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class CorrectedTester:
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
    
    def authenticate(self):
        """Authenticate with the backend"""
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
                    self.log_result("Authentication", True, "Login successful", data)
                    return True
            
            self.log_result("Authentication", False, f"Login failed: {response.status_code}")
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
                    self.log_result(test_name, True, f"Working perfectly ({response.status_code})", data)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Working perfectly ({response.status_code}) - non-JSON response")
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, "Endpoint not found (404) - Not implemented")
                return False, None
            elif response.status_code == 405:
                self.log_result(test_name, False, "Method not allowed (405)")
                return False, None
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    self.log_result(test_name, False, f"Validation error (422): {error_data.get('message', 'Request parameters issue')}")
                except:
                    self.log_result(test_name, False, f"Validation error (422): {response.text}")
                return False, None
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unexpected error')
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}")
                return False, None
            else:
                self.log_result(test_name, False, f"Error - Status {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False, None
    
    def check_mock_data(self, response_data, test_name):
        """Check if response contains mock data patterns"""
        if not response_data:
            return True
            
        response_str = str(response_data).lower()
        mock_patterns = [
            'sample', 'mock', 'test_', 'dummy', 'fake', 'example',
            'lorem ipsum', 'placeholder', 'demo_', 'temp_'
        ]
        
        for pattern in mock_patterns:
            if pattern in response_str:
                self.log_result(f"{test_name} - Mock Data Check", False, f"MOCK DATA DETECTED: Found '{pattern}' in response")
                return False
        
        self.log_result(f"{test_name} - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        return True
    
    def test_template_marketplace(self):
        """Test Template Marketplace with correct endpoints"""
        print("\n🛍️ TESTING TEMPLATE MARKETPLACE (CORRECTED ENDPOINTS)")
        print("=" * 60)
        
        # Test the actual template endpoints found in OpenAPI
        success, data = self.test_endpoint("/marketing-website/templates/marketplace", "GET", test_name="Template Marketplace - Get Marketplace Templates")
        if success and data:
            self.check_mock_data(data, "Template Marketplace")
        
        success, data = self.test_endpoint("/templates/templates", "GET", test_name="Template Marketplace - Get Templates")
        if success and data:
            self.check_mock_data(data, "Template Marketplace")
        
        # Test template creation
        template_data = {
            "name": "Test Marketing Template",
            "description": "A test template for marketing campaigns",
            "category": "marketing",
            "price": 29.99
        }
        success, data = self.test_endpoint("/templates/templates", "POST", template_data, "Template Marketplace - Create Template")
        
        # Test other template endpoints
        self.test_endpoint("/ai-content-generation/content-templates", "GET", test_name="Template Marketplace - AI Content Templates")
        self.test_endpoint("/automation/templates", "GET", test_name="Template Marketplace - Automation Templates")
        self.test_endpoint("/email-automation/templates", "GET", test_name="Template Marketplace - Email Templates")
    
    def test_social_media_leads(self):
        """Test Social Media Leads with correct endpoints"""
        print("\n📱 TESTING SOCIAL MEDIA LEADS (CORRECTED ENDPOINTS)")
        print("=" * 60)
        
        # Test the actual social media endpoints found in OpenAPI
        success, data = self.test_endpoint("/social-media-leads/discover/twitter", "GET", test_name="Social Media Leads - Discover Twitter")
        if success and data:
            self.check_mock_data(data, "Social Media Twitter")
        
        success, data = self.test_endpoint("/social-media-leads/discover/tiktok", "GET", test_name="Social Media Leads - Discover TikTok")
        if success and data:
            self.check_mock_data(data, "Social Media TikTok")
        
        # Test alternative endpoints
        success, data = self.test_endpoint("/social-media-leads/twitter/search", "GET", test_name="Social Media Leads - Twitter Search")
        if success and data:
            self.check_mock_data(data, "Social Media Twitter Search")
        
        success, data = self.test_endpoint("/social-media-leads/tiktok/search", "GET", test_name="Social Media Leads - TikTok Search")
        if success and data:
            self.check_mock_data(data, "Social Media TikTok Search")
        
        # Test analytics and other endpoints
        success, data = self.test_endpoint("/social-media-leads/analytics/overview", "GET", test_name="Social Media Leads - Analytics Overview")
        if success and data:
            self.check_mock_data(data, "Social Media Analytics")
        
        self.test_endpoint("/social-media-leads/health", "GET", test_name="Social Media Leads - Health Check")
        self.test_endpoint("/social-media-leads/leads", "GET", test_name="Social Media Leads - Get Leads")
        self.test_endpoint("/social-media-leads/platforms/info", "GET", test_name="Social Media Leads - Platform Info")
    
    def test_booking_system(self):
        """Test Booking System with correct endpoints"""
        print("\n📅 TESTING BOOKING SYSTEM (CORRECTED ENDPOINTS)")
        print("=" * 60)
        
        # Test the actual booking endpoints
        self.test_endpoint("/booking/health", "GET", test_name="Booking System - Health Check")
        
        success, data = self.test_endpoint("/booking/services", "GET", test_name="Booking System - Get Services")
        if success and data:
            self.check_mock_data(data, "Booking Services")
        
        success, data = self.test_endpoint("/booking/bookings", "GET", test_name="Booking System - Get Bookings")
        if success and data:
            self.check_mock_data(data, "Booking Bookings")
        
        success, data = self.test_endpoint("/booking/dashboard", "GET", test_name="Booking System - Dashboard")
        if success and data:
            self.check_mock_data(data, "Booking Dashboard")
        
        # Test create operations
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "duration": 60,
            "price": 100.00
        }
        self.test_endpoint("/booking/services", "POST", service_data, "Booking System - Create Service")
        
        booking_data = {
            "service_id": "test-service-id",
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "date": "2025-01-25",
            "time": "10:00"
        }
        self.test_endpoint("/booking/bookings", "POST", booking_data, "Booking System - Create Booking")
        
        # Test other endpoints
        self.test_endpoint("/booking/analytics/provider", "GET", test_name="Booking System - Analytics")
        self.test_endpoint("/booking/statuses", "GET", test_name="Booking System - Statuses")
        self.test_endpoint("/booking/notification-methods", "GET", test_name="Booking System - Notification Methods")
    
    def test_team_management(self):
        """Test Team Management with correct endpoints"""
        print("\n👥 TESTING TEAM MANAGEMENT (CORRECTED ENDPOINTS)")
        print("=" * 60)
        
        # Test the actual team endpoints
        success, data = self.test_endpoint("/teams/dashboard", "GET", test_name="Team Management - Dashboard")
        if success and data:
            self.check_mock_data(data, "Team Dashboard")
        
        success, data = self.test_endpoint("/teams/members", "GET", test_name="Team Management - Get Members")
        if success and data:
            self.check_mock_data(data, "Team Members")
        
        success, data = self.test_endpoint("/teams/activity", "GET", test_name="Team Management - Activity Log")
        if success and data:
            self.check_mock_data(data, "Team Activity")
        
        # Test invitation system
        invitation_data = {
            "email": f"newmember{uuid.uuid4().hex[:8]}@example.com",
            "role": "member"
        }
        self.test_endpoint("/teams/invite", "POST", invitation_data, "Team Management - Send Invitation")
        
        # Test accept invitation
        self.test_endpoint("/teams/accept-invitation", "POST", {"token": "test-token"}, "Team Management - Accept Invitation")
    
    def test_mobile_pwa_features(self):
        """Test Mobile PWA Features with correct endpoints"""
        print("\n📱 TESTING MOBILE PWA FEATURES (CORRECTED ENDPOINTS)")
        print("=" * 60)
        
        # Test the actual PWA endpoints
        success, data = self.test_endpoint("/mobile-pwa/health", "GET", test_name="Mobile PWA - Health Check")
        if success and data:
            self.check_mock_data(data, "PWA Health")
        
        success, data = self.test_endpoint("/mobile-pwa/pwa/manifest", "GET", test_name="Mobile PWA - PWA Manifest")
        if success and data:
            self.check_mock_data(data, "PWA Manifest")
        
        # Test push notifications
        push_data = {
            "endpoint": "https://example.com/push",
            "keys": {
                "p256dh": "test-key",
                "auth": "test-auth"
            }
        }
        self.test_endpoint("/mobile-pwa/push/subscribe", "POST", push_data, "Mobile PWA - Subscribe to Push")
        
        notification_data = {
            "title": "Test Notification",
            "body": "This is a test notification",
            "user_id": "test-user"
        }
        self.test_endpoint("/mobile-pwa/push/send", "POST", notification_data, "Mobile PWA - Send Push Notification")
        
        # Test device management
        device_data = {
            "device_id": "test-device-123",
            "device_type": "mobile",
            "user_agent": "Test Browser"
        }
        self.test_endpoint("/mobile-pwa/device/register", "POST", device_data, "Mobile PWA - Register Device")
        
        # Test offline caching
        cache_data = {
            "url": "/api/dashboard",
            "type": "api",
            "content": {"test": "data"}
        }
        self.test_endpoint("/mobile-pwa/offline/cache", "POST", cache_data, "Mobile PWA - Cache Resource")
        
        # Test background sync
        sync_data = {
            "type": "data_sync",
            "endpoint": "/api/sync"
        }
        self.test_endpoint("/mobile-pwa/sync/queue", "POST", sync_data, "Mobile PWA - Queue Background Sync")
        self.test_endpoint("/mobile-pwa/sync/process", "POST", test_name="Mobile PWA - Process Background Sync")
        
        # Test analytics
        success, data = self.test_endpoint("/mobile-pwa/analytics/mobile", "GET", test_name="Mobile PWA - Mobile Analytics")
        if success and data:
            self.check_mock_data(data, "Mobile Analytics")
    
    def run_comprehensive_test(self):
        """Run comprehensive test with corrected endpoints"""
        print("🎯 CORRECTED REVIEW REQUEST TESTING - JANUARY 2025")
        print("Testing with ACTUAL endpoint paths from OpenAPI specification")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with testing")
            return
        
        # Test all areas with correct endpoints
        self.test_template_marketplace()
        self.test_social_media_leads()
        self.test_booking_system()
        self.test_team_management()
        self.test_mobile_pwa_features()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 CORRECTED TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Categorize results by feature
        categories = {}
        for result in self.test_results:
            test_name = result['test']
            if 'Template' in test_name:
                category = 'Template Marketplace'
            elif 'Social Media' in test_name:
                category = 'Social Media Leads'
            elif 'Booking' in test_name:
                category = 'Booking System'
            elif 'Team' in test_name:
                category = 'Team Management'
            elif 'PWA' in test_name or 'Mobile' in test_name:
                category = 'Mobile PWA Features'
            else:
                category = 'Other'
            
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0}
            
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
        
        print(f"\n📋 FEATURE-BY-FEATURE RESULTS:")
        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = "✅" if success_rate >= 75 else "⚠️" if success_rate >= 50 else "❌"
            print(f"   {status} {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_results = [result for result in self.test_results if not result['success']]
        if failed_results:
            print(f"\n🔍 FAILED TESTS SUMMARY:")
            for result in failed_results:
                print(f"   ❌ {result['test']}: {result['message']}")
        
        # Production readiness assessment
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            print(f"   🟢 EXCELLENT - Production ready with exceptional performance")
        elif success_rate >= 75:
            print(f"   🟡 GOOD - Production ready with minor issues to address")
        elif success_rate >= 50:
            print(f"   🟠 FAIR - Needs significant improvements before production")
        else:
            print(f"   🔴 POOR - Major issues requiring immediate attention")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = CorrectedTester()
    tester.run_comprehensive_test()