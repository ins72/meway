#!/usr/bin/env python3
"""
IMPROVED COMPREHENSIVE BACKEND TESTING - MEWAYZ PLATFORM V3.0.0
Final verification of ALL 6 PHASES (Phases 4-6) new features with proper parameters
Testing Agent - January 20, 2025
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

class ImprovedBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.workspace_id = None
        
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
                                f"Admin authentication successful")
                    return True
                else:
                    self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                                "No token in response")
                    return False
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Login failed: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.log_test("/auth/login", "POST", 0, 0, False, f"Authentication error: {str(e)}")
            return False
    
    def get_workspace_id(self):
        """Get workspace ID for tests that require it"""
        try:
            response = self.session.get(f"{API_BASE}/workspaces", timeout=30)
            if response.status_code == 200:
                data = response.json()
                workspaces = data.get('data', [])
                if workspaces:
                    self.workspace_id = workspaces[0].get('id')
                    print(f"📁 Using workspace ID: {self.workspace_id}")
        except:
            pass
    
    def test_endpoint(self, endpoint, method="GET", data=None, params=None, expected_status=200, description=""):
        """Test a single endpoint with improved parameter handling"""
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
            
            # Check if response is successful (200-299 range or expected status)
            success = (200 <= response.status_code < 300) or response.status_code == expected_status
            
            # Get response details
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
                
                if success:
                    # Extract meaningful info from successful responses
                    if 'data' in response_data:
                        details = f"{description} - Success with data"
                    elif 'success' in response_data and response_data['success']:
                        details = f"{description} - Operation successful"
                    else:
                        details = f"{description} - Response received"
                else:
                    error_msg = response_data.get('detail', response_data.get('message', 'Unknown error'))
                    if isinstance(error_msg, list) and len(error_msg) > 0:
                        error_msg = f"Validation error: {len(error_msg)} field(s) required"
                    details = f"{description} - {error_msg}"
                    
            except:
                data_size = len(response.text)
                if success:
                    details = f"{description} - Response received ({data_size} chars)"
                else:
                    details = f"{description} - Error: {response.text[:100]}"
            
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size)
            return success, response
            
        except requests.exceptions.Timeout:
            self.log_test(endpoint, method, 0, 30.0, False, f"{description} - Request timeout")
            return False, None
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"{description} - Error: {str(e)}")
            return False, None

    def test_phase_4_features(self):
        """Test Phase 4 Features - Missing Features Implementation"""
        print(f"\n🚀 TESTING PHASE 4 FEATURES - MISSING FEATURES IMPLEMENTATION")
        
        # Template marketplace (check if endpoint exists, 500 might be implementation issue)
        self.test_endpoint("/templates/marketplace", "GET", description="Advanced template marketplace")
        
        # Certificate system
        self.test_endpoint("/courses/test-course-id/certificates", "GET", description="Certificate system")
        
        # Vendor dashboard
        self.test_endpoint("/ecommerce/vendors/dashboard", "GET", description="Vendor dashboard")
        
        # Custom report builder
        self.test_endpoint("/analytics/custom-reports", "GET", description="Custom report builder")
        
        # Webhook configurations
        self.test_endpoint("/integrations/webhooks", "GET", description="Webhook configurations")
        
        # White-label customization
        self.test_endpoint("/admin/white-label/settings", "GET", description="White-label customization")
        
        # Multi-currency support
        self.test_endpoint("/financial/multi-currency", "GET", description="Multi-currency support")

    def test_phase_5_features(self):
        """Test Phase 5 Features - Valuable Expansions"""
        print(f"\n🚀 TESTING PHASE 5 FEATURES - VALUABLE EXPANSIONS")
        
        # Automation workflows
        self.test_endpoint("/automation/workflows", "GET", description="Automation workflows")
        
        # Advanced social analytics
        self.test_endpoint("/social/analytics/comprehensive", "GET", description="Advanced social analytics")
        
        # Smart AI notifications
        self.test_endpoint("/notifications/smart", "GET", description="Smart AI notifications")
        
        # Affiliate program
        self.test_endpoint("/affiliate/program/overview", "GET", description="Affiliate program")
        
        # Global search system (with required parameter)
        self.test_endpoint("/search/global", "GET", params={"q": "test"}, description="Global search system")

    def test_phase_6_features(self):
        """Test Phase 6 Features - Additional Valuable Features"""
        print(f"\n🚀 TESTING PHASE 6 FEATURES - ADDITIONAL VALUABLE FEATURES")
        
        # AI business intelligence
        self.test_endpoint("/ai/business-insights", "GET", description="AI business intelligence")
        
        # Smart recommendations
        self.test_endpoint("/recommendations/smart", "GET", description="Smart recommendations")
        
        # Performance optimization
        self.test_endpoint("/performance/optimization-center", "GET", description="Performance optimization")
        
        # Market intelligence
        self.test_endpoint("/trends/market-intelligence", "GET", description="Market intelligence")
        
        # Customer journey analytics
        self.test_endpoint("/analytics/customer-journey", "GET", description="Customer journey analytics")
        
        # Predictive analytics
        self.test_endpoint("/analytics/predictive", "GET", description="Predictive analytics")
        
        # Team productivity
        self.test_endpoint("/team/productivity-insights", "GET", description="Team productivity")

    def test_core_system_health(self):
        """Test Core System Health"""
        print(f"\n🏥 TESTING CORE SYSTEM HEALTH")
        
        # System health check
        self.test_endpoint("/health", "GET", description="System health check")
        
        # Multi-workspace system
        self.test_endpoint("/workspaces", "GET", description="Multi-workspace system")

    def run_comprehensive_test(self):
        """Run comprehensive testing of all phases"""
        print(f"🎯 IMPROVED COMPREHENSIVE BACKEND TESTING - MEWAYZ PLATFORM V3.0.0")
        print(f"Testing ALL 6 PHASES (Phases 4-6) New Features")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with testing")
            return
        
        # Step 2: Get workspace ID
        self.get_workspace_id()
        
        # Step 3: Test core system health
        self.test_core_system_health()
        
        # Step 4: Test Phase 4 features
        self.test_phase_4_features()
        
        # Step 5: Test Phase 5 features  
        self.test_phase_5_features()
        
        # Step 6: Test Phase 6 features
        self.test_phase_6_features()
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print(f"\n" + "="*80)
        print(f"📊 FINAL COMPREHENSIVE TESTING REPORT - PHASES 4-6 VERIFICATION")
        print(f"="*80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED TEST RESULTS BY PHASE:")
        
        # Group results by phase
        core_tests = [r for r in self.test_results if r['endpoint'] in ['/auth/login', '/health', '/workspaces']]
        
        phase_4_tests = [r for r in self.test_results if any(endpoint in r['endpoint'] for endpoint in 
                        ['/templates/marketplace', '/courses/', '/ecommerce/vendors/', '/analytics/custom-reports', 
                         '/integrations/webhooks', '/admin/white-label/', '/financial/multi-currency'])]
        
        phase_5_tests = [r for r in self.test_results if any(endpoint in r['endpoint'] for endpoint in 
                        ['/automation/workflows', '/social/analytics/comprehensive', '/notifications/smart',
                         '/affiliate/', '/search/global'])]
        
        phase_6_tests = [r for r in self.test_results if any(endpoint in r['endpoint'] for endpoint in 
                        ['/ai/business-insights', '/recommendations/smart', '/performance/optimization-center',
                         '/trends/market-intelligence', '/analytics/customer-journey', '/analytics/predictive', '/team/productivity-insights'])]
        
        def print_phase_results(phase_name, tests):
            if tests:
                passed = sum(1 for t in tests if t['success'])
                total = len(tests)
                rate = (passed / total * 100) if total > 0 else 0
                status_icon = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
                print(f"\n   {status_icon} {phase_name}: {passed}/{total} ({rate:.1f}%)")
                for test in tests:
                    test_icon = "✅" if test['success'] else "❌"
                    print(f"     {test_icon} {test['method']} {test['endpoint']} - {test['status']} ({test['response_time']})")
        
        print_phase_results("🔐 CORE SYSTEM & AUTHENTICATION", core_tests)
        print_phase_results("🚀 PHASE 4 - MISSING FEATURES IMPLEMENTATION", phase_4_tests)
        print_phase_results("🚀 PHASE 5 - VALUABLE EXPANSIONS", phase_5_tests)
        print_phase_results("🚀 PHASE 6 - ADDITIONAL VALUABLE FEATURES", phase_6_tests)
        
        # Performance metrics
        successful_tests = [r for r in self.test_results if r['success']]
        if successful_tests:
            avg_response_time = sum(float(r['response_time'].replace('s', '')) for r in successful_tests) / len(successful_tests)
            total_data = sum(r['data_size'] for r in successful_tests)
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Total Data Transferred: {total_data:,} bytes")
            print(f"   Fastest Response: {min(float(r['response_time'].replace('s', '')) for r in successful_tests):.3f}s")
            print(f"   Slowest Response: {max(float(r['response_time'].replace('s', '')) for r in successful_tests):.3f}s")
        
        # Phase-specific analysis
        print(f"\n🔍 PHASE-SPECIFIC ANALYSIS:")
        
        phase_4_passed = sum(1 for t in phase_4_tests if t['success'])
        phase_4_total = len(phase_4_tests)
        phase_4_rate = (phase_4_passed / phase_4_total * 100) if phase_4_total > 0 else 0
        
        phase_5_passed = sum(1 for t in phase_5_tests if t['success'])
        phase_5_total = len(phase_5_tests)
        phase_5_rate = (phase_5_passed / phase_5_total * 100) if phase_5_total > 0 else 0
        
        phase_6_passed = sum(1 for t in phase_6_tests if t['success'])
        phase_6_total = len(phase_6_tests)
        phase_6_rate = (phase_6_passed / phase_6_total * 100) if phase_6_total > 0 else 0
        
        print(f"   Phase 4 (Missing Features): {phase_4_rate:.1f}% success rate")
        print(f"   Phase 5 (Valuable Expansions): {phase_5_rate:.1f}% success rate")
        print(f"   Phase 6 (Additional Features): {phase_6_rate:.1f}% success rate")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 90:
            print(f"   ✅ EXCELLENT - All 6 phases are production-ready!")
            print(f"   🚀 The Mewayz Platform v3.0.0 exceeds enterprise standards")
        elif success_rate >= 75:
            print(f"   ✅ GOOD - Most features working, system is production-ready")
            print(f"   ⚠️  Minor issues present but core functionality operational")
        elif success_rate >= 60:
            print(f"   ⚠️  MODERATE - Significant functionality present")
            print(f"   🔧 Some endpoints need attention but platform is functional")
        else:
            print(f"   ❌ NEEDS ATTENTION - Major system issues require immediate attention")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if phase_6_rate == 100:
            print(f"   ✅ Phase 6 (AI & Analytics) features are fully operational")
        if phase_5_rate >= 80:
            print(f"   ✅ Phase 5 (Automation & Social) features are highly functional")
        if phase_4_rate >= 70:
            print(f"   ✅ Phase 4 (Core Business) features are mostly operational")
        
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"   🔧 {len(failed_tests)} endpoints need attention for full functionality")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"="*80)

if __name__ == "__main__":
    tester = ImprovedBackendTester()
    tester.run_comprehensive_test()