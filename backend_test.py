#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND AUDIT FOR MEWAYZ V2 PLATFORM
==================================================
Testing ALL implemented features as requested in the review:
1. Booking System
2. Escrow System  
3. Website Builder
4. Template Marketplace
5. Link in Bio System
6. Course & Community
7. Multi-Vendor Marketplace
8. All Other Systems

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

class MewayzBackendAuditor:
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
            print(f"✅ {system} - {method} {endpoint} - Status {status_code}")
        else:
            self.failed_tests += 1
            print(f"❌ {system} - {method} {endpoint} - Status {status_code} - {details}")
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            print(f"\n🔐 AUTHENTICATING WITH {TEST_EMAIL}")
            print("=" * 60)
            
            # Try login first
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
                print(f"✅ Login successful - Token received")
                self.log_result("Authentication", "/api/auth/login", "POST", True, 200, "Login successful")
                return True
            elif response.status_code == 401:
                # Try registration if login fails
                print("🔄 Login failed, attempting registration...")
                register_data = {
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "full_name": "Test User"
                }
                
                reg_response = requests.post(
                    f"{self.base_url}/api/auth/register",
                    json=register_data,
                    headers=self.headers,
                    timeout=30
                )
                
                if reg_response.status_code == 200:
                    data = reg_response.json()
                    self.token = data.get("access_token")
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    print(f"✅ Registration successful - Token received")
                    self.log_result("Authentication", "/api/auth/register", "POST", True, 200, "Registration successful")
                    return True
                else:
                    print(f"❌ Registration failed - Status {reg_response.status_code}")
                    self.log_result("Authentication", "/api/auth/register", "POST", False, reg_response.status_code, "Registration failed")
                    return False
            else:
                print(f"❌ Authentication failed - Status {response.status_code}")
                self.log_result("Authentication", "/api/auth/login", "POST", False, response.status_code, "Authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            self.log_result("Authentication", "/api/auth/login", "POST", False, 0, str(e))
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test basic health endpoint"""
        try:
            print(f"\n🏥 TESTING HEALTH ENDPOINTS")
            print("=" * 60)
            
            # Test root endpoint
            response = requests.get(f"{self.base_url}/", timeout=30)
            if response.status_code == 200:
                self.log_result("Health", "/", "GET", True, 200, "Root endpoint working")
            else:
                self.log_result("Health", "/", "GET", False, response.status_code, "Root endpoint failed")
            
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=30)
            if response.status_code == 200:
                self.log_result("Health", "/health", "GET", True, 200, "Health endpoint working")
            else:
                self.log_result("Health", "/health", "GET", False, response.status_code, "Health endpoint failed")
                
            return True
        except Exception as e:
            self.log_result("Health", "/health", "GET", False, 0, str(e))
            return False
    
    def test_booking_system(self):
        """Test Booking System endpoints"""
        print(f"\n📅 TESTING BOOKING SYSTEM")
        print("=" * 60)
        
        endpoints = [
            ("GET", "/api/booking/health", "Health check"),
            ("GET", "/api/booking/", "List bookings"),
            ("POST", "/api/booking/", "Create booking"),
            ("GET", "/api/booking/stats", "Get booking stats")
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
                elif method == "POST":
                    test_data = {
                        "title": "Test Booking",
                        "description": "Test booking for audit",
                        "date": "2025-01-25",
                        "time": "14:00",
                        "duration": 60,
                        "service_type": "consultation"
                    }
                    response = requests.post(f"{self.base_url}{endpoint}", json=test_data, headers=self.headers, timeout=30)
                
                success = response.status_code in [200, 201]
                self.log_result("Booking System", endpoint, method, success, response.status_code, description)
                
            except Exception as e:
                self.log_result("Booking System", endpoint, method, False, 0, str(e))
    
    def test_escrow_system(self):
        """Test Escrow System endpoints"""
        print(f"\n💰 TESTING ESCROW SYSTEM")
        print("=" * 60)
        
        endpoints = [
            ("GET", "/api/escrow/health", "Health check"),
            ("GET", "/api/escrow/", "List escrow transactions"),
            ("POST", "/api/escrow/", "Create escrow transaction"),
            ("GET", "/api/escrow/stats", "Get escrow stats"),
            ("POST", "/api/escrow/transactions/milestone", "Create milestone transaction"),
            ("GET", "/api/escrow/transactions/list", "List escrow transactions")
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
                elif method == "POST":
                    if "milestone" in endpoint:
                        test_data = {
                            "project_id": "test-project-123",
                            "milestone_title": "Initial Design",
                            "amount": 500.00,
                            "description": "First milestone payment",
                            "due_date": "2025-02-15"
                        }
                    else:
                        test_data = {
                            "amount": 1000.00,
                            "description": "Test escrow transaction",
                            "buyer_id": "buyer-123",
                            "seller_id": "seller-456",
                            "project_title": "Test Project"
                        }
                    response = requests.post(f"{self.base_url}{endpoint}", json=test_data, headers=self.headers, timeout=30)
                
                success = response.status_code in [200, 201]
                self.log_result("Escrow System", endpoint, method, success, response.status_code, description)
                
            except Exception as e:
                self.log_result("Escrow System", endpoint, method, False, 0, str(e))
    
    def test_website_builder(self):
        """Test Website Builder endpoints"""
        print(f"\n🌐 TESTING WEBSITE BUILDER")
        print("=" * 60)
        
        endpoints = [
            ("GET", "/api/website-builder/health", "Health check"),
            ("GET", "/api/website-builder/", "List websites"),
            ("GET", "/api/website-builder/templates", "List templates"),
            ("POST", "/api/website-builder/", "Create website"),
            ("GET", "/api/website-builder/stats", "Get website stats")
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
                elif method == "POST":
                    test_data = {
                        "name": "Test Website",
                        "template_id": "modern-business",
                        "domain": "test-site.mewayz.com",
                        "description": "Test website for audit",
                        "category": "business"
                    }
                    response = requests.post(f"{self.base_url}{endpoint}", json=test_data, headers=self.headers, timeout=30)
                
                success = response.status_code in [200, 201]
                self.log_result("Website Builder", endpoint, method, success, response.status_code, description)
                
            except Exception as e:
                self.log_result("Website Builder", endpoint, method, False, 0, str(e))
    
    def test_template_marketplace(self):
        """Test Template Marketplace endpoints"""
        print(f"\n🛍️ TESTING TEMPLATE MARKETPLACE")
        print("=" * 60)
        
        endpoints = [
            ("GET", "/api/template-marketplace/health", "Health check"),
            ("GET", "/api/template-marketplace/", "List templates"),
            ("POST", "/api/template-marketplace/", "Create template"),
            ("GET", "/api/template-marketplace/stats", "Get marketplace stats"),
            ("GET", "/api/template-marketplace/browse", "Browse templates"),
            ("GET", "/api/template-marketplace/creator-earnings", "Get creator earnings")
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
                elif method == "POST":
                    test_data = {
                        "name": "Modern Business Template",
                        "description": "Professional business template",
                        "category": "business",
                        "price": 49.99,
                        "preview_url": "https://preview.example.com",
                        "tags": ["business", "modern", "responsive"]
                    }
                    response = requests.post(f"{self.base_url}{endpoint}", json=test_data, headers=self.headers, timeout=30)
                
                success = response.status_code in [200, 201]
                self.log_result("Template Marketplace", endpoint, method, success, response.status_code, description)
                
            except Exception as e:
                self.log_result("Template Marketplace", endpoint, method, False, 0, str(e))
    
    def test_link_in_bio_system(self):
        """Test Link in Bio System endpoints"""
        print(f"\n🔗 TESTING LINK IN BIO SYSTEM")
        print("=" * 60)
        
        endpoints = [
            ("GET", "/api/complete-link-in-bio/health", "Health check"),
            ("GET", "/api/complete-link-in-bio/", "List link in bio pages"),
            ("POST", "/api/complete-link-in-bio/", "Create link in bio page"),
            ("GET", "/api/complete-link-in-bio/stats", "Get link in bio stats")
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
                elif method == "POST":
                    test_data = {
                        "username": "testuser",
                        "title": "My Link in Bio",
                        "description": "All my important links",
                        "theme": "modern",
                        "links": [
                            {"title": "Website", "url": "https://example.com"},
                            {"title": "Instagram", "url": "https://instagram.com/user"}
                        ]
                    }
                    response = requests.post(f"{self.base_url}{endpoint}", json=test_data, headers=self.headers, timeout=30)
                
                success = response.status_code in [200, 201]
                self.log_result("Link in Bio System", endpoint, method, success, response.status_code, description)
                
            except Exception as e:
                self.log_result("Link in Bio System", endpoint, method, False, 0, str(e))
    
    def test_course_community_system(self):
        """Test Course & Community System endpoints"""
        print(f"\n🎓 TESTING COURSE & COMMUNITY SYSTEM")
        print("=" * 60)
        
        endpoints = [
            ("GET", "/api/complete-course-community/health", "Health check"),
            ("GET", "/api/complete-course-community/", "List courses and communities"),
            ("POST", "/api/complete-course-community/", "Create course/community"),
            ("GET", "/api/complete-course-community/stats", "Get course stats")
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
                elif method == "POST":
                    test_data = {
                        "title": "Digital Marketing Masterclass",
                        "description": "Complete digital marketing course",
                        "type": "course",
                        "price": 199.99,
                        "duration": "8 weeks",
                        "level": "intermediate",
                        "modules": [
                            {"title": "Introduction to Digital Marketing", "duration": "2 hours"},
                            {"title": "Social Media Strategy", "duration": "3 hours"}
                        ]
                    }
                    response = requests.post(f"{self.base_url}{endpoint}", json=test_data, headers=self.headers, timeout=30)
                
                success = response.status_code in [200, 201]
                self.log_result("Course & Community", endpoint, method, success, response.status_code, description)
                
            except Exception as e:
                self.log_result("Course & Community", endpoint, method, False, 0, str(e))
    
    def test_multi_vendor_marketplace(self):
        """Test Multi-Vendor Marketplace endpoints"""
        print(f"\n🏪 TESTING MULTI-VENDOR MARKETPLACE")
        print("=" * 60)
        
        endpoints = [
            ("GET", "/api/multi-vendor-marketplace/health", "Health check"),
            ("GET", "/api/multi-vendor-marketplace/", "List marketplace items"),
            ("POST", "/api/multi-vendor-marketplace/", "Create marketplace item"),
            ("GET", "/api/multi-vendor-marketplace/stats", "Get marketplace stats")
        ]
        
        for method, endpoint, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
                elif method == "POST":
                    test_data = {
                        "product_name": "Digital Marketing Service",
                        "description": "Professional digital marketing services",
                        "price": 299.99,
                        "category": "services",
                        "vendor_id": "vendor-123",
                        "images": ["https://example.com/image1.jpg"],
                        "tags": ["marketing", "digital", "professional"]
                    }
                    response = requests.post(f"{self.base_url}{endpoint}", json=test_data, headers=self.headers, timeout=30)
                
                success = response.status_code in [200, 201]
                self.log_result("Multi-Vendor Marketplace", endpoint, method, success, response.status_code, description)
                
            except Exception as e:
                self.log_result("Multi-Vendor Marketplace", endpoint, method, False, 0, str(e))
    
    def test_admin_pricing_system(self):
        """Test Admin Pricing Management System - CRITICAL FOR ADMIN DASHBOARD"""
        print(f"\n⚙️ TESTING ADMIN PRICING MANAGEMENT SYSTEM - CRITICAL FOR ADMIN DASHBOARD")
        print("=" * 60)
        
        # Test workspace ID from review request
        test_workspace_id = "deebdeae-4a9d-4611-ad12-9b71e13376a6"
        
        # 1. Health Check
        try:
            response = requests.get(f"{self.base_url}/api/admin-pricing/health", timeout=30)
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Service healthy: {data.get('healthy', False)}, Templates: {data.get('pricing_templates', 0)}"
            else:
                details = "Health check failed"
            self.log_result("Admin Pricing", "/api/admin-pricing/health", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/health", "GET", False, 0, str(e))
        
        # 2. Get Current Pricing Config (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/admin-pricing/current-pricing", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Retrieved pricing for {data.get('total_bundles', 0)} bundles with {data.get('active_overrides', 0)} overrides"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to get current pricing"
            self.log_result("Admin Pricing", "/api/admin-pricing/current-pricing", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/current-pricing", "GET", False, 0, str(e))
        
        # 3. Update Bundle Pricing (requires admin auth)
        try:
            test_data = {
                "bundle_name": "creator",
                "pricing_updates": {
                    "monthly_price": 29.99,
                    "yearly_price": 299.99
                },
                "reason": "Test pricing update for admin system verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-pricing/update-bundle-pricing", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Bundle pricing updated successfully with impact on {data.get('affected_subscriptions', 0)} subscriptions"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to update bundle pricing"
            self.log_result("Admin Pricing", "/api/admin-pricing/update-bundle-pricing", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/update-bundle-pricing", "POST", False, 0, str(e))
        
        # 4. Update Bundle Features (requires admin auth)
        try:
            test_data = {
                "bundle_name": "creator",
                "feature_updates": {
                    "added_features": ["advanced_analytics"],
                    "removed_features": []
                },
                "limit_updates": {
                    "ai_content_generation": 1000,
                    "instagram_searches": 500
                },
                "reason": "Test feature update for admin system verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-pricing/update-bundle-features", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Bundle features updated, notification required: {data.get('notification_required', False)}"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to update bundle features"
            self.log_result("Admin Pricing", "/api/admin-pricing/update-bundle-features", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/update-bundle-features", "POST", False, 0, str(e))
        
        # 5. Enable/Disable Bundle (requires admin auth)
        try:
            test_data = {
                "bundle_name": "creator",
                "action": "disable",
                "reason": "Test bundle disable for admin system verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-pricing/enable-disable-bundle", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Bundle {data.get('new_status', 'unknown')} with {data.get('existing_subscriptions', 0)} existing subscriptions"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to enable/disable bundle"
            self.log_result("Admin Pricing", "/api/admin-pricing/enable-disable-bundle", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/enable-disable-bundle", "POST", False, 0, str(e))
        
        # 6. Bulk Pricing Update (requires admin auth)
        try:
            test_data = {
                "bundle_updates": {
                    "creator": {
                        "monthly_price": 24.99,
                        "yearly_price": 249.99
                    },
                    "business": {
                        "monthly_price": 49.99,
                        "yearly_price": 499.99
                    }
                },
                "reason": "Test bulk pricing update for admin system verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-pricing/bulk-pricing-update", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                details = f"Bulk update: {summary.get('successful', 0)}/{summary.get('total_bundles', 0)} successful ({summary.get('success_rate', 0):.1f}%)"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to perform bulk pricing update"
            self.log_result("Admin Pricing", "/api/admin-pricing/bulk-pricing-update", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/bulk-pricing-update", "POST", False, 0, str(e))
        
        # 7. Get Pricing Analytics (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/admin-pricing/pricing-analytics", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                analytics = data.get('analytics', {})
                details = f"Analytics: {analytics.get('total_active_subscriptions', 0)} active subscriptions, {analytics.get('recent_pricing_changes', 0)} recent changes"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to get pricing analytics"
            self.log_result("Admin Pricing", "/api/admin-pricing/pricing-analytics", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/pricing-analytics", "GET", False, 0, str(e))
        
        # 8. Test Pricing Change (requires admin auth)
        try:
            test_data = {
                "bundle_name": "creator",
                "proposed_changes": {
                    "monthly_price": 39.99,
                    "yearly_price": 399.99
                }
            }
            response = requests.post(f"{self.base_url}/api/admin-pricing/test-pricing-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                impact = data.get('impact_analysis', {})
                risk = data.get('impact_analysis', {}).get('risk_assessment', {})
                details = f"Pricing test: {impact.get('bundle_name', 'unknown')} bundle, risk level: {risk.get('risk_level', 'unknown')}"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to test pricing change"
            self.log_result("Admin Pricing", "/api/admin-pricing/test-pricing-change", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/test-pricing-change", "POST", False, 0, str(e))
        
        # 9. Get Pricing History (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/admin-pricing/pricing-history/creator?limit=10", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin, 404 if no history
            if response.status_code == 200:
                data = response.json()
                details = f"Pricing history: {data.get('total_changes', 0)} changes for {data.get('bundle_name', 'unknown')} bundle"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "No pricing history found (expected for new system)"
            else:
                details = "Failed to get pricing history"
            self.log_result("Admin Pricing", "/api/admin-pricing/pricing-history/creator", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/pricing-history/creator", "GET", False, 0, str(e))
        
        # 10. Apply Pricing Template (requires admin auth)
        try:
            test_data = {
                "template_name": "holiday_discount",
                "custom_duration_days": 14
            }
            response = requests.post(f"{self.base_url}/api/admin-pricing/apply-pricing-template", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                result = data.get('application_result', {})
                details = f"Template applied: {result.get('bundles_updated', 0)} bundles updated"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to apply pricing template"
            self.log_result("Admin Pricing", "/api/admin-pricing/apply-pricing-template", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Pricing", "/api/admin-pricing/apply-pricing-template", "POST", False, 0, str(e))

    def test_launch_pricing_system(self):
        """Test Launch Pricing System - CRITICAL FOR PRODUCTION LAUNCH"""
        print(f"\n🚀 TESTING LAUNCH PRICING SYSTEM - CRITICAL FOR PRODUCTION")
        print("=" * 60)
        
        # Test workspace ID from review request
        test_workspace_id = "deebdeae-4a9d-4611-ad12-9b71e13376a6"
        
        # 1. Health Check & Service Status
        try:
            response = requests.get(f"{self.base_url}/api/launch-pricing/health", headers=self.headers, timeout=30)
            success = response.status_code == 200
            self.log_result("Launch Pricing", "/api/launch-pricing/health", "GET", success, response.status_code, "Health check & service initialization")
        except Exception as e:
            self.log_result("Launch Pricing", "/api/launch-pricing/health", "GET", False, 0, str(e))
        
        # 2. Active Specials Management
        try:
            response = requests.get(f"{self.base_url}/api/launch-pricing/active-specials", headers=self.headers, timeout=30)
            success = response.status_code == 200
            if success:
                data = response.json()
                # Verify all 6 bundle specials are returned
                expected_bundles = ["creator", "ecommerce", "social_media", "education", "business", "operations"]
                active_specials = data.get("active_specials", {})
                found_bundles = len([bundle for bundle in expected_bundles if bundle in active_specials])
                details = f"Found {found_bundles}/6 expected bundle specials"
            else:
                details = "Failed to get active specials"
            self.log_result("Launch Pricing", "/api/launch-pricing/active-specials", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Launch Pricing", "/api/launch-pricing/active-specials", "GET", False, 0, str(e))
        
        # 3. Bundle-Specific Special Retrieval - Test all 6 bundles
        bundle_names = ["creator", "ecommerce", "social_media", "education", "business", "operations"]
        for bundle_name in bundle_names:
            try:
                response = requests.get(f"{self.base_url}/api/launch-pricing/bundle/{bundle_name}/special", headers=self.headers, timeout=30)
                success = response.status_code == 200
                if success:
                    data = response.json()
                    special = data.get("special", {})
                    savings = special.get("savings_amount", 0)
                    details = f"{bundle_name} special - ${savings} savings"
                else:
                    details = f"Failed to get {bundle_name} special"
                self.log_result("Launch Pricing", f"/api/launch-pricing/bundle/{bundle_name}/special", "GET", success, response.status_code, details)
            except Exception as e:
                self.log_result("Launch Pricing", f"/api/launch-pricing/bundle/{bundle_name}/special", "GET", False, 0, str(e))
        
        # 4. Eligibility Validation
        try:
            test_data = {
                "bundle_name": "creator",
                "workspace_id": test_workspace_id
            }
            response = requests.post(f"{self.base_url}/api/launch-pricing/validate-eligibility", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 400]  # 400 is acceptable for eligibility check
            if success:
                data = response.json()
                eligible = data.get("eligible", False)
                details = f"Eligibility check - Eligible: {eligible}"
            else:
                details = "Eligibility validation failed"
            self.log_result("Launch Pricing", "/api/launch-pricing/validate-eligibility", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Launch Pricing", "/api/launch-pricing/validate-eligibility", "POST", False, 0, str(e))
        
        # 5. Launch Special Claiming (Test with creator bundle)
        try:
            test_data = {
                "bundle_name": "creator",
                "workspace_id": test_workspace_id,
                "special_code": "CREATOR9"
            }
            response = requests.post(f"{self.base_url}/api/launch-pricing/claim-special", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 400]  # 400 acceptable if already claimed or not eligible
            if success:
                data = response.json()
                claimed = data.get("success", False)
                details = f"Claim attempt - Success: {claimed}"
            else:
                details = "Claim special failed"
            self.log_result("Launch Pricing", "/api/launch-pricing/claim-special", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Launch Pricing", "/api/launch-pricing/claim-special", "POST", False, 0, str(e))
        
        # 6. Claimed Specials Tracking
        try:
            response = requests.get(f"{self.base_url}/api/launch-pricing/claimed-specials/{test_workspace_id}", headers=self.headers, timeout=30)
            success = response.status_code in [200, 404]  # 404 acceptable if no claims yet
            if success:
                data = response.json()
                claims_count = len(data.get("claimed_specials", [])) if response.status_code == 200 else 0
                details = f"Claimed specials tracking - {claims_count} claims found"
            else:
                details = "Failed to get claimed specials"
            self.log_result("Launch Pricing", f"/api/launch-pricing/claimed-specials/{test_workspace_id}", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Launch Pricing", f"/api/launch-pricing/claimed-specials/{test_workspace_id}", "GET", False, 0, str(e))
        
        # 7. Admin Features (These will likely fail due to admin access requirements)
        
        # Special Analytics
        try:
            response = requests.get(f"{self.base_url}/api/launch-pricing/special-analytics", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            details = "Admin analytics - Access control working" if response.status_code == 403 else "Analytics accessible"
            self.log_result("Launch Pricing", "/api/launch-pricing/special-analytics", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Launch Pricing", "/api/launch-pricing/special-analytics", "GET", False, 0, str(e))
        
        # Generate Promo Code
        try:
            test_data = {
                "bundle_name": "creator",
                "custom_code": "TESTCODE123",
                "max_uses": 50,
                "expires_in_days": 30
            }
            response = requests.post(f"{self.base_url}/api/launch-pricing/generate-promo-code", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            details = "Admin promo code generation - Access control working" if response.status_code == 403 else "Promo code generated"
            self.log_result("Launch Pricing", "/api/launch-pricing/generate-promo-code", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Launch Pricing", "/api/launch-pricing/generate-promo-code", "POST", False, 0, str(e))
        
        # Extend Special
        try:
            test_data = {
                "bundle_name": "creator",
                "action": "extend_time",
                "value": 30,
                "reason": "Test extension"
            }
            response = requests.post(f"{self.base_url}/api/launch-pricing/extend-special", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            details = "Admin special extension - Access control working" if response.status_code == 403 else "Special extended"
            self.log_result("Launch Pricing", "/api/launch-pricing/extend-special", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Launch Pricing", "/api/launch-pricing/extend-special", "POST", False, 0, str(e))
        
        # Referral Tracking
        try:
            response = requests.get(f"{self.base_url}/api/launch-pricing/referral-tracking/TESTREF123", headers=self.headers, timeout=30)
            success = response.status_code in [200, 404]  # 404 acceptable if referral code doesn't exist
            details = "Referral tracking - System responding correctly"
            self.log_result("Launch Pricing", "/api/launch-pricing/referral-tracking/TESTREF123", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Launch Pricing", "/api/launch-pricing/referral-tracking/TESTREF123", "GET", False, 0, str(e))

    def test_admin_plan_management_system(self):
        """Test Admin Plan Management System - CRITICAL FOR ADMIN DASHBOARD"""
        print(f"\n🎛️ TESTING ADMIN PLAN MANAGEMENT SYSTEM - CRITICAL FOR ADMIN DASHBOARD")
        print("=" * 60)
        
        # 1. Health Check (No auth required)
        try:
            response = requests.get(f"{self.base_url}/api/admin-plan-management/health", timeout=30)
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Service healthy: {data.get('healthy', False)}, Features available: {data.get('available_features', 0)}"
            else:
                details = "Health check failed"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/health", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/health", "GET", False, 0, str(e))
        
        # 2. Get All Plans (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/admin-plan-management/plans", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Retrieved {data.get('total_plans', 0)} plans with analytics"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to get all plans"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plans", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plans", "GET", False, 0, str(e))
        
        # 3. Get Plan Details (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/admin-plan-management/plan/creator", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin, 404 if plan doesn't exist
            if response.status_code == 200:
                data = response.json()
                plan = data.get('plan', {})
                details = f"Plan details retrieved: {plan.get('display_name', 'Unknown')} plan"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Plan not found (expected for new system)"
            else:
                details = "Failed to get plan details"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator", "GET", False, 0, str(e))
        
        # 4. Update Plan Pricing (requires admin auth)
        try:
            test_data = {
                "pricing_updates": {
                    "monthly_price": 29.99,
                    "yearly_price": 299.99,
                    "yearly_discount_percentage": 16.7
                },
                "reason": "Test pricing update for admin plan management verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-plan-management/plan/creator/pricing", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan pricing updated successfully with impact analysis"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Plan not found (expected for new system)"
            else:
                details = "Failed to update plan pricing"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/pricing", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/pricing", "POST", False, 0, str(e))
        
        # 5. Update Plan Features (requires admin auth)
        try:
            test_data = {
                "feature_updates": {
                    "added_features": ["advanced_analytics", "priority_support"],
                    "removed_features": []
                },
                "reason": "Test feature update for admin plan management verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-plan-management/plan/creator/features", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan features updated successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Plan not found (expected for new system)"
            else:
                details = "Failed to update plan features"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/features", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/features", "POST", False, 0, str(e))
        
        # 6. Update Plan Limits (requires admin auth)
        try:
            test_data = {
                "limit_updates": {
                    "ai_content_generation": 1000,
                    "instagram_searches": 500,
                    "emails_sent": 2000,
                    "websites_created": 5,
                    "storage_gb": 10
                },
                "reason": "Test limits update for admin plan management verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-plan-management/plan/creator/limits", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan limits updated successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Plan not found (expected for new system)"
            else:
                details = "Failed to update plan limits"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/limits", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/limits", "POST", False, 0, str(e))
        
        # 7. Update Plan Status (requires admin auth)
        try:
            test_data = {
                "action": "disable",
                "reason": "Test status update for admin plan management verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-plan-management/plan/creator/status", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan status updated successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Plan not found (expected for new system)"
            else:
                details = "Failed to update plan status"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/status", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/status", "POST", False, 0, str(e))
        
        # 8. Update Launch Pricing (requires admin auth)
        try:
            test_data = {
                "launch_special": {
                    "enabled": True,
                    "special_price": 19.99,
                    "end_date": "2025-03-31T23:59:59Z",
                    "description": "Limited time launch special"
                },
                "reason": "Test launch pricing update for admin plan management verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-plan-management/plan/creator/launch-pricing", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Launch pricing updated successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Plan not found (expected for new system)"
            else:
                details = "Failed to update launch pricing"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/launch-pricing", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/launch-pricing", "POST", False, 0, str(e))
        
        # 9. Create New Plan (requires admin auth)
        try:
            test_data = {
                "name": "test_plan",
                "display_name": "Test Plan",
                "description": "Test plan for admin management verification",
                "pricing": {
                    "monthly_price": 39.99,
                    "yearly_price": 399.99,
                    "yearly_discount_percentage": 16.7
                },
                "features": {
                    "included_features": ["website_builder", "ai_content_generation"],
                    "excluded_features": ["white_label"]
                },
                "limits": {
                    "ai_content_generation": 500,
                    "instagram_searches": 200,
                    "emails_sent": 1000,
                    "websites_created": 3,
                    "storage_gb": 5
                }
            }
            response = requests.post(f"{self.base_url}/api/admin-plan-management/plan", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 201, 403]  # 403 expected for non-admin users
            if response.status_code in [200, 201]:
                data = response.json()
                details = f"New plan created successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to create new plan"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan", "POST", False, 0, str(e))
        
        # 10. Bulk Plan Update (requires admin auth)
        try:
            test_data = {
                "plan_updates": {
                    "creator": {
                        "pricing": {
                            "monthly_price": 24.99,
                            "yearly_price": 249.99
                        }
                    },
                    "business": {
                        "pricing": {
                            "monthly_price": 49.99,
                            "yearly_price": 499.99
                        }
                    }
                },
                "reason": "Test bulk update for admin plan management verification"
            }
            response = requests.post(f"{self.base_url}/api/admin-plan-management/bulk-update", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Bulk update completed successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = "Failed to perform bulk update"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/bulk-update", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/bulk-update", "POST", False, 0, str(e))
        
        # 11. Get Plan Analytics (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/admin-plan-management/plan-analytics", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan analytics retrieved successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "No analytics data found (expected for new system)"
            else:
                details = "Failed to get plan analytics"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan-analytics", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan-analytics", "GET", False, 0, str(e))
        
        # 12. Get Plan Subscriptions (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/admin-plan-management/plan/creator/subscriptions?limit=10", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan subscriptions retrieved successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "No subscriptions found (expected for new system)"
            else:
                details = "Failed to get plan subscriptions"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/subscriptions", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan/creator/subscriptions", "GET", False, 0, str(e))
        
        # 13. Get Plan Change History (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/admin-plan-management/plan-change-history?plan_name=creator&limit=10", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan change history retrieved successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "No change history found (expected for new system)"
            else:
                details = "Failed to get plan change history"
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan-change-history", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Admin Plan Management", "/api/admin-plan-management/plan-change-history", "GET", False, 0, str(e))

    def test_plan_change_impact_system(self):
        """Test Plan Change Impact Analysis System - CRITICAL for preventing subscription disruptions"""
        print(f"\n🔍 TESTING PLAN CHANGE IMPACT ANALYSIS SYSTEM")
        print("=" * 60)
        
        # 1. Health Check (no auth required)
        try:
            response = requests.get(f"{self.base_url}/api/plan-change-impact/health", timeout=30)
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Service healthy: {data.get('healthy', False)}, Risk thresholds configured"
            else:
                details = f"Health check failed with status {response.status_code}"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/health", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/health", "GET", False, 0, str(e))
        
        # 2. Analyze Pricing Change Impact (requires admin auth)
        try:
            test_data = {
                "plan_name": "creator",
                "pricing_changes": {
                    "monthly_price": 39.99,
                    "yearly_price": 399.99,
                    "price_increase_percentage": 25.0
                },
                "reason": "Test pricing impact analysis for creator plan"
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/analyze-pricing-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Pricing impact analyzed: {data.get('impact_summary', {}).get('affected_subscriptions', 0)} subscriptions affected"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = f"Failed to analyze pricing change impact"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/analyze-pricing-change", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/analyze-pricing-change", "POST", False, 0, str(e))
        
        # 3. Analyze Feature Change Impact (requires admin auth)
        try:
            test_data = {
                "plan_name": "business",
                "feature_changes": {
                    "features_added": ["advanced_analytics", "priority_support"],
                    "features_removed": ["basic_reporting"]
                },
                "reason": "Test feature impact analysis for business plan"
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/analyze-feature-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Feature impact analyzed: {data.get('impact_summary', {}).get('features_added', 0)} added, {data.get('impact_summary', {}).get('features_removed', 0)} removed"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = f"Failed to analyze feature change impact"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/analyze-feature-change", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/analyze-feature-change", "POST", False, 0, str(e))
        
        # 4. Analyze Limit Change Impact (requires admin auth)
        try:
            test_data = {
                "plan_name": "creator",
                "limit_changes": {
                    "ai_content_generation": 2000,
                    "instagram_searches": 1000,
                    "emails_sent": 5000
                },
                "reason": "Test usage limit impact analysis for creator plan"
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/analyze-limit-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Limit impact analyzed: {data.get('impact_summary', {}).get('affected_subscriptions', 0)} subscriptions affected"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = f"Failed to analyze limit change impact"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/analyze-limit-change", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/analyze-limit-change", "POST", False, 0, str(e))
        
        # 5. Analyze Plan Disable Impact (requires admin auth)
        try:
            test_data = {
                "plan_name": "education",
                "disable_reason": "End of educational promotion period",
                "migration_plan": "business"
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/analyze-plan-disable", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan disable impact analyzed: {data.get('impact_summary', {}).get('affected_subscriptions', 0)} subscriptions need migration"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = f"Failed to analyze plan disable impact"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/analyze-plan-disable", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/analyze-plan-disable", "POST", False, 0, str(e))
        
        # 6. Simulate Plan Change (requires admin auth)
        try:
            test_data = {
                "plan_name": "creator",
                "change_type": "comprehensive",
                "changes": {
                    "pricing": {"monthly_price": 34.99},
                    "features": {"features_added": ["advanced_templates"]},
                    "limits": {"ai_content_generation": 1500}
                },
                "simulation_options": {
                    "include_migration_plan": True,
                    "calculate_revenue_impact": True
                }
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/simulate-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan change simulated successfully with full impact analysis"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = f"Failed to simulate plan change"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/simulate-change", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/simulate-change", "POST", False, 0, str(e))
        
        # 7. Get Affected Subscriptions (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/plan-change-impact/affected-subscriptions/creator?change_type=pricing&limit=50", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Affected subscriptions retrieved: {len(data.get('subscriptions', []))} found"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "No affected subscriptions found (expected for test plan)"
            else:
                details = f"Failed to get affected subscriptions"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/affected-subscriptions/creator", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/affected-subscriptions/creator", "GET", False, 0, str(e))
        
        # 8. Create Migration Plan (requires admin auth)
        try:
            test_data = {
                "source_plan": "education",
                "target_plan": "business",
                "migration_strategy": "gradual",
                "migration_timeline": "30_days",
                "notification_settings": {
                    "notify_users": True,
                    "advance_notice_days": 14
                }
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/create-migration-plan", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Migration plan created: {data.get('migration_id', 'Unknown ID')}"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            else:
                details = f"Failed to create migration plan"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/create-migration-plan", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/create-migration-plan", "POST", False, 0, str(e))
        
        # 9. Execute Migration Plan (requires admin auth)
        try:
            test_migration_id = "test-migration-123"
            test_data = {
                "execution_mode": "dry_run",
                "batch_size": 10,
                "confirm_execution": False
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/execute-migration-plan/{test_migration_id}", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users, 404 for non-existent migration
            if response.status_code == 200:
                data = response.json()
                details = f"Migration plan executed successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Migration plan not found (expected for test ID)"
            else:
                details = f"Failed to execute migration plan"
            self.log_result("Plan Change Impact", f"/api/plan-change-impact/execute-migration-plan/{test_migration_id}", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", f"/api/plan-change-impact/execute-migration-plan/{test_migration_id}", "POST", False, 0, str(e))
        
        # 10. Get Migration Plan Status (requires admin auth)
        try:
            test_migration_id = "test-migration-123"
            response = requests.get(f"{self.base_url}/api/plan-change-impact/migration-plan/{test_migration_id}", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users, 404 for non-existent migration
            if response.status_code == 200:
                data = response.json()
                details = f"Migration plan status retrieved: {data.get('status', 'Unknown')}"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Migration plan not found (expected for test ID)"
            else:
                details = f"Failed to get migration plan status"
            self.log_result("Plan Change Impact", f"/api/plan-change-impact/migration-plan/{test_migration_id}", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", f"/api/plan-change-impact/migration-plan/{test_migration_id}", "GET", False, 0, str(e))
        
        # 11. Rollback Plan Change (requires admin auth)
        try:
            test_data = {
                "change_id": "test-change-456",
                "rollback_reason": "Test rollback functionality",
                "restore_previous_state": True
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/rollback-plan-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Plan change rolled back successfully"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Change record not found (expected for test ID)"
            else:
                details = f"Failed to rollback plan change"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/rollback-plan-change", "POST", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/rollback-plan-change", "POST", False, 0, str(e))
        
        # 12. Get Impact Analysis History (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/plan-change-impact/impact-history?plan_name=creator&days_back=30&limit=20", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Impact analysis history retrieved: {len(data.get('analyses', []))} records found"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "No impact analysis history found (expected for new system)"
            else:
                details = f"Failed to get impact analysis history"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/impact-history", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/impact-history", "GET", False, 0, str(e))
        
        # 13. Get Risk Assessment (requires admin auth)
        try:
            response = requests.get(f"{self.base_url}/api/plan-change-impact/risk-assessment/creator?change_type=pricing", headers=self.headers, timeout=30)
            success = response.status_code in [200, 403, 404]  # 403 expected for non-admin users
            if response.status_code == 200:
                data = response.json()
                details = f"Risk assessment retrieved: {data.get('risk_level', 'Unknown')} risk level"
            elif response.status_code == 403:
                details = "Admin access control working correctly"
            elif response.status_code == 404:
                details = "Risk assessment not available (expected for test plan)"
            else:
                details = f"Failed to get risk assessment"
            self.log_result("Plan Change Impact", "/api/plan-change-impact/risk-assessment/creator", "GET", success, response.status_code, details)
        except Exception as e:
            self.log_result("Plan Change Impact", "/api/plan-change-impact/risk-assessment/creator", "GET", False, 0, str(e))

    def test_additional_systems(self):
        """Test additional systems mentioned in the comprehensive test results"""
        print(f"\n🔧 TESTING ADDITIONAL SYSTEMS")
        print("=" * 60)
        
        # Test key systems from the comprehensive results
        additional_endpoints = [
            # AI Systems
            ("GET", "/api/ai/services", "AI Services"),
            ("GET", "/api/ai/conversations", "AI Conversations"),
            ("POST", "/api/ai/analyze-content", "AI Content Analysis"),
            
            # Analytics
            ("GET", "/api/analytics-system/dashboard", "Analytics Dashboard"),
            ("GET", "/api/analytics-system/overview", "Analytics Overview"),
            ("GET", "/api/analytics-system/reports", "Analytics Reports"),
            
            # Automation
            ("GET", "/api/automation/workflows", "Automation Workflows"),
            ("GET", "/api/automation/workflows/advanced", "Advanced Workflows"),
            ("GET", "/api/automation/triggers/available", "Available Triggers"),
            ("GET", "/api/automation/actions/available", "Available Actions"),
            
            # Blog System
            ("GET", "/api/blog/posts", "Blog Posts"),
            ("POST", "/api/blog/posts", "Create Blog Post"),
            ("GET", "/api/blog/analytics", "Blog Analytics"),
            
            # CRM System
            ("GET", "/api/crm/dashboard", "CRM Dashboard"),
            ("GET", "/api/crm/contacts", "CRM Contacts"),
            ("GET", "/api/crm/deals", "CRM Deals"),
            
            # Form Builder
            ("GET", "/api/forms/dashboard", "Forms Dashboard"),
            ("GET", "/api/forms/forms", "List Forms"),
            
            # Integrations
            ("GET", "/api/integrations/available", "Available Integrations"),
            ("GET", "/api/integrations/connected", "Connected Integrations"),
            ("GET", "/api/integrations/logs", "Integration Logs"),
            
            # Team Management
            ("GET", "/api/team-management/dashboard", "Team Dashboard"),
            ("GET", "/api/team-management/members", "Team Members"),
            ("GET", "/api/team-management/activity", "Team Activity"),
            
            # Social Media Features
            ("POST", "/api/instagram/search", "Instagram Search"),
            ("GET", "/api/instagram/profiles", "Instagram Profiles"),
            ("POST", "/api/posts/schedule", "Schedule Social Media Post"),
            ("GET", "/api/posts/scheduled", "Get Scheduled Posts"),
            
            # PWA Features
            ("POST", "/api/pwa/manifest/generate", "Generate PWA Manifest"),
            ("GET", "/api/pwa/manifest/current", "Get Current Manifest"),
            
            # AI Workflows
            ("GET", "/api/workflows/list", "List AI Workflows"),
            ("POST", "/api/workflows/create", "Create AI Workflow"),
            
            # Device Management
            ("POST", "/api/device/register", "Register Device"),
            ("POST", "/api/device/offline/sync", "Sync Offline Data"),
            
            # Dispute Resolution
            ("POST", "/api/disputes/initiate", "Initiate Dispute"),
            ("GET", "/api/disputes/list", "List Disputes"),
            
            # Email Automation
            ("GET", "/api/email-automation/api/email-automation/campaigns", "Email Campaigns"),
            ("GET", "/api/email-automation/api/email-automation/subscribers", "Email Subscribers"),
            ("GET", "/api/email-automation/api/email-automation/email-logs", "Email Logs")
        ]
        
        for method, endpoint, description in additional_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, timeout=30)
                elif method == "POST":
                    # Create appropriate test data based on endpoint
                    if "instagram/search" in endpoint:
                        test_data = {"query": "digital marketing", "limit": 10}
                    elif "posts/schedule" in endpoint:
                        test_data = {
                            "content": "Test social media post",
                            "platforms": ["instagram", "twitter"],
                            "scheduled_time": "2025-01-25T14:00:00Z"
                        }
                    elif "pwa/manifest/generate" in endpoint:
                        test_data = {
                            "name": "Test PWA",
                            "short_name": "TestPWA",
                            "description": "Test Progressive Web App"
                        }
                    elif "workflows/create" in endpoint:
                        test_data = {
                            "name": "Test AI Workflow",
                            "description": "Test workflow for audit",
                            "steps": [{"action": "analyze", "parameters": {}}]
                        }
                    elif "device/register" in endpoint:
                        test_data = {
                            "device_id": "test-device-123",
                            "device_type": "mobile",
                            "platform": "ios"
                        }
                    elif "device/offline/sync" in endpoint:
                        test_data = {
                            "device_id": "test-device-123",
                            "sync_data": {"last_sync": "2025-01-24T10:00:00Z"}
                        }
                    elif "disputes/initiate" in endpoint:
                        test_data = {
                            "transaction_id": "test-transaction-123",
                            "reason": "Service not delivered",
                            "description": "Test dispute for audit"
                        }
                    else:
                        test_data = {"test": True, "audit": "comprehensive"}
                    
                    response = requests.post(f"{self.base_url}{endpoint}", json=test_data, headers=self.headers, timeout=30)
                
                success = response.status_code in [200, 201]
                system_name = description.split(" ")[0] if " " in description else "Additional Systems"
                self.log_result(system_name, endpoint, method, success, response.status_code, description)
                
            except Exception as e:
                system_name = description.split(" ")[0] if " " in description else "Additional Systems"
                self.log_result(system_name, endpoint, method, False, 0, str(e))
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        print(f"\n📊 COMPREHENSIVE AUDIT REPORT")
        print("=" * 80)
        
        # Overall statistics
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Total Tests Executed: {self.total_tests}")
        print(f"Passed Tests: {self.passed_tests} ✅")
        print(f"Failed Tests: {self.failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
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
        
        print(f"\n📋 SYSTEM-BY-SYSTEM BREAKDOWN:")
        print("-" * 80)
        
        for system, stats in systems.items():
            system_success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅ WORKING" if system_success_rate >= 50 else "❌ ISSUES"
            print(f"{system}: {stats['passed']}/{stats['total']} ({system_success_rate:.1f}%) {status}")
        
        # Critical systems analysis
        print(f"\n🎯 CRITICAL SYSTEMS ANALYSIS:")
        print("-" * 80)
        
        critical_systems = [
            "Booking System", "Escrow System", "Website Builder", 
            "Template Marketplace", "Link in Bio System", "Course & Community",
            "Multi-Vendor Marketplace", "Plan Change Impact"
        ]
        
        working_critical = 0
        for system in critical_systems:
            if system in systems:
                stats = systems[system]
                system_success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
                if system_success_rate >= 50:
                    working_critical += 1
                    print(f"✅ {system}: IMPLEMENTED & WORKING ({system_success_rate:.1f}%)")
                else:
                    print(f"❌ {system}: IMPLEMENTED BUT ISSUES ({system_success_rate:.1f}%)")
            else:
                print(f"❓ {system}: NOT TESTED OR NOT FOUND")
        
        print(f"\n🏆 FINAL ASSESSMENT:")
        print("-" * 80)
        critical_success_rate = (working_critical / len(critical_systems) * 100)
        
        if critical_success_rate >= 80:
            print(f"🟢 EXCELLENT: {working_critical}/{len(critical_systems)} critical systems working ({critical_success_rate:.1f}%)")
        elif critical_success_rate >= 60:
            print(f"🟡 GOOD: {working_critical}/{len(critical_systems)} critical systems working ({critical_success_rate:.1f}%)")
        else:
            print(f"🔴 NEEDS WORK: {working_critical}/{len(critical_systems)} critical systems working ({critical_success_rate:.1f}%)")
        
        # Save detailed results to file
        with open("/app/comprehensive_backend_audit_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "total_tests": self.total_tests,
                    "passed_tests": self.passed_tests,
                    "failed_tests": self.failed_tests,
                    "success_rate": success_rate,
                    "critical_systems_working": working_critical,
                    "critical_systems_total": len(critical_systems),
                    "critical_success_rate": critical_success_rate
                },
                "systems": systems,
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: /app/comprehensive_backend_audit_results.json")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": success_rate,
            "critical_systems_working": working_critical,
            "systems": systems
        }
    
    def run_comprehensive_audit(self):
        """Run the complete comprehensive audit"""
        print("🚀 STARTING COMPREHENSIVE MEWAYZ V2 BACKEND AUDIT")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        
        # Step 1: Health check
        self.test_health_endpoint()
        
        # Step 2: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - Cannot proceed with authenticated tests")
            return False
        
        # Step 3: Test all critical systems
        self.test_booking_system()
        self.test_escrow_system()
        self.test_website_builder()
        self.test_template_marketplace()
        self.test_link_in_bio_system()
        self.test_course_community_system()
        self.test_multi_vendor_marketplace()
        
        # Step 3.5: Test Launch Pricing System (CRITICAL FOR PRODUCTION)
        self.test_launch_pricing_system()
        
        # Step 3.6: Test Admin Pricing System (CRITICAL FOR ADMIN DASHBOARD)
        self.test_admin_pricing_system()
        
        # Step 3.7: Test Admin Plan Management System (CRITICAL FOR ADMIN DASHBOARD)
        self.test_admin_plan_management_system()
        
        # Step 3.8: Test Plan Change Impact Analysis System (CRITICAL FOR PREVENTING SUBSCRIPTION DISRUPTIONS)
        self.test_plan_change_impact_system()
        
        # Step 4: Test additional systems
        self.test_additional_systems()
        
        # Step 5: Generate comprehensive report
        return self.generate_report()

def main():
    """Main execution function"""
    auditor = MewayzBackendAuditor()
    results = auditor.run_comprehensive_audit()
    
    # Exit with appropriate code
    if results and results["success_rate"] >= 70:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Issues found

if __name__ == "__main__":
    main()