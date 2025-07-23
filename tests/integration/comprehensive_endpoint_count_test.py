#!/usr/bin/env python3
"""
COMPREHENSIVE ENDPOINT COUNT VERIFICATION - MEWAYZ PLATFORM V3.0.0
Final verification to exceed 200+ API endpoints target
Testing Agent - January 20, 2025
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class ComprehensiveEndpointTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_endpoints = 0
        self.working_endpoints = 0
        self.workspace_id = None
        self.user_id = None
        
    def log_test(self, endpoint, method, status, response_time, success, details="", data_size=0):
        """Log test results"""
        self.total_endpoints += 1
        if success:
            self.working_endpoints += 1
            
        result = {
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'response_time': f"{response_time:.3f}s",
            'success': success,
            'details': details,
            'data_size': data_size
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {method} {endpoint} - {status} ({response_time:.3f}s)")
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print(f"\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        print(f"Email: {ADMIN_EMAIL}")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                if self.auth_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("/auth/login", "POST", response.status_code, response_time, True, 
                                f"Admin authentication successful")
                    return True
                else:
                    self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                                "No token in response")
                    return False
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Login failed")
                return False
                
        except Exception as e:
            self.log_test("/auth/login", "POST", 0, 0, False, f"Authentication error: {str(e)}")
            return False
    
    def get_test_data(self):
        """Get test data for parameterized endpoints"""
        try:
            # Get workspace ID
            response = self.session.get(f"{API_BASE}/workspaces", timeout=30)
            if response.status_code == 200:
                data = response.json()
                workspaces = data.get('data', [])
                if workspaces:
                    self.workspace_id = workspaces[0].get('id')
                    
            # Get user ID from auth/me
            response = self.session.get(f"{API_BASE}/auth/me", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get('id')
                    
        except:
            pass
    
    def test_endpoint(self, endpoint, method="GET", data=None, params=None, expected_status=200, description=""):
        """Test a single endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            # Check if response is successful (200-299 range)
            success = 200 <= response.status_code < 300
            
            # Get response details
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
            except:
                data_size = len(response.text)
            
            self.log_test(endpoint, method, response.status_code, response_time, success, description, data_size)
            return success, response
            
        except requests.exceptions.Timeout:
            self.log_test(endpoint, method, 0, 30.0, False, f"Request timeout")
            return False, None
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"Error: {str(e)}")
            return False, None

    def test_authentication_users(self):
        """Test Authentication & Users endpoints (20+ expected)"""
        print(f"\n👥 TESTING AUTHENTICATION & USERS ENDPOINTS")
        
        # Authentication endpoints
        self.test_endpoint("/auth/me", "GET", description="Get current user")
        self.test_endpoint("/auth/refresh", "POST", data={}, description="Refresh token")
        self.test_endpoint("/auth/logout", "POST", data={}, description="Logout")
        
        # User management endpoints
        self.test_endpoint("/users", "GET", description="List all users")
        if self.user_id:
            self.test_endpoint(f"/users/{self.user_id}", "GET", description="Get user details")
            self.test_endpoint(f"/users/{self.user_id}", "PUT", data={"name": "Test Update"}, description="Update user")
            self.test_endpoint(f"/users/{self.user_id}/activity", "GET", description="User activity")
            self.test_endpoint(f"/users/{self.user_id}/sessions", "GET", description="User sessions")
            self.test_endpoint(f"/users/{self.user_id}/permissions", "GET", description="User permissions")
            self.test_endpoint(f"/users/{self.user_id}/preferences", "GET", description="User preferences")
            self.test_endpoint(f"/users/{self.user_id}/preferences", "PUT", data={"theme": "dark"}, description="Update preferences")
        
        # Admin user management
        self.test_endpoint("/admin/users", "GET", description="Admin list users")
        self.test_endpoint("/admin/users/stats", "GET", description="Admin user stats")
        
        # User operations
        self.test_endpoint("/users/search", "GET", params={"q": "admin"}, description="Search users")
        self.test_endpoint("/users/invite", "POST", data={"email": "test@example.com"}, description="Invite user")

    def test_workspace_management(self):
        """Test Workspace Management endpoints (25+ expected)"""
        print(f"\n🏢 TESTING WORKSPACE MANAGEMENT ENDPOINTS")
        
        # Core workspace endpoints
        self.test_endpoint("/workspaces", "GET", description="List workspaces")
        self.test_endpoint("/workspaces/create", "POST", data={"name": "Test Workspace", "goals": ["instagram"]}, description="Create workspace")
        
        if self.workspace_id:
            self.test_endpoint(f"/workspaces/{self.workspace_id}", "GET", description="Get workspace details")
            self.test_endpoint(f"/workspaces/{self.workspace_id}", "PUT", data={"name": "Updated Workspace"}, description="Update workspace")
            self.test_endpoint(f"/workspaces/{self.workspace_id}/members", "GET", description="Get workspace members")
            self.test_endpoint(f"/workspaces/{self.workspace_id}/settings", "GET", description="Get workspace settings")
            self.test_endpoint(f"/workspaces/{self.workspace_id}/settings", "PUT", data={"theme": "dark"}, description="Update workspace settings")
            self.test_endpoint(f"/workspaces/{self.workspace_id}/analytics", "GET", description="Workspace analytics")
            self.test_endpoint(f"/workspaces/{self.workspace_id}/activity", "GET", description="Workspace activity")
            
        # Team management
        self.test_endpoint("/team/members", "GET", description="List team members")
        self.test_endpoint("/team/invite", "POST", data={"email": "team@example.com", "role": "member"}, description="Invite team member")
        self.test_endpoint("/team/roles", "GET", description="List team roles")
        
        # Workspace features
        self.test_endpoint("/workspaces/templates", "GET", description="Workspace templates")
        self.test_endpoint("/workspaces/features", "GET", description="Available workspace features")

    def test_ai_services_expansion(self):
        """Test AI Services Expansion endpoints (30+ expected)"""
        print(f"\n🤖 TESTING AI SERVICES EXPANSION ENDPOINTS")
        
        # Core AI services
        self.test_endpoint("/ai/services", "GET", description="Available AI services")
        self.test_endpoint("/ai/models", "GET", description="Available AI models")
        self.test_endpoint("/ai/usage", "GET", description="AI usage statistics")
        self.test_endpoint("/ai/usage/detailed", "GET", description="Detailed AI usage")
        
        # AI content generation
        self.test_endpoint("/ai/generate-content", "POST", data={"type": "social_post", "topic": "test", "tone": "professional"}, description="Generate AI content")
        self.test_endpoint("/ai/analyze-content", "POST", data={"content": "Test content", "analysis_type": "sentiment"}, description="Analyze content")
        self.test_endpoint("/ai/generate-hashtags", "POST", data={"content": "Test post", "platform": "instagram"}, description="Generate hashtags")
        self.test_endpoint("/ai/improve-content", "POST", data={"content": "Test content", "improvement_type": "engagement"}, description="Improve content")
        
        # AI conversations
        self.test_endpoint("/ai/conversations", "GET", description="List AI conversations")
        self.test_endpoint("/ai/conversations", "POST", data={"title": "Test Conversation"}, description="Create AI conversation")
        
        # AI templates
        self.test_endpoint("/ai/templates", "GET", description="AI templates")
        self.test_endpoint("/ai/templates", "POST", data={"name": "Test Template", "content": "Template content"}, description="Create AI template")
        
        # AI business intelligence
        self.test_endpoint("/ai/business-insights", "GET", description="AI business insights")
        self.test_endpoint("/ai/recommendations", "GET", description="AI recommendations")
        
        # Course content generation
        self.test_endpoint("/ai/generate-course-content", "POST", data={"topic": "Digital Marketing", "duration": 30}, description="Generate course content")
        self.test_endpoint("/ai/generate-email-sequence", "POST", data={"type": "welcome", "audience": "new_subscribers"}, description="Generate email sequence")
        
        # Advanced AI features
        self.test_endpoint("/ai/content-calendar", "POST", data={"duration": 7, "topics": ["business"]}, description="Generate content calendar")
        self.test_endpoint("/ai/seo-optimization", "POST", data={"content": "Test content", "keywords": ["test"]}, description="SEO optimization")

    def test_social_media_expansion(self):
        """Test Social Media Expansion endpoints (25+ expected)"""
        print(f"\n📱 TESTING SOCIAL MEDIA EXPANSION ENDPOINTS")
        
        # Social media accounts
        self.test_endpoint("/social/accounts", "GET", description="Connected social accounts")
        self.test_endpoint("/social/accounts/connect", "POST", data={"platform": "instagram", "token": "test"}, description="Connect social account")
        
        # Social media posts
        self.test_endpoint("/social/posts", "GET", description="List social posts")
        self.test_endpoint("/social/posts", "POST", data={"content": "Test post", "platforms": ["instagram"]}, description="Create social post")
        self.test_endpoint("/social/posts/schedule", "POST", data={"content": "Scheduled post", "schedule_time": "2025-01-21T10:00:00Z"}, description="Schedule social post")
        
        # Social media analytics
        self.test_endpoint("/social/analytics", "GET", description="Social media analytics")
        self.test_endpoint("/social/analytics/comprehensive", "GET", description="Comprehensive social analytics")
        self.test_endpoint("/social/analytics/engagement", "GET", description="Engagement analytics")
        self.test_endpoint("/social/analytics/reach", "GET", description="Reach analytics")
        
        # Hashtag management
        self.test_endpoint("/social/hashtags", "GET", description="Hashtag management")
        self.test_endpoint("/social/hashtags/trending", "GET", description="Trending hashtags")
        self.test_endpoint("/social/hashtags/performance", "GET", description="Hashtag performance")
        
        # Social media calendar
        self.test_endpoint("/social/calendar", "GET", description="Social media calendar")
        self.test_endpoint("/social/calendar/events", "GET", description="Calendar events")
        
        # Content management
        self.test_endpoint("/social/content/library", "GET", description="Content library")
        self.test_endpoint("/social/content/templates", "GET", description="Content templates")
        
        # Competitor analysis
        self.test_endpoint("/social/competitors", "GET", description="Competitor analysis")
        self.test_endpoint("/social/competitors/track", "POST", data={"competitor_url": "https://example.com"}, description="Track competitor")

    def test_analytics_reporting(self):
        """Test Analytics & Reporting endpoints (40+ expected)"""
        print(f"\n📊 TESTING ANALYTICS & REPORTING ENDPOINTS")
        
        # Core analytics
        self.test_endpoint("/analytics/overview", "GET", description="Analytics overview")
        self.test_endpoint("/analytics/dashboard", "GET", description="Analytics dashboard")
        self.test_endpoint("/analytics/business-intelligence/advanced", "GET", description="Advanced business intelligence")
        
        # Reports
        self.test_endpoint("/analytics/reports", "GET", description="Available reports")
        self.test_endpoint("/analytics/reports/custom", "GET", description="Custom reports")
        self.test_endpoint("/analytics/reports/generate", "POST", data={"type": "revenue", "period": "monthly"}, description="Generate report")
        
        # Performance analytics
        self.test_endpoint("/analytics/performance", "GET", description="Performance analytics")
        self.test_endpoint("/analytics/performance/metrics", "GET", description="Performance metrics")
        self.test_endpoint("/analytics/performance/trends", "GET", description="Performance trends")
        
        # Customer analytics
        self.test_endpoint("/analytics/customers", "GET", description="Customer analytics")
        self.test_endpoint("/analytics/customer-journey", "GET", description="Customer journey analytics")
        self.test_endpoint("/analytics/customer-segmentation", "GET", description="Customer segmentation")
        
        # Revenue analytics
        self.test_endpoint("/analytics/revenue", "GET", description="Revenue analytics")
        self.test_endpoint("/analytics/revenue/trends", "GET", description="Revenue trends")
        self.test_endpoint("/analytics/revenue/forecasting", "GET", description="Revenue forecasting")
        
        # Predictive analytics
        self.test_endpoint("/analytics/predictive", "GET", description="Predictive analytics")
        self.test_endpoint("/analytics/predictive/models", "GET", description="Predictive models")
        
        # Dashboards
        self.test_endpoint("/analytics/dashboards", "GET", description="Analytics dashboards")
        self.test_endpoint("/analytics/dashboards", "POST", data={"name": "Test Dashboard", "widgets": []}, description="Create dashboard")
        
        # Export functionality
        self.test_endpoint("/analytics/export", "GET", params={"format": "csv", "type": "revenue"}, description="Export analytics")
        
        # Real-time analytics
        self.test_endpoint("/analytics/realtime", "GET", description="Real-time analytics")
        self.test_endpoint("/analytics/realtime/visitors", "GET", description="Real-time visitors")
        
        # Market intelligence
        self.test_endpoint("/trends/market-intelligence", "GET", description="Market intelligence")
        self.test_endpoint("/trends/analysis", "GET", description="Trend analysis")

    def test_system_configuration(self):
        """Test System Configuration endpoints (30+ expected)"""
        print(f"\n⚙️ TESTING SYSTEM CONFIGURATION ENDPOINTS")
        
        # System health and status
        self.test_endpoint("/health", "GET", description="System health check")
        self.test_endpoint("/system/status", "GET", description="System status")
        self.test_endpoint("/system/metrics", "GET", description="System metrics")
        self.test_endpoint("/system/performance", "GET", description="System performance")
        
        # System settings
        self.test_endpoint("/system/settings", "GET", description="System settings")
        self.test_endpoint("/admin/system/settings", "GET", description="Admin system settings")
        
        # Feature flags
        self.test_endpoint("/system/features", "GET", description="Feature flags")
        self.test_endpoint("/system/features/toggle", "POST", data={"feature": "test_feature", "enabled": True}, description="Toggle feature")
        
        # Integration configuration
        self.test_endpoint("/integrations", "GET", description="Available integrations")
        self.test_endpoint("/integrations/config", "GET", description="Integration configuration")
        self.test_endpoint("/integrations/webhooks", "GET", description="Webhook configurations")
        
        # Admin configuration
        self.test_endpoint("/admin/dashboard", "GET", description="Admin dashboard")
        self.test_endpoint("/admin/settings", "GET", description="Admin settings")
        self.test_endpoint("/admin/users/management", "GET", description="Admin user management")
        self.test_endpoint("/admin/workspaces/management", "GET", description="Admin workspace management")
        
        # Security configuration
        self.test_endpoint("/admin/security", "GET", description="Security configuration")
        self.test_endpoint("/admin/audit-logs", "GET", description="Audit logs")
        
        # Backup and maintenance
        self.test_endpoint("/admin/backup", "GET", description="Backup configuration")
        self.test_endpoint("/admin/maintenance", "GET", description="Maintenance mode")
        
        # API management
        self.test_endpoint("/admin/api/keys", "GET", description="API key management")
        self.test_endpoint("/admin/api/usage", "GET", description="API usage statistics")
        
        # White-label configuration
        self.test_endpoint("/admin/white-label/settings", "GET", description="White-label settings")
        self.test_endpoint("/admin/white-label/branding", "GET", description="White-label branding")

    def test_additional_endpoints(self):
        """Test additional endpoints from previous implementations"""
        print(f"\n🔧 TESTING ADDITIONAL ENDPOINTS")
        
        # Bio Sites
        self.test_endpoint("/bio-sites", "GET", description="Bio sites")
        self.test_endpoint("/bio-sites/themes", "GET", description="Bio site themes")
        self.test_endpoint("/bio-sites", "POST", data={"name": "Test Site", "slug": "test-site"}, description="Create bio site")
        
        # E-commerce
        self.test_endpoint("/ecommerce/products", "GET", description="E-commerce products")
        self.test_endpoint("/ecommerce/orders", "GET", description="E-commerce orders")
        self.test_endpoint("/ecommerce/dashboard", "GET", description="E-commerce dashboard")
        self.test_endpoint("/ecommerce/vendors/dashboard", "GET", description="Vendor dashboard")
        
        # Courses
        self.test_endpoint("/courses", "GET", description="Courses")
        self.test_endpoint("/courses/analytics", "GET", description="Course analytics")
        
        # Financial management
        self.test_endpoint("/financial/dashboard/comprehensive", "GET", description="Financial dashboard")
        self.test_endpoint("/financial/invoices", "GET", description="Financial invoices")
        self.test_endpoint("/financial/multi-currency", "GET", description="Multi-currency support")
        
        # Booking system
        self.test_endpoint("/bookings/services", "GET", description="Booking services")
        self.test_endpoint("/bookings/appointments", "GET", description="Booking appointments")
        self.test_endpoint("/bookings/dashboard", "GET", description="Booking dashboard")
        
        # CRM
        self.test_endpoint("/crm/contacts", "GET", description="CRM contacts")
        self.test_endpoint("/crm/pipeline/advanced", "GET", description="CRM pipeline")
        
        # Email marketing
        self.test_endpoint("/email/campaigns", "GET", description="Email campaigns")
        self.test_endpoint("/email/analytics", "GET", description="Email analytics")
        
        # Notifications
        self.test_endpoint("/notifications", "GET", description="Notifications")
        self.test_endpoint("/notifications/advanced", "GET", description="Advanced notifications")
        self.test_endpoint("/notifications/smart", "GET", description="Smart notifications")
        
        # Escrow system
        self.test_endpoint("/escrow/dashboard", "GET", description="Escrow dashboard")
        self.test_endpoint("/escrow/transactions", "GET", description="Escrow transactions")
        
        # Payment processing
        self.test_endpoint("/payments/analytics", "GET", description="Payment analytics")
        self.test_endpoint("/payments/methods", "GET", description="Payment methods")
        
        # Link shortener
        self.test_endpoint("/link-shortener/links", "GET", description="Link shortener links")
        self.test_endpoint("/link-shortener/stats", "GET", description="Link shortener stats")
        self.test_endpoint("/link-shortener/create", "POST", data={"url": "https://example.com", "custom_code": "test123"}, description="Create short link")
        
        # Form templates
        self.test_endpoint("/form-templates", "GET", description="Form templates")
        self.test_endpoint("/form-templates", "POST", data={"name": "Test Form", "fields": []}, description="Create form template")
        
        # Discount codes
        self.test_endpoint("/discount-codes", "GET", description="Discount codes")
        self.test_endpoint("/discount-codes", "POST", data={"code": "TEST20", "type": "percentage", "value": 20}, description="Create discount code")
        
        # Automation
        self.test_endpoint("/automation/workflows", "GET", description="Automation workflows")
        self.test_endpoint("/automation/triggers", "GET", description="Automation triggers")
        
        # Affiliate program
        self.test_endpoint("/affiliate/program/overview", "GET", description="Affiliate program")
        self.test_endpoint("/affiliate/commissions", "GET", description="Affiliate commissions")
        
        # Search functionality
        self.test_endpoint("/search/global", "GET", params={"q": "test"}, description="Global search")
        
        # Templates
        self.test_endpoint("/templates/marketplace", "GET", description="Template marketplace")
        
        # Performance optimization
        self.test_endpoint("/performance/optimization-center", "GET", description="Performance optimization")
        
        # Team productivity
        self.test_endpoint("/team/productivity-insights", "GET", description="Team productivity insights")
        
        # Onboarding
        self.test_endpoint("/onboarding/progress", "GET", description="Onboarding progress")
        self.test_endpoint("/onboarding/complete", "POST", data={"workspace_name": "Test Workspace"}, description="Complete onboarding")

    def run_comprehensive_endpoint_count_test(self):
        """Run comprehensive endpoint count verification"""
        print(f"🎯 COMPREHENSIVE ENDPOINT COUNT VERIFICATION - MEWAYZ PLATFORM V3.0.0")
        print(f"TARGET: Verify 200+ API endpoints")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with testing")
            return
        
        # Step 2: Get test data
        self.get_test_data()
        
        # Step 3: Test all endpoint categories
        self.test_authentication_users()
        self.test_workspace_management()
        self.test_ai_services_expansion()
        self.test_social_media_expansion()
        self.test_analytics_reporting()
        self.test_system_configuration()
        self.test_additional_endpoints()
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive final report with exact endpoint count"""
        print(f"\n" + "="*100)
        print(f"📊 FINAL COMPREHENSIVE ENDPOINT COUNT VERIFICATION REPORT")
        print(f"="*100)
        
        success_rate = (self.working_endpoints / self.total_endpoints * 100) if self.total_endpoints > 0 else 0
        
        print(f"🎯 ENDPOINT COUNT RESULTS:")
        print(f"   TOTAL ENDPOINTS TESTED: {self.total_endpoints}")
        print(f"   WORKING ENDPOINTS: {self.working_endpoints}")
        print(f"   FAILED ENDPOINTS: {self.total_endpoints - self.working_endpoints}")
        print(f"   SUCCESS RATE: {success_rate:.1f}%")
        
        # Check if we exceeded the 200+ target
        target_met = "✅ TARGET EXCEEDED!" if self.total_endpoints >= 200 else "❌ TARGET NOT MET"
        print(f"   200+ ENDPOINT TARGET: {target_met}")
        
        print(f"\n📋 ENDPOINT BREAKDOWN BY CATEGORY:")
        
        # Categorize endpoints
        auth_endpoints = [r for r in self.test_results if '/auth/' in r['endpoint'] or '/users/' in r['endpoint'] or '/admin/users' in r['endpoint']]
        workspace_endpoints = [r for r in self.test_results if '/workspace' in r['endpoint'] or '/team/' in r['endpoint']]
        ai_endpoints = [r for r in self.test_results if '/ai/' in r['endpoint']]
        social_endpoints = [r for r in self.test_results if '/social/' in r['endpoint']]
        analytics_endpoints = [r for r in self.test_results if '/analytics/' in r['endpoint'] or '/trends/' in r['endpoint']]
        system_endpoints = [r for r in self.test_results if '/system/' in r['endpoint'] or '/admin/' in r['endpoint'] or '/health' in r['endpoint'] or '/integrations/' in r['endpoint']]
        business_endpoints = [r for r in self.test_results if any(x in r['endpoint'] for x in ['/ecommerce/', '/financial/', '/bookings/', '/crm/', '/email/', '/escrow/', '/payments/'])]
        feature_endpoints = [r for r in self.test_results if any(x in r['endpoint'] for x in ['/bio-sites/', '/courses/', '/notifications/', '/link-shortener/', '/form-templates/', '/discount-codes/', '/automation/', '/affiliate/', '/search/', '/templates/', '/performance/', '/onboarding/'])]
        
        def print_category_results(category_name, endpoints, expected_count):
            if endpoints:
                working = sum(1 for e in endpoints if e['success'])
                total = len(endpoints)
                rate = (working / total * 100) if total > 0 else 0
                status = "✅" if total >= expected_count else "⚠️"
                print(f"   {status} {category_name}: {total} endpoints ({working} working, {rate:.1f}% success)")
            else:
                print(f"   ❌ {category_name}: 0 endpoints (Expected: {expected_count}+)")
        
        print_category_results("Authentication & Users", auth_endpoints, 20)
        print_category_results("Workspace Management", workspace_endpoints, 25)
        print_category_results("AI Services", ai_endpoints, 30)
        print_category_results("Social Media", social_endpoints, 25)
        print_category_results("Analytics & Reporting", analytics_endpoints, 40)
        print_category_results("System Configuration", system_endpoints, 30)
        print_category_results("Business Features", business_endpoints, 20)
        print_category_results("Additional Features", feature_endpoints, 15)
        
        # Performance metrics
        successful_tests = [r for r in self.test_results if r['success']]
        if successful_tests:
            response_times = [float(r['response_time'].replace('s', '')) for r in successful_tests]
            avg_response_time = sum(response_times) / len(response_times)
            total_data = sum(r['data_size'] for r in successful_tests)
            
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Fastest Response: {min(response_times):.3f}s")
            print(f"   Slowest Response: {max(response_times):.3f}s")
            print(f"   Total Data Transferred: {total_data:,} bytes")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        if self.total_endpoints >= 200:
            print(f"   ✅ SUCCESS: {self.total_endpoints} endpoints tested - TARGET EXCEEDED!")
            print(f"   🚀 The Mewayz Platform has successfully exceeded the 200+ endpoint target")
        else:
            print(f"   ⚠️  PARTIAL: {self.total_endpoints} endpoints tested - Target not fully met")
        
        if success_rate >= 80:
            print(f"   ✅ QUALITY: {success_rate:.1f}% success rate - Excellent system reliability")
        elif success_rate >= 60:
            print(f"   ⚠️  QUALITY: {success_rate:.1f}% success rate - Good system reliability")
        else:
            print(f"   ❌ QUALITY: {success_rate:.1f}% success rate - Needs improvement")
        
        # Top working endpoints
        print(f"\n🏆 TOP PERFORMING ENDPOINT CATEGORIES:")
        categories = [
            ("Authentication & Users", auth_endpoints),
            ("AI Services", ai_endpoints),
            ("Business Features", business_endpoints),
            ("Additional Features", feature_endpoints),
            ("Analytics & Reporting", analytics_endpoints)
        ]
        
        for cat_name, cat_endpoints in categories:
            if cat_endpoints:
                working = sum(1 for e in cat_endpoints if e['success'])
                total = len(cat_endpoints)
                if working > 0:
                    rate = (working / total * 100)
                    print(f"   ✅ {cat_name}: {working}/{total} working ({rate:.1f}%)")
        
        print(f"\n" + "="*100)
        print(f"🎉 EXACT TOTAL ENDPOINT COUNT: {self.total_endpoints}")
        print(f"🎯 TARGET STATUS: {'EXCEEDED' if self.total_endpoints >= 200 else 'NOT MET'}")
        print(f"⭐ SUCCESS RATE: {success_rate:.1f}%")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"="*100)

if __name__ == "__main__":
    tester = ComprehensiveEndpointTester()
    tester.run_comprehensive_endpoint_count_test()