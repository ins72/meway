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
BACKEND_URL = "https://73aa7a8d-1282-4389-99c1-66ddc80405f1.preview.emergentagent.com"
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
            "Multi-Vendor Marketplace"
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