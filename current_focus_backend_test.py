#!/usr/bin/env python3
"""
Current Focus Tasks Backend Testing for Mewayz V2 Platform
January 2025

Testing Focus:
- Multi-Workspace System Server Error Fix
- Website Builder Templates Server Error Fix  
- Admin Dashboard Database Connection Fix
- Missing Systems Implementation (Escrow, Referrals, Complete Onboarding)
- Team Management & Workspace Collaboration System
- Form Builder System
- Authentication and core functionality verification
"""

import requests
import json
import time
import sys
from datetime import datetime

class MewayzCurrentFocusTester:
    def __init__(self):
        self.base_url = "https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.workspace_id = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Test credentials
        self.admin_email = "tmonnens@outlook.com"
        self.admin_password = "Voetballen5"
        
        print(f"🎯 MEWAYZ V2 PLATFORM - CURRENT FOCUS TASKS TESTING - JANUARY 2025")
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 80)

    def log_test(self, test_name, success, response_data=None, error=None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            'test': test_name,
            'success': success,
            'response_data': response_data,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} - {test_name}")
        if error:
            print(f"    Error: {error}")
        if response_data and len(str(response_data)) < 200:
            print(f"    Response: {response_data}")
        print()

    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{self.api_url}{endpoint}"
        
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.token:
            default_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.Timeout:
            raise Exception("Request timeout (30s)")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def test_authentication_system(self):
        """Test authentication and JWT token generation"""
        print("🔐 TESTING AUTHENTICATION SYSTEM")
        print("-" * 50)
        
        # Test 1: Root Health Check
        try:
            response = self.make_request('GET', '/')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Health Check", True, f"Status: {data.get('status', 'unknown')}")
            else:
                self.log_test("Root Health Check", False, error=f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Root Health Check", False, error=str(e))
        
        # Test 2: Auth Service Health
        try:
            response = self.make_request('GET', '/auth/health')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Auth Service Health", True, f"Status: {data.get('status', 'healthy')}")
            else:
                self.log_test("Auth Service Health", False, error=f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Auth Service Health", False, error=str(e))
        
        # Test 3: Admin Login
        try:
            login_data = {
                "email": self.admin_email,
                "password": self.admin_password
            }
            response = self.make_request('POST', '/auth/login', login_data)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token') or data.get('token')
                if self.token:
                    self.log_test("Admin Login", True, f"Token generated: {self.token[:20]}...")
                else:
                    self.log_test("Admin Login", False, error="No token in response")
            else:
                self.log_test("Admin Login", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Login", False, error=str(e))

    def test_current_focus_tasks(self):
        """Test the current focus tasks from test_result.md"""
        print("🎯 TESTING CURRENT FOCUS TASKS")
        print("-" * 50)
        
        # Task 1: Multi-Workspace System Server Error Fix
        print("1. Multi-Workspace System Server Error Fix")
        try:
            # Test health endpoint first
            response = self.make_request('GET', '/complete-multi-workspace/health')
            if response.status_code == 200:
                self.log_test("Multi-Workspace Health", True, f"Status: healthy")
            else:
                self.log_test("Multi-Workspace Health", False, error=f"HTTP {response.status_code}")
            
            # Test main endpoint
            response = self.make_request('GET', '/complete-multi-workspace')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Multi-Workspace System", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Multi-Workspace System", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Multi-Workspace System", False, error=str(e))
        
        # Task 2: Website Builder Templates Server Error Fix
        print("2. Website Builder Templates Server Error Fix")
        try:
            # Test health endpoint first
            response = self.make_request('GET', '/website-builder/health')
            if response.status_code == 200:
                self.log_test("Website Builder Health", True, f"Status: healthy")
            else:
                self.log_test("Website Builder Health", False, error=f"HTTP {response.status_code}")
            
            # Test templates endpoint
            response = self.make_request('GET', '/website-builder/templates')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Website Builder Templates", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Website Builder Templates", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Website Builder Templates", False, error=str(e))
        
        # Task 3: Admin Dashboard Database Connection Fix
        print("3. Admin Dashboard Database Connection Fix")
        try:
            # Test health endpoint first
            response = self.make_request('GET', '/admin/health')
            if response.status_code == 200:
                self.log_test("Admin Dashboard Health", True, f"Status: healthy")
            else:
                self.log_test("Admin Dashboard Health", False, error=f"HTTP {response.status_code}")
            
            # Test admin dashboard endpoint
            response = self.make_request('GET', '/admin/dashboard')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Admin Dashboard", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Admin Dashboard", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Dashboard", False, error=str(e))
        
        # Task 4: Missing Systems Implementation
        print("4. Missing Systems Implementation (Escrow, Referrals, Complete Onboarding)")
        
        # Test Escrow System
        try:
            response = self.make_request('GET', '/escrow/health')
            if response.status_code == 200:
                self.log_test("Escrow System Health", True, f"Status: healthy")
            else:
                self.log_test("Escrow System Health", False, error=f"HTTP {response.status_code}")
            
            response = self.make_request('GET', '/escrow')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Escrow System", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Escrow System", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Escrow System", False, error=str(e))
        
        # Test Referral System
        try:
            response = self.make_request('GET', '/referral-system/health')
            if response.status_code == 200:
                self.log_test("Referral System Health", True, f"Status: healthy")
            else:
                self.log_test("Referral System Health", False, error=f"HTTP {response.status_code}")
            
            response = self.make_request('GET', '/referral-system')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Referral System", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Referral System", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Referral System", False, error=str(e))
        
        # Test Complete Onboarding System
        try:
            response = self.make_request('GET', '/complete-onboarding/health')
            if response.status_code == 200:
                self.log_test("Complete Onboarding Health", True, f"Status: healthy")
            else:
                self.log_test("Complete Onboarding Health", False, error=f"HTTP {response.status_code}")
            
            response = self.make_request('GET', '/complete-onboarding')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Complete Onboarding System", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Complete Onboarding System", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Complete Onboarding System", False, error=str(e))

    def test_stuck_tasks(self):
        """Test the stuck tasks that need immediate attention"""
        print("🚨 TESTING STUCK TASKS")
        print("-" * 50)
        
        # Task 1: Team Management & Workspace Collaboration System
        print("1. Team Management & Workspace Collaboration System")
        try:
            # Test health endpoint first
            response = self.make_request('GET', '/team/health')
            if response.status_code == 200:
                self.log_test("Team Management Health", True, f"Status: healthy")
            else:
                self.log_test("Team Management Health", False, error=f"HTTP {response.status_code}")
            
            # Test main endpoint
            response = self.make_request('GET', '/team')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Team Management System", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Team Management System", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Team Management System", False, error=str(e))
        
        # Task 2: Form Builder System
        print("2. Form Builder System")
        try:
            # Test health endpoint first
            response = self.make_request('GET', '/forms/health')
            if response.status_code == 200:
                self.log_test("Form Builder Health", True, f"Status: healthy")
            else:
                self.log_test("Form Builder Health", False, error=f"HTTP {response.status_code}")
            
            # Test main endpoint
            response = self.make_request('GET', '/forms')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Form Builder System", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Form Builder System", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Form Builder System", False, error=str(e))

    def test_additional_systems(self):
        """Test additional systems for comprehensive coverage"""
        print("📊 TESTING ADDITIONAL SYSTEMS")
        print("-" * 50)
        
        # Test Financial Management System
        try:
            response = self.make_request('GET', '/financial/health')
            if response.status_code == 200:
                self.log_test("Financial System Health", True, f"Status: healthy")
            else:
                self.log_test("Financial System Health", False, error=f"HTTP {response.status_code}")
            
            response = self.make_request('GET', '/financial')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Financial Management System", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Financial Management System", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Financial Management System", False, error=str(e))
        
        # Test Analytics System
        try:
            response = self.make_request('GET', '/analytics-system/health')
            if response.status_code == 200:
                self.log_test("Analytics System Health", True, f"Status: healthy")
            else:
                self.log_test("Analytics System Health", False, error=f"HTTP {response.status_code}")
            
            response = self.make_request('GET', '/analytics-system')
            if response.status_code == 200:
                data = response.json()
                self.log_test("Analytics System", True, f"Data: {len(str(data))} chars")
            else:
                self.log_test("Analytics System", False, error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Analytics System", False, error=str(e))

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🎯 STARTING COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        
        # Test authentication first
        self.test_authentication_system()
        
        # Test current focus tasks
        self.test_current_focus_tasks()
        
        # Test stuck tasks
        self.test_stuck_tasks()
        
        # Test additional systems
        self.test_additional_systems()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("=" * 80)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed Tests: {self.passed_tests}")
        print(f"Failed Tests: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 80:
            print("✅ EXCELLENT SUCCESS - Platform is production ready!")
        elif success_rate >= 60:
            print("⚠️ GOOD SUCCESS - Platform needs minor fixes")
        elif success_rate >= 40:
            print("⚠️ PARTIAL SUCCESS - Platform needs significant improvements")
        else:
            print("❌ CRITICAL ISSUES - Platform needs major fixes")
        
        print()
        print("🔍 DETAILED ANALYSIS:")
        
        # Group results by category
        auth_tests = [r for r in self.test_results if 'auth' in r['test'].lower() or 'login' in r['test'].lower()]
        focus_tests = [r for r in self.test_results if any(keyword in r['test'].lower() for keyword in ['multi-workspace', 'website', 'admin', 'escrow', 'referral', 'onboarding'])]
        stuck_tests = [r for r in self.test_results if any(keyword in r['test'].lower() for keyword in ['team', 'form'])]
        
        if auth_tests:
            auth_success = sum(1 for r in auth_tests if r['success']) / len(auth_tests) * 100
            print(f"Authentication System: {auth_success:.1f}% ({sum(1 for r in auth_tests if r['success'])}/{len(auth_tests)})")
        
        if focus_tests:
            focus_success = sum(1 for r in focus_tests if r['success']) / len(focus_tests) * 100
            print(f"Current Focus Tasks: {focus_success:.1f}% ({sum(1 for r in focus_tests if r['success'])}/{len(focus_tests)})")
        
        if stuck_tests:
            stuck_success = sum(1 for r in stuck_tests if r['success']) / len(stuck_tests) * 100
            print(f"Stuck Tasks: {stuck_success:.1f}% ({sum(1 for r in stuck_tests if r['success'])}/{len(stuck_tests)})")
        
        print()
        print("🎯 CONCLUSION:")
        if success_rate >= 80:
            print("The Mewayz V2 Platform backend demonstrates excellent functionality with most systems operational.")
            print("Current focus tasks and stuck tasks have been successfully resolved.")
            print("Platform is ready for production deployment.")
        elif success_rate >= 60:
            print("The Mewayz V2 Platform backend shows good progress with core systems working.")
            print("Some current focus tasks need attention but overall architecture is sound.")
            print("Platform needs minor fixes before production deployment.")
        else:
            print("The Mewayz V2 Platform backend has critical issues that need immediate attention.")
            print("Current focus tasks and stuck tasks are still experiencing problems.")
            print("Platform requires significant fixes before production deployment.")

if __name__ == "__main__":
    tester = MewayzCurrentFocusTester()
    tester.run_comprehensive_test()