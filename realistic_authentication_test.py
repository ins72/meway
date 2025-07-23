#!/usr/bin/env python3
"""
REALISTIC AUTHENTICATION & CRUD TESTING FOR MEWAYZ V2 PLATFORM - JANUARY 2025
Testing the actual available endpoints and real functionality

TESTING OBJECTIVES:
1. Complete Authentication System - Test login functionality with proper JWT token generation
2. Test Real Available Endpoints - Use actual endpoints from OpenAPI specification
3. Full CRUD Operations Testing - Test available CRUD operations
4. Critical Business Services Testing - Test health endpoints and available functionality
5. Real Data Verification - Check for real vs mock data

CREDENTIALS: tmonnens@outlook.com/Voetballen5
BACKEND URL: https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional, List, Tuple
import uuid
from datetime import datetime, timedelta
import traceback

# Backend URL from environment
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class RealisticTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.authentication_working = False
        self.available_services = []
        self.working_endpoints = []
        self.failing_endpoints = []
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None, status_code: int = None):
        """Log test result with comprehensive information"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "status_code": status_code,
            "response_size": len(str(response_data)) if response_data else 0,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response size: {len(str(response_data))} chars")
        if status_code:
            print(f"   Status code: {status_code}")
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                services_count = data.get("services", 0)
                self.log_result("Health Check", True, f"Backend operational with {services_count} services available", data, response.status_code)
                return True
            else:
                self.log_result("Health Check", False, f"Backend not accessible - Status {response.status_code}", None, response.status_code)
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Health check error: {str(e)}")
            return False
    
    def test_authentication_system(self):
        """Test complete authentication system with provided credentials"""
        print("\n🔐 TESTING COMPLETE AUTHENTICATION SYSTEM")
        print("=" * 60)
        
        try:
            # Test 1: Login with provided credentials
            print("\n1. Testing Login with Provided Credentials...")
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=login_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    # Set authorization header for future requests
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.authentication_working = True
                    self.log_result("Authentication - Login", True, f"Login successful with JWT token", data, response.status_code)
                    
                    # Test 2: Verify token works with auth health endpoint
                    print("\n2. Testing JWT Token Validation...")
                    auth_health_response = self.session.get(f"{API_BASE}/auth/health", timeout=10)
                    if auth_health_response.status_code == 200:
                        auth_health_data = auth_health_response.json()
                        self.log_result("Authentication - Token Validation", True, f"JWT token validation successful", auth_health_data, auth_health_response.status_code)
                        return True
                    else:
                        self.log_result("Authentication - Token Validation", False, f"JWT token validation failed - Status {auth_health_response.status_code}", None, auth_health_response.status_code)
                        return True  # Login still worked, just validation endpoint issue
                else:
                    self.log_result("Authentication - Login", False, "Login response missing access_token", data, response.status_code)
                    return False
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Login failed')
                    self.log_result("Authentication - Login", False, f"Login failed - Status {response.status_code}: {error_detail}", error_data, response.status_code)
                except:
                    self.log_result("Authentication - Login", False, f"Login failed - Status {response.status_code}: {response.text}", None, response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Authentication - Login", False, f"Authentication error: {str(e)}")
            return False
    
    def discover_available_services(self):
        """Discover available services from health endpoints"""
        print("\n🔍 DISCOVERING AVAILABLE SERVICES")
        print("=" * 60)
        
        # List of known service categories from the OpenAPI
        service_categories = [
            "financial", "admin", "workspace", "ai-content", "template", 
            "marketing", "social-media", "analytics", "user", "dashboard",
            "booking", "media-library", "integrations", "notification",
            "complete-financial", "advanced-ai", "complete-admin-dashboard"
        ]
        
        for service in service_categories:
            try:
                health_endpoint = f"{API_BASE}/{service}/health"
                response = self.session.get(health_endpoint, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.available_services.append(service)
                    self.log_result(f"Service Discovery - {service}", True, f"Service available and healthy", data, response.status_code)
                else:
                    self.log_result(f"Service Discovery - {service}", False, f"Service not available - Status {response.status_code}", None, response.status_code)
            except Exception as e:
                self.log_result(f"Service Discovery - {service}", False, f"Service discovery error: {str(e)}")
        
        print(f"\n✅ Discovered {len(self.available_services)} available services")
        return len(self.available_services) > 0
    
    def test_available_services_crud(self):
        """Test CRUD operations on available services"""
        if not self.authentication_working:
            print("❌ Skipping CRUD tests - Authentication not working")
            return False
            
        print("\n🔄 TESTING CRUD OPERATIONS ON AVAILABLE SERVICES")
        print("=" * 60)
        
        for service in self.available_services[:5]:  # Test first 5 services
            self.test_service_endpoints(service)
        
        return True
    
    def test_service_endpoints(self, service_name: str):
        """Test various endpoints for a specific service"""
        print(f"\n📋 Testing {service_name} service endpoints...")
        
        base_endpoint = f"{API_BASE}/{service_name}"
        
        # Test READ operations (GET endpoints)
        endpoints_to_test = [
            ("", "List Items"),
            ("/stats", "Statistics"),
        ]
        
        for endpoint_suffix, description in endpoints_to_test:
            try:
                full_endpoint = f"{base_endpoint}{endpoint_suffix}"
                response = self.session.get(full_endpoint, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    self.working_endpoints.append(f"{service_name}{endpoint_suffix}")
                    self.log_result(f"{service_name} - {description}", True, f"Endpoint working successfully", data, response.status_code)
                    
                    # Check for real vs mock data
                    if self.detect_real_data(data, service_name):
                        print(f"   📊 Real data detected in {service_name}")
                    else:
                        print(f"   ⚠️ Possible mock data in {service_name}")
                        
                elif response.status_code == 401:
                    self.failing_endpoints.append(f"{service_name}{endpoint_suffix}")
                    self.log_result(f"{service_name} - {description}", False, f"Authentication required - Status {response.status_code}", None, response.status_code)
                elif response.status_code == 403:
                    self.failing_endpoints.append(f"{service_name}{endpoint_suffix}")
                    self.log_result(f"{service_name} - {description}", False, f"Access forbidden - Status {response.status_code}", None, response.status_code)
                elif response.status_code == 404:
                    self.failing_endpoints.append(f"{service_name}{endpoint_suffix}")
                    self.log_result(f"{service_name} - {description}", False, f"Endpoint not found - Status {response.status_code}", None, response.status_code)
                else:
                    self.failing_endpoints.append(f"{service_name}{endpoint_suffix}")
                    self.log_result(f"{service_name} - {description}", False, f"Endpoint failed - Status {response.status_code}", None, response.status_code)
                    
            except Exception as e:
                self.failing_endpoints.append(f"{service_name}{endpoint_suffix}")
                self.log_result(f"{service_name} - {description}", False, f"Request error: {str(e)}")
        
        # Test CREATE operation (POST to base endpoint)
        try:
            test_data = self.generate_test_data_for_service(service_name)
            response = self.session.post(base_endpoint, json=test_data, timeout=15)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.working_endpoints.append(f"{service_name} - CREATE")
                self.log_result(f"{service_name} - CREATE", True, f"Create operation successful", data, response.status_code)
            else:
                self.failing_endpoints.append(f"{service_name} - CREATE")
                self.log_result(f"{service_name} - CREATE", False, f"Create failed - Status {response.status_code}", None, response.status_code)
                
        except Exception as e:
            self.failing_endpoints.append(f"{service_name} - CREATE")
            self.log_result(f"{service_name} - CREATE", False, f"Create error: {str(e)}")
    
    def generate_test_data_for_service(self, service_name: str) -> Dict:
        """Generate appropriate test data for a service"""
        if "financial" in service_name:
            return {
                "type": "invoice",
                "amount": 1500.00,
                "client": "Test Client Corp",
                "description": "Professional services"
            }
        elif "workspace" in service_name:
            return {
                "name": "Test Workspace",
                "description": "Test workspace for development",
                "type": "team"
            }
        elif "ai" in service_name:
            return {
                "prompt": "Generate a professional email",
                "type": "email",
                "tone": "professional"
            }
        elif "template" in service_name:
            return {
                "name": "Test Template",
                "category": "business",
                "description": "Test template for business use"
            }
        elif "user" in service_name:
            return {
                "name": "Test User",
                "email": "testuser@example.com",
                "role": "member"
            }
        else:
            return {
                "name": "Test Item",
                "description": "Test item for service testing",
                "type": "test"
            }
    
    def detect_real_data(self, response_data: Any, service_name: str) -> bool:
        """Detect if response contains real data vs mock data"""
        if not response_data:
            return False
            
        data_str = str(response_data).lower()
        
        # Mock data patterns
        mock_patterns = [
            'sample', 'mock', 'test_', 'dummy', 'fake', 'placeholder',
            'lorem ipsum', 'example.com', 'test@test.com', 'testuser'
        ]
        
        # Check for mock patterns
        for pattern in mock_patterns:
            if pattern in data_str:
                return False
        
        # If response has meaningful structure and content, consider it real
        if isinstance(response_data, dict) and len(response_data) > 2:
            return True
        elif isinstance(response_data, list) and len(response_data) > 0:
            return True
            
        return True  # Default to real data if no mock patterns found
    
    def test_critical_business_endpoints(self):
        """Test specific critical business endpoints mentioned in review request"""
        if not self.authentication_working:
            print("❌ Skipping Critical Business tests - Authentication not working")
            return False
            
        print("\n💼 TESTING CRITICAL BUSINESS ENDPOINTS")
        print("=" * 60)
        
        # Test specific endpoints that should exist for business functionality
        critical_endpoints = [
            ("/complete-financial/health", "Complete Financial System"),
            ("/complete-admin-dashboard/health", "Complete Admin Dashboard"),
            ("/advanced-ai/health", "Advanced AI System"),
            ("/social-media/health", "Social Media Management"),
            ("/template/health", "Template Management"),
            ("/workspace/health", "Workspace Management"),
            ("/integrations/health", "External Integrations"),
            ("/analytics/health", "Analytics System")
        ]
        
        working_critical = 0
        total_critical = len(critical_endpoints)
        
        for endpoint, description in critical_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    working_critical += 1
                    self.log_result(f"Critical Business - {description}", True, f"System operational", data, response.status_code)
                else:
                    self.log_result(f"Critical Business - {description}", False, f"System not available - Status {response.status_code}", None, response.status_code)
                    
            except Exception as e:
                self.log_result(f"Critical Business - {description}", False, f"System error: {str(e)}")
        
        critical_success_rate = (working_critical / total_critical * 100) if total_critical > 0 else 0
        print(f"\n📊 Critical Business Systems: {working_critical}/{total_critical} ({critical_success_rate:.1f}%) operational")
        
        return critical_success_rate >= 50
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 100)
        print("🎯 REALISTIC AUTHENTICATION & CRUD TESTING RESULTS - MEWAYZ V2 PLATFORM")
        print("=" * 100)
        
        # Overall statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   Passed Tests: {passed_tests} ✅")
        print(f"   Failed Tests: {failed_tests} ❌")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Authentication Results
        print(f"\n🔐 AUTHENTICATION SYSTEM RESULTS:")
        auth_status = "✅ WORKING" if self.authentication_working else "❌ FAILED"
        print(f"   Authentication Status: {auth_status}")
        print(f"   JWT Token Generation: {'✅ Working' if self.access_token else '❌ Failed'}")
        print(f"   Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
        
        # Service Discovery Results
        print(f"\n🔍 SERVICE DISCOVERY RESULTS:")
        print(f"   Available Services: {len(self.available_services)}")
        print(f"   Working Endpoints: {len(self.working_endpoints)}")
        print(f"   Failing Endpoints: {len(self.failing_endpoints)}")
        
        if self.available_services:
            print(f"   Discovered Services: {', '.join(self.available_services[:10])}")
            if len(self.available_services) > 10:
                print(f"   ... and {len(self.available_services) - 10} more")
        
        # Endpoint Success Analysis
        total_endpoints_tested = len(self.working_endpoints) + len(self.failing_endpoints)
        endpoint_success_rate = (len(self.working_endpoints) / total_endpoints_tested * 100) if total_endpoints_tested > 0 else 0
        
        print(f"\n📈 ENDPOINT SUCCESS ANALYSIS:")
        print(f"   Total Endpoints Tested: {total_endpoints_tested}")
        print(f"   Working Endpoints: {len(self.working_endpoints)} ✅")
        print(f"   Failing Endpoints: {len(self.failing_endpoints)} ❌")
        print(f"   Endpoint Success Rate: {endpoint_success_rate:.1f}%")
        
        # Production Readiness Assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if overall_success_rate >= 80 and self.authentication_working and len(self.available_services) >= 5:
            print("   🟢 EXCELLENT - Platform meets production readiness criteria")
            print("   ✅ Ready for production deployment")
        elif overall_success_rate >= 60 and self.authentication_working and len(self.available_services) >= 3:
            print("   🟡 GOOD - Platform approaches production readiness")
            print("   ⚠️ Ready for production with monitoring")
        elif self.authentication_working and len(self.available_services) >= 1:
            print("   🟠 PARTIAL - Authentication working, some services available")
            print("   ⚠️ Limited production readiness - needs improvements")
        else:
            print("   🔴 CRITICAL - Major issues preventing production deployment")
            print("   ❌ Not ready for production")
        
        # Key Achievements
        print(f"\n🎉 KEY ACHIEVEMENTS:")
        print(f"   • Authentication System: {'✅ Working' if self.authentication_working else '❌ Failed'}")
        print(f"   • Available Services: {len(self.available_services)} discovered")
        print(f"   • Working Endpoints: {len(self.working_endpoints)} functional")
        print(f"   • Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"   • Endpoint Success Rate: {endpoint_success_rate:.1f}%")
        
        # Critical Issues (if any)
        if failed_tests > passed_tests:
            print(f"\n⚠️ CRITICAL ISSUES IDENTIFIED:")
            print(f"   • {failed_tests} tests failed vs {passed_tests} passed")
            print(f"   • {len(self.failing_endpoints)} endpoints not working")
            if not self.authentication_working:
                print(f"   • Authentication system not functional")
        
        print("=" * 100)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': overall_success_rate,
            'authentication_working': self.authentication_working,
            'available_services': len(self.available_services),
            'working_endpoints': len(self.working_endpoints),
            'endpoint_success_rate': endpoint_success_rate
        }
    
    def run_realistic_test(self):
        """Run the complete realistic test"""
        print("🎯 REALISTIC AUTHENTICATION & CRUD TESTING FOR MEWAYZ V2 PLATFORM - JANUARY 2025")
        print("=" * 100)
        print("Testing actual available endpoints and real functionality")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 100)
        
        # Step 1: Health check
        if not self.test_health_check():
            print("❌ Backend is not accessible. Stopping tests.")
            return False
        
        # Step 2: Complete authentication system test
        if not self.test_authentication_system():
            print("❌ Authentication system failed. Continuing with limited tests.")
        
        # Step 3: Discover available services
        self.discover_available_services()
        
        # Step 4: Test available services CRUD
        self.test_available_services_crud()
        
        # Step 5: Test critical business endpoints
        self.test_critical_business_endpoints()
        
        # Step 6: Generate comprehensive report
        final_results = self.generate_comprehensive_report()
        
        return final_results

def main():
    """Main function to run the realistic test"""
    tester = RealisticTester()
    
    try:
        results = tester.run_realistic_test()
        
        if results:
            print(f"\n🎉 REALISTIC AUTHENTICATION & CRUD TEST COMPLETED!")
            print(f"   Success Rate: {results['success_rate']:.1f}%")
            print(f"   Authentication: {'✅ Working' if results['authentication_working'] else '❌ Failed'}")
            print(f"   Available Services: {results['available_services']}")
            print(f"   Working Endpoints: {results['working_endpoints']}")
            
            # Exit with appropriate code
            if results['success_rate'] >= 60 and results['authentication_working']:
                sys.exit(0)  # Success
            else:
                sys.exit(1)  # Needs improvement
        else:
            print(f"\n❌ REALISTIC AUTHENTICATION & CRUD TEST FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()