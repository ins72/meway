#!/usr/bin/env python3
"""
SECOND WAVE MIGRATION TESTING - MEWAYZ PLATFORM
Testing newly migrated Team Management & Form Builder features + First Wave regression testing
Testing Agent - July 20, 2025
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class SecondWaveTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, endpoint, method, status, response_time, success, details="", data_size=0):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
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
        print(f"{status_icon} {method} {endpoint} - {status} ({response_time:.3f}s) - {details}")
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print(f"\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        print(f"Email: {ADMIN_EMAIL}")
        
        # Try different authentication formats
        auth_formats = [
            # Format 1: JSON with email/password
            {"json": {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}},
            # Format 2: Form data with username/password (OAuth2PasswordRequestForm)
            {"data": {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}},
            # Format 3: JSON with username/password
            {"json": {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}}
        ]
        
        for i, auth_format in enumerate(auth_formats, 1):
            try:
                print(f"Trying authentication format {i}...")
                start_time = time.time()
                
                if "json" in auth_format:
                    response = self.session.post(f"{API_BASE}/auth/login", json=auth_format["json"], timeout=30)
                else:
                    response = self.session.post(f"{API_BASE}/auth/login", data=auth_format["data"], timeout=30)
                    
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get('access_token') or data.get('token')
                    if self.auth_token:
                        self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                        self.log_test("/auth/login", "POST", response.status_code, response_time, True, 
                                    f"Admin authentication successful (format {i}), token: {self.auth_token[:20]}...")
                        return True
                    else:
                        print(f"Format {i} - No access token in response: {data}")
                else:
                    print(f"Format {i} failed - Status: {response.status_code}, Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"Format {i} error: {str(e)}")
                continue
        
        # If all formats failed
        self.log_test("/auth/login", "POST", 0, 0, False, "All authentication formats failed")
        return False
    
    def test_endpoint(self, endpoint, method="GET", data=None, expected_status=200, description=""):
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
                    details += f" - Error: {response_data.get('detail', 'Unknown error')}"
            except:
                data_size = len(response.text)
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    details += f" - Error: {response.text[:100]}"
            
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size)
            return success, response
            
        except requests.exceptions.Timeout:
            self.log_test(endpoint, method, 0, 30.0, False, f"{description} - Request timeout")
            return False, None
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"{description} - Error: {str(e)}")
            return False, None

    def test_team_management_system(self):
        """Test Team Management & Workspace Collaboration System"""
        print(f"\n👥 TESTING TEAM MANAGEMENT & WORKSPACE COLLABORATION SYSTEM")
        
        # 1. Team Dashboard
        print(f"\n📊 Testing Team Management Dashboard...")
        self.test_endpoint("/team/dashboard", "GET", 
                         description="Team management dashboard with metrics")
        
        # 2. Get Team Members
        print(f"\n👤 Testing Get Team Members...")
        self.test_endpoint("/team/members", "GET",
                         description="Get team members with detailed information")
        
        # 3. Invite Team Member
        print(f"\n📧 Testing Team Member Invitation...")
        invite_data = {
            "email": "newmember@example.com",
            "role": "member",
            "permissions": ["read", "write"]
        }
        self.test_endpoint("/team/invite", "POST", data=invite_data,
                         description="Invite team member with role-based permissions")
        
        # 4. Accept Team Invitation (simulate)
        print(f"\n✅ Testing Accept Team Invitation...")
        accept_data = {
            "invitation_token": "sample_token_123",
            "accept": True
        }
        self.test_endpoint("/team/accept-invitation", "POST", data=accept_data,
                         description="Accept team invitation and join workspace")
        
        # 5. Update Team Member Role
        print(f"\n🔄 Testing Update Team Member Role...")
        update_data = {
            "role": "admin",
            "permissions": ["read", "write", "admin"]
        }
        self.test_endpoint("/team/members/sample_member_id", "PUT", data=update_data,
                         description="Update team member role/permissions")
        
        # 6. Remove Team Member
        print(f"\n🗑️ Testing Remove Team Member...")
        self.test_endpoint("/team/members/sample_member_id", "DELETE",
                         description="Remove team member from workspace")
        
        # 7. Get Team Activity Log
        print(f"\n📋 Testing Team Activity Log...")
        self.test_endpoint("/team/activity", "GET",
                         description="Get team activity log")

    def test_form_builder_system(self):
        """Test Form Builder System"""
        print(f"\n📝 TESTING FORM BUILDER SYSTEM")
        
        # 1. Forms Dashboard
        print(f"\n📊 Testing Forms Dashboard...")
        self.test_endpoint("/forms/dashboard", "GET",
                         description="Forms dashboard with analytics and overview")
        
        # 2. Get User's Forms
        print(f"\n📋 Testing Get User's Forms...")
        self.test_endpoint("/forms/forms", "GET",
                         description="Get user's forms with filtering and pagination")
        
        # 3. Create New Form
        print(f"\n➕ Testing Create New Form...")
        form_data = {
            "title": "Customer Feedback Form",
            "description": "Collect customer feedback and suggestions",
            "fields": [
                {
                    "type": "text",
                    "label": "Name",
                    "required": True
                },
                {
                    "type": "email",
                    "label": "Email Address",
                    "required": True
                },
                {
                    "type": "textarea",
                    "label": "Feedback",
                    "required": True
                },
                {
                    "type": "rating",
                    "label": "Overall Rating",
                    "required": False,
                    "max_rating": 5
                }
            ],
            "settings": {
                "allow_multiple_submissions": True,
                "require_login": False,
                "send_confirmation_email": True
            }
        }
        self.test_endpoint("/forms/create", "POST", data=form_data,
                         description="Create new form with validation")
        
        # 4. Get Form Details
        print(f"\n🔍 Testing Get Form Details...")
        self.test_endpoint("/forms/forms/sample_form_id", "GET",
                         description="Get form details with submission statistics")
        
        # 5. Update Form
        print(f"\n✏️ Testing Update Form...")
        update_form_data = {
            "title": "Updated Customer Feedback Form",
            "description": "Updated description for customer feedback collection",
            "fields": [
                {
                    "type": "text",
                    "label": "Full Name",
                    "required": True
                },
                {
                    "type": "email",
                    "label": "Email Address",
                    "required": True
                },
                {
                    "type": "textarea",
                    "label": "Detailed Feedback",
                    "required": True
                }
            ]
        }
        self.test_endpoint("/forms/forms/sample_form_id", "PUT", data=update_form_data,
                         description="Update form with validation")
        
        # 6. Submit Form Data
        print(f"\n📤 Testing Submit Form Data...")
        submission_data = {
            "form_id": "sample_form_id",
            "responses": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "feedback": "Great service! Very satisfied with the experience.",
                "rating": 5
            }
        }
        self.test_endpoint("/forms/submit", "POST", data=submission_data,
                         description="Submit form data with validation")
        
        # 7. Get Form Submissions
        print(f"\n📥 Testing Get Form Submissions...")
        self.test_endpoint("/forms/forms/sample_form_id/submissions", "GET",
                         description="Get form submissions with pagination")
        
        # 8. Delete Form
        print(f"\n🗑️ Testing Delete Form...")
        self.test_endpoint("/forms/forms/sample_form_id", "DELETE",
                         description="Delete form and all its submissions")

    def test_first_wave_regression(self):
        """Test First Wave Features for Regression"""
        print(f"\n🔄 TESTING FIRST WAVE FEATURES FOR REGRESSION")
        
        # 1. Subscription Management
        print(f"\n💳 Testing Subscription Management...")
        self.test_endpoint("/subscriptions/plans", "GET",
                         description="Get subscription plans")
        self.test_endpoint("/subscriptions/current", "GET",
                         description="Get current subscription")
        self.test_endpoint("/subscriptions/usage", "GET",
                         description="Get subscription usage")
        
        # 2. Google OAuth Integration
        print(f"\n🔐 Testing Google OAuth Integration...")
        self.test_endpoint("/oauth/google/url", "GET",
                         description="Get Google OAuth URL")
        self.test_endpoint("/oauth/status", "GET",
                         description="Get OAuth connection status")
        
        # 3. Financial Management
        print(f"\n💰 Testing Financial Management...")
        self.test_endpoint("/financial/dashboard", "GET",
                         description="Financial dashboard")
        self.test_endpoint("/financial/transactions", "GET",
                         description="Get financial transactions")
        self.test_endpoint("/financial/invoices", "GET",
                         description="Get invoices")
        
        # 4. Link Shortener
        print(f"\n🔗 Testing Link Shortener...")
        self.test_endpoint("/links/dashboard", "GET",
                         description="Link shortener dashboard")
        self.test_endpoint("/links/links", "GET",
                         description="Get shortened links")
        
        # Create a new short link
        link_data = {
            "original_url": "https://example.com/very-long-url-for-testing",
            "custom_slug": "test-link",
            "title": "Test Link"
        }
        self.test_endpoint("/links/create", "POST", data=link_data,
                         description="Create new short link")
        
        # 5. Analytics System
        print(f"\n📈 Testing Analytics System...")
        self.test_endpoint("/analytics-system/dashboard", "GET",
                         description="Analytics system dashboard")
        self.test_endpoint("/analytics-system/reports", "GET",
                         description="Get analytics reports")
        self.test_endpoint("/analytics-system/metrics", "GET",
                         description="Get system metrics")

    def run_comprehensive_test(self):
        """Run comprehensive second wave testing"""
        print("🚀 STARTING SECOND WAVE MIGRATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with testing")
            return
        
        # Test Second Wave Features
        self.test_team_management_system()
        self.test_form_builder_system()
        
        # Test First Wave for Regression
        self.test_first_wave_regression()
        
        # Print comprehensive results
        self.print_results()
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🎯 SECOND WAVE MIGRATION TESTING RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Calculate performance metrics
        response_times = []
        total_data_size = 0
        
        for result in self.test_results:
            if result['success']:
                try:
                    response_times.append(float(result['response_time'].replace('s', '')))
                    total_data_size += result['data_size']
                except:
                    pass
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Total Data Processed: {total_data_size:,} bytes")
        
        print(f"\n📋 DETAILED RESULTS:")
        
        # Group results by system
        systems = {
            "Authentication": [],
            "Team Management": [],
            "Form Builder": [],
            "Subscription Management": [],
            "Google OAuth": [],
            "Financial Management": [],
            "Link Shortener": [],
            "Analytics System": []
        }
        
        for result in self.test_results:
            endpoint = result['endpoint']
            if '/auth/' in endpoint:
                systems["Authentication"].append(result)
            elif '/team/' in endpoint:
                systems["Team Management"].append(result)
            elif '/forms/' in endpoint:
                systems["Form Builder"].append(result)
            elif '/subscriptions/' in endpoint:
                systems["Subscription Management"].append(result)
            elif '/oauth/' in endpoint:
                systems["Google OAuth"].append(result)
            elif '/financial/' in endpoint:
                systems["Financial Management"].append(result)
            elif '/links/' in endpoint:
                systems["Link Shortener"].append(result)
            elif '/analytics-system/' in endpoint:
                systems["Analytics System"].append(result)
        
        for system_name, results in systems.items():
            if results:
                passed = sum(1 for r in results if r['success'])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅ WORKING" if rate >= 75 else "⚠️ PARTIAL" if rate >= 50 else "❌ BROKEN"
                print(f"   {system_name}: {passed}/{total} ({rate:.1f}%) {status}")
        
        print(f"\n🎉 SECOND WAVE MIGRATION TESTING COMPLETED")
        print(f"Status: {'✅ SUCCESS' if success_rate >= 75 else '⚠️ NEEDS ATTENTION' if success_rate >= 50 else '❌ CRITICAL ISSUES'}")
        print("=" * 80)

if __name__ == "__main__":
    tester = SecondWaveTester()
    tester.run_comprehensive_test()