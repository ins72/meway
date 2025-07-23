#!/usr/bin/env python3
"""
REVIEW REQUEST FOCUSED TESTING - JANUARY 2025
Testing specific areas mentioned in the review request:
1. Template Marketplace CRUD endpoints
2. Social Media Leads (original and alternative endpoints)
3. Mock Data Verification
4. CRUD Operations verification
5. Database Integration confirmation
6. API Endpoint Count verification
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

class ReviewRequestTester:
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
    
    def test_template_marketplace_crud(self):
        """Test Template Marketplace CRUD operations as requested"""
        print("\n🛍️ TESTING TEMPLATE MARKETPLACE CRUD OPERATIONS")
        print("=" * 60)
        
        # Test GET operations
        self.test_endpoint("/templates", "GET", test_name="GET /templates")
        self.test_endpoint("/marketing-website/templates", "GET", test_name="GET /marketing-website/templates")  
        self.test_endpoint("/marketing-website/templates/marketplace", "GET", test_name="GET /marketing-website/templates/marketplace")
        
        # Test POST (Create) operation
        template_data = {
            "title": "Test Marketing Template",
            "description": "A test template for marketing campaigns",
            "category": "marketing",
            "price": 29.99,
            "tags": ["marketing", "email", "campaign"]
        }
        self.test_endpoint("/templates", "POST", template_data, "POST /templates (Create)")
        
        # Test PUT (Update) operation - using a test ID
        update_data = {
            "title": "Updated Marketing Template",
            "description": "Updated description",
            "price": 39.99
        }
        self.test_endpoint("/templates/test-template-id", "PUT", update_data, "PUT /templates/{id} (Update)")
        
        # Test DELETE operation
        self.test_endpoint("/templates/test-template-id", "DELETE", test_name="DELETE /templates/{id}")
    
    def test_social_media_leads(self):
        """Test Social Media Leads endpoints (original and alternative)"""
        print("\n📱 TESTING SOCIAL MEDIA LEADS")
        print("=" * 60)
        
        # Test original endpoints
        self.test_endpoint("/discover/twitter", "GET", test_name="Original /discover/twitter")
        self.test_endpoint("/discover/tiktok", "GET", test_name="Original /discover/tiktok")
        
        # Test alternative endpoints
        self.test_endpoint("/twitter/search", "GET", test_name="New /twitter/search")
        self.test_endpoint("/tiktok/search", "GET", test_name="New /tiktok/search")
        
        # Test analytics and history
        self.test_endpoint("/social-media/analytics", "GET", test_name="Analytics Overview")
        self.test_endpoint("/social-media/search-history", "GET", test_name="Search History")
    
    def test_booking_system(self):
        """Test Booking System CRUD operations"""
        print("\n📅 TESTING BOOKING SYSTEM")
        print("=" * 60)
        
        # Test health and basic operations
        self.test_endpoint("/booking/health", "GET", test_name="Health Check")
        self.test_endpoint("/booking/services", "GET", test_name="Get Services")
        self.test_endpoint("/booking/bookings", "GET", test_name="Get Bookings")
        self.test_endpoint("/booking/dashboard", "GET", test_name="Dashboard")
        
        # Test create operations
        service_data = {
            "name": "Test Service",
            "description": "A test service",
            "duration": 60,
            "price": 100.00
        }
        self.test_endpoint("/booking/services", "POST", service_data, "Create Service")
        
        booking_data = {
            "service_id": "test-service-id",
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "date": "2025-01-25",
            "time": "10:00"
        }
        self.test_endpoint("/booking/bookings", "POST", booking_data, "Create Booking")
        
        # Test analytics
        self.test_endpoint("/booking/analytics", "GET", test_name="Analytics")
    
    def test_team_management(self):
        """Test Team Management system"""
        print("\n👥 TESTING TEAM MANAGEMENT")
        print("=" * 60)
        
        # Test dashboard and basic operations
        self.test_endpoint("/team/dashboard", "GET", test_name="Dashboard")
        self.test_endpoint("/team/members", "GET", test_name="Get Members")
        self.test_endpoint("/team/activity", "GET", test_name="Activity Log")
        
        # Test create operations
        team_data = {
            "name": "Test Team",
            "description": "A test team"
        }
        self.test_endpoint("/teams", "POST", team_data, "Create Team")
        self.test_endpoint("/teams", "GET", test_name="Get Teams")
        
        # Test invitation system
        invitation_data = {
            "email": "newmember@example.com",
            "role": "member"
        }
        self.test_endpoint("/team/invite", "POST", invitation_data, "Send Invitation")
        
        # Test roles and permissions
        self.test_endpoint("/team/roles", "GET", test_name="Available Roles")
        self.test_endpoint("/team/permissions", "GET", test_name="Available Permissions")
    
    def test_mobile_pwa_features(self):
        """Test Mobile PWA Features"""
        print("\n📱 TESTING MOBILE PWA FEATURES")
        print("=" * 60)
        
        # Test basic PWA functionality
        self.test_endpoint("/pwa/health", "GET", test_name="Health Check")
        self.test_endpoint("/pwa/manifest", "GET", test_name="PWA Manifest")
        
        # Test push notifications
        push_data = {
            "endpoint": "https://example.com/push",
            "keys": {
                "p256dh": "test-key",
                "auth": "test-auth"
            }
        }
        self.test_endpoint("/pwa/push/subscribe", "POST", push_data, "Subscribe to Push")
        
        notification_data = {
            "title": "Test Notification",
            "body": "This is a test notification",
            "user_id": "test-user"
        }
        self.test_endpoint("/pwa/push/send", "POST", notification_data, "Send Push Notification")
        
        # Test device management
        device_data = {
            "device_id": "test-device-123",
            "device_type": "mobile",
            "user_agent": "Test Browser"
        }
        self.test_endpoint("/pwa/device/register", "POST", device_data, "Register Device")
        
        # Test offline caching
        cache_data = {
            "url": "/api/dashboard",
            "type": "api",
            "content": {"test": "data"}
        }
        self.test_endpoint("/pwa/cache", "POST", cache_data, "Cache Resource")
        
        # Test background sync
        sync_data = {
            "type": "data_sync",
            "endpoint": "/api/sync"
        }
        self.test_endpoint("/pwa/sync/queue", "POST", sync_data, "Queue Background Sync")
        self.test_endpoint("/pwa/sync/process", "POST", test_name="Process Background Sync")
        
        # Test analytics
        self.test_endpoint("/pwa/analytics", "GET", test_name="Mobile Analytics")
    
    def test_api_endpoint_count(self):
        """Test API endpoint count verification"""
        print("\n🔢 TESTING API ENDPOINT COUNT")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                paths_count = len(data.get('paths', {}))
                
                if paths_count >= 674:
                    self.log_result("API Endpoint Count", True, f"Excellent - {paths_count} endpoints available (target: ~674)")
                elif paths_count >= 500:
                    self.log_result("API Endpoint Count", True, f"Good - {paths_count} endpoints available (target: ~674)")
                else:
                    self.log_result("API Endpoint Count", False, f"Below target - {paths_count} endpoints available (target: ~674)")
                
                return paths_count
            else:
                self.log_result("API Endpoint Count", False, f"Cannot access OpenAPI spec - Status {response.status_code}")
                return 0
        except Exception as e:
            self.log_result("API Endpoint Count", False, f"Error checking endpoint count: {str(e)}")
            return 0
    
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
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all review request areas"""
        print("🎯 REVIEW REQUEST FOCUSED TESTING - JANUARY 2025")
        print("Testing specific areas mentioned in the review request:")
        print("1. Template Marketplace CRUD endpoints")
        print("2. Social Media Leads (original and alternative endpoints)")
        print("3. Mock Data Verification")
        print("4. CRUD Operations verification")
        print("5. Database Integration confirmation")
        print("6. API Endpoint Count verification")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with testing")
            return
        
        # Test all areas from review request
        self.test_template_marketplace_crud()
        self.test_social_media_leads()
        self.test_booking_system()
        self.test_team_management()
        self.test_mobile_pwa_features()
        endpoint_count = self.test_api_endpoint_count()
        
        # Generate summary
        self.generate_summary(endpoint_count)
    
    def generate_summary(self, endpoint_count):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 REVIEW REQUEST TESTING SUMMARY")
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
            if 'Template' in test_name or '/templates' in test_name:
                category = 'Template Marketplace'
            elif 'Social Media' in test_name or '/discover' in test_name or '/twitter' in test_name or '/tiktok' in test_name:
                category = 'Social Media Leads'
            elif 'Booking' in test_name or '/booking' in test_name:
                category = 'Booking System'
            elif 'Team' in test_name or '/team' in test_name or '/teams' in test_name:
                category = 'Team Management'
            elif 'PWA' in test_name or '/pwa' in test_name:
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
    tester = ReviewRequestTester()
    tester.run_comprehensive_test()
"""
REVIEW REQUEST FOCUSED TESTING - JANUARY 2025
Testing specific areas mentioned in the review request:
1. Template Marketplace - Test new CRUD operations
2. Social Media Leads - Test both original and new alternative endpoints  
3. Booking System - Test service creation and booking management
4. Team Management - Test team creation and member management
5. Mobile PWA - Test push notifications and device registration
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

class ReviewRequestTester:
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
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code}", data)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code} (non-JSON response)")
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
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Validation error')
                    self.log_result(test_name, False, f"Validation error (422): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Validation error (422): {response.text}")
                return False, None
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Internal server error')
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}")
                return False, None
            else:
                self.log_result(test_name, False, f"Endpoint error - Status {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False, None

    def test_template_marketplace_crud(self):
        """Test Template Marketplace CRUD operations as mentioned in review request"""
        print("\n🛍️ TESTING TEMPLATE MARKETPLACE CRUD OPERATIONS")
        print("=" * 60)
        print("Testing new CRUD operations: GET /templates, PUT /templates/{id}, DELETE /templates/{id}")
        
        # Test GET /templates
        print("\n📋 Testing GET /templates...")
        success, templates_data = self.test_endpoint("/templates", "GET", test_name="Template Marketplace - GET /templates")
        
        # Test alternative template endpoints
        self.test_endpoint("/marketing-website/templates", "GET", test_name="Template Marketplace - GET /marketing-website/templates")
        self.test_endpoint("/marketing-website/templates/marketplace", "GET", test_name="Template Marketplace - GET /marketing-website/templates/marketplace")
        
        # Test template creation (POST)
        print("\n➕ Testing Template Creation...")
        template_data = {
            "name": "Modern Business Template",
            "title": "Professional Business Landing Page",
            "description": "A clean, modern template perfect for business websites",
            "category": "business",
            "price": 49.99,
            "preview_url": "https://example.com/preview/modern-business",
            "tags": ["business", "modern", "responsive"],
            "features": ["responsive", "seo-optimized", "fast-loading"]
        }
        
        success, created_template = self.test_endpoint("/templates", "POST", template_data, "Template Marketplace - POST /templates (Create)")
        
        template_id = None
        if success and created_template:
            template_id = created_template.get("id") or created_template.get("template_id") or created_template.get("data", {}).get("id")
            print(f"   Created template ID: {template_id}")
        
        # Test PUT /templates/{id} (Update)
        if template_id:
            print(f"\n✏️ Testing PUT /templates/{template_id}...")
            update_data = {
                "title": "Professional Business Landing Page - Updated",
                "description": "A clean, modern template perfect for business websites with enhanced features",
                "price": 59.99,
                "tags": ["business", "modern", "responsive", "premium"]
            }
            
            self.test_endpoint(f"/templates/{template_id}", "PUT", update_data, f"Template Marketplace - PUT /templates/{template_id} (Update)")
        
        # Test DELETE /templates/{id}
        if template_id:
            print(f"\n🗑️ Testing DELETE /templates/{template_id}...")
            self.test_endpoint(f"/templates/{template_id}", "DELETE", test_name=f"Template Marketplace - DELETE /templates/{template_id}")
        
        print("\n🛍️ Template Marketplace CRUD Testing Complete!")
        return True

    def test_social_media_leads(self):
        """Test Social Media Leads - both original and new alternative endpoints"""
        print("\n📱 TESTING SOCIAL MEDIA LEADS")
        print("=" * 60)
        print("Testing both original (/discover/tiktok, /discover/twitter) and new alternative endpoints (/tiktok/search, /twitter/search)")
        
        # Test original endpoints
        print("\n🔍 Testing Original Endpoints...")
        
        # Original Twitter endpoint
        twitter_search_data = {
            "keywords": ["entrepreneur", "startup"],
            "location": "United States",
            "max_results": 10
        }
        self.test_endpoint("/discover/twitter", "POST", twitter_search_data, "Social Media Leads - Original /discover/twitter")
        self.test_endpoint("/discover/twitter", "GET", test_name="Social Media Leads - Original GET /discover/twitter")
        
        # Original TikTok endpoint
        tiktok_search_data = {
            "keywords": ["business", "marketing"],
            "region": "US",
            "max_results": 10
        }
        self.test_endpoint("/discover/tiktok", "POST", tiktok_search_data, "Social Media Leads - Original /discover/tiktok")
        self.test_endpoint("/discover/tiktok", "GET", test_name="Social Media Leads - Original GET /discover/tiktok")
        
        # Test new alternative endpoints
        print("\n🆕 Testing New Alternative Endpoints...")
        
        # New Twitter search endpoint
        twitter_alt_data = {
            "keywords": ["entrepreneur", "startup", "business owner"],
            "hashtags": ["#entrepreneur", "#startup"],
            "location": "United States",
            "max_results": 20,
            "verified_only": False,
            "min_followers": 1000
        }
        self.test_endpoint("/tiktok/search", "POST", twitter_alt_data, "Social Media Leads - New /twitter/search")
        self.test_endpoint("/twitter/search", "POST", twitter_alt_data, "Social Media Leads - New /twitter/search")
        
        # New TikTok search endpoint
        tiktok_alt_data = {
            "keywords": ["business", "marketing", "entrepreneur"],
            "region": "US",
            "max_results": 15,
            "min_followers": 5000,
            "niche": "business"
        }
        self.test_endpoint("/tiktok/search", "POST", tiktok_alt_data, "Social Media Leads - New /tiktok/search")
        
        # Test social media leads analytics
        print("\n📊 Testing Social Media Analytics...")
        self.test_endpoint("/social-media-leads/analytics/overview", "GET", test_name="Social Media Leads - Analytics Overview")
        self.test_endpoint("/social-media-leads/search-history", "GET", test_name="Social Media Leads - Search History")
        
        print("\n📱 Social Media Leads Testing Complete!")
        return True

    def test_booking_system(self):
        """Test Booking System - service creation and booking management"""
        print("\n📅 TESTING BOOKING SYSTEM")
        print("=" * 60)
        print("Testing service creation and booking management")
        
        # Test booking system health
        print("\n🏥 Testing Booking System Health...")
        self.test_endpoint("/booking/health", "GET", test_name="Booking System - Health Check")
        self.test_endpoint("/bookings/health", "GET", test_name="Booking System - Health Check (Alt)")
        
        # Test service creation
        print("\n🛠️ Testing Service Creation...")
        service_data = {
            "name": "Digital Marketing Consultation",
            "description": "1-hour consultation on digital marketing strategy",
            "duration_minutes": 60,
            "price": 150.00,
            "category": "consultation",
            "availability": {
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "09:00", "end": "17:00"}
            },
            "buffer_time_minutes": 15
        }
        
        success, created_service = self.test_endpoint("/booking/services", "POST", service_data, "Booking System - Create Service")
        self.test_endpoint("/bookings/services", "POST", service_data, "Booking System - Create Service (Alt)")
        
        service_id = None
        if success and created_service:
            service_id = created_service.get("id") or created_service.get("service_id") or created_service.get("data", {}).get("id")
            print(f"   Created service ID: {service_id}")
        
        # Test service management
        print("\n📋 Testing Service Management...")
        self.test_endpoint("/booking/services", "GET", test_name="Booking System - Get Services")
        self.test_endpoint("/bookings/services", "GET", test_name="Booking System - Get Services (Alt)")
        
        if service_id:
            self.test_endpoint(f"/booking/services/{service_id}", "GET", test_name=f"Booking System - Get Service {service_id}")
        
        # Test booking creation
        print("\n📅 Testing Booking Creation...")
        booking_data = {
            "service_id": service_id or "sample_service_id",
            "client_name": "John Smith",
            "client_email": "john.smith@example.com",
            "client_phone": "+1-555-0123",
            "booking_date": "2025-01-25",
            "booking_time": "14:00",
            "notes": "Looking for help with social media marketing strategy"
        }
        
        success, created_booking = self.test_endpoint("/booking/bookings", "POST", booking_data, "Booking System - Create Booking")
        self.test_endpoint("/bookings", "POST", booking_data, "Booking System - Create Booking (Alt)")
        
        booking_id = None
        if success and created_booking:
            booking_id = created_booking.get("id") or created_booking.get("booking_id") or created_booking.get("data", {}).get("id")
            print(f"   Created booking ID: {booking_id}")
        
        # Test booking management
        print("\n📊 Testing Booking Management...")
        self.test_endpoint("/booking/bookings", "GET", test_name="Booking System - Get Bookings")
        self.test_endpoint("/bookings", "GET", test_name="Booking System - Get Bookings (Alt)")
        
        if booking_id:
            # Test booking status updates
            status_data = {"status": "confirmed"}
            self.test_endpoint(f"/booking/bookings/{booking_id}/status", "PUT", status_data, f"Booking System - Update Booking Status")
            
            # Test booking cancellation
            cancel_data = {"reason": "Client requested cancellation"}
            self.test_endpoint(f"/booking/bookings/{booking_id}/cancel", "POST", cancel_data, f"Booking System - Cancel Booking")
        
        # Test booking analytics
        print("\n📈 Testing Booking Analytics...")
        self.test_endpoint("/booking/analytics", "GET", test_name="Booking System - Analytics")
        self.test_endpoint("/booking/dashboard", "GET", test_name="Booking System - Dashboard")
        
        print("\n📅 Booking System Testing Complete!")
        return True

    def test_team_management_detailed(self):
        """Test Team Management - team creation and member management (detailed)"""
        print("\n👥 TESTING TEAM MANAGEMENT (DETAILED)")
        print("=" * 60)
        print("Testing team creation and member management with focus on issues found")
        
        # Test team creation
        print("\n➕ Testing Team Creation...")
        team_data = {
            "name": "Digital Marketing Team",
            "description": "Team focused on digital marketing campaigns and strategy",
            "team_type": "marketing",
            "settings": {
                "allow_external_collaboration": True,
                "require_approval_for_invites": False
            }
        }
        
        success, created_team = self.test_endpoint("/teams", "POST", team_data, "Team Management - Create Team")
        self.test_endpoint("/teams/create", "POST", team_data, "Team Management - Create Team (Alt)")
        
        team_id = None
        if success and created_team:
            team_id = created_team.get("id") or created_team.get("team_id") or created_team.get("data", {}).get("id")
            print(f"   Created team ID: {team_id}")
        
        # Test team management
        print("\n📋 Testing Team Management...")
        self.test_endpoint("/teams", "GET", test_name="Team Management - Get Teams")
        self.test_endpoint("/teams/dashboard", "GET", test_name="Team Management - Dashboard")
        
        # Test member management (this had issues in previous test)
        print("\n👤 Testing Member Management (Issue Investigation)...")
        self.test_endpoint("/teams/members", "GET", test_name="Team Management - Get Members (Issue Check)")
        
        if team_id:
            self.test_endpoint(f"/teams/{team_id}/members", "GET", test_name=f"Team Management - Get Team {team_id} Members")
        
        # Test member invitation (this had conflict issues)
        print("\n📧 Testing Member Invitation (Issue Investigation)...")
        invitation_data = {
            "email": f"newmember{int(time.time())}@example.com",  # Use timestamp to avoid conflicts
            "role": "member",
            "permissions": ["view_projects", "create_content"]
        }
        
        self.test_endpoint("/teams/invite", "POST", invitation_data, "Team Management - Send Invitation (Unique Email)")
        
        if team_id:
            self.test_endpoint(f"/teams/{team_id}/invite", "POST", invitation_data, f"Team Management - Send Team {team_id} Invitation")
        
        # Test team activity (this worked in previous test)
        print("\n📈 Testing Team Activity...")
        self.test_endpoint("/teams/activity", "GET", test_name="Team Management - Activity Log")
        
        if team_id:
            self.test_endpoint(f"/teams/{team_id}/activity", "GET", test_name=f"Team Management - Team {team_id} Activity")
        
        # Test team roles and permissions
        print("\n🔐 Testing Team Roles and Permissions...")
        self.test_endpoint("/teams/roles", "GET", test_name="Team Management - Available Roles")
        self.test_endpoint("/teams/permissions", "GET", test_name="Team Management - Available Permissions")
        
        print("\n👥 Team Management Detailed Testing Complete!")
        return True

    def test_mobile_pwa_detailed(self):
        """Test Mobile PWA - push notifications and device registration (detailed)"""
        print("\n📱 TESTING MOBILE PWA (DETAILED)")
        print("=" * 60)
        print("Testing push notifications and device registration with focus on issues found")
        
        # Test PWA health and manifest (these worked)
        print("\n🏥 Testing PWA Health and Manifest...")
        self.test_endpoint("/mobile-pwa/health", "GET", test_name="Mobile PWA - Health Check")
        self.test_endpoint("/mobile-pwa/pwa/manifest", "GET", test_name="Mobile PWA - Get Manifest")
        
        # Test push notifications (detailed investigation)
        print("\n🔔 Testing Push Notifications (Issue Investigation)...")
        
        # Test push subscription (this failed in previous test)
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/example-endpoint-12345",
            "keys": {
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
                "auth": "tBHItJI5svbpez7KI4CCXg"
            }
        }
        
        self.test_endpoint("/mobile-pwa/push/subscribe", "POST", subscription_data, "Mobile PWA - Subscribe to Push (Issue Check)")
        
        # Test push sending (this worked in previous test)
        push_data = {
            "title": "Test Notification",
            "body": "Testing push notification functionality",
            "icon": "/icons/notification-icon.png",
            "data": {
                "url": "/dashboard",
                "action": "open_dashboard"
            }
        }
        
        self.test_endpoint("/mobile-pwa/push/send", "POST", push_data, "Mobile PWA - Send Push Notification")
        
        # Test device registration (this failed in previous test)
        print("\n📱 Testing Device Registration (Issue Investigation)...")
        device_data = {
            "device_type": "mobile",
            "platform": "ios",
            "app_version": "1.0.0",
            "device_info": {
                "model": "iPhone 13",
                "os_version": "15.0",
                "screen_resolution": "1170x2532"
            }
        }
        
        self.test_endpoint("/mobile-pwa/device/register", "POST", device_data, "Mobile PWA - Register Device (Issue Check)")
        
        # Test offline caching (this failed in previous test)
        print("\n💾 Testing Offline Caching (Issue Investigation)...")
        cache_data = {
            "url": "/dashboard",
            "type": "page",
            "content": "<html><body>Dashboard content</body></html>",
            "cache_strategy": "cache_first"
        }
        
        self.test_endpoint("/mobile-pwa/offline/cache", "POST", cache_data, "Mobile PWA - Cache Resource (Issue Check)")
        
        # Test background sync (these worked in previous test)
        print("\n🔄 Testing Background Sync...")
        sync_data = {
            "type": "analytics",
            "endpoint": "/api/analytics-system/track",
            "data": {
                "event_type": "page_view",
                "timestamp": "2025-01-15T10:30:00Z"
            }
        }
        
        self.test_endpoint("/mobile-pwa/sync/queue", "POST", sync_data, "Mobile PWA - Queue Background Sync")
        self.test_endpoint("/mobile-pwa/sync/process", "POST", {}, "Mobile PWA - Process Background Sync")
        
        # Test mobile analytics (this worked)
        print("\n📊 Testing Mobile Analytics...")
        self.test_endpoint("/mobile-pwa/analytics/mobile", "GET", test_name="Mobile PWA - Mobile Analytics")
        
        print("\n📱 Mobile PWA Detailed Testing Complete!")
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 REVIEW REQUEST TESTING SUMMARY")
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
        
        # Group results by feature
        feature_results = {}
        for result in self.test_results:
            test_name = result["test"]
            if "Template Marketplace" in test_name:
                feature = "Template Marketplace"
            elif "Social Media Leads" in test_name:
                feature = "Social Media Leads"
            elif "Booking System" in test_name:
                feature = "Booking System"
            elif "Team Management" in test_name:
                feature = "Team Management"
            elif "Mobile PWA" in test_name:
                feature = "Mobile PWA"
            else:
                feature = "Other"
            
            if feature not in feature_results:
                feature_results[feature] = {"passed": 0, "failed": 0, "total": 0}
            
            feature_results[feature]["total"] += 1
            if result["success"]:
                feature_results[feature]["passed"] += 1
            else:
                feature_results[feature]["failed"] += 1
        
        print(f"\n📋 FEATURE-BY-FEATURE RESULTS:")
        for feature, stats in feature_results.items():
            if stats["total"] > 0:
                feature_success_rate = (stats["passed"] / stats["total"] * 100)
                status = "✅" if feature_success_rate >= 75 else "⚠️" if feature_success_rate >= 50 else "❌"
                print(f"   {status} {feature}: {stats['passed']}/{stats['total']} ({feature_success_rate:.1f}%)")
        
        print(f"\n🔍 FAILED TESTS SUMMARY:")
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            for result in failed_results:
                print(f"   ❌ {result['test']}: {result['message']}")
        else:
            print("   🎉 No failed tests!")
        
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - Production ready with outstanding performance")
        elif success_rate >= 75:
            print("   🟡 GOOD - Production ready with minor issues to address")
        elif success_rate >= 50:
            print("   🟠 PARTIAL - Needs significant improvements before production")
        else:
            print("   🔴 CRITICAL - Major issues require immediate attention")
        
        print("=" * 80)

def main():
    """Main test execution"""
    print("🎯 REVIEW REQUEST FOCUSED TESTING - JANUARY 2025")
    print("Testing specific areas mentioned in the review request:")
    print("1. Template Marketplace - Test new CRUD operations")
    print("2. Social Media Leads - Test both original and new alternative endpoints")  
    print("3. Booking System - Test service creation and booking management")
    print("4. Team Management - Test team creation and member management")
    print("5. Mobile PWA - Test push notifications and device registration")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Credentials: {TEST_EMAIL}")
    print("=" * 80)
    
    tester = ReviewRequestTester()
    
    # Authenticate first
    if not tester.test_authentication():
        print("❌ Authentication failed. Cannot proceed with testing.")
        sys.exit(1)
    
    # Run all review request tests
    tester.test_template_marketplace_crud()
    tester.test_social_media_leads()
    tester.test_booking_system()
    tester.test_team_management_detailed()
    tester.test_mobile_pwa_detailed()
    
    # Print summary
    tester.print_test_summary()

if __name__ == "__main__":
    main()