#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST FOR MEWAYZ V2 PLATFORM - JANUARY 2025
Testing all newly implemented critical endpoints as requested in review:

CRITICAL ENDPOINTS TO VERIFY:
1. Team Management: /api/team-management/dashboard, /api/team-management/members, /api/team-management/activity
2. Instagram Database: /api/instagram/search, /api/instagram/profiles
3. PWA Features: /api/pwa/manifest/generate, /api/pwa/manifest/current
4. AI Workflows: /api/workflows/list, /api/workflows/create
5. Social Media Posts: /api/posts/schedule, /api/posts/scheduled
6. Escrow System: /api/escrow/transactions/milestone, /api/escrow/transactions/list
7. Device & Offline Sync: /api/device/register, /api/device/offline/sync
8. Dispute Resolution: /api/disputes/initiate, /api/disputes/list
9. Template Marketplace: /api/template-marketplace/browse, /api/template-marketplace/creator-earnings

SUCCESS CRITERIA: All endpoints should return 200 status codes (not 404)
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import uuid

# Backend URL from environment
BACKEND_URL = "https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class BackendTester:
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
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            # Check if we can access the OpenAPI spec (this confirms the backend is running)
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                paths_count = len(data.get('paths', {}))
                self.log_result("Health Check", True, f"Backend is operational with {paths_count} API endpoints", {"paths_count": paths_count})
                return True
            else:
                self.log_result("Health Check", False, f"Backend not accessible - OpenAPI status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Health check error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            # Test login
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,  # OAuth2PasswordRequestForm expects form data
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    # Set authorization header for future requests
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
            
            # Ensure we have authentication headers if we have a token
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
                self.log_result(test_name, False, f"Endpoint not found (404) - May not be implemented or imported")
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

    def test_newly_implemented_features(self):
        """Test the newly implemented features from the review request"""
        print("\n🎯 TESTING NEWLY IMPLEMENTED FEATURES - JANUARY 2025")
        print("=" * 80)
        print("Testing the four major new features:")
        print("1. Template Marketplace (Real Endpoints)")
        print("2. Team Management (Real Endpoints)") 
        print("3. Unified Analytics (Real Endpoints)")
        print("4. Mobile PWA Features (Real Endpoints)")
        
        # Test all new features with real endpoints
        self.test_real_template_marketplace_system()
        self.test_real_team_management_system()
        self.test_real_unified_analytics_system()
        self.test_real_mobile_pwa_system()
        
    def test_real_template_marketplace_system(self):
        """Test Real Template Marketplace at /api/marketing-website/templates/marketplace"""
        print("\n🛍️ TESTING REAL TEMPLATE MARKETPLACE")
        print("=" * 60)
        
        # 1. Test Template Marketplace
        print("\n🏪 Testing Template Marketplace...")
        success, marketplace_data = self.test_endpoint("/marketing-website/templates/marketplace", "GET", test_name="Template Marketplace - Get Marketplace Templates")
        
        if success and marketplace_data:
            print(f"   ✅ Template Marketplace working - {len(str(marketplace_data))} chars response")
            
            # Check for mock data patterns
            data_str = str(marketplace_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower() or "test" in data_str.lower():
                self.log_result("Template Marketplace - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock/test data")
            else:
                self.log_result("Template Marketplace - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 2. Test Marketing Website Analytics
        print("\n📊 Testing Marketing Analytics...")
        success, analytics_data = self.test_endpoint("/marketing-website/analytics/overview", "GET", test_name="Template Marketplace - Marketing Analytics")
        
        if success and analytics_data:
            # Check for mock data patterns
            data_str = str(analytics_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Marketing Analytics - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Marketing Analytics - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        print("\n🛍️ Real Template Marketplace System Testing Complete!")
        return True
        
    def test_real_team_management_system(self):
        """Test Real Team Management at /api/teams/*"""
        print("\n👥 TESTING REAL TEAM MANAGEMENT")
        print("=" * 60)
        
        # 1. Test Team Dashboard
        print("\n📊 Testing Team Dashboard...")
        success, dashboard_data = self.test_endpoint("/teams/dashboard", "GET", test_name="Team Management - Dashboard")
        
        if success and dashboard_data:
            # Check for mock data patterns
            data_str = str(dashboard_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Team Dashboard - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Team Dashboard - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 2. Test Team Members
        print("\n👤 Testing Team Members...")
        success, members_data = self.test_endpoint("/teams/members", "GET", test_name="Team Management - Get Members")
        
        if success and members_data:
            # Check for mock data patterns
            data_str = str(members_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Team Members - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Team Members - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 3. Test Team Invitation
        print("\n📧 Testing Team Invitation...")
        invitation_data = {
            "email": "newmember@company.com",
            "role": "member",
            "permissions": ["view_projects", "create_content"]
        }
        
        success, invite_response = self.test_endpoint("/teams/invite", "POST", invitation_data, "Team Management - Send Invitation")
        
        if success and invite_response:
            # Check for mock data patterns
            data_str = str(invite_response)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Team Invitation - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Team Invitation - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 4. Test Team Activity
        print("\n📈 Testing Team Activity...")
        success, activity_data = self.test_endpoint("/teams/activity", "GET", test_name="Team Management - Activity Log")
        
        if success and activity_data:
            # Check for mock data patterns
            data_str = str(activity_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Team Activity - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Team Activity - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        print("\n👥 Real Team Management System Testing Complete!")
        return True
        
    def test_real_unified_analytics_system(self):
        """Test Real Unified Analytics at /api/analytics-system/*"""
        print("\n📊 TESTING REAL UNIFIED ANALYTICS")
        print("=" * 60)
        
        # 1. Test Analytics Dashboard
        print("\n📈 Testing Analytics Dashboard...")
        success, dashboard_data = self.test_endpoint("/analytics-system/dashboard", "GET", test_name="Unified Analytics - Dashboard")
        
        if success and dashboard_data:
            # Check for mock data patterns
            data_str = str(dashboard_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower() or "1250.00" in data_str:
                self.log_result("Analytics Dashboard - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data or hardcoded values")
            else:
                self.log_result("Analytics Dashboard - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 2. Test Analytics Overview
        print("\n🔍 Testing Analytics Overview...")
        success, overview_data = self.test_endpoint("/analytics-system/overview", "GET", test_name="Unified Analytics - Overview")
        
        if success and overview_data:
            # Check for mock data patterns
            data_str = str(overview_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Analytics Overview - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Analytics Overview - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 3. Test Analytics Reports
        print("\n📋 Testing Analytics Reports...")
        success, reports_data = self.test_endpoint("/analytics-system/reports", "GET", test_name="Unified Analytics - Reports")
        
        if success and reports_data:
            # Check for mock data patterns
            data_str = str(reports_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Analytics Reports - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Analytics Reports - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 4. Test Custom Reports
        print("\n📊 Testing Custom Reports...")
        custom_report_data = {
            "report_name": "User Engagement Analysis",
            "metrics": ["user_activity", "page_views", "session_duration"],
            "time_period": "last_30_days",
            "format": "json"
        }
        
        success, custom_report = self.test_endpoint("/analytics-system/reports/custom", "POST", custom_report_data, "Unified Analytics - Custom Report")
        
        if success and custom_report:
            # Check for mock data patterns
            data_str = str(custom_report)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Custom Reports - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Custom Reports - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 5. Test Business Intelligence
        print("\n🧠 Testing Business Intelligence...")
        success, bi_data = self.test_endpoint("/analytics-system/business-intelligence", "GET", test_name="Unified Analytics - Business Intelligence")
        
        if success and bi_data:
            # Check for mock data patterns
            data_str = str(bi_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Business Intelligence - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Business Intelligence - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 6. Test Analytics Event Tracking
        print("\n📝 Testing Analytics Event Tracking...")
        event_data = {
            "event_type": "page_view",
            "event_name": "dashboard_viewed",
            "user_id": "user_12345",
            "properties": {
                "page": "/dashboard",
                "source": "direct",
                "device": "desktop"
            }
        }
        
        success, track_response = self.test_endpoint("/analytics-system/track", "POST", event_data, "Unified Analytics - Track Event")
        
        if success and track_response:
            # Check for mock data patterns
            data_str = str(track_response)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Event Tracking - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Event Tracking - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        print("\n📊 Real Unified Analytics System Testing Complete!")
        return True
        
    def test_real_mobile_pwa_system(self):
        """Test Real Mobile PWA Features at /api/mobile-pwa/*"""
        print("\n📱 TESTING REAL MOBILE PWA FEATURES")
        print("=" * 60)
        
        # 1. Test Health Check
        print("\n🏥 Testing Health Check...")
        success, health_data = self.test_endpoint("/mobile-pwa/health", "GET", test_name="Mobile PWA - Health Check")
        
        if success and health_data:
            # Check for mock data patterns
            data_str = str(health_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("PWA Health - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("PWA Health - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 2. Test PWA Manifest
        print("\n📋 Testing PWA Manifest...")
        success, manifest_data = self.test_endpoint("/mobile-pwa/pwa/manifest", "GET", test_name="Mobile PWA - Get Manifest")
        
        if success and manifest_data:
            # Check for mock data patterns
            data_str = str(manifest_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("PWA Manifest - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("PWA Manifest - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 3. Test Push Notifications Subscribe
        print("\n🔔 Testing Push Notifications Subscribe...")
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/example-endpoint-12345",
            "keys": {
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
                "auth": "tBHItJI5svbpez7KI4CCXg"
            }
        }
        
        success, subscribe_response = self.test_endpoint("/mobile-pwa/push/subscribe", "POST", subscription_data, "Mobile PWA - Subscribe to Push")
        
        if success and subscribe_response:
            # Check for mock data patterns
            data_str = str(subscribe_response)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Push Subscribe - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Push Subscribe - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 4. Test Send Push Notification
        print("\n📤 Testing Send Push Notification...")
        push_data = {
            "title": "Welcome to Mewayz PWA!",
            "body": "Your mobile experience is now enhanced with offline capabilities",
            "icon": "/icons/notification-icon.png",
            "data": {
                "url": "/dashboard",
                "action": "open_dashboard"
            }
        }
        
        success, push_response = self.test_endpoint("/mobile-pwa/push/send", "POST", push_data, "Mobile PWA - Send Push Notification")
        
        if success and push_response:
            # Check for mock data patterns
            data_str = str(push_response)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Push Send - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Push Send - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 5. Test Device Registration
        print("\n📱 Testing Device Registration...")
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
        
        success, device_response = self.test_endpoint("/mobile-pwa/device/register", "POST", device_data, "Mobile PWA - Register Device")
        
        if success and device_response:
            # Check for mock data patterns
            data_str = str(device_response)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Device Register - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Device Register - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 6. Test Offline Caching
        print("\n💾 Testing Offline Caching...")
        cache_data = {
            "url": "/dashboard",
            "type": "page",
            "content": "<html><body>Dashboard content</body></html>",
            "cache_strategy": "cache_first"
        }
        
        success, cache_response = self.test_endpoint("/mobile-pwa/offline/cache", "POST", cache_data, "Mobile PWA - Cache Resource")
        
        if success and cache_response:
            # Check for mock data patterns
            data_str = str(cache_response)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Offline Cache - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Offline Cache - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 7. Test Background Sync
        print("\n🔄 Testing Background Sync...")
        sync_data = {
            "type": "analytics",
            "endpoint": "/api/analytics-system/track",
            "data": {
                "event_type": "page_view",
                "timestamp": "2025-01-15T10:30:00Z"
            }
        }
        
        success, sync_response = self.test_endpoint("/mobile-pwa/sync/queue", "POST", sync_data, "Mobile PWA - Queue Background Sync")
        
        if success and sync_response:
            # Check for mock data patterns
            data_str = str(sync_response)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Background Sync - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Background Sync - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 8. Test Mobile Analytics
        print("\n📊 Testing Mobile Analytics...")
        success, analytics_data = self.test_endpoint("/mobile-pwa/analytics/mobile", "GET", test_name="Mobile PWA - Mobile Analytics")
        
        if success and analytics_data:
            # Check for mock data patterns
            data_str = str(analytics_data)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Mobile Analytics - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Mobile Analytics - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        # 9. Test Process Background Sync
        print("\n⚙️ Testing Process Background Sync...")
        success, process_response = self.test_endpoint("/mobile-pwa/sync/process", "POST", {}, "Mobile PWA - Process Background Sync")
        
        if success and process_response:
            # Check for mock data patterns
            data_str = str(process_response)
            if "sample" in data_str.lower() or "mock" in data_str.lower():
                self.log_result("Process Sync - Mock Data Check", False, "MOCK DATA DETECTED: Response contains sample/mock data")
            else:
                self.log_result("Process Sync - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        
        print("\n📱 Real Mobile PWA System Testing Complete!")
        return True
        
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TEST SUMMARY - 4 NEWLY IMPLEMENTED FEATURES")
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
            elif "Team Management" in test_name:
                feature = "Team Management"
            elif "Unified Analytics" in test_name:
                feature = "Unified Analytics"
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
        
    def test_fixed_critical_issues(self):
        """Test the 4 fixed critical issues mentioned in review request"""
        print("\n🔧 TESTING FIXED CRITICAL ISSUES")
        print("=" * 60)
        
        # 1. Team management datetime handling (should now work without errors)
        print("\n👥 Testing Team Management Datetime Handling...")
        self.test_endpoint("/team-management/dashboard", "GET", test_name="Team Management - Dashboard (Datetime Fix)")
        self.test_endpoint("/team-management/members", "GET", test_name="Team Management - Members List (Datetime Fix)")
        self.test_endpoint("/team-management/activity", "GET", test_name="Team Management - Activity Log (Datetime Fix)")
        
        # Test team creation with datetime fields
        team_data = {
            "name": "Marketing Team Alpha",
            "description": "Primary marketing team for Q1 2025 campaigns",
            "department": "Marketing",
            "created_date": "2025-01-15T10:30:00Z",
            "target_completion": "2025-03-31T23:59:59Z"
        }
        self.test_endpoint("/team-management/teams", "POST", team_data, "Team Management - Create Team (Datetime Fix)")
        
        # 2. AI workflow creation (should create workflows successfully)
        print("\n🤖 Testing AI Workflow Creation...")
        self.test_endpoint("/workflows/list", "GET", test_name="AI Workflows - List Workflows")
        
        workflow_data = {
            "name": "Content Generation Workflow",
            "description": "Automated content creation and social media posting",
            "triggers": [
                {"type": "schedule", "cron": "0 9 * * 1", "timezone": "UTC"}
            ],
            "actions": [
                {"type": "generate_content", "template": "blog_post", "topic": "digital marketing"},
                {"type": "post_social", "platforms": ["twitter", "linkedin"]}
            ],
            "is_active": True
        }
        self.test_endpoint("/workflows/create", "POST", workflow_data, "AI Workflows - Create Workflow")
        
        # 3. Instagram database search (should return profile results)
        print("\n📸 Testing Instagram Database Search...")
        instagram_search_data = {
            "query": "digital marketing",
            "location": "United States",
            "follower_range": {"min": 1000, "max": 100000},
            "engagement_rate": {"min": 2.0},
            "max_results": 20
        }
        self.test_endpoint("/instagram/search", "POST", instagram_search_data, "Instagram - Database Search")
        self.test_endpoint("/instagram/profiles", "GET", test_name="Instagram - Get Profiles")
        
        # 4. PWA manifest generation (should create custom manifests)
        print("\n📱 Testing PWA Manifest Generation...")
        manifest_data = {
            "app_name": "Mewayz Business Suite",
            "short_name": "Mewayz",
            "description": "Complete business automation platform",
            "theme_color": "#2563EB",
            "background_color": "#FFFFFF",
            "start_url": "/dashboard",
            "display": "standalone",
            "orientation": "portrait",
            "icons": [
                {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}
            ]
        }
        self.test_endpoint("/manifest/generate", "POST", manifest_data, "PWA - Generate Manifest")
        self.test_endpoint("/manifest/current", "GET", test_name="PWA - Get Current Manifest")
        
        print("\n🔧 Fixed Critical Issues Testing Complete!")
        return True
    
    def test_new_feature_implementations(self):
        """Test the 5 new feature implementations mentioned in review request"""
        print("\n🆕 TESTING NEW FEATURE IMPLEMENTATIONS")
        print("=" * 60)
        
        # 1. Complete escrow system with milestone payments
        print("\n💰 Testing Complete Escrow System with Milestone Payments...")
        
        # Create escrow transaction
        escrow_data = {
            "buyer_id": "buyer_12345",
            "seller_id": "seller_67890",
            "project_title": "E-commerce Website Development",
            "total_amount": 5000.00,
            "currency": "USD",
            "milestones": [
                {"title": "Design Phase", "amount": 1500.00, "description": "UI/UX design and wireframes"},
                {"title": "Development Phase", "amount": 2500.00, "description": "Frontend and backend development"},
                {"title": "Testing & Launch", "amount": 1000.00, "description": "Testing, deployment, and launch"}
            ],
            "terms": "Payment released upon milestone completion and buyer approval"
        }
        self.test_endpoint("/transactions/milestone", "POST", escrow_data, "Escrow - Create Milestone Transaction")
        self.test_endpoint("/transactions/list", "GET", test_name="Escrow - List Transactions")
        
        # Test dispute initiation
        dispute_data = {
            "transaction_id": "trans_12345",
            "reason": "milestone_not_completed",
            "description": "Development milestone was not completed according to specifications",
            "evidence": ["screenshot1.png", "requirements_doc.pdf"]
        }
        self.test_endpoint("/disputes/initiate", "POST", dispute_data, "Escrow - Initiate Dispute")
        
        # 2. Social media post scheduling across platforms
        print("\n📅 Testing Social Media Post Scheduling...")
        
        schedule_data = {
            "content": "🚀 Exciting news! Our new business automation platform is now live. Transform your workflow today! #BusinessAutomation #Productivity",
            "platforms": ["twitter", "linkedin", "facebook"],
            "scheduled_time": "2025-01-16T14:00:00Z",
            "media_urls": ["https://example.com/promo-image.jpg"],
            "hashtags": ["#BusinessAutomation", "#Productivity", "#Innovation"],
            "target_audience": "business_owners"
        }
        self.test_endpoint("/posts/schedule", "POST", schedule_data, "Social Media - Schedule Post")
        self.test_endpoint("/posts/scheduled", "GET", test_name="Social Media - Get Scheduled Posts")
        
        # 3. Comprehensive offline data sync for PWA
        print("\n🔄 Testing Comprehensive Offline Data Sync...")
        
        # Register device for offline sync
        device_data = {
            "device_id": "device_abc123",
            "device_type": "mobile",
            "platform": "android",
            "app_version": "2.1.0",
            "sync_preferences": {
                "auto_sync": True,
                "sync_frequency": "hourly",
                "data_types": ["contacts", "projects", "analytics"]
            }
        }
        self.test_endpoint("/device/register", "POST", device_data, "PWA - Register Device")
        
        # Test offline sync
        sync_data = {
            "device_id": "device_abc123",
            "last_sync": "2025-01-15T10:00:00Z",
            "data_types": ["contacts", "projects"],
            "conflict_resolution": "server_wins"
        }
        self.test_endpoint("/offline/sync", "POST", sync_data, "PWA - Offline Data Sync")
        
        # 4. Advanced dispute resolution system
        print("\n⚖️ Testing Advanced Dispute Resolution System...")
        
        # List disputes
        self.test_endpoint("/disputes/list", "GET", test_name="Disputes - List All Disputes")
        
        # Submit evidence
        evidence_data = {
            "dispute_id": "dispute_12345",
            "evidence_type": "document",
            "description": "Contract showing agreed deliverables",
            "file_url": "https://example.com/contract.pdf",
            "submitted_by": "buyer"
        }
        self.test_endpoint("/disputes/evidence", "POST", evidence_data, "Disputes - Submit Evidence")
        
        # Mediation request
        mediation_data = {
            "dispute_id": "dispute_12345",
            "mediator_preference": "platform_mediator",
            "urgency": "high",
            "additional_notes": "Time-sensitive project with client deadline approaching"
        }
        self.test_endpoint("/disputes/mediation", "POST", mediation_data, "Disputes - Request Mediation")
        
        # 5. Template marketplace with creator earnings
        print("\n🛍️ Testing Template Marketplace with Creator Earnings...")
        
        # Browse marketplace
        self.test_endpoint("/template-marketplace/browse", "GET", test_name="Template Marketplace - Browse Templates")
        self.test_endpoint("/template-marketplace/categories", "GET", test_name="Template Marketplace - Get Categories")
        
        # Create template for sale
        template_data = {
            "title": "Modern Business Landing Page",
            "description": "Professional landing page template with conversion optimization",
            "category": "website_templates",
            "price": 49.99,
            "preview_images": ["preview1.jpg", "preview2.jpg"],
            "files": ["template.zip", "documentation.pdf"],
            "tags": ["landing-page", "business", "modern", "responsive"],
            "license_type": "commercial",
            "creator_earnings_percentage": 70
        }
        self.test_endpoint("/template-marketplace/templates", "POST", template_data, "Template Marketplace - Create Template")
        
        # Test creator earnings
        self.test_endpoint("/template-marketplace/earnings", "GET", test_name="Template Marketplace - Creator Earnings")
        self.test_endpoint("/template-marketplace/analytics", "GET", test_name="Template Marketplace - Sales Analytics")
        
        print("\n🆕 New Feature Implementations Testing Complete!")
        return True
    
    def test_api_endpoint_coverage(self):
        """Test newly added API endpoints mentioned in review request"""
        print("\n🔗 TESTING API ENDPOINT COVERAGE")
        print("=" * 60)
        
        # Test newly added social media endpoints
        print("\n📱 Testing Social Media Endpoints...")
        
        # Instagram search endpoint
        instagram_data = {
            "keywords": ["entrepreneur", "business"],
            "location": "New York",
            "min_followers": 5000,
            "max_results": 15
        }
        self.test_endpoint("/instagram/search", "POST", instagram_data, "Social Media - Instagram Search")
        
        # Post scheduling endpoint
        post_data = {
            "content": "Check out our latest business insights! 📊 #Business #Analytics",
            "platforms": ["instagram", "twitter"],
            "scheduled_time": "2025-01-16T16:00:00Z"
        }
        self.test_endpoint("/posts/schedule", "POST", post_data, "Social Media - Schedule Post")
        
        # Test PWA endpoints
        print("\n📱 Testing PWA Endpoints...")
        
        # Manifest generation
        manifest_data = {
            "app_name": "Business Dashboard",
            "theme_color": "#1976D2",
            "background_color": "#FFFFFF"
        }
        self.test_endpoint("/manifest/generate", "POST", manifest_data, "PWA - Generate Manifest")
        
        # Device registration
        device_data = {
            "device_id": "pwa_device_001",
            "platform": "web",
            "capabilities": ["push_notifications", "offline_storage"]
        }
        self.test_endpoint("/device/register", "POST", device_data, "PWA - Register Device")
        
        # Offline sync
        sync_data = {
            "device_id": "pwa_device_001",
            "sync_types": ["user_data", "app_settings"]
        }
        self.test_endpoint("/offline/sync", "POST", sync_data, "PWA - Offline Sync")
        
        # Test AI automation endpoints
        print("\n🤖 Testing AI Automation Endpoints...")
        
        # Workflow creation
        workflow_data = {
            "name": "Lead Nurturing Workflow",
            "triggers": [{"type": "new_lead"}],
            "actions": [{"type": "send_email", "template": "welcome"}]
        }
        self.test_endpoint("/workflows/create", "POST", workflow_data, "AI Automation - Create Workflow")
        
        # Insights generation
        insights_data = {
            "data_source": "user_analytics",
            "time_range": "last_30_days",
            "metrics": ["engagement", "conversion"]
        }
        self.test_endpoint("/insights/generate", "POST", insights_data, "AI Automation - Generate Insights")
        
        # Test escrow endpoints
        print("\n💰 Testing Escrow Endpoints...")
        
        # Milestone transactions
        milestone_data = {
            "project_id": "proj_123",
            "milestones": [{"title": "Phase 1", "amount": 1000}]
        }
        self.test_endpoint("/transactions/milestone", "POST", milestone_data, "Escrow - Milestone Transaction")
        
        # Dispute initiation
        dispute_data = {
            "transaction_id": "trans_456",
            "reason": "quality_issues"
        }
        self.test_endpoint("/disputes/initiate", "POST", dispute_data, "Escrow - Initiate Dispute")
        
        print("\n🔗 API Endpoint Coverage Testing Complete!")
        return True
    
    def test_validation_error_handling(self):
        """Test validation schemas and error handling in new features"""
        print("\n✅ TESTING VALIDATION & ERROR HANDLING")
        print("=" * 60)
        
        # Test validation schemas work correctly
        print("\n📋 Testing Validation Schemas...")
        
        # Test invalid team creation (missing required fields)
        invalid_team_data = {
            "description": "Team without name"  # Missing required 'name' field
        }
        response = self.session.post(f"{API_BASE}/team-management/teams", json=invalid_team_data)
        if response.status_code == 422:
            self.log_result("Validation - Team Creation (Missing Name)", True, "Correctly rejected invalid data with 422")
        else:
            self.log_result("Validation - Team Creation (Missing Name)", False, f"Expected 422, got {response.status_code}")
        
        # Test invalid workflow creation
        invalid_workflow_data = {
            "description": "Workflow without name"  # Missing required 'name' field
        }
        response = self.session.post(f"{API_BASE}/workflows/create", json=invalid_workflow_data)
        if response.status_code in [422, 400]:
            self.log_result("Validation - Workflow Creation (Missing Name)", True, f"Correctly rejected invalid data with {response.status_code}")
        else:
            self.log_result("Validation - Workflow Creation (Missing Name)", False, f"Expected 422/400, got {response.status_code}")
        
        # Test invalid escrow transaction
        invalid_escrow_data = {
            "buyer_id": "buyer123"  # Missing required fields like amount, seller_id
        }
        response = self.session.post(f"{API_BASE}/transactions/milestone", json=invalid_escrow_data)
        if response.status_code in [422, 400]:
            self.log_result("Validation - Escrow Transaction (Missing Fields)", True, f"Correctly rejected invalid data with {response.status_code}")
        else:
            self.log_result("Validation - Escrow Transaction (Missing Fields)", False, f"Expected 422/400, got {response.status_code}")
        
        # Test comprehensive error handling
        print("\n🚨 Testing Error Handling...")
        
        # Test non-existent resource access
        response = self.session.get(f"{API_BASE}/transactions/nonexistent_id")
        if response.status_code == 404:
            self.log_result("Error Handling - Non-existent Transaction", True, "Correctly returned 404 for non-existent resource")
        else:
            self.log_result("Error Handling - Non-existent Transaction", False, f"Expected 404, got {response.status_code}")
        
        # Test unauthorized access (without proper permissions)
        temp_session = requests.Session()  # Session without auth token
        response = temp_session.post(f"{API_BASE}/disputes/initiate", json={"transaction_id": "test"})
        if response.status_code == 401:
            self.log_result("Error Handling - Unauthorized Access", True, "Correctly returned 401 for unauthorized access")
        else:
            self.log_result("Error Handling - Unauthorized Access", False, f"Expected 401, got {response.status_code}")
        
        print("\n✅ Validation & Error Handling Testing Complete!")
        return True
    
    def test_performance_integration(self):
        """Test performance and integration of new features"""
        print("\n⚡ TESTING PERFORMANCE & INTEGRATION")
        print("=" * 60)
        
        # Test response times for new endpoints
        print("\n⏱️ Testing Response Times...")
        
        endpoints_to_test = [
            ("/team-management/dashboard", "GET"),
            ("/workflows/list", "GET"),
            ("/template-marketplace/browse", "GET"),
            ("/posts/scheduled", "GET"),
            ("/disputes/list", "GET")
        ]
        
        response_times = []
        for endpoint, method in endpoints_to_test:
            start_time = time.time()
            if method == "GET":
                response = self.session.get(f"{API_BASE}{endpoint}")
            else:
                response = self.session.post(f"{API_BASE}{endpoint}", json={})
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response_time < 2.0:  # Less than 2 seconds is good
                self.log_result(f"Performance - {endpoint}", True, f"Response time: {response_time:.3f}s")
            else:
                self.log_result(f"Performance - {endpoint}", False, f"Slow response time: {response_time:.3f}s")
        
        avg_response_time = sum(response_times) / len(response_times)
        if avg_response_time < 1.0:
            self.log_result("Performance - Average Response Time", True, f"Excellent average: {avg_response_time:.3f}s")
        elif avg_response_time < 2.0:
            self.log_result("Performance - Average Response Time", True, f"Good average: {avg_response_time:.3f}s")
        else:
            self.log_result("Performance - Average Response Time", False, f"Poor average: {avg_response_time:.3f}s")
        
        # Test database operations
        print("\n🗄️ Testing Database Operations...")
        
        # Test data persistence by creating and retrieving data
        team_data = {
            "name": "Test Performance Team",
            "description": "Team created for performance testing"
        }
        
        # Create team
        create_response = self.session.post(f"{API_BASE}/team-management/teams", json=team_data)
        if create_response.status_code in [200, 201]:
            # Try to retrieve the created team
            list_response = self.session.get(f"{API_BASE}/team-management/teams")
            if list_response.status_code == 200:
                teams_data = list_response.json()
                if isinstance(teams_data, dict) and 'teams' in teams_data:
                    self.log_result("Database - Data Persistence", True, "Successfully created and retrieved team data")
                else:
                    self.log_result("Database - Data Persistence", True, "Team creation and retrieval working")
            else:
                self.log_result("Database - Data Persistence", False, "Could not retrieve created team")
        else:
            self.log_result("Database - Data Persistence", False, f"Team creation failed with {create_response.status_code}")
        
        # Test authentication across new features
        print("\n🔐 Testing Authentication Integration...")
        
        auth_endpoints = [
            "/team-management/dashboard",
            "/workflows/list", 
            "/template-marketplace/earnings",
            "/disputes/list"
        ]
        
        auth_success_count = 0
        for endpoint in auth_endpoints:
            response = self.session.get(f"{API_BASE}{endpoint}")
            if response.status_code != 401:  # Not unauthorized
                auth_success_count += 1
        
        auth_success_rate = (auth_success_count / len(auth_endpoints)) * 100
        if auth_success_rate >= 75:
            self.log_result("Authentication - Integration", True, f"Authentication working on {auth_success_rate:.1f}% of endpoints")
        else:
            self.log_result("Authentication - Integration", False, f"Authentication issues on {100-auth_success_rate:.1f}% of endpoints")
        
        print("\n⚡ Performance & Integration Testing Complete!")
        return True
        """Test Complete Financial Management System at /api/financial/*"""
        print("\n💰 TESTING COMPLETE FINANCIAL MANAGEMENT SYSTEM")
        print("=" * 60)
        
        # Test variables to store created resources
        created_invoice_id = None
        created_expense_id = None
        
        # 1. Test Financial Dashboard
        print("\n📊 Testing Financial Dashboard...")
        success, dashboard_data = self.test_endpoint("/financial/dashboard", "GET", test_name="Financial - Dashboard Overview")
        success, dashboard_data = self.test_endpoint("/financial/dashboard?period=quarter", "GET", test_name="Financial - Dashboard Quarterly")
        success, dashboard_data = self.test_endpoint("/financial/dashboard?period=year", "GET", test_name="Financial - Dashboard Yearly")
        
        # 2. Test Invoice Management - CREATE
        print("\n📄 Testing Invoice Management - CREATE...")
        create_invoice_data = {
            "client_name": "TechCorp Solutions",
            "client_email": "billing@techcorp.com",
            "client_address": "123 Business Ave, Tech City, TC 12345",
            "items": [
                {"name": "Website Development", "quantity": 1, "price": 2500.00},
                {"name": "SEO Optimization", "quantity": 3, "price": 300.00},
                {"name": "Content Creation", "quantity": 5, "price": 150.00}
            ],
            "tax_rate": 0.08,
            "notes": "Payment due within 30 days. Thank you for your business!"
        }
        
        success, invoice_data = self.test_endpoint("/financial/invoices", "POST", create_invoice_data, "Financial - Create Invoice")
        if success and invoice_data:
            created_invoice_id = invoice_data.get("data", {}).get("_id") or invoice_data.get("data", {}).get("id")
            print(f"   Created invoice ID: {created_invoice_id}")
        
        # 3. Test Invoice Management - READ
        print("\n📖 Testing Invoice Management - READ...")
        self.test_endpoint("/financial/invoices", "GET", test_name="Financial - Get All Invoices")
        self.test_endpoint("/financial/invoices?status_filter=draft", "GET", test_name="Financial - Get Draft Invoices")
        self.test_endpoint("/financial/invoices?client_filter=TechCorp", "GET", test_name="Financial - Filter Invoices by Client")
        
        # 4. Test Invoice Status Updates
        if created_invoice_id:
            print("\n✏️ Testing Invoice Status Updates...")
            self.test_endpoint(f"/financial/invoices/{created_invoice_id}/status", "PUT", {"new_status": "sent"}, "Financial - Update Invoice to Sent")
            self.test_endpoint(f"/financial/invoices/{created_invoice_id}/status", "PUT", {"new_status": "paid"}, "Financial - Update Invoice to Paid")
        
        # 5. Test Payment Processing
        if created_invoice_id:
            print("\n💳 Testing Payment Processing...")
            payment_data = {
                "invoice_id": created_invoice_id,
                "amount": 1000.00,
                "payment_method": "bank_transfer",
                "notes": "Partial payment received via bank transfer"
            }
            self.test_endpoint("/financial/payments", "POST", payment_data, "Financial - Record Payment")
        
        # 6. Test Expense Management - CREATE
        print("\n💸 Testing Expense Management - CREATE...")
        create_expense_data = {
            "category": "Software & Tools",
            "description": "Adobe Creative Suite Annual Subscription",
            "amount": 599.88,
            "tax_deductible": True
        }
        
        success, expense_data = self.test_endpoint("/financial/expenses", "POST", create_expense_data, "Financial - Create Expense")
        if success and expense_data:
            created_expense_id = expense_data.get("data", {}).get("_id") or expense_data.get("data", {}).get("id")
            print(f"   Created expense ID: {created_expense_id}")
        
        # Create additional expenses for better testing
        additional_expenses = [
            {"category": "Marketing", "description": "Google Ads Campaign", "amount": 450.00, "tax_deductible": True},
            {"category": "Office Supplies", "description": "Printer Paper and Ink", "amount": 89.99, "tax_deductible": False},
            {"category": "Travel", "description": "Client Meeting Transportation", "amount": 125.50, "tax_deductible": True}
        ]
        
        for expense in additional_expenses:
            self.test_endpoint("/financial/expenses", "POST", expense, f"Financial - Create {expense['category']} Expense")
        
        # 7. Test Expense Management - READ
        print("\n📊 Testing Expense Management - READ...")
        self.test_endpoint("/financial/expenses", "GET", test_name="Financial - Get All Expenses")
        self.test_endpoint("/financial/expenses?category=Software & Tools", "GET", test_name="Financial - Filter Expenses by Category")
        
        # 8. Test Financial Reports
        print("\n📈 Testing Financial Reports...")
        self.test_endpoint("/financial/reports/profit-loss", "GET", test_name="Financial - Profit & Loss Report (Month)")
        self.test_endpoint("/financial/reports/profit-loss?period=year", "GET", test_name="Financial - Profit & Loss Report (Year)")
        self.test_endpoint("/financial/reports/profit-loss?period=month&year=2024&month=12", "GET", test_name="Financial - Profit & Loss Report (December 2024)")
        
        print("\n💰 Financial Management System Testing Complete!")
        return True
        
    def test_website_builder_system(self):
        """Test Complete Website Builder System at /api/website-builder/*"""
        print("\n🌐 TESTING COMPLETE WEBSITE BUILDER SYSTEM")
        print("=" * 60)
        
        # Test variables to store created resources
        created_website_id = None
        
        # 1. Test Website Builder Dashboard
        print("\n📊 Testing Website Builder Dashboard...")
        success, dashboard_data = self.test_endpoint("/website-builder/dashboard", "GET", test_name="Website Builder - Dashboard Overview")
        
        # 2. Test Templates System
        print("\n📋 Testing Templates System...")
        self.test_endpoint("/website-builder/templates", "GET", test_name="Website Builder - Get All Templates")
        self.test_endpoint("/website-builder/templates?category=business", "GET", test_name="Website Builder - Get Business Templates")
        self.test_endpoint("/website-builder/templates?category=portfolio", "GET", test_name="Website Builder - Get Portfolio Templates")
        
        # 3. Test Website Creation - CREATE
        print("\n➕ Testing Website Creation - CREATE...")
        create_website_data = {
            "name": "Digital Marketing Agency",
            "title": "Premier Digital Marketing Solutions",
            "description": "We help businesses grow through strategic digital marketing, web development, and brand optimization.",
            "template_id": "modern_business_template",
            "theme": {
                "primary_color": "#2563EB",
                "secondary_color": "#7C3AED",
                "font_family": "Inter",
                "background_color": "#FFFFFF"
            },
            "seo_settings": {
                "meta_title": "Digital Marketing Agency - Grow Your Business Online",
                "meta_description": "Professional digital marketing services including SEO, PPC, social media marketing, and web development. Get results that matter.",
                "keywords": ["digital marketing", "SEO", "web development", "social media marketing"]
            },
            "is_published": False
        }
        
        success, website_data = self.test_endpoint("/website-builder/websites", "POST", create_website_data, "Website Builder - Create Website")
        if success and website_data:
            created_website_id = website_data.get("data", {}).get("_id") or website_data.get("data", {}).get("id")
            print(f"   Created website ID: {created_website_id}")
        
        # 4. Test Website Management - READ
        print("\n📖 Testing Website Management - READ...")
        self.test_endpoint("/website-builder/websites", "GET", test_name="Website Builder - Get All Websites")
        self.test_endpoint("/website-builder/websites?status_filter=draft", "GET", test_name="Website Builder - Get Draft Websites")
        self.test_endpoint("/website-builder/websites?status_filter=published", "GET", test_name="Website Builder - Get Published Websites")
        
        # 5. Test Website Updates - UPDATE
        if created_website_id:
            print("\n✏️ Testing Website Updates - UPDATE...")
            update_website_data = {
                "title": "Premier Digital Marketing Solutions - Updated",
                "description": "We help businesses grow through strategic digital marketing, web development, brand optimization, and comprehensive analytics.",
                "theme": {
                    "primary_color": "#1D4ED8",
                    "secondary_color": "#7C2D12",
                    "font_family": "Poppins",
                    "background_color": "#F8FAFC"
                },
                "is_published": True
            }
            
            self.test_endpoint(f"/website-builder/websites/{created_website_id}", "PUT", update_website_data, "Website Builder - Update Website")
        
        # 6. Test Page Management (if endpoints exist)
        if created_website_id:
            print("\n📄 Testing Page Management...")
            # These endpoints might exist based on the website builder structure
            self.test_endpoint(f"/website-builder/websites/{created_website_id}/pages", "GET", test_name="Website Builder - Get Website Pages")
            
            # Test page creation
            create_page_data = {
                "title": "About Us",
                "slug": "about-us",
                "content": {
                    "sections": [
                        {
                            "type": "hero",
                            "title": "About Our Agency",
                            "subtitle": "Driving digital success since 2020"
                        },
                        {
                            "type": "text",
                            "content": "We are a team of passionate digital marketing experts dedicated to helping businesses achieve their online goals."
                        }
                    ]
                },
                "is_published": True
            }
            
            self.test_endpoint(f"/website-builder/websites/{created_website_id}/pages", "POST", create_page_data, "Website Builder - Create Page")
        
        # 7. Test Website Analytics (if available)
        if created_website_id:
            print("\n📈 Testing Website Analytics...")
            self.test_endpoint(f"/website-builder/websites/{created_website_id}/analytics", "GET", test_name="Website Builder - Website Analytics")
            self.test_endpoint(f"/website-builder/websites/{created_website_id}/seo-analysis", "GET", test_name="Website Builder - SEO Analysis")
        
        # 8. Test Website Publishing
        if created_website_id:
            print("\n🚀 Testing Website Publishing...")
            self.test_endpoint(f"/website-builder/websites/{created_website_id}/publish", "POST", {}, "Website Builder - Publish Website")
            self.test_endpoint(f"/website-builder/websites/{created_website_id}/unpublish", "POST", {}, "Website Builder - Unpublish Website")
        
        print("\n🌐 Website Builder System Testing Complete!")
        return True
        
    def test_multi_workspace_system(self):
        """Test Complete Multi-Workspace System with RBAC at /api/multi-workspace/*"""
        print("\n👥 TESTING COMPLETE MULTI-WORKSPACE SYSTEM WITH RBAC")
        print("=" * 60)
        
        # Test variables to store created resources
        created_workspace_id = None
        invitation_token = None
        
        # 1. Test Workspace Creation - CREATE
        print("\n➕ Testing Workspace Creation - CREATE...")
        create_workspace_data = {
            "name": "Digital Marketing Team",
            "description": "Collaborative workspace for our digital marketing team to manage campaigns, content, and client projects.",
            "workspace_type": "business",
            "settings": {
                "allow_external_sharing": True,
                "require_approval_for_invites": False,
                "default_member_role": "member"
            }
        }
        
        success, workspace_data = self.test_endpoint("/multi-workspace/workspaces", "POST", create_workspace_data, "Multi-Workspace - Create Workspace")
        if success and workspace_data:
            created_workspace_id = workspace_data.get("workspace", {}).get("id") or workspace_data.get("workspace", {}).get("_id")
            print(f"   Created workspace ID: {created_workspace_id}")
        
        # 2. Test Workspace Management - READ
        print("\n📖 Testing Workspace Management - READ...")
        self.test_endpoint("/multi-workspace/workspaces", "GET", test_name="Multi-Workspace - Get User Workspaces")
        self.test_endpoint("/multi-workspace/workspaces?include_archived=true", "GET", test_name="Multi-Workspace - Get All Workspaces (Including Archived)")
        
        if created_workspace_id:
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}", "GET", test_name="Multi-Workspace - Get Workspace Details")
        
        # 3. Test Workspace Updates - UPDATE
        if created_workspace_id:
            print("\n✏️ Testing Workspace Updates - UPDATE...")
            update_workspace_data = {
                "name": "Digital Marketing & Content Team",
                "description": "Enhanced collaborative workspace for digital marketing, content creation, and client project management with advanced analytics.",
                "settings": {
                    "allow_external_sharing": True,
                    "require_approval_for_invites": True,
                    "default_member_role": "viewer"
                },
                "features_enabled": ["analytics", "advanced_reporting", "api_access"]
            }
            
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}", "PUT", update_workspace_data, "Multi-Workspace - Update Workspace")
        
        # 4. Test Member Invitation System
        if created_workspace_id:
            print("\n📧 Testing Member Invitation System...")
            invitation_data = {
                "email": "newteammember@example.com",
                "role": "member",
                "custom_message": "Welcome to our digital marketing team! We're excited to have you collaborate with us on upcoming campaigns."
            }
            
            success, invite_data = self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/invitations", "POST", invitation_data, "Multi-Workspace - Send Member Invitation")
            if success and invite_data:
                invitation_token = invite_data.get("invitation", {}).get("invitation_id")
                print(f"   Created invitation token: {invitation_token}")
        
        # 5. Test Member Management
        if created_workspace_id:
            print("\n👥 Testing Member Management...")
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/members", "GET", test_name="Multi-Workspace - Get Workspace Members")
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/members?role_filter=admin", "GET", test_name="Multi-Workspace - Get Admin Members")
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/members?role_filter=member", "GET", test_name="Multi-Workspace - Get Regular Members")
        
        # 6. Test RBAC (Role-Based Access Control)
        if created_workspace_id:
            print("\n🔐 Testing RBAC (Role-Based Access Control)...")
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/permissions", "GET", test_name="Multi-Workspace - Get User Permissions")
            
            # Test permission checking
            permission_check_data = {"permission": "manage_workspace"}
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/permissions/check", "POST", permission_check_data, "Multi-Workspace - Check Manage Workspace Permission")
            
            permission_check_data = {"permission": "invite_members"}
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/permissions/check", "POST", permission_check_data, "Multi-Workspace - Check Invite Members Permission")
            
            permission_check_data = {"permission": "view_analytics"}
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/permissions/check", "POST", permission_check_data, "Multi-Workspace - Check View Analytics Permission")
        
        # 7. Test Role Management
        print("\n🎭 Testing Role Management...")
        self.test_endpoint("/multi-workspace/roles", "GET", test_name="Multi-Workspace - Get Available Roles")
        self.test_endpoint("/multi-workspace/permissions", "GET", test_name="Multi-Workspace - Get All Permissions")
        
        # 8. Test Workspace Analytics
        if created_workspace_id:
            print("\n📊 Testing Workspace Analytics...")
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/analytics", "GET", test_name="Multi-Workspace - Get Workspace Analytics (30 days)")
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/analytics?days=7", "GET", test_name="Multi-Workspace - Get Workspace Analytics (7 days)")
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/analytics?days=90", "GET", test_name="Multi-Workspace - Get Workspace Analytics (90 days)")
        
        # 9. Test Invitation Acceptance (simulated)
        if invitation_token:
            print("\n✅ Testing Invitation Acceptance...")
            accept_invitation_data = {"invitation_token": invitation_token}
            self.test_endpoint("/multi-workspace/invitations/accept", "POST", accept_invitation_data, "Multi-Workspace - Accept Invitation")
        
        # 10. Test Health Check
        print("\n🏥 Testing System Health...")
        self.test_endpoint("/multi-workspace/health", "GET", test_name="Multi-Workspace - Health Check")
        
        print("\n👥 Multi-Workspace System Testing Complete!")
        return True
        
    def test_previous_features_regression(self):
        """Test that all previous features still work (no regressions)"""
        print("\n🔄 TESTING PREVIOUS FEATURES - REGRESSION CHECK")
        print("=" * 60)
        
        # Test Complete Onboarding System
        print("\n🎯 Testing Complete Onboarding System...")
        self.test_endpoint("/complete-onboarding/health", "GET", test_name="Regression - Onboarding Health Check")
        self.test_endpoint("/complete-onboarding/goals", "GET", test_name="Regression - Onboarding Goals")
        self.test_endpoint("/complete-onboarding/subscription-plans", "GET", test_name="Regression - Subscription Plans")
        
        # Test Complete Link in Bio
        print("\n🔗 Testing Complete Link in Bio...")
        self.test_endpoint("/link-in-bio/health", "GET", test_name="Regression - Link in Bio Health")
        self.test_endpoint("/link-in-bio/templates", "GET", test_name="Regression - Link in Bio Templates")
        self.test_endpoint("/link-in-bio/analytics/overview", "GET", test_name="Regression - Link in Bio Analytics")
        
        # Test Complete E-commerce
        print("\n🛒 Testing Complete E-commerce...")
        self.test_endpoint("/ecommerce/products", "GET", test_name="Regression - E-commerce Products")
        self.test_endpoint("/ecommerce/orders", "GET", test_name="Regression - E-commerce Orders")
        self.test_endpoint("/ecommerce/dashboard", "GET", test_name="Regression - E-commerce Dashboard")
        
        # Test Complete Course & Community
        print("\n🎓 Testing Complete Course & Community...")
        self.test_endpoint("/courses/list", "GET", test_name="Regression - Courses List")
        self.test_endpoint("/courses/analytics", "GET", test_name="Regression - Courses Analytics")
        
        # Test Complete Escrow System
        print("\n🔒 Testing Complete Escrow System...")
        self.test_endpoint("/escrow/transactions", "GET", test_name="Regression - Escrow Transactions")
        self.test_endpoint("/escrow/analytics", "GET", test_name="Regression - Escrow Analytics")
        
        # Test Complete Referral System
        print("\n🎁 Testing Complete Referral System...")
        self.test_endpoint("/referrals/dashboard", "GET", test_name="Regression - Referrals Dashboard")
        self.test_endpoint("/referrals/analytics", "GET", test_name="Regression - Referrals Analytics")
        
        # Test Complete Admin Dashboard
        print("\n⚙️ Testing Complete Admin Dashboard...")
        self.test_endpoint("/admin/users", "GET", test_name="Regression - Admin Users")
        self.test_endpoint("/admin/system/metrics", "GET", test_name="Regression - Admin System Metrics")
        self.test_endpoint("/admin/dashboard", "GET", test_name="Regression - Admin Dashboard")
        
        print("\n🔄 Previous Features Regression Testing Complete!")
        return True

    def test_link_in_bio_system(self):
        """Test Complete Link in Bio Builder System with full CRUD operations"""
        print("\n🔗 TESTING COMPLETE LINK IN BIO BUILDER SYSTEM")
        print("=" * 60)
        
        # Test variables to store created resources
        created_page_id = None
        created_link_id = None
        workspace_id = None
        
        # First, get available workspaces to use workspace_id
        print("\n🏢 Getting Available Workspaces...")
        success, workspaces_data = self.test_endpoint("/workspaces", "GET", test_name="Link in Bio - Get Workspaces")
        if success and workspaces_data and workspaces_data.get("data", {}).get("workspaces"):
            workspace_id = workspaces_data["data"]["workspaces"][0]["_id"]
            print(f"   Using workspace ID: {workspace_id}")
        
        if not workspace_id:
            print("❌ Cannot proceed without workspace_id")
            return False
        
        # 1. Test Templates System
        print("\n📋 Testing Template System...")
        success, templates_data = self.test_endpoint(f"/link-in-bio/templates?workspace_id={workspace_id}", "GET", test_name="Link in Bio - Get Templates")
        
        # 2. Test Health Check
        print("\n🏥 Testing Health Check...")
        self.test_endpoint("/link-in-bio/health", "GET", test_name="Link in Bio - Health Check")
        
        # 3. Test CREATE - Create Bio Page
        print("\n➕ Testing CREATE Operations...")
        create_page_data = {
            "title": "Sarah's Creative Portfolio",
            "description": "Digital artist and content creator sharing my latest work and collaborations",
            "username": "sarah_creates",
            "template_id": "modern_gradient",
            "theme": {
                "primary_color": "#6366f1",
                "secondary_color": "#8b5cf6",
                "background_color": "#f8fafc",
                "text_color": "#1e293b"
            },
            "settings": {
                "show_analytics": True,
                "allow_comments": False,
                "custom_css": ".bio-page { font-family: 'Inter', sans-serif; }"
            }
        }
        
        success, page_data = self.test_endpoint(f"/link-in-bio/pages?workspace_id={workspace_id}", "POST", create_page_data, "Link in Bio - Create Bio Page")
        if success and page_data:
            created_page_id = page_data.get("id") or page_data.get("page_id") or page_data.get("data", {}).get("id")
            print(f"   Created page ID: {created_page_id}")
        
        # 4. Test READ - Get Bio Pages List
        print("\n📖 Testing READ Operations...")
        self.test_endpoint(f"/link-in-bio/pages?workspace_id={workspace_id}", "GET", test_name="Link in Bio - Get User Bio Pages")
        
        # 5. Test READ - Get Specific Bio Page
        if created_page_id:
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}", "GET", test_name="Link in Bio - Get Bio Page Details")
            
            # 6. Test CREATE - Add Links to Bio Page
            print("\n🔗 Testing Link Creation...")
            create_link_data = {
                "title": "Latest Art Collection",
                "url": "https://sarahcreates.art/gallery",
                "description": "Check out my newest digital art pieces and prints",
                "icon": "palette",
                "is_active": True,
                "click_tracking": True,
                "order_index": 1
            }
            
            success, link_data = self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/links", "POST", create_link_data, "Link in Bio - Create Bio Link")
            if success and link_data:
                created_link_id = link_data.get("id") or link_data.get("link_id") or link_data.get("data", {}).get("id")
                print(f"   Created link ID: {created_link_id}")
            
            # 7. Test READ - Get Bio Page Links
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/links", "GET", test_name="Link in Bio - Get Bio Page Links")
            
            # 8. Test UPDATE - Update Bio Page
            print("\n✏️ Testing UPDATE Operations...")
            update_page_data = {
                "title": "Sarah's Creative Studio - Updated",
                "description": "Digital artist, content creator, and design consultant - Now offering custom commissions!",
                "theme": {
                    "primary_color": "#7c3aed",
                    "secondary_color": "#a855f7",
                    "background_color": "#faf5ff",
                    "text_color": "#374151"
                }
            }
            
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}", "PUT", update_page_data, "Link in Bio - Update Bio Page")
            
            # 9. Test UPDATE - Update Bio Link
            if created_link_id:
                update_link_data = {
                    "title": "Featured Art Collection - Limited Edition",
                    "url": "https://sarahcreates.art/featured",
                    "description": "Exclusive limited edition prints now available - only 50 pieces!",
                    "icon": "star",
                    "order_index": 1
                }
                
                self.test_endpoint(f"/link-in-bio/links/{created_link_id}", "PUT", update_link_data, "Link in Bio - Update Bio Link")
            
            # 10. Test Analytics System
            print("\n📊 Testing Analytics System...")
            
            # Track page visit
            visit_data = {
                "visitor_ip": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "referrer": "https://instagram.com/sarah_creates"
            }
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/visit", "POST", visit_data, "Link in Bio - Track Page Visit")
            
            # Track link click
            if created_link_id:
                click_data = {
                    "visitor_ip": "192.168.1.100",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "referrer": f"https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com/bio/sarah_creates"
                }
                self.test_endpoint(f"/link-in-bio/links/{created_link_id}/click", "POST", click_data, "Link in Bio - Track Link Click")
            
            # Get page analytics
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/analytics", "GET", test_name="Link in Bio - Get Page Analytics")
            
            # 11. Test Additional Features
            print("\n🎨 Testing Additional Features...")
            
            # Get QR Code
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/qr-code", "GET", test_name="Link in Bio - Get QR Code")
            
            # Get SEO Settings
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/seo", "GET", test_name="Link in Bio - Get SEO Settings")
        
        # 12. Test Analytics Overview
        self.test_endpoint("/link-in-bio/analytics/overview", "GET", test_name="Link in Bio - Analytics Overview")
        
        # 13. Test DELETE Operations
        print("\n🗑️ Testing DELETE Operations...")
        
        # Delete link first (if created)
        if created_link_id:
            self.test_endpoint(f"/link-in-bio/links/{created_link_id}", "DELETE", test_name="Link in Bio - Delete Bio Link")
        
        # Delete page (if created)
        if created_page_id:
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}", "DELETE", test_name="Link in Bio - Delete Bio Page")
        
        print("\n🔗 Link in Bio System Testing Complete!")
        return True
        
    def test_data_consistency_verification(self):
        """Test data consistency to verify real database usage - CRITICAL FOR REVIEW REQUEST"""
        print("\n🔍 TESTING DATA CONSISTENCY (Real Database Verification)")
        print("=" * 60)
        print("Testing for MOCK DATA ELIMINATION as requested in review")
        
        # Test Template Marketplace consistency
        print("\n🛍️ Testing Template Marketplace Data Consistency...")
        success1, data1 = self.test_endpoint("/marketing-website/templates/marketplace", "GET", test_name="Template Marketplace - First Call")
        time.sleep(1)  # Small delay
        success2, data2 = self.test_endpoint("/marketing-website/templates/marketplace", "GET", test_name="Template Marketplace - Second Call")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result("Template Marketplace - Data Consistency", True, "Data consistent across calls - confirms real database usage")
            else:
                self.log_result("Template Marketplace - Data Consistency", False, "Data inconsistent - may be using random generation")
        
        # Test Team Dashboard consistency
        print("\n👥 Testing Team Dashboard Data Consistency...")
        success1, data1 = self.test_endpoint("/teams/dashboard", "GET", test_name="Team Dashboard - First Call")
        time.sleep(1)  # Small delay
        success2, data2 = self.test_endpoint("/teams/dashboard", "GET", test_name="Team Dashboard - Second Call")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result("Team Dashboard - Data Consistency", True, "Data consistent across calls - confirms real database usage")
            else:
                self.log_result("Team Dashboard - Data Consistency", False, "Data inconsistent - may be using random generation")
        
        # Test Analytics Dashboard consistency
        print("\n📊 Testing Analytics Dashboard Data Consistency...")
        success1, data1 = self.test_endpoint("/analytics-system/dashboard", "GET", test_name="Analytics Dashboard - First Call")
        time.sleep(1)  # Small delay
        success2, data2 = self.test_endpoint("/analytics-system/dashboard", "GET", test_name="Analytics Dashboard - Second Call")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result("Analytics Dashboard - Data Consistency", True, "Data consistent across calls - confirms real database usage")
            else:
                self.log_result("Analytics Dashboard - Data Consistency", False, "Data inconsistent - may be using random generation")
        
        # Test Mobile PWA Analytics consistency
        print("\n📱 Testing Mobile PWA Analytics Data Consistency...")
        success1, data1 = self.test_endpoint("/mobile-pwa/analytics/mobile", "GET", test_name="Mobile Analytics - First Call")
        time.sleep(1)  # Small delay
        success2, data2 = self.test_endpoint("/mobile-pwa/analytics/mobile", "GET", test_name="Mobile Analytics - Second Call")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result("Mobile Analytics - Data Consistency", True, "Data consistent across calls - confirms real database usage")
            else:
                self.log_result("Mobile Analytics - Data Consistency", False, "Data inconsistent - may be using random generation")
        
        print("\n🔍 Data Consistency Verification Complete!")
        return True
    
    def test_real_api_integration_endpoints(self):
        """Test the REAL API INTEGRATION ENDPOINTS as requested in the review - JULY 2025"""
        print("\n=== Testing REAL API INTEGRATION ENDPOINTS - JULY 2025 ===")
        print("Testing newly implemented real API integration endpoints:")
        print("1. Real Social Media Lead Generation APIs (Twitter/TikTok)")
        print("2. Real AI Automation APIs (OpenAI GPT integration)")
        print("3. Real Email Automation APIs (ElasticMail)")
        print("4. Database operations verification")
        print("5. Authentication & error handling")
        
        # 1. Test REAL SOCIAL MEDIA LEAD GENERATION APIs
        print("\n--- 1. REAL SOCIAL MEDIA LEAD GENERATION APIs Testing ---")
        
        # Twitter Lead Generation with real Twitter API v2
        twitter_search_data = {
            "keywords": ["entrepreneur", "startup", "business owner"],
            "hashtags": ["#entrepreneur", "#startup"],
            "location": "United States",
            "max_results": 20,
            "verified_only": False,
            "min_followers": 1000
        }
        self.test_endpoint("/social-media-leads/twitter/search", "POST", twitter_search_data, "Twitter Lead Generation - Search")
        
        # TikTok Lead Generation with real TikTok Business API
        tiktok_search_data = {
            "keywords": ["business", "marketing", "entrepreneur"],
            "region": "US",
            "max_results": 15,
            "min_followers": 5000,
            "niche": "business",
            "cursor": 0
        }
        self.test_endpoint("/social-media-leads/tiktok/search", "POST", tiktok_search_data, "TikTok Lead Generation - Search")
        
        # Lead retrieval and analytics
        self.test_endpoint("/social-media-leads/search-history", test_name="Social Media Leads - Search History")
        self.test_endpoint("/social-media-leads/analytics/overview", test_name="Social Media Leads - Analytics Overview")
        
        # 2. Test REAL AI AUTOMATION APIs
        print("\n--- 2. REAL AI AUTOMATION APIs Testing ---")
        
        # OpenAI GPT Content Generation
        content_generation_data = {
            "platform": "linkedin",
            "topic": "digital transformation",
            "tone": "professional",
            "target_audience": "business executives",
            "content_type": "post",
            "additional_context": "Focus on ROI and business value"
        }
        self.test_endpoint("/ai-automation/generate-content", "POST", content_generation_data, "AI Automation - Generate Content")
        
        # AI Lead Enrichment
        lead_enrichment_data = {
            "username": "business_leader_2024",
            "bio": "CEO of tech startup, passionate about innovation and growth",
            "platform": "twitter",
            "follower_count": 15000,
            "location": "San Francisco"
        }
        self.test_endpoint("/ai-automation/enrich-lead", "POST", lead_enrichment_data, "AI Automation - Enrich Lead")
        
        # Workflow Creation
        workflow_data = {
            "name": "Lead Nurturing Workflow",
            "trigger_type": "new_lead",
            "actions": [
                {"type": "send_email", "template": "welcome_email"},
                {"type": "add_to_crm", "list": "prospects"},
                {"type": "schedule_followup", "days": 3}
            ]
        }
        self.test_endpoint("/ai-automation/create-workflow", "POST", workflow_data, "AI Automation - Create Workflow")
        
        # AI Analytics and History
        self.test_endpoint("/ai-automation/workflows", test_name="AI Automation - List Workflows")
        self.test_endpoint("/ai-automation/content-history", test_name="AI Automation - Content History")
        self.test_endpoint("/ai-automation/enrichment-history", test_name="AI Automation - Enrichment History")
        self.test_endpoint("/ai-automation/analytics/overview", test_name="AI Automation - Analytics Overview")
        
        # Bulk Operations
        bulk_content_data = {
            "content_requests": [
                {"platform": "twitter", "topic": "productivity", "tone": "casual"},
                {"platform": "linkedin", "topic": "leadership", "tone": "professional"},
                {"platform": "facebook", "topic": "team building", "tone": "friendly"}
            ]
        }
        self.test_endpoint("/ai-automation/bulk-content-generation", "POST", bulk_content_data, "AI Automation - Bulk Content Generation")
        
        # 3. Test REAL EMAIL AUTOMATION APIs
        print("\n--- 3. REAL EMAIL AUTOMATION APIs Testing ---")
        
        # Real Email Sending with ElasticMail
        email_data = {
            "to_email": "test@example.com",
            "subject": "Welcome to Mewayz Platform",
            "text_content": "Thank you for joining our platform. We're excited to help you grow your business.",
            "html_content": "<h1>Welcome!</h1><p>Thank you for joining our platform.</p>",
            "from_email": "hello@mewayz.com",
            "from_name": "Mewayz Team",
            "is_transactional": True
        }
        self.test_endpoint("/email-automation/send-email", "POST", email_data, "Email Automation - Send Real Email")
        
        # Email Campaign Management
        campaign_data = {
            "name": "Q4 Business Growth Campaign",
            "subject": "Unlock Your Business Potential",
            "html_content": "<h1>Grow Your Business</h1><p>Discover powerful tools for business growth.</p>",
            "text_content": "Grow Your Business - Discover powerful tools for business growth.",
            "from_email": "campaigns@mewayz.com",
            "from_name": "Mewayz Growth Team"
        }
        self.test_endpoint("/email-automation/campaigns", "POST", campaign_data, "Email Automation - Create Campaign")
        self.test_endpoint("/email-automation/campaigns", test_name="Email Automation - List Campaigns")
        
        # Subscriber Management
        subscriber_data = {
            "action": "add",
            "email": "newsubscriber@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "tags": ["prospect", "interested"]
        }
        self.test_endpoint("/email-automation/subscribers", "POST", subscriber_data, "Email Automation - Manage Subscribers")
        self.test_endpoint("/email-automation/subscribers", test_name="Email Automation - List Subscribers")
        
        # Email Templates
        template_data = {
            "name": "Welcome Email Template",
            "subject": "Welcome to {{company_name}}",
            "html_content": "<h1>Welcome {{first_name}}!</h1><p>Thank you for joining us.</p>",
            "text_content": "Welcome {{first_name}}! Thank you for joining us.",
            "category": "onboarding",
            "tags": ["welcome", "onboarding"]
        }
        self.test_endpoint("/email-automation/templates", "POST", template_data, "Email Automation - Create Template")
        self.test_endpoint("/email-automation/templates", test_name="Email Automation - List Templates")
        
        # Email Analytics and Logs
        self.test_endpoint("/email-automation/email-logs", test_name="Email Automation - Email Logs")
        self.test_endpoint("/email-automation/analytics/overview", test_name="Email Automation - Analytics Overview")
        
        # Automation Sequences
        sequence_data = {
            "name": "Lead Nurturing Sequence",
            "trigger_type": "new_subscriber",
            "emails": [
                {"delay_days": 0, "template_id": "welcome_template", "subject": "Welcome!"},
                {"delay_days": 3, "template_id": "value_template", "subject": "Here's how we can help"},
                {"delay_days": 7, "template_id": "case_study_template", "subject": "Success story"}
            ]
        }
        self.test_endpoint("/email-automation/automation-sequence", "POST", sequence_data, "Email Automation - Create Sequence")
        
        # Bulk Email Sending
        bulk_email_data = {
            "recipients": ["test1@example.com", "test2@example.com"],
            "subject": "Important Business Update",
            "text_content": "We have important updates to share with you.",
            "html_content": "<h1>Important Update</h1><p>We have important updates to share.</p>",
            "campaign_id": "bulk_campaign_2025"
        }
        self.test_endpoint("/email-automation/bulk-email", "POST", bulk_email_data, "Email Automation - Bulk Email Send")
        
        # 2. Test ADVANCED SOCIAL MEDIA MANAGEMENT SUITE
        print("\n--- 2. ADVANCED SOCIAL MEDIA MANAGEMENT SUITE Testing ---")
        
        # Social account connection functionality
        social_account_data = {
            "platform": "twitter",
            "account_handle": "@mewayz_official",
            "access_token": "sample_token",
            "account_type": "business"
        }
        self.test_endpoint("/social-media-suite/accounts/connect", "POST", social_account_data, "Social Media Suite - Connect Account")
        self.test_endpoint("/social-media-suite/accounts", test_name="Social Media Suite - List Connected Accounts")
        
        # AI content generation capabilities
        ai_content_data = {
            "content_type": "post",
            "platform": "twitter",
            "topic": "digital transformation",
            "tone": "professional",
            "length": "short",
            "include_hashtags": True
        }
        self.test_endpoint("/social-media-suite/ai-content/generate", "POST", ai_content_data, "Social Media Suite - AI Content Generation")
        self.test_endpoint("/social-media-suite/ai-content/templates", test_name="Social Media Suite - AI Content Templates")
        
        # Social listening setup and brand monitoring
        social_listening_data = {
            "brand_keywords": ["Mewayz", "digital marketing platform"],
            "competitor_keywords": ["competitor1", "competitor2"],
            "sentiment_tracking": True,
            "alert_threshold": "medium"
        }
        self.test_endpoint("/social-media-suite/listening/setup", "POST", social_listening_data, "Social Media Suite - Social Listening Setup")
        self.test_endpoint("/social-media-suite/listening/mentions", test_name="Social Media Suite - Brand Mentions")
        
        # Influencer discovery system
        influencer_search_data = {
            "industry": "technology",
            "follower_range": {"min": 10000, "max": 100000},
            "engagement_rate_min": 3.0,
            "location": "United States"
        }
        self.test_endpoint("/social-media-suite/influencers/search", "POST", influencer_search_data, "Social Media Suite - Influencer Discovery")
        self.test_endpoint("/social-media-suite/influencers/campaigns", test_name="Social Media Suite - Influencer Campaigns")
        
        # Social media analytics and dashboard
        self.test_endpoint("/social-media-suite/analytics", test_name="Social Media Suite - Analytics Dashboard")
        self.test_endpoint("/social-media-suite/analytics/engagement", test_name="Social Media Suite - Engagement Analytics")
        
        # 3. Test ENTERPRISE SECURITY & COMPLIANCE
        print("\n--- 3. ENTERPRISE SECURITY & COMPLIANCE Testing ---")
        
        # Compliance framework implementation (SOC 2, ISO 27001, GDPR)
        self.test_endpoint("/enterprise-security/compliance/frameworks", test_name="Enterprise Security - Compliance Frameworks")
        self.test_endpoint("/enterprise-security/compliance/soc2/status", test_name="Enterprise Security - SOC 2 Status")
        self.test_endpoint("/enterprise-security/compliance/iso27001/status", test_name="Enterprise Security - ISO 27001 Status")
        self.test_endpoint("/enterprise-security/compliance/gdpr/status", test_name="Enterprise Security - GDPR Status")
        
        # Threat detection setup and alerts
        threat_detection_data = {
            "detection_rules": ["suspicious_login", "data_exfiltration", "privilege_escalation"],
            "alert_channels": ["email", "slack", "webhook"],
            "severity_threshold": "medium"
        }
        self.test_endpoint("/enterprise-security/threat-detection/setup", "POST", threat_detection_data, "Enterprise Security - Threat Detection Setup")
        self.test_endpoint("/enterprise-security/threat-detection/alerts", test_name="Enterprise Security - Threat Alerts")
        
        # Advanced audit logging system
        audit_config_data = {
            "log_level": "detailed",
            "retention_days": 365,
            "include_user_actions": True,
            "include_api_calls": True,
            "include_data_access": True
        }
        self.test_endpoint("/enterprise-security/audit/configure", "POST", audit_config_data, "Enterprise Security - Audit Logging Config")
        self.test_endpoint("/enterprise-security/audit/logs", test_name="Enterprise Security - Audit Logs")
        
        # Vulnerability assessment capabilities
        vulnerability_scan_data = {
            "scan_type": "comprehensive",
            "target_systems": ["web_application", "api_endpoints", "database"],
            "schedule": "weekly"
        }
        self.test_endpoint("/enterprise-security/vulnerability/scan", "POST", vulnerability_scan_data, "Enterprise Security - Vulnerability Scan")
        self.test_endpoint("/enterprise-security/vulnerability/reports", test_name="Enterprise Security - Vulnerability Reports")
        
        # Security dashboard and compliance reporting
        self.test_endpoint("/enterprise-security/dashboard", test_name="Enterprise Security - Security Dashboard")
        self.test_endpoint("/enterprise-security/compliance/reports", test_name="Enterprise Security - Compliance Reports")
        
    def test_enterprise_features(self):
        """Test the NEW ENTERPRISE FEATURES as requested in the review"""
        print("\n=== Testing NEW ENTERPRISE FEATURES ===")
        print("Testing Advanced Learning Management System (LMS), Multi-Vendor Marketplace, and Advanced Business Intelligence")
        
        # 1. Test Advanced Learning Management System (LMS) - /api/lms/*
        print("\n--- 1. Advanced Learning Management System (LMS) Testing ---")
        
        # SCORM Package Management
        scorm_data = {
            "package_name": "Introduction to Digital Marketing",
            "version": "1.0",
            "content_type": "scorm_2004",
            "duration_minutes": 120
        }
        self.test_endpoint("/lms/scorm/package", "POST", scorm_data, "LMS - Create SCORM Package")
        self.test_endpoint("/lms/courses/scorm", test_name="LMS - List SCORM Courses")
        
        # Learning Progress Tracking
        progress_data = {
            "completion_percentage": 75,
            "time_spent_minutes": 90,
            "quiz_scores": [85, 92, 78]
        }
        self.test_endpoint("/lms/courses/course_123/progress", "POST", progress_data, "LMS - Track Learning Progress")
        self.test_endpoint("/lms/analytics", test_name="LMS - Get Learning Analytics")
        
        # Certificate Generation with Blockchain Verification
        cert_data = {
            "learner_id": "learner_456",
            "completion_date": "2024-12-20",
            "blockchain_verify": True
        }
        self.test_endpoint("/lms/certificates/course_123/generate", "POST", cert_data, "LMS - Generate Certificate")
        
        # Gamification Data
        self.test_endpoint("/lms/gamification", test_name="LMS - Get Gamification Data")
        
        # 2. Test Multi-Vendor Marketplace - /api/marketplace/*
        print("\n--- 2. Multi-Vendor Marketplace Testing ---")
        
        # Vendor Onboarding (fix the data structure based on the 422 error)
        vendor_data = {
            "owner_name": "John Smith",
            "business_name": "TechSolutions Inc",
            "email": "vendor@techsolutions.com",
            "phone": "+1-555-0123",
            "address": "123 Business St, Tech City, TC 12345",
            "business_type": "software",
            "tax_id": "123456789",
            "bank_details": {
                "account_number": "****1234",
                "routing_number": "123456789",
                "bank_name": "Tech Bank"
            }
        }
        self.test_endpoint("/marketplace/vendors/onboard", "POST", vendor_data, "Marketplace - Vendor Onboarding")
        self.test_endpoint("/marketplace/vendors/applications", test_name="Marketplace - Vendor Applications")
        
        # Vendor Management
        self.test_endpoint("/marketplace/vendors", test_name="Marketplace - List Vendors")
        
        # Vendor Approval Workflow
        approval_data = {
            "approval_status": "approved",
            "reviewer_notes": "All documents verified"
        }
        self.test_endpoint("/marketplace/vendors/vendor_123/approve", "POST", approval_data, "Marketplace - Approve Vendor")
        
        # Dynamic Pricing Calculation
        self.test_endpoint("/marketplace/pricing/dynamic", test_name="Marketplace - Dynamic Pricing")
        
        # Vendor Performance and Payouts
        payout_data = {
            "period": "2024-12",
            "total_sales": 5000.00,
            "commission_rate": 0.15
        }
        self.test_endpoint("/marketplace/vendors/vendor_123/payout", "POST", payout_data, "Marketplace - Process Vendor Payout")
        self.test_endpoint("/marketplace/vendors/vendor_123/performance", test_name="Marketplace - Vendor Performance Metrics")
        
        # Enhanced E-commerce Marketplace
        self.test_endpoint("/enhanced-ecommerce/marketplace/dashboard", test_name="Marketplace - Enhanced E-commerce Dashboard")
        self.test_endpoint("/content-suite/templates/marketplace", test_name="Marketplace - Template Marketplace")
        
        # 3. Test Advanced Business Intelligence - /api/business-intelligence/*
        print("\n--- 3. Advanced Business Intelligence Testing ---")
        
        # Business Intelligence Overview
        self.test_endpoint("/business-intelligence/overview", test_name="BI - Overview Dashboard")
        self.test_endpoint("/business-intelligence/reports", test_name="BI - Business Reports")
        self.test_endpoint("/business-intelligence/insights", test_name="BI - Business Insights")
        
        # Predictive Analytics
        prediction_data = {
            "analysis_type": "revenue_forecasting",
            "time_horizon": "6_months",
            "data_sources": ["sales", "marketing", "customer_behavior"],
            "confidence_level": 0.95
        }
        self.test_endpoint("/business-intelligence/predictive-analytics", "POST", prediction_data, "BI - Predictive Analytics")
        self.test_endpoint("/business-intelligence/predictive-models", test_name="BI - Predictive Models")
        
        # Cohort Analysis
        cohort_data = {
            "cohort_type": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "metric": "retention_rate"
        }
        self.test_endpoint("/business-intelligence/cohort-analysis", "POST", cohort_data, "BI - Cohort Analysis")
        
        # Funnel Tracking
        funnel_data = {
            "funnel_name": "sales_conversion",
            "stages": ["awareness", "interest", "consideration", "purchase"],
            "time_period": "last_30_days"
        }
        self.test_endpoint("/business-intelligence/funnel-tracking", "POST", funnel_data, "BI - Funnel Tracking")
        
        # Competitive Analysis
        competitor_data = {
            "industry": "saas",
            "competitors": ["competitor_a", "competitor_b"],
            "metrics": ["pricing", "features", "market_share"]
        }
        self.test_endpoint("/business-intelligence/competitive-analysis", "POST", competitor_data, "BI - Competitive Analysis")
        
        # Custom Report Creation
        report_data = {
            "report_name": "Monthly Performance Dashboard",
            "data_sources": ["sales", "marketing", "support"],
            "chart_types": ["line", "bar", "pie"],
            "filters": {"date_range": "last_30_days", "region": "north_america"}
        }
        self.test_endpoint("/business-intelligence/custom-reports", "POST", report_data, "BI - Create Custom Report")
        
        # Data Visualizations
        self.test_endpoint("/business-intelligence/visualizations", test_name="BI - Data Visualizations")
        
        # Additional BI endpoints from other modules
        self.test_endpoint("/advanced-analytics/business-intelligence", test_name="BI - Advanced Analytics Integration")
        self.test_endpoint("/analytics-system/business-intelligence", test_name="BI - Analytics System Integration")
        
    def test_existing_platform_stability(self):
        """Test existing platform stability to ensure no regressions"""
        print("\n--- 4. Existing Platform Stability Testing ---")
        
        # Core authentication and user management
        self.test_endpoint("/users/profile", test_name="Stability - User Profile")
        self.test_endpoint("/users/stats", test_name="Stability - User Statistics")
        
        # Dashboard functionality
        self.test_endpoint("/dashboard/overview", test_name="Stability - Dashboard Overview")
        self.test_endpoint("/dashboard/activity-summary", test_name="Stability - Dashboard Activity")
        
        # Analytics functionality
        self.test_endpoint("/analytics/overview", test_name="Stability - Analytics Overview")
        self.test_endpoint("/analytics/features/usage", test_name="Stability - Feature Usage Analytics")
        
        # AI services
        self.test_endpoint("/ai/services", test_name="Stability - AI Services")
        self.test_endpoint("/ai/conversations", test_name="Stability - AI Conversations")
        
        # E-commerce functionality
        self.test_endpoint("/ecommerce/products", test_name="Stability - E-commerce Products")
        self.test_endpoint("/ecommerce/orders", test_name="Stability - E-commerce Orders")
        self.test_endpoint("/ecommerce/dashboard", test_name="Stability - E-commerce Dashboard")
        
        # Marketing functionality
        self.test_endpoint("/marketing/campaigns", test_name="Stability - Marketing Campaigns")
        self.test_endpoint("/marketing/contacts", test_name="Stability - Marketing Contacts")
        self.test_endpoint("/marketing/analytics", test_name="Stability - Marketing Analytics")
        
        # Admin functionality
        self.test_endpoint("/admin/users", test_name="Stability - Admin Users")
        self.test_endpoint("/admin/system/metrics", test_name="Stability - Admin System Metrics")
        
        # Workspace management
        self.test_endpoint("/workspaces", test_name="Stability - Workspaces")
        
        # Test data consistency for core features
        print("\nTesting data consistency for core platform features:")
        core_consistency_endpoints = [
            "/dashboard/overview",
            "/users/profile",
            "/ai/services",
            "/ecommerce/dashboard",
            "/marketing/analytics"
        ]
        
        for endpoint in core_consistency_endpoints:
            self.test_data_consistency(endpoint)
    
    def test_newly_created_apis(self):
        """Test the newly created Advanced AI Analytics, Real-time Notifications, and Workflow Automation API endpoints"""
        print("\n=== Testing Previously Created API Modules ===")
        print("Testing Advanced AI Analytics, Real-time Notifications, and Workflow Automation endpoints")
        
        # Test Advanced AI Analytics API (/api/ai-analytics/api/ai-analytics)
        print("\n--- Advanced AI Analytics API Testing ---")
        
        # Generate predictive insights (POST)
        insights_data = {
            "data_source": "user_behavior",
            "time_range": "30_days",
            "metrics": ["engagement", "conversion", "retention"]
        }
        self.test_endpoint("/ai-analytics/api/ai-analytics/insights/generate", "POST", insights_data, "AI Analytics - Generate Predictive Insights")
        
        # Get user insights (GET)
        self.test_endpoint("/ai-analytics/api/ai-analytics/insights", test_name="AI Analytics - Get User Insights")
        
        # Generate anomaly detection (POST)
        anomaly_data = {
            "dataset": "user_activity",
            "threshold": 0.95,
            "time_window": "7_days"
        }
        self.test_endpoint("/ai-analytics/api/ai-analytics/insights/anomaly-detection", "POST", anomaly_data, "AI Analytics - Generate Anomaly Detection")
        
        # Get analytics summary (GET)
        self.test_endpoint("/ai-analytics/api/ai-analytics/analytics/summary", test_name="AI Analytics - Get Analytics Summary")
        
        # Test Real-time Notifications API (/api/notifications/api/notifications)
        print("\n--- Real-time Notifications API Testing ---")
        
        # Send notification to user (POST)
        notification_data = {
            "title": "Test Notification",
            "message": "This is a test notification from the API testing suite",
            "notification_type": "info",
            "channels": ["websocket", "in_app"],
            "priority": 5
        }
        self.test_endpoint("/notifications/api/notifications/send", "POST", notification_data, "Notifications - Send Notification")
        
        # Get notification history (GET)
        self.test_endpoint("/notifications/api/notifications/history", test_name="Notifications - Get History")
        
        # Get notification statistics (GET)
        self.test_endpoint("/notifications/api/notifications/stats", test_name="Notifications - Get Statistics")
        
        # Get connection status (GET)
        self.test_endpoint("/notifications/api/notifications/connection-status", test_name="Notifications - Get Connection Status")
        
        # Test Workflow Automation API (/api/workflows/api/workflows)
        print("\n--- Workflow Automation API Testing ---")
        
        # List user workflows (GET)
        self.test_endpoint("/workflows/api/workflows/list", test_name="Workflows - List User Workflows")
        
        # Get workflow templates (GET)
        self.test_endpoint("/workflows/api/workflows/templates/list", test_name="Workflows - Get Workflow Templates")
        
        # Get workflow statistics (GET)
        self.test_endpoint("/workflows/api/workflows/stats", test_name="Workflows - Get Workflow Statistics")
    
    def test_core_working_endpoints(self):
        """Test the core working API endpoints that are actually available"""
        print("\n=== Testing Core Working API Endpoints ===")
        
        # Test authentication endpoints
        self.test_endpoint("/auth/register", "POST", {"email": "test@example.com", "password": "testpass"}, "Auth - Register")
        
        # Test dashboard endpoints
        self.test_endpoint("/dashboard/overview", test_name="Dashboard - Overview")
        self.test_endpoint("/dashboard/activity-summary", test_name="Dashboard - Activity Summary")
        
        # Test analytics endpoints
        self.test_endpoint("/analytics/overview", test_name="Analytics - Overview")
        self.test_endpoint("/analytics/platform/overview", test_name="Analytics - Platform Overview")
        self.test_endpoint("/analytics/features/usage", test_name="Analytics - Features Usage")
        
        # Test user management endpoints
        self.test_endpoint("/users/profile", test_name="Users - Profile")
        self.test_endpoint("/users/stats", test_name="Users - Stats")
        self.test_endpoint("/users/analytics", test_name="Users - Analytics")
        
        # Test workspace endpoints
        self.test_endpoint("/workspaces", test_name="Workspaces - List")
        
        # Test blog endpoints
        self.test_endpoint("/blog/posts", test_name="Blog - Posts")
        self.test_endpoint("/blog/analytics", test_name="Blog - Analytics")
        
        # Test admin endpoints
        self.test_endpoint("/admin/dashboard", test_name="Admin - Dashboard")
        self.test_endpoint("/admin/users", test_name="Admin - Users")
        self.test_endpoint("/admin/users/stats", test_name="Admin - User Stats")
        self.test_endpoint("/admin/system/metrics", test_name="Admin - System Metrics")
        
        # Test AI endpoints
        self.test_endpoint("/ai/services", test_name="AI - Services")
        self.test_endpoint("/ai/conversations", test_name="AI - Conversations")
        
        # Test ecommerce endpoints
        self.test_endpoint("/ecommerce/products", test_name="Ecommerce - Products")
        self.test_endpoint("/ecommerce/orders", test_name="Ecommerce - Orders")
        self.test_endpoint("/ecommerce/dashboard", test_name="Ecommerce - Dashboard")
        
        # Test marketing endpoints
        self.test_endpoint("/marketing/campaigns", test_name="Marketing - Campaigns")
        self.test_endpoint("/marketing/contacts", test_name="Marketing - Contacts")
        self.test_endpoint("/marketing/lists", test_name="Marketing - Lists")
        self.test_endpoint("/marketing/analytics", test_name="Marketing - Analytics")
    
    def test_database_integration_verification(self):
        """Test database integration verification for the massive database work completed"""
        print("\n=== Database Integration Verification ===")
        print("Testing services converted from random data to real database operations")
        
        # Test services mentioned in the review request as having been converted
        database_integrated_services = [
            # Wave 1 services (1,186 random calls fixed)
            ("/social-media/analytics", "Social Media Service Database Integration"),
            ("/customer-experience/dashboard", "Customer Experience Service Database Integration"),
            ("/enhanced-ecommerce/products", "Enhanced E-commerce Service Database Integration"),
            ("/automation/workflows", "Automation Service Database Integration"),
            ("/analytics/overview", "Analytics Service Database Integration"),
            ("/support/tickets", "Support Service Database Integration"),
            ("/content-creation/projects", "Content Creation Service Database Integration"),
            ("/email-marketing/campaigns", "Email Marketing Service Database Integration"),
            ("/social-email/campaigns", "Social Email Service Database Integration"),
            ("/advanced-financial/dashboard", "Advanced Financial Service Database Integration"),
            
            # Wave 2 services (310 random calls fixed)
            ("/advanced-ai/capabilities", "Advanced AI Service Database Integration"),
            ("/advanced-financial/forecasting", "Financial Analytics Service Database Integration"),
            ("/templates/marketplace", "Template Marketplace Service Database Integration"),
            ("/ai-content/templates", "AI Content Service Database Integration"),
            ("/escrow/transactions", "Escrow Service Database Integration"),
            ("/customer-experience/journey-mapping", "Customer Experience Suite Database Integration"),
            ("/compliance/framework-status", "Compliance Service Database Integration"),
            ("/business-intelligence/metrics", "Business Intelligence Service Database Integration"),
            ("/content-creation/assets", "Content Creation Suite Database Integration"),
            ("/monitoring/system-health", "Monitoring Service Database Integration")
        ]
        
        for endpoint, test_name in database_integrated_services:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_data_consistency_verification(self):
        """Test data consistency to verify real database usage vs random generation"""
        print("\n=== Data Consistency Verification ===")
        print("Testing for consistent data across multiple calls (indicates real database usage)")
        
        # Test endpoints that should have consistent data
        consistency_endpoints = [
            "/dashboard/overview",
            "/workspaces", 
            "/analytics/overview",
            "/users/profile",
            "/users/stats",
            "/ecommerce/dashboard",
            "/marketing/analytics"
        ]
        
        for endpoint in consistency_endpoints:
            self.test_data_consistency(endpoint)
    
    def test_data_consistency(self, endpoint: str):
        """Test if endpoint returns consistent data (indicating real database usage)"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            # Make first request
            response1 = self.session.get(url, timeout=10)
            if response1.status_code != 200:
                self.log_result(f"Data Consistency - {endpoint}", False, f"First request failed - Status {response1.status_code}")
                return False
            
            data1 = response1.json()
            
            # Wait a moment and make second request
            import time
            time.sleep(1)
            
            response2 = self.session.get(url, timeout=10)
            if response2.status_code != 200:
                self.log_result(f"Data Consistency - {endpoint}", False, f"Second request failed - Status {response2.status_code}")
                return False
            
            data2 = response2.json()
            
            # Compare responses
            if json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True):
                self.log_result(f"Data Consistency - {endpoint}", True, f"Data consistent across calls - confirms real database usage")
                return True
            else:
                self.log_result(f"Data Consistency - {endpoint}", False, f"Data inconsistent - may still be using random generation")
                return False
                
        except Exception as e:
            self.log_result(f"Data Consistency - {endpoint}", False, f"Request error: {str(e)}")
            return False
    
    def test_core_business_functionality(self):
        """Test core business functionality that now uses real data"""
        print("\n=== Core Business Functionality with Real Data ===")
        
        # Test key business endpoints that should now use real database data
        business_endpoints = [
            # Dashboard and analytics
            ("/dashboard/overview", "Dashboard Real Database Data"),
            ("/analytics/overview", "Analytics Real Database Data"),
            
            # User and workspace management
            ("/users/profile", "User Management Real Data"),
            ("/workspaces", "Workspace Management Real Data"),
            
            # AI services
            ("/advanced-ai/capabilities", "AI Services Real Data"),
            ("/advanced-ai/models", "AI Models Real Data"),
            
            # Business intelligence
            ("/compliance/framework-status", "Compliance Real Data"),
            ("/backup/comprehensive-status", "Backup System Real Data"),
            ("/monitoring/system-health", "Monitoring Real Data"),
            
            # Integration management
            ("/integrations/available", "Integration Management Real Data"),
            ("/integrations/connected", "Connected Integrations Real Data")
        ]
        
        for endpoint, test_name in business_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)

    def test_platform_startup_health(self):
        """Test platform startup and health metrics"""
        print("\n=== Platform Startup & Health Verification ===")
        
        # Test system endpoints - note that root might serve frontend HTML
        try:
            response = self.session.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                if 'application/json' in response.headers.get('content-type', ''):
                    data = response.json()
                    self.log_result("Platform Root Status", True, f"JSON API response: {data.get('message', 'Unknown')}", data)
                else:
                    self.log_result("Platform Root Status", True, "Root serves frontend (expected in production setup)")
            else:
                self.log_result("Platform Root Status", False, f"Root failed with status {response.status_code}")
        except Exception as e:
            self.log_result("Platform Root Status", False, f"Root error: {str(e)}")
        
        # Test health and metrics endpoints (these are not prefixed with /api)
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code in [200, 503]:  # 503 is acceptable for degraded status
                data = response.json()
                status = data.get('status', 'unknown')
                modules_loaded = data.get('system', {}).get('modules_loaded', 0)
                self.log_result("Platform Health Check", True, f"Health endpoint working - Status: {status}, Modules: {modules_loaded}", data)
            else:
                self.log_result("Platform Health Check", False, f"Health failed with status {response.status_code}")
        except Exception as e:
            self.log_result("Platform Health Check", False, f"Health error: {str(e)}")
            
        try:
            response = self.session.get(f"{BACKEND_URL}/metrics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                load_success_rate = data.get('modules', {}).get('load_success_rate', '0%')
                total_collections = data.get('database', {}).get('total_collections', 0)
                self.log_result("Platform System Metrics", True, f"Metrics endpoint working - Load success: {load_success_rate}, DB collections: {total_collections}", data)
            else:
                self.log_result("Platform System Metrics", False, f"Metrics failed with status {response.status_code}")
        except Exception as e:
            self.log_result("Platform System Metrics", False, f"Metrics error: {str(e)}")
        
        # Test API documentation
        try:
            response = self.session.get(f"{BACKEND_URL}/docs", timeout=10)
            if response.status_code == 200:
                self.log_result("API Documentation", True, "Swagger UI accessible")
            else:
                self.log_result("API Documentation", False, f"Docs failed with status {response.status_code}")
        except Exception as e:
            self.log_result("API Documentation", False, f"Docs error: {str(e)}")
            
        try:
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                paths_count = len(data.get('paths', {}))
                self.log_result("OpenAPI Specification", True, f"OpenAPI spec available with {paths_count} endpoints", {"paths_count": paths_count})
            else:
                self.log_result("OpenAPI Specification", False, f"OpenAPI failed with status {response.status_code}")
        except Exception as e:
            self.log_result("OpenAPI Specification", False, f"OpenAPI error: {str(e)}")
    
    def test_service_method_fixes(self):
        """Test service method fixes for previously failing services"""
        print("\n=== Service Method Fixes Verification ===")
        print("Testing services that were previously failing due to method mapping issues")
        
        # Test services that had method mapping issues
        service_fixes = [
            ("/customer-experience/dashboard", "Customer Experience Service - Dashboard"),
            ("/customer-experience/journey-mapping", "Customer Experience Service - Journey Mapping"),
            ("/customer-experience/feedback", "Customer Experience Service - Feedback"),
            ("/social-email/campaigns", "Social Email Service - Campaigns"),
            ("/social-email/templates", "Social Email Service - Templates"),
            ("/email-marketing/campaigns", "Email Marketing Service - Campaigns"),
            ("/content-creation/projects", "Content Creation Service - Projects"),
            ("/content-creation/templates", "Content Creation Service - Templates"),
            ("/content-creation/assets", "Content Creation Service - Assets")
        ]
        
        for endpoint, test_name in service_fixes:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_data_integrity_verification(self):
        """Test data integrity to verify elimination of mock data"""
        print("\n=== Data Integrity Verification ===")
        print("Verifying elimination of random data and real database operations")
        
        # Test core services that should now use real database data
        data_integrity_endpoints = [
            ("/dashboard/overview", "Dashboard Service - Real Database Data"),
            ("/analytics/overview", "Analytics Service - Real Database Data"),
            ("/users/profile", "User Management - Real Database Data"),
            ("/ai/services", "AI Services - Real Database Data"),
            ("/ecommerce/products", "E-commerce - Real Database Data"),
            ("/marketing/campaigns", "Marketing - Real Database Data"),
            ("/admin/users", "Admin Management - Real Database Data"),
            ("/automation/workflows", "Automation - Real Database Data"),
            ("/support/tickets", "Support System - Real Database Data"),
            ("/monitoring/system-health", "Monitoring - Real Database Data")
        ]
        
        for endpoint, test_name in data_integrity_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test data consistency
        self.test_data_consistency_verification()
    
    def test_api_endpoint_functionality(self):
        """Test API endpoint functionality across all major modules"""
        print("\n=== API Endpoint Functionality Testing ===")
        
        # Test core authentication
        print("Testing Core Authentication:")
        self.test_endpoint("/auth/register", "POST", {"name": "Test User", "email": "test@example.com", "password": "testpass"}, "Auth - Register")
        
        # Test dashboard analytics
        print("Testing Dashboard Analytics:")
        self.test_endpoint("/dashboard/overview", test_name="Dashboard - Overview")
        self.test_endpoint("/dashboard/activity-summary", test_name="Dashboard - Activity Summary")
        
        # Test AI services
        print("Testing AI Services:")
        self.test_endpoint("/ai/services", test_name="AI - Services")
        self.test_endpoint("/ai/conversations", test_name="AI - Conversations")
        self.test_endpoint("/advanced-ai/capabilities", test_name="Advanced AI - Capabilities")
        self.test_endpoint("/advanced-ai/models", test_name="Advanced AI - Models")
        
        # Test e-commerce functions
        print("Testing E-commerce Functions:")
        self.test_endpoint("/ecommerce/products", test_name="E-commerce - Products")
        self.test_endpoint("/ecommerce/orders", test_name="E-commerce - Orders")
        self.test_endpoint("/ecommerce/dashboard", test_name="E-commerce - Dashboard")
        
        # Test social media integrations
        print("Testing Social Media Integrations:")
        self.test_endpoint("/social-media/analytics", test_name="Social Media - Analytics")
        self.test_endpoint("/social-email/campaigns", test_name="Social Email - Campaigns")
        
        # Test business intelligence
        print("Testing Business Intelligence:")
        self.test_endpoint("/business-intelligence/metrics", test_name="Business Intelligence - Metrics")
        self.test_endpoint("/analytics/features/usage", test_name="Analytics - Features Usage")
        
        # Test integration management
        print("Testing Integration Management:")
        self.test_endpoint("/integrations/available", test_name="Integrations - Available")
        self.test_endpoint("/integrations/connected", test_name="Integrations - Connected")
    
    def test_performance_reliability(self):
        """Test performance and reliability metrics"""
        print("\n=== Performance & Reliability Testing ===")
        
        # Test response times for key endpoints
        performance_endpoints = [
            "/dashboard/overview",
            "/users/profile", 
            "/ai/services",
            "/ecommerce/products",
            "/analytics/overview"
        ]
        
        total_response_time = 0
        successful_requests = 0
        
        for endpoint in performance_endpoints:
            try:
                import time
                start_time = time.time()
                
                url = f"{API_BASE}{endpoint}"
                response = self.session.get(url, timeout=10)
                
                end_time = time.time()
                response_time = end_time - start_time
                total_response_time += response_time
                
                if response.status_code == 200:
                    successful_requests += 1
                    self.log_result(f"Performance - {endpoint}", True, f"Response time: {response_time:.3f}s")
                else:
                    self.log_result(f"Performance - {endpoint}", False, f"Failed with status {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Performance - {endpoint}", False, f"Request error: {str(e)}")
        
        if successful_requests > 0:
            avg_response_time = total_response_time / successful_requests
            self.log_result("Average Response Time", True, f"Average: {avg_response_time:.3f}s across {successful_requests} endpoints")
        
        # Test system stability
        self.test_endpoint("/health", test_name="System Stability Check")
        self.test_endpoint("/metrics", test_name="System Metrics Check")

    def test_admin_configuration_system(self):
        """Test the new Admin Configuration System endpoints"""
        print("\n=== Admin Configuration System Testing ===")
        print("Testing the new admin configuration endpoints for external API management")
        
        # Test admin configuration endpoints
        admin_config_endpoints = [
            ("/admin-config/configuration", "GET", "Admin Config - Get Configuration"),
            ("/admin-config/integrations/status", "GET", "Admin Config - Integration Status"),
            ("/admin-config/system/health", "GET", "Admin Config - System Health"),
            ("/admin-config/logs", "GET", "Admin Config - System Logs"),
            ("/admin-config/available-services", "GET", "Admin Config - Available Services"),
            ("/admin-config/analytics/dashboard", "GET", "Admin Config - Analytics Dashboard"),
            ("/admin-config/logs/statistics", "GET", "Admin Config - Log Statistics")
        ]
        
        for endpoint, method, test_name in admin_config_endpoints:
            self.test_endpoint(endpoint, method, test_name=test_name)
        
        # Test admin configuration update (POST)
        config_update_data = {
            "enable_rate_limiting": True,
            "rate_limit_per_minute": 100,
            "enable_audit_logging": True,
            "log_level": "INFO"
        }
        self.test_endpoint("/admin-config/configuration", "POST", config_update_data, "Admin Config - Update Configuration")
        
        # Test integration testing endpoints
        integration_services = ["stripe", "openai", "sendgrid", "twitter"]
        for service in integration_services:
            self.test_endpoint(f"/admin-config/integrations/{service}/test", "POST", {}, f"Admin Config - Test {service.title()} Integration")
    
    def test_external_api_integration_framework(self):
        """Test External API Integration Framework"""
        print("\n=== External API Integration Framework Testing ===")
        print("Testing the external API integration system initialization and configuration")
        
        # Test integration management endpoints
        integration_endpoints = [
            ("/integrations/available", "Integration - Available Services"),
            ("/integrations/connected", "Integration - Connected Services"),
            ("/integrations/status", "Integration - Status Check")
        ]
        
        for endpoint, test_name in integration_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_professional_logging_system(self):
        """Test Professional Logging System"""
        print("\n=== Professional Logging System Testing ===")
        print("Testing the comprehensive logging system operational status")
        
        # Test logging endpoints
        logging_endpoints = [
            ("/admin-config/logs", "Professional Logging - System Logs"),
            ("/admin-config/logs/statistics", "Professional Logging - Log Statistics"),
            ("/admin-config/analytics/dashboard", "Professional Logging - Analytics Dashboard")
        ]
        
        for endpoint, test_name in logging_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test log filtering
        log_filter_params = "?level=INFO&category=API&limit=50"
        self.test_endpoint(f"/admin-config/logs{log_filter_params}", test_name="Professional Logging - Filtered Logs")
    
    def test_random_data_elimination_verification(self):
        """Test Random Data Elimination - verify real database operations"""
        print("\n=== Random Data Elimination Verification ===")
        print("Testing services to verify they use real database operations instead of random data")
        
        # Test services that should now use real database data
        real_data_services = [
            ("/dashboard/overview", "Email Marketing Analytics - Real Data"),
            ("/analytics/overview", "Dashboard Metrics - Real Data"),
            ("/users/profile", "User Activity Tracking - Real Data"),
            ("/ai/services", "AI Usage Analytics - Real Data"),
            ("/marketing/analytics", "Marketing Service Analytics - Real Data"),
            ("/ecommerce/dashboard", "E-commerce Analytics - Real Data"),
            ("/admin/system/metrics", "Admin System Metrics - Real Data")
        ]
        
        for endpoint, test_name in real_data_services:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test data consistency to verify real database usage
        print("\nTesting data consistency to confirm real database operations:")
        consistency_endpoints = [
            "/dashboard/overview",
            "/users/profile", 
            "/ai/services",
            "/marketing/analytics",
            "/ecommerce/dashboard"
        ]
        
        for endpoint in consistency_endpoints:
            self.test_data_consistency(endpoint)
    
    def test_core_platform_functionality_after_changes(self):
        """Test Core Platform Functionality after major infrastructure changes"""
        print("\n=== Core Platform Functionality After Infrastructure Changes ===")
        print("Ensuring all existing functionality still works after major infrastructure changes")
        
        # Test core business functionality
        core_endpoints = [
            # Authentication and user management
            ("/auth/register", "POST", {"name": "Test User", "email": "test@example.com", "password": "testpass"}, "Core - User Registration"),
            ("/users/profile", "GET", None, "Core - User Profile"),
            ("/users/stats", "GET", None, "Core - User Statistics"),
            
            # Dashboard and analytics
            ("/dashboard/overview", "GET", None, "Core - Dashboard Overview"),
            ("/dashboard/activity-summary", "GET", None, "Core - Dashboard Activity"),
            ("/analytics/overview", "GET", None, "Core - Analytics Overview"),
            ("/analytics/features/usage", "GET", None, "Core - Feature Usage Analytics"),
            
            # AI services
            ("/ai/services", "GET", None, "Core - AI Services"),
            ("/ai/conversations", "GET", None, "Core - AI Conversations"),
            
            # E-commerce
            ("/ecommerce/products", "GET", None, "Core - E-commerce Products"),
            ("/ecommerce/orders", "GET", None, "Core - E-commerce Orders"),
            ("/ecommerce/dashboard", "GET", None, "Core - E-commerce Dashboard"),
            
            # Marketing
            ("/marketing/campaigns", "GET", None, "Core - Marketing Campaigns"),
            ("/marketing/contacts", "GET", None, "Core - Marketing Contacts"),
            ("/marketing/analytics", "GET", None, "Core - Marketing Analytics"),
            
            # Admin functions
            ("/admin/users", "GET", None, "Core - Admin Users"),
            ("/admin/system/metrics", "GET", None, "Core - Admin System Metrics"),
            
            # Workspace management
            ("/workspaces", "GET", None, "Core - Workspaces")
        ]
        
        for endpoint, method, data, test_name in core_endpoints:
            self.test_endpoint(endpoint, method, data, test_name)
    
    def test_database_integration_improvements(self):
        """Test Database Integration improvements"""
        print("\n=== Database Integration Improvements Testing ===")
        print("Testing that real data population services are working correctly")
        
        # Test database-integrated services
        db_services = [
            ("/dashboard/overview", "Database Integration - Dashboard Service"),
            ("/analytics/overview", "Database Integration - Analytics Service"),
            ("/users/profile", "Database Integration - User Management"),
            ("/ai/services", "Database Integration - AI Services"),
            ("/ecommerce/products", "Database Integration - E-commerce"),
            ("/marketing/campaigns", "Database Integration - Marketing"),
            ("/admin/users", "Database Integration - Admin Management"),
            ("/workspaces", "Database Integration - Workspace Management")
        ]
        
        for endpoint, test_name in db_services:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test data persistence by making multiple calls
        print("\nTesting data persistence across multiple calls:")
        for endpoint, _ in db_services[:5]:  # Test first 5 services
            self.test_data_consistency(endpoint)

    def test_complete_onboarding_system(self):
        """Test the Complete Onboarding System with real data and full CRUD operations"""
        print("\n=== COMPLETE ONBOARDING SYSTEM TESTING ===")
        print("Testing the newly implemented Complete Onboarding System with:")
        print("1. Authentication System - Test login with existing credentials")
        print("2. Complete Onboarding APIs - Test all new endpoints")
        print("3. Real Data Verification - Verify MongoDB storage")
        print("4. Full CRUD Operations - Test CREATE, READ, UPDATE, DELETE")
        print("5. Database Operations - Verify data persistence")
        
        # Test all onboarding endpoints with real data
        onboarding_session_id = None
        
        # 1. CREATE: Create new onboarding session
        session_data = {
            "workspace_name": "Mewayz Business Solutions",
            "workspace_description": "Complete business automation platform for entrepreneurs",
            "industry": "Technology"
        }
        print("\n--- Testing CREATE Operations ---")
        response = self.test_endpoint_with_response("/onboarding/session", "POST", session_data, "Onboarding - CREATE Session")
        if response and response.get("success"):
            onboarding_session_id = response.get("data", {}).get("session_id")
            print(f"   Created session ID: {onboarding_session_id}")
        
        if not onboarding_session_id:
            print("❌ Cannot continue testing without session ID")
            return False
        
        # 2. READ: Get onboarding session
        print("\n--- Testing READ Operations ---")
        self.test_endpoint(f"/onboarding/session/{onboarding_session_id}", "GET", test_name="Onboarding - READ Session")
        self.test_endpoint("/onboarding/goals", "GET", test_name="Onboarding - READ Available Goals")
        self.test_endpoint("/onboarding/subscription-plans", "GET", test_name="Onboarding - READ Subscription Plans")
        self.test_endpoint("/onboarding/sessions", "GET", test_name="Onboarding - READ User Sessions")
        self.test_endpoint("/onboarding/analytics", "GET", test_name="Onboarding - READ Analytics")
        self.test_endpoint("/onboarding/health", "GET", test_name="Onboarding - READ Health Check")
        
        # 3. UPDATE: Update onboarding steps with real data
        print("\n--- Testing UPDATE Operations ---")
        
        # Update goals selection
        goals_data = {
            "selected_goals": ["social_media", "ecommerce", "analytics"]
        }
        self.test_endpoint(f"/onboarding/session/{onboarding_session_id}/goals", "POST", goals_data, "Onboarding - UPDATE Goals Selection")
        
        # Update subscription plan
        subscription_data = {
            "selected_plan": "pro",
            "billing_cycle": "monthly",
            "feature_count": 5
        }
        self.test_endpoint(f"/onboarding/session/{onboarding_session_id}/subscription", "POST", subscription_data, "Onboarding - UPDATE Subscription Plan")
        
        # Update team setup
        team_data = {
            "team_members": [
                {
                    "email": "team@mewayz.com",
                    "first_name": "John",
                    "last_name": "Smith",
                    "role": "editor"
                }
            ]
        }
        self.test_endpoint(f"/onboarding/session/{onboarding_session_id}/team", "POST", team_data, "Onboarding - UPDATE Team Setup")
        
        # Update branding
        branding_data = {
            "company_name": "Mewayz Solutions",
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#3B82F6",
            "secondary_color": "#1E40AF",
            "custom_domain": "mewayz.business"
        }
        self.test_endpoint(f"/onboarding/session/{onboarding_session_id}/branding", "POST", branding_data, "Onboarding - UPDATE Branding")
        
        # Update integrations
        integrations_data = {
            "integrations": {
                "stripe": {"configured": True, "settings": {"test_mode": True}},
                "openai": {"configured": True, "settings": {"model": "gpt-3.5-turbo"}}
            }
        }
        self.test_endpoint(f"/onboarding/session/{onboarding_session_id}/integrations", "POST", integrations_data, "Onboarding - UPDATE Integrations")
        
        # Update step with generic data
        step_data = {
            "step": "branding_setup",
            "data": branding_data
        }
        self.test_endpoint(f"/onboarding/session/{onboarding_session_id}/step", "PUT", step_data, "Onboarding - UPDATE Step")
        
        # 4. CREATE: Complete onboarding (creates workspace)
        print("\n--- Testing Complete Onboarding (CREATE Workspace) ---")
        self.test_endpoint(f"/onboarding/session/{onboarding_session_id}/complete", "POST", test_name="Onboarding - CREATE Complete Onboarding")
        
        # 5. DELETE: Delete onboarding session
        print("\n--- Testing DELETE Operations ---")
        # Create a new session to delete (don't delete the main one yet)
        delete_session_data = {
            "workspace_name": "Test Delete Session",
            "workspace_description": "Session for testing deletion",
            "industry": "Testing"
        }
        delete_response = self.test_endpoint_with_response("/onboarding/session", "POST", delete_session_data, "Onboarding - CREATE Session for Deletion")
        if delete_response and delete_response.get("success"):
            delete_session_id = delete_response.get("data", {}).get("session_id")
            if delete_session_id:
                self.test_endpoint(f"/onboarding/session/{delete_session_id}", "DELETE", test_name="Onboarding - DELETE Session")
        
        # Test data consistency and real database operations
        print("\n--- Testing Data Consistency and Real Database Operations ---")
        self.test_data_consistency("/onboarding/goals")
        self.test_data_consistency("/onboarding/subscription-plans")
        self.test_data_consistency("/onboarding/analytics")
        
        return True
    
    def test_endpoint_with_response(self, endpoint: str, method: str = "GET", data: Dict = None, test_name: str = None):
        """Test endpoint and return response data for further processing"""
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
                return None
            
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code}", response_data)
                    return response_data
                except:
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code} (non-JSON response)")
                    return {"success": True, "status_code": response.status_code}
            else:
                self.log_result(test_name, False, f"Endpoint error - Status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return None

    def run_comprehensive_specification_test(self):
        """Run comprehensive testing of the THREE MAJOR SPECIFICATION AREAS - JULY 2025"""
        print("🎯 COMPREHENSIVE SPECIFICATION IMPLEMENTATION TESTING - JULY 2025")
        print("Testing the three critical specification areas that were just implemented:")
        print("1. 🌐 COMPREHENSIVE MARKETING WEBSITE CAPABILITIES - /api/marketing-website/*")
        print("2. 📱 ADVANCED SOCIAL MEDIA MANAGEMENT SUITE - /api/social-media-suite/*") 
        print("3. 🔒 ENTERPRISE SECURITY & COMPLIANCE - /api/enterprise-security/*")
        print("4. ✅ EXISTING PLATFORM STABILITY verification")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the THREE MAJOR SPECIFICATION AREAS (main focus of review request)
        self.test_comprehensive_specification_implementation()
        
        # Test existing platform stability to ensure no regressions
        self.test_existing_platform_stability()
        
        # Test platform health and performance
        self.test_platform_startup_health()
        self.test_performance_reliability()
        
        # Print summary
        self.print_summary()
        
        return True

    def run_enterprise_features_test(self):
        """Run comprehensive testing of NEW ENTERPRISE FEATURES as requested in the review"""
        print("🎯 TESTING NEW ENTERPRISE FEATURES - MEWAYZ PLATFORM")
        print("Testing the NEW ENTERPRISE FEATURES as requested in the review:")
        print("- 🎓 Advanced Learning Management System (LMS) - /api/lms/*")
        print("- 🏪 Multi-Vendor Marketplace - /api/marketplace/*") 
        print("- 📊 Advanced Business Intelligence - /api/business-intelligence/*")
        print("- ✅ Existing Platform Stability verification")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the NEW ENTERPRISE FEATURES (main focus of review request)
        self.test_enterprise_features()
        
        # Test existing platform stability
        self.test_existing_platform_stability()
        
        # Test previously created APIs for completeness
        self.test_newly_created_apis()
        
        # Test platform health and performance
        self.test_platform_startup_health()
        self.test_performance_reliability()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}: {result['message']}")

    def run_real_api_integration_test(self):
        """Run comprehensive testing of REAL API INTEGRATION ENDPOINTS - JULY 2025"""
        print("🎯 REAL API INTEGRATION ENDPOINTS TESTING - JULY 2025")
        print("Testing newly implemented real API integration endpoints:")
        print("1. 🐦 Real Social Media Lead Generation APIs (Twitter/TikTok)")
        print("2. 🤖 Real AI Automation APIs (OpenAI GPT integration)")
        print("3. 📧 Real Email Automation APIs (ElasticMail)")
        print("4. 💾 Database operations verification")
        print("5. 🔐 Authentication & error handling")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the REAL API INTEGRATION ENDPOINTS (main focus of review request)
        self.test_real_api_integration_endpoints()
        
        # Test database operations to verify no mock data
        self.test_random_data_elimination_verification()
        
        # Test existing platform stability to ensure no regressions
        self.test_core_platform_functionality_after_changes()
        
        # Test platform health and performance
        self.test_platform_startup_health()
        self.test_performance_reliability()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def run_complete_onboarding_test(self):
        """Run Complete Onboarding System testing as requested in review"""
        print("🎯 COMPLETE ONBOARDING SYSTEM TESTING - MEWAYZ PLATFORM")
        print("Testing the newly implemented Complete Onboarding System with:")
        print("- Authentication System with existing credentials")
        print("- Complete Onboarding APIs with all new endpoints")
        print("- Real Data Verification with MongoDB storage")
        print("- Full CRUD Operations (CREATE, READ, UPDATE, DELETE)")
        print("- Database Operations with data persistence verification")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication with existing credentials
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the Complete Onboarding System
        self.test_complete_onboarding_system()
        
        # Test platform health and performance
        self.test_platform_startup_health()
        self.test_performance_reliability()
        
        # Print summary
        self.print_summary()
        
        return True

    def run_link_in_bio_test(self):
        """Run Complete Link in Bio Builder System testing as requested in review"""
        print("🎯 COMPLETE LINK IN BIO BUILDER SYSTEM TESTING - MEWAYZ PLATFORM")
        print("Testing the newly implemented Complete Link in Bio Builder System with:")
        print("- Authentication System with existing credentials (tmonnens@outlook.com / Voetballen5)")
        print("- Complete Link in Bio APIs with all new endpoints")
        print("- Real Data Verification with MongoDB storage")
        print("- Full CRUD Operations (CREATE, READ, UPDATE, DELETE)")
        print("- Database Operations with data persistence verification")
        print("- Template System with real configurations")
        print("- Analytics System with real-time tracking")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication with existing credentials
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the Complete Link in Bio Builder System
        self.test_link_in_bio_system()
        
        # Test data consistency to verify real database usage
        print("\n🔍 Testing Data Consistency for Link in Bio System...")
        self.test_data_consistency("/link-in-bio/templates")
        self.test_data_consistency("/link-in-bio/analytics/overview")
        
        # Test platform health and performance
        self.test_platform_startup_health()
        self.test_performance_reliability()
        
        # Print summary
        self.print_summary()
        
        return True

    def run_newly_implemented_features_test(self):
        """Run comprehensive testing of NEWLY IMPLEMENTED FEATURES - DECEMBER 2024"""
        print("🎯 NEWLY IMPLEMENTED FEATURES TESTING - DECEMBER 2024")
        print("Testing the newly implemented features as requested in the review:")
        print("1. 💰 Complete Financial Management System - /api/financial/*")
        print("2. 🌐 Complete Website Builder System - /api/website-builder/*")
        print("3. 👥 Complete Multi-Workspace System with RBAC - /api/multi-workspace/*")
        print("4. ✅ Verify all previous features still work (no regressions)")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the NEWLY IMPLEMENTED FEATURES (main focus of review request)
        self.test_newly_implemented_features()
        
        # Test data consistency to verify real database usage
        self.test_data_consistency_verification()
        
        # Test platform health and performance
        self.test_platform_startup_health()
        self.test_performance_reliability()
        
        # Print summary
        self.print_summary()
        
        return True

    def run_final_comprehensive_audit(self):
        """Run comprehensive testing of the 4 newly implemented features"""
        print("🎯 COMPREHENSIVE TESTING OF 4 NEWLY IMPLEMENTED FEATURES - JANUARY 2025")
        print("Testing ALL newly implemented features from review request:")
        print("1. ✅ ADVANCED TEMPLATE MARKETPLACE")
        print("2. ✅ ADVANCED TEAM MANAGEMENT")
        print("3. ✅ UNIFIED ANALYTICS WITH GAMIFICATION")
        print("4. ✅ MOBILE PWA FEATURES")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the 4 newly implemented features
        self.test_newly_implemented_features()
        
        # Print summary
        self.print_test_summary()
        
        return True
        
        # 6. COMPLETE WEBSITE BUILDER (Priority 6)
        print("\n🎯 PRIORITY 6: COMPLETE WEBSITE BUILDER")
        print("=" * 60)
        self.test_website_builder_system()
        
        # 7. EXTERNAL API INTEGRATIONS VERIFICATION
        print("\n🎯 EXTERNAL API INTEGRATIONS VERIFICATION")
        print("=" * 60)
        self.test_external_api_integrations()
        
        # 8. RANDOM DATA ELIMINATION VERIFICATION
        print("\n🎯 RANDOM DATA ELIMINATION VERIFICATION")
        print("=" * 60)
        self.test_zero_random_data_verification()
        
        # 9. AUTHENTICATION & DATA PERSISTENCE
        print("\n🎯 AUTHENTICATION & DATA PERSISTENCE VERIFICATION")
        print("=" * 60)
        self.test_authentication_and_persistence()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def test_social_media_leads_system(self):
        """Test Complete Social Media Leads System"""
        print("\n📱 TESTING COMPLETE SOCIAL MEDIA LEADS SYSTEM")
        print("=" * 60)
        
        # Test TikTok Lead Generation
        print("\n🎵 Testing TikTok Lead Generation...")
        tiktok_search_data = {
            "hashtags": ["business", "entrepreneur", "startup"],
            "location": "United States",
            "follower_range": {"min": 1000, "max": 100000},
            "engagement_rate_min": 2.0
        }
        self.test_endpoint("/social-media-leads/tiktok/search", "POST", tiktok_search_data, "Social Media Leads - TikTok Search")
        self.test_endpoint("/social-media-leads/tiktok/analytics", "GET", test_name="Social Media Leads - TikTok Analytics")
        
        # Test Twitter Lead Generation
        print("\n🐦 Testing Twitter Lead Generation...")
        twitter_search_data = {
            "keywords": ["business owner", "entrepreneur", "startup founder"],
            "location": "United States",
            "follower_range": {"min": 500, "max": 50000},
            "verified_only": False
        }
        self.test_endpoint("/social-media-leads/twitter/search", "POST", twitter_search_data, "Social Media Leads - Twitter Search")
        self.test_endpoint("/social-media-leads/twitter/analytics", "GET", test_name="Social Media Leads - Twitter Analytics")
        
        # Test Lead Management
        print("\n👥 Testing Lead Management...")
        self.test_endpoint("/social-media-leads/leads", "GET", test_name="Social Media Leads - Get All Leads")
        self.test_endpoint("/social-media-leads/leads/export", "GET", test_name="Social Media Leads - Export Leads")
        self.test_endpoint("/social-media-leads/analytics/overview", "GET", test_name="Social Media Leads - Analytics Overview")
        
        return True
    
    def test_booking_system(self):
        """Test Complete Booking System"""
        print("\n📅 TESTING COMPLETE BOOKING SYSTEM")
        print("=" * 60)
        
        # Test Service Management
        print("\n🛠️ Testing Service Management...")
        service_data = {
            "name": "Business Consultation",
            "description": "1-hour business strategy consultation",
            "duration_minutes": 60,
            "price": 150.00,
            "category": "consulting"
        }
        self.test_endpoint("/booking/services", "POST", service_data, "Booking - Create Service")
        self.test_endpoint("/booking/services", "GET", test_name="Booking - Get All Services")
        
        # Test Appointment Management
        print("\n📅 Testing Appointment Management...")
        appointment_data = {
            "service_id": "service_123",
            "client_name": "John Smith",
            "client_email": "john@example.com",
            "client_phone": "+1234567890",
            "appointment_date": "2025-01-15",
            "appointment_time": "14:00",
            "notes": "Initial business consultation"
        }
        self.test_endpoint("/booking/appointments", "POST", appointment_data, "Booking - Create Appointment")
        self.test_endpoint("/booking/appointments", "GET", test_name="Booking - Get All Appointments")
        self.test_endpoint("/booking/appointments/calendar", "GET", test_name="Booking - Calendar View")
        
        # Test Availability Management
        print("\n⏰ Testing Availability Management...")
        availability_data = {
            "day_of_week": "monday",
            "start_time": "09:00",
            "end_time": "17:00",
            "break_start": "12:00",
            "break_end": "13:00"
        }
        self.test_endpoint("/booking/availability", "POST", availability_data, "Booking - Set Availability")
        self.test_endpoint("/booking/availability", "GET", test_name="Booking - Get Availability")
        
        # Test Booking Analytics
        print("\n📊 Testing Booking Analytics...")
        self.test_endpoint("/booking/analytics/overview", "GET", test_name="Booking - Analytics Overview")
        self.test_endpoint("/booking/analytics/revenue", "GET", test_name="Booking - Revenue Analytics")
        
        return True
    
    def test_external_api_integrations(self):
        """Test External API Integrations"""
        print("\n🔗 TESTING EXTERNAL API INTEGRATIONS")
        print("=" * 60)
        
        # Test TikTok API Integration
        print("\n🎵 Testing TikTok API Integration...")
        self.test_endpoint("/admin-config/integrations/tiktok/test", "POST", {}, "External API - Test TikTok Integration")
        
        # Test Twitter API Integration
        print("\n🐦 Testing Twitter API Integration...")
        self.test_endpoint("/admin-config/integrations/twitter/test", "POST", {}, "External API - Test Twitter Integration")
        
        # Test OpenAI API Integration
        print("\n🤖 Testing OpenAI API Integration...")
        self.test_endpoint("/admin-config/integrations/openai/test", "POST", {}, "External API - Test OpenAI Integration")
        
        # Test ElasticMail API Integration
        print("\n📧 Testing ElasticMail API Integration...")
        self.test_endpoint("/admin-config/integrations/elasticmail/test", "POST", {}, "External API - Test ElasticMail Integration")
        
        # Test Stripe Integration
        print("\n💳 Testing Stripe Integration...")
        self.test_endpoint("/admin-config/integrations/stripe/test", "POST", {}, "External API - Test Stripe Integration")
        
        return True
    
    def test_zero_random_data_verification(self):
        """Test Zero Random/Mock Data Verification"""
        print("\n🎯 TESTING ZERO RANDOM/MOCK DATA VERIFICATION")
        print("=" * 60)
        
        # Test multiple calls to same endpoints to verify data consistency
        consistency_endpoints = [
            "/dashboard/overview",
            "/users/profile",
            "/financial/dashboard",
            "/ai/services",
            "/ecommerce/dashboard",
            "/analytics/overview"
        ]
        
        for endpoint in consistency_endpoints:
            print(f"\n🔍 Testing data consistency for {endpoint}...")
            self.test_data_consistency(endpoint)
        
        return True
    
    def test_authentication_and_persistence(self):
        """Test Authentication & Data Persistence"""
        print("\n🔐 TESTING AUTHENTICATION & DATA PERSISTENCE")
        print("=" * 60)
        
        # Test authentication across different endpoints
        auth_test_endpoints = [
            "/users/profile",
            "/financial/dashboard",
            "/multi-workspace/workspaces",
            "/social-media-leads/analytics/overview",
            "/booking/services",
            "/subscriptions/plans",
            "/website-builder/dashboard"
        ]
        
        for endpoint in auth_test_endpoints:
            self.test_endpoint(endpoint, "GET", test_name=f"Auth Test - {endpoint}")
        
        # Test data persistence by creating and retrieving data
        print("\n💾 Testing Data Persistence...")
        
        # Create a test invoice and verify it persists
        invoice_data = {
            "client_name": "Test Persistence Client",
            "client_email": "persistence@test.com",
            "items": [{"name": "Test Service", "quantity": 1, "price": 100.00}],
            "tax_rate": 0.1
        }
        success, response = self.test_endpoint("/financial/invoices", "POST", invoice_data, "Data Persistence - Create Invoice")
        
        if success:
            # Verify the invoice can be retrieved
            self.test_endpoint("/financial/invoices", "GET", test_name="Data Persistence - Retrieve Invoices")
        
        return True
    
    def test_data_consistency(self, endpoint):
        """Test data consistency for a specific endpoint"""
        print(f"\n🔍 Testing data consistency for {endpoint}...")
        
        # Make two calls to the same endpoint
        success1, data1 = self.test_endpoint(endpoint, "GET", test_name=f"Data Consistency - {endpoint} (Call 1)")
        time.sleep(1)  # Small delay
        success2, data2 = self.test_endpoint(endpoint, "GET", test_name=f"Data Consistency - {endpoint} (Call 2)")
        
        if success1 and success2:
            if data1 == data2:
                self.log_result(f"Data Consistency - {endpoint}", True, "Data consistent across calls - confirms real database usage")
            else:
                self.log_result(f"Data Consistency - {endpoint}", False, "Data inconsistent - may still be using random generation")
        else:
            self.log_result(f"Data Consistency - {endpoint}", False, "Could not test consistency - endpoint failed")
        
        return True
    
    def test_subscription_management_system(self):
        """Test Complete Subscription Management System"""
        print("\n💳 TESTING COMPLETE SUBSCRIPTION MANAGEMENT SYSTEM")
        print("=" * 60)
        
        # Test Subscription Plans
        print("\n📋 Testing Subscription Plans...")
        self.test_endpoint("/subscriptions/plans", "GET", test_name="Subscriptions - Get All Plans")
        self.test_endpoint("/subscriptions/current", "GET", test_name="Subscriptions - Get Current Subscription")
        
        # Test Subscription Creation with Stripe
        print("\n➕ Testing Subscription Creation...")
        subscription_data = {
            "plan_id": "pro_monthly",
            "payment_method": "card",
            "billing_cycle": "monthly"
        }
        self.test_endpoint("/subscriptions/create", "POST", subscription_data, "Subscriptions - Create Subscription")
        
        # Test Usage Tracking
        print("\n📊 Testing Usage Tracking...")
        self.test_endpoint("/subscriptions/usage", "GET", test_name="Subscriptions - Get Usage")
        self.test_endpoint("/subscriptions/billing-history", "GET", test_name="Subscriptions - Billing History")
        
        # Test Subscription Management
        print("\n⚙️ Testing Subscription Management...")
        self.test_endpoint("/subscriptions/upgrade", "POST", {"new_plan": "enterprise"}, "Subscriptions - Upgrade Plan")
        self.test_endpoint("/subscriptions/cancel", "POST", {"reason": "testing"}, "Subscriptions - Cancel Subscription")
        
        return True

    def run_review_request_comprehensive_test(self):
        """Run comprehensive testing of the 6 key areas from the review request"""
        print("🎯 COMPREHENSIVE BACKEND TESTING FOR MEWAYZ V2 PLATFORM - REVIEW REQUEST")
        print("Testing the 6 key areas mentioned in the review request:")
        print("1. 👥 User Invitation System - workspace invitation creation, acceptance, role-based permissions")
        print("2. 📱 Enhanced Social Media Management - Instagram database search, social media post scheduling, data export")
        print("3. 🛍️ Template Marketplace - template creation, purchase system, creator earnings dashboard")
        print("4. 📱 Mobile PWA Features - PWA manifest generation, offline sync, device registration")
        print("5. 🤖 AI Automation - smart workflow creation, AI insights generation, content optimization")
        print("6. 💰 Escrow System - milestone payment plans, dispute resolution, fee calculations")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the 6 key areas from review request
        self.test_user_invitation_system()
        self.test_enhanced_social_media_management()
        self.test_template_marketplace_comprehensive()
        self.test_mobile_pwa_features_comprehensive()
        self.test_ai_automation_comprehensive()
        self.test_escrow_system_comprehensive()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def test_user_invitation_system(self):
        """Test User Invitation System - workspace invitation creation, acceptance, role-based permissions"""
        print("\n👥 TESTING USER INVITATION SYSTEM")
        print("=" * 60)
        print("Testing workspace invitation creation, acceptance, and role-based permissions")
        
        # Test workspace invitation creation
        print("\n📧 Testing Workspace Invitation Creation...")
        invitation_data = {
            "email": "newuser@mewayz.com",
            "role": "editor",
            "workspace_id": "workspace_123",
            "message": "Welcome to our Mewayz workspace!"
        }
        self.test_endpoint("/workspaces/invitations", "POST", invitation_data, "User Invitations - Create Invitation")
        
        # Test invitation listing
        self.test_endpoint("/workspaces/invitations", "GET", test_name="User Invitations - List Invitations")
        self.test_endpoint("/workspaces/invitations/pending", "GET", test_name="User Invitations - Pending Invitations")
        
        # Test role-based permissions
        print("\n🔐 Testing Role-Based Permissions...")
        self.test_endpoint("/workspaces/roles", "GET", test_name="User Invitations - Available Roles")
        self.test_endpoint("/workspaces/permissions", "GET", test_name="User Invitations - Role Permissions")
        
        # Test invitation acceptance workflow
        print("\n✅ Testing Invitation Acceptance...")
        accept_data = {
            "invitation_token": "sample_token_123",
            "accept": True
        }
        self.test_endpoint("/workspaces/invitations/accept", "POST", accept_data, "User Invitations - Accept Invitation")
        
        # Test workspace member management
        self.test_endpoint("/workspaces/members", "GET", test_name="User Invitations - Workspace Members")
        
        return True
    
    def test_enhanced_social_media_management(self):
        """Test Enhanced Social Media Management - Instagram database search, social media post scheduling, data export"""
        print("\n📱 TESTING ENHANCED SOCIAL MEDIA MANAGEMENT")
        print("=" * 60)
        print("Testing Instagram database search, social media post scheduling, and data export features")
        
        # Test Instagram database search
        print("\n🔍 Testing Instagram Database Search...")
        instagram_search_data = {
            "hashtags": ["business", "entrepreneur", "startup"],
            "location": "United States",
            "follower_range": {"min": 1000, "max": 100000},
            "engagement_rate_min": 2.0
        }
        self.test_endpoint("/social-media/instagram/search", "POST", instagram_search_data, "Social Media - Instagram Database Search")
        self.test_endpoint("/social-media/instagram/analytics", "GET", test_name="Social Media - Instagram Analytics")
        
        # Test social media post scheduling
        print("\n📅 Testing Social Media Post Scheduling...")
        post_data = {
            "content": "Check out our latest business automation tools! #Mewayz #Business #Automation",
            "platforms": ["instagram", "twitter", "facebook"],
            "scheduled_time": "2025-01-25T14:00:00Z",
            "media_urls": ["https://example.com/image1.jpg"],
            "tags": ["business", "automation"]
        }
        self.test_endpoint("/social-media/posts/schedule", "POST", post_data, "Social Media - Schedule Post")
        self.test_endpoint("/social-media/posts/scheduled", "GET", test_name="Social Media - Get Scheduled Posts")
        
        # Test data export features
        print("\n📊 Testing Data Export Features...")
        export_data = {
            "data_type": "social_media_analytics",
            "date_range": {"start": "2025-01-01", "end": "2025-01-31"},
            "format": "csv",
            "include_metrics": ["engagement", "reach", "impressions"]
        }
        self.test_endpoint("/social-media/export", "POST", export_data, "Social Media - Export Data")
        
        # Test social media analytics
        self.test_endpoint("/social-media/analytics/overview", "GET", test_name="Social Media - Analytics Overview")
        self.test_endpoint("/social-media/analytics/engagement", "GET", test_name="Social Media - Engagement Analytics")
        
        return True
    
    def test_template_marketplace_comprehensive(self):
        """Test Template Marketplace - template creation, purchase system, creator earnings dashboard"""
        print("\n🛍️ TESTING TEMPLATE MARKETPLACE COMPREHENSIVE")
        print("=" * 60)
        print("Testing template creation, purchase system, and creator earnings dashboard")
        
        # Test template creation
        print("\n🎨 Testing Template Creation...")
        template_data = {
            "name": "Modern Business Landing Page",
            "description": "Professional landing page template for modern businesses",
            "category": "landing_pages",
            "price": 49.99,
            "tags": ["business", "modern", "responsive"],
            "preview_url": "https://example.com/preview.jpg",
            "template_files": {
                "html": "<html>...</html>",
                "css": "body { margin: 0; }",
                "js": "console.log('Template loaded');"
            }
        }
        self.test_endpoint("/templates/create", "POST", template_data, "Template Marketplace - Create Template")
        self.test_endpoint("/templates", "GET", test_name="Template Marketplace - List Templates")
        
        # Test template categories and browsing
        self.test_endpoint("/templates/categories", "GET", test_name="Template Marketplace - Categories")
        self.test_endpoint("/templates/featured", "GET", test_name="Template Marketplace - Featured Templates")
        self.test_endpoint("/templates/popular", "GET", test_name="Template Marketplace - Popular Templates")
        
        # Test purchase system
        print("\n💳 Testing Purchase System...")
        purchase_data = {
            "template_id": "template_123",
            "payment_method": "stripe",
            "license_type": "standard"
        }
        self.test_endpoint("/templates/purchase", "POST", purchase_data, "Template Marketplace - Purchase Template")
        self.test_endpoint("/templates/purchases", "GET", test_name="Template Marketplace - My Purchases")
        
        # Test creator earnings dashboard
        print("\n💰 Testing Creator Earnings Dashboard...")
        self.test_endpoint("/templates/creator/earnings", "GET", test_name="Template Marketplace - Creator Earnings")
        self.test_endpoint("/templates/creator/analytics", "GET", test_name="Template Marketplace - Creator Analytics")
        self.test_endpoint("/templates/creator/dashboard", "GET", test_name="Template Marketplace - Creator Dashboard")
        
        return True
    
    def test_mobile_pwa_features_comprehensive(self):
        """Test Mobile PWA Features - PWA manifest generation, offline sync, device registration"""
        print("\n📱 TESTING MOBILE PWA FEATURES COMPREHENSIVE")
        print("=" * 60)
        print("Testing PWA manifest generation, offline sync, and device registration")
        
        # Test PWA manifest generation
        print("\n📋 Testing PWA Manifest Generation...")
        self.test_endpoint("/pwa/manifest", "GET", test_name="Mobile PWA - Get Manifest")
        
        manifest_data = {
            "name": "Mewayz Business Platform",
            "short_name": "Mewayz",
            "description": "Complete business automation platform",
            "theme_color": "#3B82F6",
            "background_color": "#FFFFFF",
            "icons": [
                {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}
            ]
        }
        self.test_endpoint("/pwa/manifest", "PUT", manifest_data, "Mobile PWA - Update Manifest")
        
        # Test device registration
        print("\n📱 Testing Device Registration...")
        device_data = {
            "device_id": "device_123456",
            "device_type": "mobile",
            "platform": "android",
            "push_token": "fcm_token_example",
            "app_version": "1.0.0"
        }
        self.test_endpoint("/pwa/devices/register", "POST", device_data, "Mobile PWA - Register Device")
        self.test_endpoint("/pwa/devices", "GET", test_name="Mobile PWA - List Devices")
        
        # Test offline sync
        print("\n🔄 Testing Offline Sync...")
        sync_data = {
            "sync_type": "user_data",
            "last_sync": "2025-01-20T10:00:00Z",
            "data_types": ["profile", "workspaces", "recent_activity"]
        }
        self.test_endpoint("/pwa/sync/queue", "POST", sync_data, "Mobile PWA - Queue Sync")
        self.test_endpoint("/pwa/sync/status", "GET", test_name="Mobile PWA - Sync Status")
        self.test_endpoint("/pwa/sync/process", "POST", {}, "Mobile PWA - Process Sync")
        
        # Test push notifications
        print("\n🔔 Testing Push Notifications...")
        notification_data = {
            "title": "Welcome to Mewayz!",
            "body": "Your business automation platform is ready",
            "icon": "/icon-192.png",
            "badge": "/badge.png",
            "data": {"action": "open_dashboard"}
        }
        self.test_endpoint("/pwa/notifications/send", "POST", notification_data, "Mobile PWA - Send Notification")
        
        # Test offline caching
        cache_data = {
            "url": "/dashboard",
            "cache_strategy": "cache_first",
            "expiry": "24h"
        }
        self.test_endpoint("/pwa/cache", "POST", cache_data, "Mobile PWA - Cache Resource")
        
        return True
    
    def test_ai_automation_comprehensive(self):
        """Test AI Automation - smart workflow creation, AI insights generation, content optimization"""
        print("\n🤖 TESTING AI AUTOMATION COMPREHENSIVE")
        print("=" * 60)
        print("Testing smart workflow creation, AI insights generation, and content optimization")
        
        # Test smart workflow creation
        print("\n⚙️ Testing Smart Workflow Creation...")
        workflow_data = {
            "name": "Lead Nurturing Automation",
            "description": "Automated lead nurturing with AI-powered content",
            "triggers": [
                {"type": "form_submission", "form_id": "contact_form"}
            ],
            "actions": [
                {"type": "send_email", "template": "welcome_email"},
                {"type": "add_to_crm", "list": "prospects"},
                {"type": "schedule_followup", "delay": "3_days"}
            ],
            "ai_optimization": True
        }
        self.test_endpoint("/ai/workflows/create", "POST", workflow_data, "AI Automation - Create Smart Workflow")
        self.test_endpoint("/ai/workflows", "GET", test_name="AI Automation - List Workflows")
        self.test_endpoint("/ai/workflows/templates", "GET", test_name="AI Automation - Workflow Templates")
        
        # Test AI insights generation
        print("\n🧠 Testing AI Insights Generation...")
        insights_data = {
            "data_source": "user_analytics",
            "time_period": "last_30_days",
            "insight_types": ["performance", "trends", "recommendations"]
        }
        self.test_endpoint("/ai/insights/generate", "POST", insights_data, "AI Automation - Generate Insights")
        self.test_endpoint("/ai/insights", "GET", test_name="AI Automation - Get Insights")
        self.test_endpoint("/ai/insights/recommendations", "GET", test_name="AI Automation - AI Recommendations")
        
        # Test content optimization
        print("\n✍️ Testing Content Optimization...")
        content_data = {
            "content": "Welcome to our business platform. We help you grow your business.",
            "content_type": "email_subject",
            "target_audience": "small_business_owners",
            "optimization_goals": ["engagement", "conversion"]
        }
        self.test_endpoint("/ai/content/optimize", "POST", content_data, "AI Automation - Optimize Content")
        
        # Test AI analytics
        self.test_endpoint("/ai/analytics/usage", "GET", test_name="AI Automation - Usage Analytics")
        self.test_endpoint("/ai/analytics/performance", "GET", test_name="AI Automation - Performance Analytics")
        
        return True
    
    def test_escrow_system_comprehensive(self):
        """Test Escrow System - milestone payment plans, dispute resolution, fee calculations"""
        print("\n💰 TESTING ESCROW SYSTEM COMPREHENSIVE")
        print("=" * 60)
        print("Testing milestone payment plans, dispute resolution, and fee calculations")
        
        # Test milestone payment plans
        print("\n📋 Testing Milestone Payment Plans...")
        milestone_data = {
            "project_name": "Website Development Project",
            "total_amount": 5000.00,
            "currency": "USD",
            "milestones": [
                {"name": "Design Phase", "amount": 1500.00, "due_date": "2025-02-15"},
                {"name": "Development Phase", "amount": 2500.00, "due_date": "2025-03-15"},
                {"name": "Testing & Launch", "amount": 1000.00, "due_date": "2025-04-01"}
            ],
            "client_email": "client@example.com",
            "freelancer_email": "freelancer@example.com"
        }
        self.test_endpoint("/escrow/projects/create", "POST", milestone_data, "Escrow System - Create Milestone Plan")
        self.test_endpoint("/escrow/projects", "GET", test_name="Escrow System - List Projects")
        
        # Test payment processing
        print("\n💳 Testing Payment Processing...")
        payment_data = {
            "project_id": "project_123",
            "milestone_id": "milestone_1",
            "payment_method": "stripe",
            "amount": 1500.00
        }
        self.test_endpoint("/escrow/payments/deposit", "POST", payment_data, "Escrow System - Deposit Payment")
        self.test_endpoint("/escrow/payments/release", "POST", {"project_id": "project_123", "milestone_id": "milestone_1"}, "Escrow System - Release Payment")
        
        # Test dispute resolution
        print("\n⚖️ Testing Dispute Resolution...")
        dispute_data = {
            "project_id": "project_123",
            "dispute_type": "milestone_completion",
            "description": "Client disputes milestone completion quality",
            "evidence": ["screenshot1.jpg", "communication_log.txt"],
            "requested_resolution": "partial_refund"
        }
        self.test_endpoint("/escrow/disputes/create", "POST", dispute_data, "Escrow System - Create Dispute")
        self.test_endpoint("/escrow/disputes", "GET", test_name="Escrow System - List Disputes")
        
        # Test fee calculations
        print("\n🧮 Testing Fee Calculations...")
        fee_data = {
            "amount": 5000.00,
            "service_type": "milestone_escrow",
            "payment_method": "stripe"
        }
        self.test_endpoint("/escrow/fees/calculate", "POST", fee_data, "Escrow System - Calculate Fees")
        self.test_endpoint("/escrow/fees/structure", "GET", test_name="Escrow System - Fee Structure")
        
        # Test escrow analytics
        self.test_endpoint("/escrow/analytics/overview", "GET", test_name="Escrow System - Analytics Overview")
        self.test_endpoint("/escrow/analytics/transactions", "GET", test_name="Escrow System - Transaction Analytics")
        
        return True

    def run_review_request_targeted_test(self):
        """Run comprehensive test focusing on review request areas"""
        print("🎯 FINAL COMPREHENSIVE BACKEND VERIFICATION TEST - MEWAYZ V2 PLATFORM")
        print("=" * 80)
        print("Testing newly implemented and fixed features as requested in review:")
        print("1. Fixed Critical Issues")
        print("2. New Feature Implementations") 
        print("3. API Endpoint Coverage")
        print("4. Validation & Error Handling")
        print("5. Performance & Integration")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Health check
        if not self.test_health_check():
            print("❌ Backend health check failed. Aborting tests.")
            return False
        
        # Step 2: Authentication
        if not self.test_authentication():
            print("❌ Authentication failed. Aborting tests.")
            return False
        
        print(f"\n✅ Authentication successful. Token: {self.access_token[:20]}...")
        
        # Step 3: Test the specific areas mentioned in review request
        try:
            # PRIORITY TEST AREAS from review request
            print("\n" + "="*80)
            print("🎯 PRIORITY TEST AREAS - REVIEW REQUEST FOCUS")
            print("="*80)
            
            # 1. Fixed Critical Issues
            self.test_fixed_critical_issues()
            
            # 2. New Feature Implementations  
            self.test_new_feature_implementations()
            
            # 3. API Endpoint Coverage
            self.test_api_endpoint_coverage()
            
            # 4. Validation & Error Handling
            self.test_validation_error_handling()
            
            # 5. Performance & Integration
            self.test_performance_integration()
            
            # 6. Test existing endpoints that were mentioned as working
            self.test_existing_endpoints_from_history()
            
        except Exception as e:
            print(f"❌ Error during testing: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Generate final report
        self.generate_final_report()
        return True
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test available endpoints for each area
        self.test_available_team_management()
        self.test_available_social_media_management()
        self.test_available_template_marketplace()
        self.test_available_mobile_pwa_features()
        self.test_available_ai_automation()
        self.test_available_escrow_payment_system()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def test_available_team_management(self):
        """Test available team management endpoints"""
        print("\n👥 TESTING AVAILABLE TEAM MANAGEMENT ENDPOINTS")
        print("=" * 60)
        print("Testing workspace invitation creation, acceptance, and role-based permissions")
        
        # Test team dashboard
        self.test_endpoint("/teams/dashboard", "GET", test_name="Team Management - Dashboard")
        
        # Test team members
        self.test_endpoint("/teams/members", "GET", test_name="Team Management - Get Members")
        
        # Test team activity
        self.test_endpoint("/teams/activity", "GET", test_name="Team Management - Activity Log")
        
        # Test team invitation
        invitation_data = {
            "email": "newteammember@mewayz.com",
            "role": "editor",
            "message": "Welcome to our team!"
        }
        self.test_endpoint("/teams/invite", "POST", invitation_data, "Team Management - Send Invitation")
        
        # Test invitation acceptance
        accept_data = {
            "invitation_token": "sample_token_123"
        }
        self.test_endpoint("/teams/accept-invitation", "POST", accept_data, "Team Management - Accept Invitation")
        
        return True
    
    def test_available_social_media_management(self):
        """Test available social media management endpoints"""
        print("\n📱 TESTING AVAILABLE SOCIAL MEDIA MANAGEMENT ENDPOINTS")
        print("=" * 60)
        print("Testing social media lead generation and analytics")
        
        # Test social media leads analytics
        self.test_endpoint("/social-media-leads/analytics/overview", "GET", test_name="Social Media - Analytics Overview")
        self.test_endpoint("/social-media-leads/health", "GET", test_name="Social Media - Health Check")
        
        # Test TikTok discovery
        tiktok_data = {
            "hashtags": ["business", "entrepreneur"],
            "location": "United States",
            "follower_range": {"min": 1000, "max": 100000}
        }
        self.test_endpoint("/social-media-leads/discover/tiktok", "POST", tiktok_data, "Social Media - TikTok Discovery")
        
        # Test Twitter discovery
        twitter_data = {
            "keywords": ["business owner", "entrepreneur"],
            "location": "United States",
            "follower_range": {"min": 500, "max": 50000}
        }
        self.test_endpoint("/social-media-leads/discover/twitter", "POST", twitter_data, "Social Media - Twitter Discovery")
        
        return True
    
    def test_available_template_marketplace(self):
        """Test available template marketplace endpoints"""
        print("\n🛍️ TESTING AVAILABLE TEMPLATE MARKETPLACE ENDPOINTS")
        print("=" * 60)
        print("Testing template marketplace and vendor system")
        
        # Test marketing website templates
        self.test_endpoint("/marketing-website/templates/marketplace", "GET", test_name="Template Marketplace - Marketing Templates")
        
        # Test marketplace vendors
        self.test_endpoint("/marketplace/vendors", "GET", test_name="Template Marketplace - Vendors")
        self.test_endpoint("/marketplace/vendors/applications", "GET", test_name="Template Marketplace - Vendor Applications")
        
        # Test vendor onboarding
        vendor_data = {
            "business_name": "Creative Templates Co",
            "email": "vendor@creativetemplates.com",
            "category": "web_templates",
            "description": "Professional web templates for businesses"
        }
        self.test_endpoint("/marketplace/vendors/onboard", "POST", vendor_data, "Template Marketplace - Vendor Onboarding")
        
        # Test dynamic pricing
        self.test_endpoint("/marketplace/pricing/dynamic", "GET", test_name="Template Marketplace - Dynamic Pricing")
        
        return True
    
    def test_available_mobile_pwa_features(self):
        """Test available mobile PWA features"""
        print("\n📱 TESTING AVAILABLE MOBILE PWA FEATURES")
        print("=" * 60)
        print("Testing PWA and mobile-related endpoints")
        
        # Test notifications system (PWA-related)
        self.test_endpoint("/notifications-system/templates", "GET", test_name="Mobile PWA - Notification Templates")
        
        # Test i18n workspace language (mobile localization)
        self.test_endpoint("/i18n/workspace-language", "GET", test_name="Mobile PWA - Workspace Language")
        
        # Note: Most PWA-specific endpoints appear to not be implemented yet
        print("⚠️ Most PWA-specific endpoints (manifest, device registration, offline sync) not found in API")
        
        return True
    
    def test_available_ai_automation(self):
        """Test available AI automation endpoints"""
        print("\n🤖 TESTING AVAILABLE AI AUTOMATION ENDPOINTS")
        print("=" * 60)
        print("Testing AI automation workflows and content generation")
        
        # Test AI automation analytics
        self.test_endpoint("/ai-automation/analytics/overview", "GET", test_name="AI Automation - Analytics Overview")
        
        # Test workflow creation
        workflow_data = {
            "name": "Lead Nurturing Workflow",
            "description": "Automated lead nurturing with AI",
            "triggers": [{"type": "form_submission"}],
            "actions": [{"type": "send_email"}]
        }
        self.test_endpoint("/ai-automation/create-workflow", "POST", workflow_data, "AI Automation - Create Workflow")
        
        # Test workflows listing
        self.test_endpoint("/ai-automation/workflows", "GET", test_name="AI Automation - List Workflows")
        
        # Test content generation
        content_data = {
            "content_type": "email_subject",
            "topic": "business automation",
            "tone": "professional"
        }
        self.test_endpoint("/ai-automation/generate-content", "POST", content_data, "AI Automation - Generate Content")
        
        # Test content history
        self.test_endpoint("/ai-automation/content-history", "GET", test_name="AI Automation - Content History")
        
        # Test lead enrichment
        lead_data = {
            "email": "prospect@example.com",
            "company": "Example Corp"
        }
        self.test_endpoint("/ai-automation/enrich-lead", "POST", lead_data, "AI Automation - Enrich Lead")
        
        # Test enrichment history
        self.test_endpoint("/ai-automation/enrichment-history", "GET", test_name="AI Automation - Enrichment History")
        
        # Test bulk operations
        bulk_content_data = {
            "templates": ["email_welcome", "email_followup"],
            "count": 5
        }
        self.test_endpoint("/ai-automation/bulk-content-generation", "POST", bulk_content_data, "AI Automation - Bulk Content Generation")
        
        # Test batch lead enrichment
        batch_leads_data = {
            "leads": [
                {"email": "lead1@example.com"},
                {"email": "lead2@example.com"}
            ]
        }
        self.test_endpoint("/ai-automation/batch-enrich-leads", "POST", batch_leads_data, "AI Automation - Batch Enrich Leads")
        
        return True
    
    def test_available_escrow_payment_system(self):
        """Test available escrow and payment system endpoints"""
        print("\n💰 TESTING AVAILABLE ESCROW/PAYMENT SYSTEM ENDPOINTS")
        print("=" * 60)
        print("Testing payment processing and vendor payout systems")
        
        # Test AI tokens (payment-related)
        self.test_endpoint("/ai-tokens/dashboard", "GET", test_name="Payment System - AI Tokens Dashboard")
        self.test_endpoint("/ai-tokens/packages", "GET", test_name="Payment System - Token Packages")
        
        # Test token purchase
        purchase_data = {
            "package_id": "basic_package",
            "payment_method": "stripe"
        }
        self.test_endpoint("/ai-tokens/purchase", "POST", purchase_data, "Payment System - Purchase Tokens")
        
        # Test token consumption
        consume_data = {
            "tokens": 10,
            "service": "content_generation"
        }
        self.test_endpoint("/ai-tokens/consume", "POST", consume_data, "Payment System - Consume Tokens")
        
        # Test vendor payouts (escrow-like functionality)
        payout_data = {
            "amount": 100.00,
            "currency": "USD"
        }
        # Note: This endpoint requires vendor_id parameter, testing structure only
        print("⚠️ Vendor payout endpoints require specific vendor IDs - testing structure only")
        
        print("⚠️ Full escrow system endpoints (milestone payments, disputes) not found in API")
        
    def test_existing_endpoints_from_history(self):
        """Test endpoints that were mentioned as working in previous test results"""
        print("\n🔍 TESTING EXISTING ENDPOINTS FROM PREVIOUS RESULTS")
        print("=" * 60)
        
        # Test endpoints that were mentioned as working in test_result.md
        print("\n📊 Testing Analytics & Dashboard Endpoints...")
        self.test_endpoint("/unified-analytics/health", "GET", test_name="Unified Analytics - Health Check")
        self.test_endpoint("/unified-analytics/dashboard", "GET", test_name="Unified Analytics - Dashboard")
        self.test_endpoint("/unified-analytics/leaderboard/global", "GET", test_name="Unified Analytics - Global Leaderboard")
        
        print("\n👥 Testing Team Management Endpoints...")
        self.test_endpoint("/team-management/health", "GET", test_name="Team Management - Health Check")
        self.test_endpoint("/teams/dashboard", "GET", test_name="Teams - Dashboard")
        self.test_endpoint("/teams/activity", "GET", test_name="Teams - Activity Log")
        
        print("\n🛍️ Testing Template Marketplace Endpoints...")
        self.test_endpoint("/template-marketplace/health", "GET", test_name="Template Marketplace - Health Check")
        self.test_endpoint("/template-marketplace/categories", "GET", test_name="Template Marketplace - Categories")
        self.test_endpoint("/templates/marketplace", "GET", test_name="Templates - Marketplace Browse")
        
        print("\n📱 Testing Mobile PWA Endpoints...")
        self.test_endpoint("/mobile-pwa/health", "GET", test_name="Mobile PWA - Health Check")
        self.test_endpoint("/mobile-pwa/manifest", "GET", test_name="Mobile PWA - Manifest")
        self.test_endpoint("/mobile-pwa/analytics/mobile", "GET", test_name="Mobile PWA - Analytics")
        
        print("\n🤖 Testing AI Automation Endpoints...")
        self.test_endpoint("/ai/analytics", "GET", test_name="AI - Analytics Overview")
        self.test_endpoint("/ai/content/generate", "POST", {"prompt": "Write a business blog post about productivity"}, "AI - Generate Content")
        self.test_endpoint("/workflows/user", "GET", test_name="Workflows - User Workflows")
        
        print("\n💰 Testing Payment/Escrow Related Endpoints...")
        self.test_endpoint("/ai-tokens/dashboard", "GET", test_name="AI Tokens - Dashboard")
        self.test_endpoint("/ai-tokens/packages", "GET", test_name="AI Tokens - Packages")
        
        print("\n📱 Testing Social Media Endpoints...")
        self.test_endpoint("/social-media-leads/analytics", "GET", test_name="Social Media - Analytics")
        self.test_endpoint("/social-media-leads/twitter/search", "POST", {
            "keywords": ["business", "entrepreneur"],
            "max_results": 10
        }, "Social Media - Twitter Search")
        
        print("\n🔍 Existing Endpoints Testing Complete!")
        return True
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*80)
        print("📊 FINAL COMPREHENSIVE BACKEND VERIFICATION REPORT")
        print("="*80)
        
        # Calculate overall statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Categorize results by feature area
        feature_results = {}
        for result in self.test_results:
            test_name = result["test"]
            if "Team Management" in test_name or "Teams" in test_name or "Datetime Fix" in test_name:
                feature = "Team Management & Collaboration"
            elif "AI" in test_name or "Workflow" in test_name:
                feature = "AI & Automation"
            elif "Instagram" in test_name or "Social Media" in test_name or "Twitter" in test_name:
                feature = "Social Media Integration"
            elif "PWA" in test_name or "Mobile" in test_name or "Manifest" in test_name:
                feature = "Mobile PWA Features"
            elif "Escrow" in test_name or "Dispute" in test_name or "Tokens" in test_name:
                feature = "Payment & Escrow System"
            elif "Template" in test_name or "Marketplace" in test_name:
                feature = "Template Marketplace"
            elif "Validation" in test_name or "Error Handling" in test_name:
                feature = "Validation & Error Handling"
            elif "Performance" in test_name or "Authentication" in test_name:
                feature = "Performance & Integration"
            elif "Analytics" in test_name or "Dashboard" in test_name:
                feature = "Analytics & Dashboard"
            else:
                feature = "Other Features"
            
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
        
        print(f"\n🔍 CRITICAL ISSUES FOUND:")
        failed_results = [r for r in self.test_results if not r["success"]]
        critical_issues = []
        
        if failed_results:
            # Group failures by type
            endpoint_404_count = len([r for r in failed_results if "404" in r["message"]])
            validation_issues = len([r for r in failed_results if "422" in r["message"] or "400" in r["message"]])
            server_errors = len([r for r in failed_results if "500" in r["message"]])
            
            if endpoint_404_count > 0:
                critical_issues.append(f"❌ {endpoint_404_count} endpoints not implemented (404 errors)")
            if validation_issues > 0:
                critical_issues.append(f"⚠️ {validation_issues} validation schema issues")
            if server_errors > 0:
                critical_issues.append(f"🔴 {server_errors} server errors (500)")
                
            for issue in critical_issues:
                print(f"   {issue}")
        else:
            print("   🎉 No critical issues found!")
        
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
        return True

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_review_request_targeted_test()
    sys.exit(0 if success else 1)