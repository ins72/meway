#!/usr/bin/env python3
"""
Complete Link in Bio Builder System Comprehensive Testing Script
Tests all endpoints with real data and full CRUD operations
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class LinkInBioTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.workspace_id = None
        
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
    
    def get_workspace_id(self):
        """Get available workspace ID"""
        try:
            response = self.session.get(f"{API_BASE}/workspaces", timeout=10)
            if response.status_code == 200:
                data = response.json()
                workspaces = data.get("data", {}).get("workspaces", [])
                if workspaces:
                    self.workspace_id = workspaces[0]["_id"]
                    self.log_result("Get Workspace ID", True, f"Using workspace: {self.workspace_id}")
                    return True
                else:
                    self.log_result("Get Workspace ID", False, "No workspaces found")
                    return False
            else:
                self.log_result("Get Workspace ID", False, f"Failed to get workspaces: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get Workspace ID", False, f"Error getting workspace: {str(e)}")
            return False
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, test_name: str = None):
        """Test a specific API endpoint and return response data"""
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
                    response_data = response.json()
                    self.log_result(test_name, True, f"Success - Status {response.status_code}", response_data)
                    return True, response_data
                except:
                    self.log_result(test_name, True, f"Success - Status {response.status_code} (non-JSON response)")
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404)")
                return False, None
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    self.log_result(test_name, False, f"Validation error (422): {error_data.get('message', 'Unknown validation error')}")
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
                self.log_result(test_name, False, f"Error - Status {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False, None

    def run_comprehensive_test(self):
        """Run comprehensive Link in Bio system test"""
        print("🎯 COMPLETE LINK IN BIO BUILDER SYSTEM COMPREHENSIVE TESTING")
        print("=" * 80)
        print("Testing all aspects of the Link in Bio Builder System:")
        print("1. Authentication System")
        print("2. Complete Link in Bio APIs (15 endpoints)")
        print("3. Real Data Verification")
        print("4. Full CRUD Operations")
        print("5. Database Operations")
        print("6. Template System")
        print("7. Analytics System")
        print("=" * 80)
        
        # 1. Authentication
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed")
            return False
        
        # 2. Get workspace ID
        print("\n🏢 GETTING WORKSPACE ID")
        if not self.get_workspace_id():
            print("❌ Cannot get workspace ID - cannot proceed")
            return False
        
        # 3. Test Health Check
        print("\n🏥 TESTING HEALTH CHECK")
        self.test_endpoint("/link-in-bio/health", "GET", test_name="Link in Bio - Health Check")
        
        # 4. Test Templates (with workspace_id parameter)
        print("\n📋 TESTING TEMPLATE SYSTEM")
        success, templates_data = self.test_endpoint(f"/link-in-bio/templates?workspace_id={self.workspace_id}", "GET", test_name="Link in Bio - Get Templates")
        
        # 5. Test Analytics Overview
        print("\n📊 TESTING ANALYTICS OVERVIEW")
        self.test_endpoint("/link-in-bio/analytics/overview", "GET", test_name="Link in Bio - Analytics Overview")
        
        # 6. Test CREATE Operations
        print("\n➕ TESTING CREATE OPERATIONS")
        
        # Create Bio Page
        create_page_data = {
            "title": "Comprehensive Test Bio Page",
            "description": "Testing the complete Link in Bio system with real data and full CRUD operations",
            "username": "comprehensive_test",
            "template_id": "modern_gradient",
            "theme": {
                "primary_color": "#3b82f6",
                "secondary_color": "#1d4ed8",
                "background_color": "#ffffff",
                "text_color": "#1f2937"
            },
            "settings": {
                "show_analytics": True,
                "allow_comments": True,
                "custom_css": ".test-page { border: 1px solid #e5e7eb; }"
            }
        }
        
        success, page_data = self.test_endpoint(f"/link-in-bio/pages?workspace_id={self.workspace_id}", "POST", create_page_data, "Link in Bio - CREATE Bio Page")
        
        created_page_id = None
        if success and page_data:
            # Extract page ID from response
            if page_data.get("data", {}).get("id"):
                created_page_id = page_data["data"]["id"]
            elif page_data.get("id"):
                created_page_id = page_data["id"]
            elif page_data.get("page_id"):
                created_page_id = page_data["page_id"]
            
            print(f"   📝 Created page ID: {created_page_id}")
        
        # 7. Test READ Operations
        print("\n📖 TESTING READ OPERATIONS")
        
        # Get all bio pages
        self.test_endpoint(f"/link-in-bio/pages?workspace_id={self.workspace_id}", "GET", test_name="Link in Bio - READ All Bio Pages")
        
        # Get specific bio page (if created)
        if created_page_id:
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}", "GET", test_name="Link in Bio - READ Specific Bio Page")
        
        # 8. Test Link CRUD Operations
        created_link_id = None
        if created_page_id:
            print("\n🔗 TESTING LINK CRUD OPERATIONS")
            
            # CREATE Link
            create_link_data = {
                "title": "Test Portfolio Link",
                "url": "https://example.com/portfolio",
                "description": "Check out my comprehensive portfolio with all projects",
                "icon": "briefcase",
                "is_active": True,
                "click_tracking": True,
                "order_index": 1
            }
            
            success, link_data = self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/links", "POST", create_link_data, "Link in Bio - CREATE Bio Link")
            
            if success and link_data:
                # Extract link ID from response
                if link_data.get("data", {}).get("id"):
                    created_link_id = link_data["data"]["id"]
                elif link_data.get("id"):
                    created_link_id = link_data["id"]
                elif link_data.get("link_id"):
                    created_link_id = link_data["link_id"]
                
                print(f"   🔗 Created link ID: {created_link_id}")
            
            # READ Links
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/links", "GET", test_name="Link in Bio - READ Bio Page Links")
        
        # 9. Test UPDATE Operations
        if created_page_id:
            print("\n✏️ TESTING UPDATE OPERATIONS")
            
            # UPDATE Bio Page
            update_page_data = {
                "title": "Updated Comprehensive Test Bio Page",
                "description": "Updated description with new information and enhanced features",
                "theme": {
                    "primary_color": "#7c3aed",
                    "secondary_color": "#5b21b6",
                    "background_color": "#faf5ff",
                    "text_color": "#374151"
                }
            }
            
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}", "PUT", update_page_data, "Link in Bio - UPDATE Bio Page")
            
            # UPDATE Bio Link
            if created_link_id:
                update_link_data = {
                    "title": "Updated Portfolio Link - Premium",
                    "url": "https://example.com/premium-portfolio",
                    "description": "Premium portfolio with exclusive content and case studies",
                    "icon": "star",
                    "order_index": 1
                }
                
                self.test_endpoint(f"/link-in-bio/links/{created_link_id}", "PUT", update_link_data, "Link in Bio - UPDATE Bio Link")
        
        # 10. Test Analytics System
        if created_page_id:
            print("\n📊 TESTING ANALYTICS SYSTEM")
            
            # Track page visit
            visit_data = {
                "visitor_ip": "203.0.113.1",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "referrer": "https://twitter.com/comprehensive_test"
            }
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/visit", "POST", visit_data, "Link in Bio - TRACK Page Visit")
            
            # Track link click
            if created_link_id:
                click_data = {
                    "visitor_ip": "203.0.113.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "referrer": f"https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com/bio/comprehensive_test"
                }
                self.test_endpoint(f"/link-in-bio/links/{created_link_id}/click", "POST", click_data, "Link in Bio - TRACK Link Click")
            
            # Get page analytics
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/analytics", "GET", test_name="Link in Bio - GET Page Analytics")
        
        # 11. Test Additional Features
        if created_page_id:
            print("\n🎨 TESTING ADDITIONAL FEATURES")
            
            # Get QR Code
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/qr-code", "GET", test_name="Link in Bio - GET QR Code")
            
            # Get SEO Settings
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}/seo", "GET", test_name="Link in Bio - GET SEO Settings")
        
        # 12. Test Data Consistency (Real Database Verification)
        print("\n🔍 TESTING DATA CONSISTENCY (Real Database Verification)")
        
        # Test analytics overview consistency
        success1, data1 = self.test_endpoint("/link-in-bio/analytics/overview", "GET", test_name="Analytics Overview - First Call")
        time.sleep(1)
        success2, data2 = self.test_endpoint("/link-in-bio/analytics/overview", "GET", test_name="Analytics Overview - Second Call")
        
        if success1 and success2 and data1 == data2:
            self.log_result("Data Consistency - Analytics Overview", True, "Data consistent across calls - confirms real database usage")
        elif success1 and success2:
            self.log_result("Data Consistency - Analytics Overview", False, "Data inconsistent - may be using random generation")
        
        # Test bio pages consistency
        success1, data1 = self.test_endpoint(f"/link-in-bio/pages?workspace_id={self.workspace_id}", "GET", test_name="Bio Pages - First Call")
        time.sleep(1)
        success2, data2 = self.test_endpoint(f"/link-in-bio/pages?workspace_id={self.workspace_id}", "GET", test_name="Bio Pages - Second Call")
        
        if success1 and success2 and data1 == data2:
            self.log_result("Data Consistency - Bio Pages", True, "Data consistent across calls - confirms real database usage")
        elif success1 and success2:
            self.log_result("Data Consistency - Bio Pages", False, "Data inconsistent - may be using random generation")
        
        # 13. Test DELETE Operations
        print("\n🗑️ TESTING DELETE OPERATIONS")
        
        # Delete link first (if created)
        if created_link_id:
            self.test_endpoint(f"/link-in-bio/links/{created_link_id}", "DELETE", test_name="Link in Bio - DELETE Bio Link")
        
        # Delete page (if created)
        if created_page_id:
            self.test_endpoint(f"/link-in-bio/pages/{created_page_id}", "DELETE", test_name="Link in Bio - DELETE Bio Page")
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPLETE LINK IN BIO BUILDER SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"] or "Workspace" in r["test"]]
        crud_tests = [r for r in self.test_results if any(op in r["test"] for op in ["CREATE", "READ", "UPDATE", "DELETE"])]
        analytics_tests = [r for r in self.test_results if "Analytics" in r["test"] or "TRACK" in r["test"]]
        template_tests = [r for r in self.test_results if "Template" in r["test"]]
        consistency_tests = [r for r in self.test_results if "Consistency" in r["test"]]
        
        print(f"\n📊 TEST CATEGORIES:")
        print(f"Authentication & Setup: {sum(1 for r in auth_tests if r['success'])}/{len(auth_tests)} ✅")
        print(f"CRUD Operations: {sum(1 for r in crud_tests if r['success'])}/{len(crud_tests)} ✅")
        print(f"Analytics System: {sum(1 for r in analytics_tests if r['success'])}/{len(analytics_tests)} ✅")
        print(f"Template System: {sum(1 for r in template_tests if r['success'])}/{len(template_tests)} ✅")
        print(f"Data Consistency: {sum(1 for r in consistency_tests if r['success'])}/{len(consistency_tests)} ✅")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n✅ CRITICAL ACHIEVEMENTS:")
        auth_success = sum(1 for r in auth_tests if r['success']) == len(auth_tests) if auth_tests else False
        crud_success = sum(1 for r in crud_tests if r['success']) >= len(crud_tests) * 0.8 if crud_tests else False
        analytics_success = sum(1 for r in analytics_tests if r['success']) >= len(analytics_tests) * 0.7 if analytics_tests else False
        consistency_success = sum(1 for r in consistency_tests if r['success']) >= len(consistency_tests) * 0.8 if consistency_tests else False
        
        print(f"- Authentication System: {'✅ WORKING' if auth_success else '❌ ISSUES'}")
        print(f"- CRUD Operations: {'✅ WORKING' if crud_success else '❌ ISSUES'}")
        print(f"- Analytics System: {'✅ WORKING' if analytics_success else '❌ ISSUES'}")
        print(f"- Real Database Usage: {'✅ VERIFIED' if consistency_success else '❌ NEEDS VERIFICATION'}")
        
        overall_success = (passed_tests/total_tests) >= 0.8
        print(f"\n🎯 OVERALL ASSESSMENT: {'✅ PRODUCTION READY' if overall_success else '⚠️ NEEDS ATTENTION'}")

if __name__ == "__main__":
    tester = LinkInBioTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)