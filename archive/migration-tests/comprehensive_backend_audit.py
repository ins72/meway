#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND AUDIT - MEWAYZ PLATFORM
Systematic audit to identify what's working vs what needs migration
Testing Agent - Current Date
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class BackendAuditor:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.critical_failures = []
        self.working_endpoints = []
        self.broken_endpoints = []
        
    def log_test(self, endpoint, method, status, response_time, success, details="", data_size=0, critical=False):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            self.working_endpoints.append(f"{method} {endpoint}")
        else:
            self.broken_endpoints.append(f"{method} {endpoint} - {details}")
            if critical:
                self.critical_failures.append(f"{method} {endpoint} - {details}")
            
        result = {
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'response_time': f"{response_time:.3f}s",
            'success': success,
            'details': details,
            'data_size': data_size,
            'critical': critical
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        critical_flag = " [CRITICAL]" if critical else ""
        print(f"{status_icon} {method} {endpoint} - {status} ({response_time:.3f}s){critical_flag} - {details}")
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print(f"\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        print(f"Email: {ADMIN_EMAIL}")
        
        login_data = {
            "username": ADMIN_EMAIL,  # OAuth2PasswordRequestForm uses 'username'
            "password": ADMIN_PASSWORD
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/auth/login", data=login_data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                if self.auth_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("/auth/login", "POST", response.status_code, response_time, True, 
                                f"Admin authentication successful, token: {self.auth_token[:20]}...")
                    return True
                else:
                    self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                                "No access token in response", critical=True)
                    return False
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Login failed: {response.text[:100]}", critical=True)
                return False
                
        except Exception as e:
            self.log_test("/auth/login", "POST", 0, 0, False, f"Authentication error: {str(e)}", critical=True)
            return False
    
    def test_endpoint(self, endpoint, method="GET", data=None, expected_status=200, description="", critical=False):
        """Test a single endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            # Check if response is successful
            success = response.status_code == expected_status
            
            # Get response details
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    error_detail = response_data.get('detail', 'Unknown error')
                    details += f" - Error: {error_detail}"
            except:
                data_size = len(response.text)
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    details += f" - Error: {response.text[:100]}"
            
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size, critical)
            return success, response
            
        except requests.exceptions.Timeout:
            self.log_test(endpoint, method, 0, 30.0, False, f"{description} - Request timeout", critical=critical)
            return False, None
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"{description} - Error: {str(e)}", critical=critical)
            return False, None

    def audit_authentication_system(self):
        """Audit authentication system"""
        print(f"\n🔐 AUDITING AUTHENTICATION SYSTEM (/api/auth/*)")
        
        # Test token verification
        self.test_endpoint("/auth/verify", "GET", description="Token verification", critical=True)
        
        # Test logout
        self.test_endpoint("/auth/logout", "POST", description="User logout")

    def audit_admin_dashboard(self):
        """Audit admin dashboard system"""
        print(f"\n👑 AUDITING ADMIN DASHBOARD SYSTEM (/api/admin/*)")
        
        # Test admin dashboard
        self.test_endpoint("/admin/dashboard", "GET", description="Admin dashboard access", critical=True)
        
        # Test user management
        self.test_endpoint("/admin/users", "GET", description="Admin user management")
        
        # Test user statistics
        self.test_endpoint("/admin/users/stats", "GET", description="Admin user statistics")
        
        # Test system metrics
        self.test_endpoint("/admin/system/metrics", "GET", description="Admin system metrics")

    def audit_ai_services(self):
        """Audit AI services system"""
        print(f"\n🤖 AUDITING AI SERVICES SYSTEM (/api/ai/*)")
        
        # Test AI services list
        self.test_endpoint("/ai/services", "GET", description="Available AI services", critical=True)
        
        # Test AI conversations
        self.test_endpoint("/ai/conversations", "GET", description="AI conversations list")
        
        # Test content analysis
        analysis_data = {
            "content": "This is a test content for AI analysis to check sentiment and readability.",
            "analysis_type": ["sentiment", "keywords", "readability"]
        }
        self.test_endpoint("/ai/analyze-content", "POST", data=analysis_data, description="AI content analysis")
        
        # Test conversation creation
        conversation_data = {
            "message": "Hello, I need help with content creation for my business.",
            "context": {"type": "business_help"},
            "conversation_type": "chat"
        }
        self.test_endpoint("/ai/conversations", "POST", data=conversation_data, description="AI conversation creation")

    def audit_bio_sites(self):
        """Audit bio sites (link-in-bio) system"""
        print(f"\n🔗 AUDITING BIO SITES SYSTEM (/api/bio-sites/*)")
        
        # Test bio sites list
        self.test_endpoint("/bio-sites", "GET", description="User bio sites list", critical=True)
        
        # Test available themes
        self.test_endpoint("/bio-sites/themes", "GET", description="Available bio site themes")
        
        # Test bio site creation
        bio_site_data = {
            "title": "Test Bio Site",
            "description": "A test bio site for audit purposes",
            "theme": "modern",
            "links": [
                {"title": "Website", "url": "https://example.com", "type": "website"}
            ]
        }
        self.test_endpoint("/bio-sites", "POST", data=bio_site_data, description="Bio site creation")

    def audit_ecommerce_system(self):
        """Audit e-commerce system"""
        print(f"\n🛒 AUDITING E-COMMERCE SYSTEM (/api/ecommerce/*)")
        
        # Test products list
        self.test_endpoint("/ecommerce/products", "GET", description="E-commerce products list", critical=True)
        
        # Test orders list
        self.test_endpoint("/ecommerce/orders", "GET", description="E-commerce orders list")
        
        # Test e-commerce dashboard
        self.test_endpoint("/ecommerce/dashboard", "GET", description="E-commerce dashboard")
        
        # Test product creation
        product_data = {
            "name": "Test Product",
            "description": "A test product for audit purposes",
            "price": 29.99,
            "category": "digital",
            "inventory": 100
        }
        self.test_endpoint("/ecommerce/products", "POST", data=product_data, description="Product creation")

    def audit_booking_system(self):
        """Audit booking system"""
        print(f"\n📅 AUDITING BOOKING SYSTEM (/api/bookings/*)")
        
        # Test services list
        self.test_endpoint("/bookings/services", "GET", description="Booking services list", critical=True)
        
        # Test appointments list
        self.test_endpoint("/bookings/appointments", "GET", description="Booking appointments list")
        
        # Test booking dashboard
        self.test_endpoint("/bookings/dashboard", "GET", description="Booking dashboard")
        
        # Test service creation
        service_data = {
            "name": "Test Service",
            "description": "A test service for audit purposes",
            "duration": 60,
            "price": 99.99,
            "category": "consultation"
        }
        self.test_endpoint("/bookings/services", "POST", data=service_data, description="Service creation")

    def audit_social_media(self):
        """Audit social media management system"""
        print(f"\n📱 AUDITING SOCIAL MEDIA SYSTEM (/api/social-media/*)")
        
        # Test social accounts
        self.test_endpoint("/social-media/accounts", "GET", description="Connected social accounts")
        
        # Test social posts
        self.test_endpoint("/social-media/posts", "GET", description="Social media posts")
        
        # Test social analytics
        self.test_endpoint("/social-media/analytics", "GET", description="Social media analytics")
        
        # Test account connection
        account_data = {
            "platform": "twitter",
            "account_name": "test_account",
            "access_token": "test_token"
        }
        self.test_endpoint("/social-media/accounts", "POST", data=account_data, description="Social account connection")
        
        # Test post creation
        post_data = {
            "content": "Test post for audit purposes #testing",
            "platforms": ["twitter"],
            "schedule_time": None
        }
        self.test_endpoint("/social-media/posts", "POST", data=post_data, description="Social media post creation")

    def audit_marketing_email(self):
        """Audit marketing & email system"""
        print(f"\n📧 AUDITING MARKETING & EMAIL SYSTEM (/api/marketing/*)")
        
        # Test campaigns list
        self.test_endpoint("/marketing/campaigns", "GET", description="Email campaigns list")
        
        # Test contacts list
        self.test_endpoint("/marketing/contacts", "GET", description="Marketing contacts list")
        
        # Test contact lists
        self.test_endpoint("/marketing/lists", "GET", description="Contact lists")
        
        # Test marketing analytics
        self.test_endpoint("/marketing/analytics", "GET", description="Marketing analytics")
        
        # Test contact list creation
        list_data = {
            "name": "Test Contact List",
            "description": "A test contact list for audit purposes",
            "tags": ["test", "audit"]
        }
        self.test_endpoint("/marketing/lists", "POST", data=list_data, description="Contact list creation")
        
        # Test contact addition
        contact_data = {
            "email": "test@example.com",
            "name": "Test Contact",
            "list_id": "test_list_id",
            "tags": ["test"]
        }
        self.test_endpoint("/marketing/contacts", "POST", data=contact_data, description="Contact addition")
        
        # Test campaign creation
        campaign_data = {
            "name": "Test Campaign",
            "subject": "Test Email Campaign",
            "content": "This is a test email campaign for audit purposes.",
            "list_id": "test_list_id"
        }
        self.test_endpoint("/marketing/campaigns", "POST", data=campaign_data, description="Email campaign creation")

    def audit_analytics(self):
        """Audit analytics system"""
        print(f"\n📊 AUDITING ANALYTICS SYSTEM (/api/analytics/*)")
        
        # Test analytics dashboard
        self.test_endpoint("/analytics/dashboard", "GET", description="Analytics dashboard")
        
        # Test reports
        self.test_endpoint("/analytics/reports", "GET", description="Analytics reports")
        
        # Test business intelligence
        self.test_endpoint("/analytics/business-intelligence", "GET", description="Business intelligence")

    def audit_user_management(self):
        """Audit user management system"""
        print(f"\n👤 AUDITING USER MANAGEMENT SYSTEM (/api/users/*)")
        
        # Test user profile
        self.test_endpoint("/users/profile", "GET", description="User profile access", critical=True)
        
        # Test user settings
        self.test_endpoint("/users/settings", "GET", description="User settings access")

    def audit_workspace_management(self):
        """Audit workspace management system"""
        print(f"\n🏢 AUDITING WORKSPACE MANAGEMENT SYSTEM (/api/workspaces/*)")
        
        # Test workspaces list
        self.test_endpoint("/workspaces", "GET", description="User workspaces list")
        
        # Test workspace creation
        workspace_data = {
            "name": "Test Workspace",
            "description": "A test workspace for audit purposes",
            "type": "business"
        }
        self.test_endpoint("/workspaces", "POST", data=workspace_data, description="Workspace creation")

    def audit_business_intelligence(self):
        """Audit business intelligence system"""
        print(f"\n📈 AUDITING BUSINESS INTELLIGENCE SYSTEM (/api/business-intelligence/*)")
        
        # Test BI dashboard
        self.test_endpoint("/business-intelligence/dashboard", "GET", description="Business intelligence dashboard")
        
        # Test BI reports
        self.test_endpoint("/business-intelligence/reports", "GET", description="Business intelligence reports")

    def audit_integrations(self):
        """Audit integrations system"""
        print(f"\n🔌 AUDITING INTEGRATIONS SYSTEM (/api/integrations/*)")
        
        # Test available integrations
        self.test_endpoint("/integrations/available", "GET", description="Available integrations")
        
        # Test connected integrations
        self.test_endpoint("/integrations/connected", "GET", description="Connected integrations")
        
        # Test webhooks
        self.test_endpoint("/integrations/webhooks", "GET", description="Integration webhooks")
        
        # Test integration logs
        self.test_endpoint("/integrations/logs", "GET", description="Integration logs")
        
        # Test integration connection
        integration_data = {
            "service": "zapier",
            "config": {"api_key": "test_key"},
            "enabled": True
        }
        self.test_endpoint("/integrations/connect", "POST", data=integration_data, description="Integration connection")

    def audit_core_system(self):
        """Audit core system endpoints"""
        print(f"\n🏥 AUDITING CORE SYSTEM")
        
        # Test health check
        self.test_endpoint("/health", "GET", description="System health check", critical=True)
        
        # Test root endpoint
        success, response = self.test_endpoint("/", "GET", description="Root endpoint")

    def run_comprehensive_audit(self):
        """Run comprehensive backend audit"""
        print(f"🔍 COMPREHENSIVE BACKEND AUDIT - MEWAYZ PLATFORM")
        print(f"Systematic audit to identify what's working vs what needs migration")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Test core system first
        self.audit_core_system()
        
        # Step 2: Authenticate (critical for most endpoints)
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Limited audit possible")
            self.generate_audit_report()
            return
        
        # Step 3: Audit all major systems
        self.audit_authentication_system()
        self.audit_admin_dashboard()
        self.audit_ai_services()
        self.audit_bio_sites()
        self.audit_ecommerce_system()
        self.audit_booking_system()
        self.audit_social_media()
        self.audit_marketing_email()
        self.audit_analytics()
        self.audit_user_management()
        self.audit_workspace_management()
        self.audit_business_intelligence()
        self.audit_integrations()
        
        # Generate comprehensive audit report
        self.generate_audit_report()

    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print(f"\n" + "="*100)
        print(f"📊 COMPREHENSIVE BACKEND AUDIT REPORT - MEWAYZ PLATFORM")
        print(f"="*100)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"🎯 OVERALL AUDIT RESULTS:")
        print(f"   Total Endpoints Tested: {self.total_tests}")
        print(f"   Working Endpoints: {self.passed_tests}")
        print(f"   Broken Endpoints: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Critical Failures: {len(self.critical_failures)}")
        
        # System-by-system breakdown
        print(f"\n📋 SYSTEM-BY-SYSTEM AUDIT RESULTS:")
        
        systems = {
            "Authentication": [r for r in self.test_results if r['endpoint'].startswith('/auth/')],
            "Admin Dashboard": [r for r in self.test_results if r['endpoint'].startswith('/admin/')],
            "AI Services": [r for r in self.test_results if r['endpoint'].startswith('/ai/')],
            "Bio Sites": [r for r in self.test_results if r['endpoint'].startswith('/bio-sites')],
            "E-commerce": [r for r in self.test_results if r['endpoint'].startswith('/ecommerce/')],
            "Booking System": [r for r in self.test_results if r['endpoint'].startswith('/bookings/')],
            "Social Media": [r for r in self.test_results if r['endpoint'].startswith('/social-media/')],
            "Marketing & Email": [r for r in self.test_results if r['endpoint'].startswith('/marketing/')],
            "Analytics": [r for r in self.test_results if r['endpoint'].startswith('/analytics/')],
            "User Management": [r for r in self.test_results if r['endpoint'].startswith('/users/')],
            "Workspaces": [r for r in self.test_results if r['endpoint'].startswith('/workspaces')],
            "Business Intelligence": [r for r in self.test_results if r['endpoint'].startswith('/business-intelligence/')],
            "Integrations": [r for r in self.test_results if r['endpoint'].startswith('/integrations/')],
            "Core System": [r for r in self.test_results if r['endpoint'] in ['/health', '/']]
        }
        
        for system_name, tests in systems.items():
            if tests:
                passed = sum(1 for t in tests if t['success'])
                total = len(tests)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅ WORKING" if rate >= 75 else "⚠️ PARTIAL" if rate >= 50 else "❌ BROKEN"
                print(f"   {system_name}: {passed}/{total} ({rate:.1f}%) {status}")
        
        # Critical failures
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES (BLOCKING ISSUES):")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
        
        # Working endpoints summary
        print(f"\n✅ WORKING ENDPOINTS ({len(self.working_endpoints)}):")
        for endpoint in self.working_endpoints[:20]:  # Show first 20
            print(f"   ✅ {endpoint}")
        if len(self.working_endpoints) > 20:
            print(f"   ... and {len(self.working_endpoints) - 20} more")
        
        # Broken endpoints summary
        if self.broken_endpoints:
            print(f"\n❌ BROKEN ENDPOINTS ({len(self.broken_endpoints)}):")
            for endpoint in self.broken_endpoints[:15]:  # Show first 15
                print(f"   ❌ {endpoint}")
            if len(self.broken_endpoints) > 15:
                print(f"   ... and {len(self.broken_endpoints) - 15} more")
        
        # Performance metrics
        successful_tests = [r for r in self.test_results if r['success']]
        if successful_tests:
            avg_response_time = sum(float(r['response_time'].replace('s', '')) for r in successful_tests) / len(successful_tests)
            total_data = sum(r['data_size'] for r in successful_tests)
            fastest = min(float(r['response_time'].replace('s', '')) for r in successful_tests)
            slowest = max(float(r['response_time'].replace('s', '')) for r in successful_tests)
            
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Fastest Response: {fastest:.3f}s")
            print(f"   Slowest Response: {slowest:.3f}s")
            print(f"   Total Data Processed: {total_data:,} bytes")
        
        # Migration recommendations
        print(f"\n🔄 MIGRATION RECOMMENDATIONS:")
        if success_rate >= 80:
            print(f"   ✅ EXCELLENT - Most systems operational, minor fixes needed")
            print(f"   🎯 Focus on fixing broken endpoints and optimizing performance")
            print(f"   📈 Platform ready for production with minor enhancements")
        elif success_rate >= 60:
            print(f"   ⚠️ GOOD - Core functionality working, some systems need attention")
            print(f"   🔧 Priority: Fix critical failures and broken core features")
            print(f"   📋 Migrate missing features from monolithic structure")
        elif success_rate >= 40:
            print(f"   ⚠️ MODERATE - Significant issues need resolution")
            print(f"   🚨 Priority: Address critical authentication and core system issues")
            print(f"   🔄 Major migration work needed from old monolithic file")
        else:
            print(f"   ❌ CRITICAL - Major system overhaul required")
            print(f"   🆘 Priority: Fix authentication and core infrastructure")
            print(f"   🔄 Extensive migration needed from monolithic structure")
        
        # Final assessment
        print(f"\n🎯 FINAL AUDIT ASSESSMENT:")
        if len(self.critical_failures) == 0 and success_rate >= 75:
            print(f"   ✅ PRODUCTION READY - Platform operational with good functionality")
            print(f"   🚀 Ready for deployment with minor optimizations")
        elif len(self.critical_failures) <= 2 and success_rate >= 60:
            print(f"   ⚠️ NEAR PRODUCTION - Fix critical issues before deployment")
            print(f"   🔧 Address critical failures and enhance broken systems")
        else:
            print(f"   ❌ DEVELOPMENT PHASE - Significant work needed before production")
            print(f"   🔄 Focus on core functionality and critical system fixes")
        
        print(f"\nAudit completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"="*100)

if __name__ == "__main__":
    auditor = BackendAuditor()
    auditor.run_comprehensive_audit()