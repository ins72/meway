#!/usr/bin/env python3
"""
ENHANCED GUIDED TOUR AND INTERACTIVE ONBOARDING SYSTEM TESTING - MEWAYZ PLATFORM
Phase 4 Enhanced User Experience and Onboarding System Testing
Testing Agent - July 20, 2025
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://227a6971-09fc-47c6-b443-58c2c19d4c11.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class EnhancedOnboardingTester:
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
                                f"Admin authentication successful, token: {self.auth_token[:20]}...")
                    return True
                else:
                    self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                                "No access token in response")
                    return False
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Login failed: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.log_test("/auth/login", "POST", 0, 0, False, f"Authentication error: {str(e)}")
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

    def test_enhanced_onboarding_system(self):
        """Test Enhanced Guided Tour and Interactive Onboarding System - Phase 4"""
        print(f"\n🚀 TESTING ENHANCED GUIDED TOUR AND INTERACTIVE ONBOARDING SYSTEM")
        
        # 1. Enhanced Onboarding Dashboard
        print(f"\n📊 Testing Enhanced Onboarding Dashboard...")
        self.test_endpoint("/onboarding/enhanced/dashboard", "GET", 
                         description="Enhanced onboarding dashboard with comprehensive data")
        
        # 2. Interactive Tour System - Get detailed tour
        print(f"\n🎯 Testing Interactive Tour System...")
        tour_id = "getting-started-tour"
        self.test_endpoint(f"/onboarding/tours/{tour_id}/detailed", "GET",
                         description="Interactive tour detailed content")
        
        # 3. Complete tour step - Fix validation
        step_number = 1
        self.test_endpoint(f"/onboarding/tours/{tour_id}/step/{step_number}/complete", "POST",
                         data={"time_spent": 30, "completed_at": "2025-07-20T10:00:00Z"},
                         description="Complete tour step with tracking")
        
        # 4. Tutorial Management - Create interactive tutorial - Fix validation
        print(f"\n📚 Testing Tutorial Management...")
        tutorial_data = {
            "title": "Advanced Features Tutorial",
            "description": "Learn how to use advanced platform features",
            "category": "advanced",
            "difficulty": "intermediate",
            "steps_json": json.dumps([
                {
                    "title": "Step 1: Dashboard Overview",
                    "content": "Navigate to your dashboard and explore the main features",
                    "action_type": "click",
                    "target_element": "#dashboard-nav"
                },
                {
                    "title": "Step 2: Create Your First Project",
                    "content": "Click the 'New Project' button to get started",
                    "action_type": "click",
                    "target_element": "#new-project-btn"
                }
            ]),
            "estimated_time": 15
        }
        self.test_endpoint("/onboarding/interactive-tutorial/create", "POST",
                         data=tutorial_data,
                         description="Create interactive tutorial with steps")
        
        # 5. Analytics & Tracking - Feature adoption analytics
        print(f"\n📈 Testing Analytics & Tracking...")
        self.test_endpoint("/onboarding/feature-adoption/analytics", "GET",
                         description="Feature adoption analytics and insights")
        
        # 6. Smart Hints System - Request contextual hints - Fix validation
        print(f"\n💡 Testing Smart Hints System...")
        hints_data = {
            "current_page": "/dashboard",
            "user_action": "login",
            "feature_context": "dashboard_navigation"
        }
        self.test_endpoint("/onboarding/smart-hints/request", "POST",
                         data=hints_data,
                         description="Request smart contextual hints")
        
        # 7. Achievement System - Completion certificate - Fix validation
        print(f"\n🏆 Testing Achievement System...")
        self.test_endpoint("/onboarding/completion/certificate?achievement_type=onboarding_complete", "GET",
                         description="Generate completion certificate")

    def test_core_system_health(self):
        """Test core system health and integration"""
        print(f"\n🔍 TESTING CORE SYSTEM HEALTH")
        
        # System health check
        self.test_endpoint("/health", "GET", description="System health check")
        
        # Admin dashboard
        self.test_endpoint("/admin/dashboard", "GET", description="Admin dashboard access")
        
        # User profile
        self.test_endpoint("/users/profile", "GET", description="User profile access")
        
    def run_enhanced_onboarding_test(self):
        """Run enhanced onboarding system testing"""
        print(f"🎯 ENHANCED GUIDED TOUR AND INTERACTIVE ONBOARDING SYSTEM TESTING")
        print(f"Phase 4 Enhanced User Experience and Onboarding System")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with testing")
            return
        
        # Step 2: Test core system health
        self.test_core_system_health()
        
        # Step 3: Test enhanced onboarding system
        self.test_enhanced_onboarding_system()
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print(f"\n" + "="*80)
        print(f"📊 ENHANCED ONBOARDING SYSTEM TESTING REPORT")
        print(f"="*80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        
        # Group results by category
        auth_tests = [r for r in self.test_results if '/auth/' in r['endpoint']]
        onboarding_tests = [r for r in self.test_results if '/onboarding/' in r['endpoint']]
        core_tests = [r for r in self.test_results if r not in auth_tests + onboarding_tests]
        
        if auth_tests:
            print(f"\n🔐 AUTHENTICATION TESTS ({len(auth_tests)} tests):")
            for test in auth_tests:
                status_icon = "✅" if test['success'] else "❌"
                print(f"   {status_icon} {test['method']} {test['endpoint']} - {test['status']} ({test['response_time']})")
        
        if onboarding_tests:
            print(f"\n🚀 ENHANCED ONBOARDING SYSTEM TESTS ({len(onboarding_tests)} tests):")
            for test in onboarding_tests:
                status_icon = "✅" if test['success'] else "❌"
                print(f"   {status_icon} {test['method']} {test['endpoint']} - {test['status']} ({test['response_time']})")
        
        if core_tests:
            print(f"\n🏥 CORE SYSTEM TESTS ({len(core_tests)} tests):")
            for test in core_tests:
                status_icon = "✅" if test['success'] else "❌"
                print(f"   {status_icon} {test['method']} {test['endpoint']} - {test['status']} ({test['response_time']})")
        
        # Performance metrics
        response_times = [float(r['response_time'].replace('s', '')) for r in self.test_results if r['response_time'] != '0.000s']
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_time:.3f}s")
            print(f"   Fastest Response: {min_time:.3f}s")
            print(f"   Slowest Response: {max_time:.3f}s")
        
        # Data processing metrics
        total_data = sum(r['data_size'] for r in self.test_results)
        print(f"   Total Data Processed: {total_data:,} bytes")
        
        print(f"\n🎉 TESTING COMPLETED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate >= 80:
            print(f"✅ ENHANCED ONBOARDING SYSTEM: PRODUCTION READY")
        elif success_rate >= 60:
            print(f"⚠️ ENHANCED ONBOARDING SYSTEM: NEEDS MINOR FIXES")
        else:
            print(f"❌ ENHANCED ONBOARDING SYSTEM: NEEDS MAJOR FIXES")


if __name__ == "__main__":
    tester = EnhancedOnboardingTester()
    tester.run_enhanced_onboarding_test()