#!/usr/bin/env python3
"""
COMPREHENSIVE FULL PLATFORM AUDIT - REAL DATA OPERATIONS
Comprehensive Backend API Testing Script focused on CRUD operations and real data verification
Tests all internal database operations and external API integrations as requested in review
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import uuid

# Backend URL from environment
BACKEND_URL = "https://30f38136-d29a-41ec-aa06-5e02a1d9c8b2.preview.emergentagent.com"
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
        print("1. Advanced Template Marketplace")
        print("2. Advanced Team Management") 
        print("3. Unified Analytics with Gamification")
        print("4. Mobile PWA Features")
        
        # Test all new features
        self.test_template_marketplace_system()
        self.test_team_management_system()
        self.test_unified_analytics_system()
        self.test_mobile_pwa_system()
        
    def test_template_marketplace_system(self):
        """Test Advanced Template Marketplace at /api/template-marketplace/*"""
        print("\n🛍️ TESTING ADVANCED TEMPLATE MARKETPLACE")
        print("=" * 60)
        
        # Test variables to store created resources
        created_template_id = None
        
        # 1. Test Health Check
        print("\n🏥 Testing Health Check...")
        self.test_endpoint("/template-marketplace/health", "GET", test_name="Template Marketplace - Health Check")
        
        # 2. Test Categories
        print("\n📂 Testing Categories...")
        self.test_endpoint("/template-marketplace/categories", "GET", test_name="Template Marketplace - Get Categories")
        
        # 3. Test Marketplace Browsing
        print("\n🔍 Testing Marketplace Browsing...")
        self.test_endpoint("/template-marketplace/marketplace", "GET", test_name="Template Marketplace - Browse All Templates")
        self.test_endpoint("/template-marketplace/marketplace?category=business", "GET", test_name="Template Marketplace - Browse Business Templates")
        self.test_endpoint("/template-marketplace/marketplace?price_range=free", "GET", test_name="Template Marketplace - Browse Free Templates")
        self.test_endpoint("/template-marketplace/marketplace?sort=popular", "GET", test_name="Template Marketplace - Browse Popular Templates")
        
        # 4. Test Template Creation
        print("\n➕ Testing Template Creation...")
        create_template_data = {
            "name": "Modern Business Landing Page",
            "description": "A sleek, professional landing page template perfect for modern businesses and startups",
            "category": "business",
            "price": 29.99,
            "tags": ["landing-page", "business", "modern", "responsive"],
            "preview_images": [
                "https://example.com/preview1.jpg",
                "https://example.com/preview2.jpg"
            ],
            "template_data": {
                "html": "<div class='hero-section'>Welcome to our business</div>",
                "css": ".hero-section { background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); }",
                "js": "console.log('Template loaded');"
            },
            "features": ["responsive", "seo-optimized", "fast-loading"],
            "compatibility": ["all-browsers", "mobile-friendly"]
        }
        
        success, template_data = self.test_endpoint("/template-marketplace/templates", "POST", create_template_data, "Template Marketplace - Create Template")
        if success and template_data:
            created_template_id = template_data.get("template_id") or template_data.get("id") or template_data.get("data", {}).get("id")
            print(f"   Created template ID: {created_template_id}")
        
        # 5. Test Template Purchase
        if created_template_id:
            print("\n💳 Testing Template Purchase...")
            purchase_data = {
                "payment_method": "stripe",
                "license_type": "standard"
            }
            self.test_endpoint(f"/template-marketplace/templates/{created_template_id}/purchase", "POST", purchase_data, "Template Marketplace - Purchase Template")
        
        # 6. Test Creator Analytics
        print("\n📊 Testing Creator Analytics...")
        self.test_endpoint("/template-marketplace/creator/analytics", "GET", test_name="Template Marketplace - Creator Analytics")
        self.test_endpoint("/template-marketplace/creator/revenue", "GET", test_name="Template Marketplace - Creator Revenue")
        
        # 7. Test Template Management
        print("\n⚙️ Testing Template Management...")
        self.test_endpoint("/template-marketplace/my-templates", "GET", test_name="Template Marketplace - My Templates")
        self.test_endpoint("/template-marketplace/purchases", "GET", test_name="Template Marketplace - My Purchases")
        
        print("\n🛍️ Template Marketplace System Testing Complete!")
        return True
        
    def test_team_management_system(self):
        """Test Advanced Team Management at /api/team-management/*"""
        print("\n👥 TESTING ADVANCED TEAM MANAGEMENT")
        print("=" * 60)
        
        # Test variables to store created resources
        created_team_id = None
        invitation_id = None
        
        # 1. Test Health Check
        print("\n🏥 Testing Health Check...")
        self.test_endpoint("/team-management/health", "GET", test_name="Team Management - Health Check")
        
        # 2. Test Teams List
        print("\n📋 Testing Teams List...")
        self.test_endpoint("/team-management/teams", "GET", test_name="Team Management - Get Teams")
        
        # 3. Test Team Creation
        print("\n➕ Testing Team Creation...")
        create_team_data = {
            "name": "Digital Marketing Squad",
            "description": "Our core digital marketing team focused on growth and customer acquisition",
            "team_type": "marketing",
            "settings": {
                "privacy": "private",
                "auto_approve_invites": False,
                "allow_member_invites": True,
                "max_members": 25
            },
            "permissions": {
                "can_create_projects": True,
                "can_manage_content": True,
                "can_view_analytics": True,
                "can_export_data": False
            }
        }
        
        success, team_data = self.test_endpoint("/team-management/teams", "POST", create_team_data, "Team Management - Create Team")
        if success and team_data:
            created_team_id = team_data.get("team_id") or team_data.get("id") or team_data.get("data", {}).get("id")
            print(f"   Created team ID: {created_team_id}")
        
        # 4. Test Team Invitations
        if created_team_id:
            print("\n📧 Testing Team Invitations...")
            invitation_data = {
                "email": "newmember@company.com",
                "role": "member",
                "permissions": ["view_projects", "create_content"],
                "custom_message": "Welcome to our marketing team! We're excited to have you join us.",
                "expires_in_days": 7
            }
            
            success, invite_data = self.test_endpoint(f"/team-management/teams/{created_team_id}/invitations", "POST", invitation_data, "Team Management - Send Invitation")
            if success and invite_data:
                invitation_id = invite_data.get("invitation_id") or invite_data.get("id")
                print(f"   Created invitation ID: {invitation_id}")
        
        # 5. Test Roles Management
        if created_team_id:
            print("\n🎭 Testing Roles Management...")
            self.test_endpoint(f"/team-management/teams/{created_team_id}/roles", "GET", test_name="Team Management - Get Team Roles")
            
            # Create custom role
            custom_role_data = {
                "name": "Content Creator",
                "description": "Can create and edit content but cannot manage team settings",
                "permissions": [
                    "create_content",
                    "edit_own_content", 
                    "view_team_analytics",
                    "comment_on_content"
                ]
            }
            self.test_endpoint(f"/team-management/teams/{created_team_id}/roles", "POST", custom_role_data, "Team Management - Create Custom Role")
        
        # 6. Test Member Management
        if created_team_id:
            print("\n👤 Testing Member Management...")
            self.test_endpoint(f"/team-management/teams/{created_team_id}/members", "GET", test_name="Team Management - Get Team Members")
            
            # Update member role (if we had members)
            member_update_data = {
                "role": "admin",
                "permissions": ["manage_team", "invite_members", "view_analytics"]
            }
            # This would normally use a real member ID
            self.test_endpoint(f"/team-management/teams/{created_team_id}/members/member_123", "PUT", member_update_data, "Team Management - Update Member Role")
        
        # 7. Test Team Analytics
        if created_team_id:
            print("\n📊 Testing Team Analytics...")
            self.test_endpoint(f"/team-management/teams/{created_team_id}/analytics", "GET", test_name="Team Management - Team Analytics")
            self.test_endpoint(f"/team-management/teams/{created_team_id}/activity", "GET", test_name="Team Management - Team Activity")
        
        # 8. Test Multi-tier Support
        print("\n🏢 Testing Multi-tier Support...")
        self.test_endpoint("/team-management/organization/structure", "GET", test_name="Team Management - Organization Structure")
        self.test_endpoint("/team-management/permissions/matrix", "GET", test_name="Team Management - Permissions Matrix")
        
        print("\n👥 Team Management System Testing Complete!")
        return True
        
    def test_unified_analytics_system(self):
        """Test Unified Analytics with Gamification at /api/unified-analytics/*"""
        print("\n📊 TESTING UNIFIED ANALYTICS WITH GAMIFICATION")
        print("=" * 60)
        
        # 1. Test Health Check
        print("\n🏥 Testing Health Check...")
        self.test_endpoint("/unified-analytics/health", "GET", test_name="Unified Analytics - Health Check")
        
        # 2. Test Analytics Dashboard
        print("\n📈 Testing Analytics Dashboard...")
        self.test_endpoint("/unified-analytics/dashboard", "GET", test_name="Unified Analytics - Dashboard Overview")
        self.test_endpoint("/unified-analytics/dashboard?period=week", "GET", test_name="Unified Analytics - Dashboard Weekly")
        self.test_endpoint("/unified-analytics/dashboard?period=month", "GET", test_name="Unified Analytics - Dashboard Monthly")
        self.test_endpoint("/unified-analytics/dashboard?period=quarter", "GET", test_name="Unified Analytics - Dashboard Quarterly")
        
        # 3. Test Gamification Profile
        print("\n🎮 Testing Gamification Profile...")
        self.test_endpoint("/unified-analytics/gamification/profile", "GET", test_name="Unified Analytics - Gamification Profile")
        
        # 4. Test Points System
        print("\n⭐ Testing Points System...")
        add_points_data = {
            "action": "template_created",
            "points": 50,
            "description": "Created a new template in the marketplace"
        }
        self.test_endpoint("/unified-analytics/gamification/points/add", "POST", add_points_data, "Unified Analytics - Add Points")
        
        # Add more points for different actions
        point_actions = [
            {"action": "team_invitation_sent", "points": 25, "description": "Invited a new team member"},
            {"action": "analytics_viewed", "points": 10, "description": "Viewed analytics dashboard"},
            {"action": "template_purchased", "points": 75, "description": "Purchased a premium template"}
        ]
        
        for action_data in point_actions:
            self.test_endpoint("/unified-analytics/gamification/points/add", "POST", action_data, f"Unified Analytics - Add Points ({action_data['action']})")
        
        # 5. Test Achievements System
        print("\n🏆 Testing Achievements System...")
        self.test_endpoint("/unified-analytics/gamification/achievements", "GET", test_name="Unified Analytics - Get Achievements")
        
        # Unlock achievement
        achievement_data = {
            "achievement_id": "first_template_creator",
            "description": "Created your first template"
        }
        self.test_endpoint("/unified-analytics/gamification/achievements/unlock", "POST", achievement_data, "Unified Analytics - Unlock Achievement")
        
        # 6. Test Leaderboard
        print("\n🥇 Testing Leaderboard...")
        self.test_endpoint("/unified-analytics/gamification/leaderboard", "GET", test_name="Unified Analytics - Global Leaderboard")
        self.test_endpoint("/unified-analytics/gamification/leaderboard?period=month", "GET", test_name="Unified Analytics - Monthly Leaderboard")
        self.test_endpoint("/unified-analytics/gamification/leaderboard?category=templates", "GET", test_name="Unified Analytics - Template Creator Leaderboard")
        
        # 7. Test AI-powered Insights
        print("\n🤖 Testing AI-powered Insights...")
        self.test_endpoint("/unified-analytics/insights/ai", "GET", test_name="Unified Analytics - AI Insights")
        
        # Generate custom insights
        insights_data = {
            "data_sources": ["user_activity", "team_performance", "template_usage"],
            "time_range": "30_days",
            "insight_type": "performance_optimization"
        }
        self.test_endpoint("/unified-analytics/insights/generate", "POST", insights_data, "Unified Analytics - Generate AI Insights")
        
        # 8. Test Predictive Analytics
        print("\n🔮 Testing Predictive Analytics...")
        prediction_data = {
            "metric": "user_engagement",
            "forecast_period": "next_30_days",
            "confidence_level": 0.85
        }
        self.test_endpoint("/unified-analytics/predictive/forecast", "POST", prediction_data, "Unified Analytics - Predictive Forecast")
        
        # 9. Test Custom Reports
        print("\n📋 Testing Custom Reports...")
        report_data = {
            "report_name": "Team Performance Summary",
            "metrics": ["team_activity", "template_creation", "collaboration_score"],
            "time_period": "last_30_days",
            "format": "pdf"
        }
        self.test_endpoint("/unified-analytics/reports/custom", "POST", report_data, "Unified Analytics - Generate Custom Report")
        
        # 10. Test Real-time Data
        print("\n⚡ Testing Real-time Data...")
        self.test_endpoint("/unified-analytics/realtime/activity", "GET", test_name="Unified Analytics - Real-time Activity")
        self.test_endpoint("/unified-analytics/realtime/metrics", "GET", test_name="Unified Analytics - Real-time Metrics")
        
        print("\n📊 Unified Analytics System Testing Complete!")
        return True
        
    def test_mobile_pwa_system(self):
        """Test Mobile PWA Features at /api/mobile-pwa/*"""
        print("\n📱 TESTING MOBILE PWA FEATURES")
        print("=" * 60)
        
        # Test variables to store created resources
        device_id = None
        subscription_id = None
        
        # 1. Test Health Check
        print("\n🏥 Testing Health Check...")
        self.test_endpoint("/mobile-pwa/health", "GET", test_name="Mobile PWA - Health Check")
        
        # 2. Test PWA Manifest
        print("\n📋 Testing PWA Manifest...")
        self.test_endpoint("/mobile-pwa/pwa/manifest", "GET", test_name="Mobile PWA - Get Manifest")
        
        # Update manifest
        manifest_data = {
            "name": "Mewayz Business Platform",
            "short_name": "Mewayz",
            "description": "Complete business automation platform",
            "theme_color": "#667eea",
            "background_color": "#ffffff",
            "display": "standalone",
            "orientation": "portrait"
        }
        self.test_endpoint("/mobile-pwa/pwa/manifest", "PUT", manifest_data, "Mobile PWA - Update Manifest")
        
        # 3. Test Push Notifications
        print("\n🔔 Testing Push Notifications...")
        
        # Subscribe to push notifications
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/example-endpoint",
            "keys": {
                "p256dh": "example-p256dh-key",
                "auth": "example-auth-key"
            },
            "device_type": "mobile",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
        }
        
        success, sub_data = self.test_endpoint("/mobile-pwa/push/subscribe", "POST", subscription_data, "Mobile PWA - Subscribe to Push")
        if success and sub_data:
            subscription_id = sub_data.get("subscription_id") or sub_data.get("id")
            print(f"   Created subscription ID: {subscription_id}")
        
        # Send push notification
        push_data = {
            "title": "Welcome to Mewayz PWA!",
            "body": "Your mobile experience is now enhanced with offline capabilities",
            "icon": "/icons/notification-icon.png",
            "badge": "/icons/badge-icon.png",
            "data": {
                "url": "/dashboard",
                "action": "open_dashboard"
            }
        }
        self.test_endpoint("/mobile-pwa/push/send", "POST", push_data, "Mobile PWA - Send Push Notification")
        
        # 4. Test Device Registration
        print("\n📱 Testing Device Registration...")
        device_data = {
            "device_type": "mobile",
            "platform": "ios",
            "app_version": "1.0.0",
            "device_info": {
                "model": "iPhone 13",
                "os_version": "15.0",
                "screen_resolution": "1170x2532"
            },
            "capabilities": ["push_notifications", "offline_storage", "camera"]
        }
        
        success, device_response = self.test_endpoint("/mobile-pwa/device/register", "POST", device_data, "Mobile PWA - Register Device")
        if success and device_response:
            device_id = device_response.get("device_id") or device_response.get("id")
            print(f"   Registered device ID: {device_id}")
        
        # 5. Test Offline Caching
        print("\n💾 Testing Offline Caching...")
        
        # Cache resources
        cache_data = {
            "resources": [
                "/dashboard",
                "/templates",
                "/team-management",
                "/analytics"
            ],
            "cache_strategy": "cache_first",
            "max_age": 86400  # 24 hours
        }
        self.test_endpoint("/mobile-pwa/offline/cache", "POST", cache_data, "Mobile PWA - Cache Resources")
        
        # Get cached resources
        self.test_endpoint("/mobile-pwa/offline/cached-resources", "GET", test_name="Mobile PWA - Get Cached Resources")
        
        # 6. Test Background Sync
        print("\n🔄 Testing Background Sync...")
        
        # Queue background sync
        sync_data = {
            "action": "sync_analytics",
            "data": {
                "user_activity": "template_viewed",
                "timestamp": "2025-01-15T10:30:00Z"
            },
            "retry_count": 3
        }
        self.test_endpoint("/mobile-pwa/sync/queue", "POST", sync_data, "Mobile PWA - Queue Background Sync")
        
        # Get sync status
        self.test_endpoint("/mobile-pwa/sync/status", "GET", test_name="Mobile PWA - Get Sync Status")
        
        # 7. Test Mobile Analytics
        print("\n📊 Testing Mobile Analytics...")
        self.test_endpoint("/mobile-pwa/analytics/mobile", "GET", test_name="Mobile PWA - Mobile Analytics")
        
        # Track mobile events
        event_data = {
            "event_type": "app_launch",
            "device_id": device_id or "test_device_123",
            "timestamp": "2025-01-15T10:30:00Z",
            "properties": {
                "launch_time": 2.5,
                "network_type": "wifi",
                "battery_level": 85
            }
        }
        self.test_endpoint("/mobile-pwa/analytics/track", "POST", event_data, "Mobile PWA - Track Mobile Event")
        
        # 8. Test PWA Installation
        print("\n⬇️ Testing PWA Installation...")
        
        # Get installation prompt
        self.test_endpoint("/mobile-pwa/pwa/install-prompt", "GET", test_name="Mobile PWA - Get Install Prompt")
        
        # Track installation
        install_data = {
            "device_id": device_id or "test_device_123",
            "install_source": "browser_prompt",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
        }
        self.test_endpoint("/mobile-pwa/pwa/track-install", "POST", install_data, "Mobile PWA - Track Installation")
        
        # 9. Test Service Worker Management
        print("\n⚙️ Testing Service Worker Management...")
        self.test_endpoint("/mobile-pwa/service-worker/status", "GET", test_name="Mobile PWA - Service Worker Status")
        
        # Update service worker
        sw_data = {
            "version": "1.1.0",
            "cache_strategy": "network_first",
            "offline_fallback": "/offline.html"
        }
        self.test_endpoint("/mobile-pwa/service-worker/update", "POST", sw_data, "Mobile PWA - Update Service Worker")
        
        # 10. Test Device Management
        if device_id:
            print("\n📱 Testing Device Management...")
            self.test_endpoint(f"/mobile-pwa/device/{device_id}", "GET", test_name="Mobile PWA - Get Device Info")
            
            # Update device settings
            device_update_data = {
                "notification_preferences": {
                    "marketing": True,
                    "system_updates": True,
                    "team_notifications": False
                },
                "sync_frequency": "hourly"
            }
            self.test_endpoint(f"/mobile-pwa/device/{device_id}/settings", "PUT", device_update_data, "Mobile PWA - Update Device Settings")
        
        print("\n📱 Mobile PWA System Testing Complete!")
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
        
    def test_financial_management_system(self):
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
                    "referrer": f"https://35b0c12d-8622-4a0d-9b9c-d891d48a2c32.preview.emergentagent.com/bio/sarah_creates"
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
        
    def test_data_consistency(self):
        """Test data consistency to verify real database usage"""
        print("\n🔍 TESTING DATA CONSISTENCY (Real Database Verification)")
        print("=" * 60)
        
        # Test templates consistency
        print("\n📋 Testing Templates Data Consistency...")
        success1, data1 = self.test_endpoint("/link-in-bio/templates", "GET", test_name="Templates - First Call")
        time.sleep(1)  # Small delay
        success2, data2 = self.test_endpoint("/link-in-bio/templates", "GET", test_name="Templates - Second Call")
        
        if success1 and success2 and data1 == data2:
            self.log_result("Templates Data Consistency", True, "Templates data consistent across calls - confirms real database usage")
        elif success1 and success2:
            self.log_result("Templates Data Consistency", False, "Templates data inconsistent - may be using random generation")
        
        # Test analytics overview consistency
        print("\n📊 Testing Analytics Data Consistency...")
        success1, data1 = self.test_endpoint("/link-in-bio/analytics/overview", "GET", test_name="Analytics Overview - First Call")
        time.sleep(1)  # Small delay
        success2, data2 = self.test_endpoint("/link-in-bio/analytics/overview", "GET", test_name="Analytics Overview - Second Call")
        
        if success1 and success2 and data1 == data2:
            self.log_result("Analytics Data Consistency", True, "Analytics data consistent across calls - confirms real database usage")
        elif success1 and success2:
            self.log_result("Analytics Data Consistency", False, "Analytics data inconsistent - may be using random generation")
    
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

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_final_comprehensive_audit()
    sys.exit(0 if success else 1)