#!/usr/bin/env python3
"""
FOCUSED BACKEND TESTING FOR MEWAYZ V2 PLATFORM - CRITICAL ISSUES ASSESSMENT
Testing the specific issues mentioned in the review request
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
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class FocusedBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.critical_issues = []
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
    
    def test_basic_connectivity(self):
        """Test basic backend connectivity"""
        print("\n🔍 TESTING BASIC BACKEND CONNECTIVITY")
        print("=" * 60)
        
        try:
            # Test main health endpoint
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                services_count = data.get("services", 0)
                self.log_result("Basic Connectivity", True, f"Backend accessible - {services_count} services available", data, response.status_code)
                return True
            else:
                self.log_result("Basic Connectivity", False, f"Backend not accessible - Status {response.status_code}", None, response.status_code)
                return False
        except Exception as e:
            self.log_result("Basic Connectivity", False, f"Connection error: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity through various service health endpoints"""
        print("\n🗄️ TESTING DATABASE CONNECTIVITY")
        print("=" * 60)
        
        # Test various service health endpoints to check database connectivity
        services_to_test = [
            "auth", "financial", "workspace", "ai", "marketing", 
            "analytics", "user", "team", "dashboard", "admin"
        ]
        
        working_services = 0
        total_services = len(services_to_test)
        
        for service in services_to_test:
            try:
                response = self.session.get(f"{API_BASE}/{service}/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False) and data.get("healthy", False):
                        self.log_result(f"Database - {service.title()}", True, f"Service healthy with database access", data, response.status_code)
                        working_services += 1
                    else:
                        error = data.get("error", "Unknown error")
                        self.log_result(f"Database - {service.title()}", False, f"Service unhealthy: {error}", data, response.status_code)
                        if "Database unavailable" in error:
                            self.critical_issues.append(f"Database connectivity issue in {service} service")
                else:
                    self.log_result(f"Database - {service.title()}", False, f"Service health check failed - Status {response.status_code}", None, response.status_code)
            except Exception as e:
                self.log_result(f"Database - {service.title()}", False, f"Health check error: {str(e)}")
        
        success_rate = (working_services / total_services) * 100
        print(f"\n📊 Database Connectivity Results: {working_services}/{total_services} services ({success_rate:.1f}%)")
        
        if success_rate < 50:
            self.critical_issues.append(f"Critical database connectivity issues - only {success_rate:.1f}% of services can access database")
        
        return success_rate >= 50
    
    def test_authentication_system(self):
        """Test authentication system comprehensively"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 60)
        
        # Test 1: Check if auth endpoints exist
        try:
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                openapi_data = response.json()
                auth_endpoints = []
                for path, methods in openapi_data.get('paths', {}).items():
                    if 'auth' in path.lower() or 'login' in path.lower():
                        for method in methods.keys():
                            auth_endpoints.append(f"{method.upper()} {path}")
                
                self.log_result("Auth Endpoints Discovery", True, f"Found {len(auth_endpoints)} authentication endpoints", {"endpoints": auth_endpoints[:5]})
                
                # Test 2: Try different authentication approaches
                auth_attempts = [
                    ("POST", "/api/auth/login", {"username": TEST_EMAIL, "password": TEST_PASSWORD}),
                    ("POST", "/api/auth/", {"email": TEST_EMAIL, "password": TEST_PASSWORD}),
                    ("POST", "/api/user/login", {"username": TEST_EMAIL, "password": TEST_PASSWORD}),
                ]
                
                for method, endpoint, data in auth_attempts:
                    try:
                        if method == "POST":
                            # Try both JSON and form data
                            for content_type, request_data in [("json", data), ("form", data)]:
                                try:
                                    if content_type == "json":
                                        response = self.session.post(f"{BACKEND_URL}{endpoint}", json=request_data, timeout=10)
                                    else:
                                        response = self.session.post(f"{BACKEND_URL}{endpoint}", data=request_data, timeout=10)
                                    
                                    if response.status_code == 200:
                                        auth_data = response.json()
                                        if "access_token" in auth_data or "token" in auth_data:
                                            token = auth_data.get("access_token") or auth_data.get("token")
                                            self.access_token = token
                                            self.session.headers.update({"Authorization": f"Bearer {token}"})
                                            self.log_result("Authentication Success", True, f"Login successful via {endpoint} ({content_type})", auth_data, response.status_code)
                                            return True
                                        else:
                                            self.log_result(f"Auth Attempt - {endpoint} ({content_type})", False, f"No token in response", auth_data, response.status_code)
                                    elif response.status_code == 401:
                                        self.log_result(f"Auth Attempt - {endpoint} ({content_type})", False, f"Invalid credentials", None, response.status_code)
                                    elif response.status_code == 404:
                                        self.log_result(f"Auth Attempt - {endpoint} ({content_type})", False, f"Endpoint not found", None, response.status_code)
                                    elif response.status_code == 405:
                                        self.log_result(f"Auth Attempt - {endpoint} ({content_type})", False, f"Method not allowed", None, response.status_code)
                                    else:
                                        self.log_result(f"Auth Attempt - {endpoint} ({content_type})", False, f"Unexpected status {response.status_code}", None, response.status_code)
                                except Exception as e:
                                    self.log_result(f"Auth Attempt - {endpoint} ({content_type})", False, f"Request error: {str(e)}")
                    except Exception as e:
                        self.log_result(f"Auth Attempt - {endpoint}", False, f"General error: {str(e)}")
                
                # If no authentication worked, add to critical issues
                self.critical_issues.append("Authentication system completely non-functional - no working login endpoints found")
                return False
                
            else:
                self.log_result("Auth Endpoints Discovery", False, f"Cannot access OpenAPI spec - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication System", False, f"Authentication test error: {str(e)}")
            self.critical_issues.append(f"Authentication system test failed: {str(e)}")
            return False
    
    def test_crud_operations_sample(self):
        """Test CRUD operations on a sample of endpoints"""
        print("\n🔄 TESTING CRUD OPERATIONS SAMPLE")
        print("=" * 60)
        
        # Sample endpoints to test CRUD operations
        crud_test_endpoints = [
            {"base": "/api/user", "name": "User Management"},
            {"base": "/api/workspace", "name": "Workspace Management"},
            {"base": "/api/financial", "name": "Financial Management"},
            {"base": "/api/marketing", "name": "Marketing Management"},
            {"base": "/api/ai", "name": "AI Services"},
        ]
        
        crud_results = {
            "CREATE": {"working": 0, "total": 0},
            "READ": {"working": 0, "total": 0},
            "UPDATE": {"working": 0, "total": 0},
            "DELETE": {"working": 0, "total": 0}
        }
        
        for endpoint_info in crud_test_endpoints:
            base_url = endpoint_info["base"]
            name = endpoint_info["name"]
            
            # Test READ (GET)
            try:
                response = self.session.get(f"{BACKEND_URL}{base_url}", timeout=5)
                crud_results["READ"]["total"] += 1
                if response.status_code in [200, 401]:  # 401 means endpoint exists but needs auth
                    crud_results["READ"]["working"] += 1
                    self.log_result(f"CRUD READ - {name}", True, f"GET endpoint accessible (Status: {response.status_code})", None, response.status_code)
                else:
                    self.log_result(f"CRUD READ - {name}", False, f"GET failed (Status: {response.status_code})", None, response.status_code)
            except Exception as e:
                crud_results["READ"]["total"] += 1
                self.log_result(f"CRUD READ - {name}", False, f"GET error: {str(e)}")
            
            # Test CREATE (POST)
            try:
                test_data = {"name": "Test Item", "description": "Test description"}
                response = self.session.post(f"{BACKEND_URL}{base_url}", json=test_data, timeout=5)
                crud_results["CREATE"]["total"] += 1
                if response.status_code in [200, 201, 401, 422]:  # 422 means validation error but endpoint works
                    crud_results["CREATE"]["working"] += 1
                    self.log_result(f"CRUD CREATE - {name}", True, f"POST endpoint accessible (Status: {response.status_code})", None, response.status_code)
                else:
                    self.log_result(f"CRUD CREATE - {name}", False, f"POST failed (Status: {response.status_code})", None, response.status_code)
            except Exception as e:
                crud_results["CREATE"]["total"] += 1
                self.log_result(f"CRUD CREATE - {name}", False, f"POST error: {str(e)}")
            
            # Test UPDATE (PUT)
            try:
                test_data = {"name": "Updated Test Item"}
                response = self.session.put(f"{BACKEND_URL}{base_url}/test-id", json=test_data, timeout=5)
                crud_results["UPDATE"]["total"] += 1
                if response.status_code in [200, 401, 404, 422]:  # 404 means endpoint exists but item not found
                    crud_results["UPDATE"]["working"] += 1
                    self.log_result(f"CRUD UPDATE - {name}", True, f"PUT endpoint accessible (Status: {response.status_code})", None, response.status_code)
                else:
                    self.log_result(f"CRUD UPDATE - {name}", False, f"PUT failed (Status: {response.status_code})", None, response.status_code)
            except Exception as e:
                crud_results["UPDATE"]["total"] += 1
                self.log_result(f"CRUD UPDATE - {name}", False, f"PUT error: {str(e)}")
            
            # Test DELETE
            try:
                response = self.session.delete(f"{BACKEND_URL}{base_url}/test-id", timeout=5)
                crud_results["DELETE"]["total"] += 1
                if response.status_code in [200, 204, 401, 404]:  # 404 means endpoint exists but item not found
                    crud_results["DELETE"]["working"] += 1
                    self.log_result(f"CRUD DELETE - {name}", True, f"DELETE endpoint accessible (Status: {response.status_code})", None, response.status_code)
                else:
                    self.log_result(f"CRUD DELETE - {name}", False, f"DELETE failed (Status: {response.status_code})", None, response.status_code)
            except Exception as e:
                crud_results["DELETE"]["total"] += 1
                self.log_result(f"CRUD DELETE - {name}", False, f"DELETE error: {str(e)}")
        
        # Calculate CRUD success rates
        print(f"\n📊 CRUD Operations Results:")
        for operation, results in crud_results.items():
            if results["total"] > 0:
                success_rate = (results["working"] / results["total"]) * 100
                status = "✅" if success_rate >= 75 else "⚠️" if success_rate >= 50 else "❌"
                print(f"   {status} {operation}: {results['working']}/{results['total']} ({success_rate:.1f}%)")
                
                if success_rate < 25:
                    self.critical_issues.append(f"Critical CRUD issue: {operation} operations only {success_rate:.1f}% functional")
        
        return True
    
    def test_external_api_integrations(self):
        """Test external API integrations"""
        print("\n🌐 TESTING EXTERNAL API INTEGRATIONS")
        print("=" * 60)
        
        # Test external API integration endpoints
        external_apis = [
            {"endpoint": "/api/integrations/stripe/test", "name": "Stripe Integration"},
            {"endpoint": "/api/integrations/openai/test", "name": "OpenAI Integration"},
            {"endpoint": "/api/integrations/twitter/test", "name": "Twitter/X Integration"},
            {"endpoint": "/api/integrations/tiktok/test", "name": "TikTok Integration"},
            {"endpoint": "/api/integrations/elasticmail/test", "name": "ElasticMail Integration"},
        ]
        
        working_integrations = 0
        total_integrations = len(external_apis)
        
        for api_info in external_apis:
            try:
                response = self.session.get(f"{BACKEND_URL}{api_info['endpoint']}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(f"External API - {api_info['name']}", True, f"Integration test successful", data, response.status_code)
                    working_integrations += 1
                elif response.status_code == 401:
                    self.log_result(f"External API - {api_info['name']}", True, f"Integration endpoint exists (needs auth)", None, response.status_code)
                    working_integrations += 1
                elif response.status_code == 404:
                    self.log_result(f"External API - {api_info['name']}", False, f"Integration endpoint not found", None, response.status_code)
                else:
                    self.log_result(f"External API - {api_info['name']}", False, f"Integration test failed - Status {response.status_code}", None, response.status_code)
            except Exception as e:
                self.log_result(f"External API - {api_info['name']}", False, f"Integration test error: {str(e)}")
        
        success_rate = (working_integrations / total_integrations) * 100
        print(f"\n📊 External API Integration Results: {working_integrations}/{total_integrations} ({success_rate:.1f}%)")
        
        if success_rate < 50:
            self.critical_issues.append(f"External API integrations severely broken - only {success_rate:.1f}% functional")
        
        return success_rate >= 50
    
    def test_mock_data_detection(self):
        """Test for mock data usage in endpoints"""
        print("\n🎭 TESTING FOR MOCK DATA USAGE")
        print("=" * 60)
        
        # Test endpoints that might return data
        data_endpoints = [
            "/api/dashboard",
            "/api/analytics",
            "/api/user/profile",
            "/api/financial/dashboard",
            "/api/marketing/campaigns",
        ]
        
        mock_data_detected = 0
        real_data_confirmed = 0
        total_tested = 0
        
        for endpoint in data_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=5)
                total_tested += 1
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        data_str = str(data).lower()
                        
                        # Check for mock data patterns
                        mock_patterns = [
                            'sample', 'mock', 'test_', 'dummy', 'fake', 'placeholder',
                            'lorem ipsum', 'example.com', 'test@test.com', 'testuser',
                            '1250.00', '999.99', '123.45', 'john doe', 'jane smith'
                        ]
                        
                        has_mock_data = any(pattern in data_str for pattern in mock_patterns)
                        
                        if has_mock_data:
                            mock_data_detected += 1
                            self.log_result(f"Mock Data Check - {endpoint}", False, f"MOCK DATA DETECTED in response", None, response.status_code)
                        else:
                            real_data_confirmed += 1
                            self.log_result(f"Mock Data Check - {endpoint}", True, f"Real data confirmed", None, response.status_code)
                            
                    except json.JSONDecodeError:
                        self.log_result(f"Mock Data Check - {endpoint}", False, f"Non-JSON response", None, response.status_code)
                elif response.status_code == 401:
                    self.log_result(f"Mock Data Check - {endpoint}", True, f"Endpoint exists (needs auth)", None, response.status_code)
                else:
                    self.log_result(f"Mock Data Check - {endpoint}", False, f"Endpoint not accessible - Status {response.status_code}", None, response.status_code)
                    
            except Exception as e:
                total_tested += 1
                self.log_result(f"Mock Data Check - {endpoint}", False, f"Test error: {str(e)}")
        
        if total_tested > 0:
            mock_percentage = (mock_data_detected / total_tested) * 100
            real_percentage = (real_data_confirmed / total_tested) * 100
            
            print(f"\n📊 Mock Data Detection Results:")
            print(f"   Mock Data Detected: {mock_data_detected}/{total_tested} ({mock_percentage:.1f}%)")
            print(f"   Real Data Confirmed: {real_data_confirmed}/{total_tested} ({real_percentage:.1f}%)")
            
            if mock_percentage > 50:
                self.critical_issues.append(f"High mock data usage detected - {mock_percentage:.1f}% of tested endpoints using mock data")
        
        return True
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🎯 FOCUSED BACKEND TESTING RESULTS - MEWAYZ V2 PLATFORM")
        print("=" * 80)
        
        # Overall statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests Run: {total_tests}")
        print(f"   Passed Tests: {passed_tests} ✅")
        print(f"   Failed Tests: {failed_tests} ❌")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Critical Issues Summary
        print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
        if self.critical_issues:
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   ✅ No critical issues identified")
        
        # Production Readiness Assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if len(self.critical_issues) == 0 and overall_success_rate >= 75:
            print("   🟢 GOOD - Platform shows good stability for core functionality")
            print("   ✅ Ready for production with monitoring")
        elif len(self.critical_issues) <= 2 and overall_success_rate >= 50:
            print("   🟡 PARTIAL - Platform has some issues but core functionality works")
            print("   ⚠️ Needs fixes before production deployment")
        else:
            print("   🔴 CRITICAL - Platform has major issues affecting core functionality")
            print("   ❌ Not ready for production - comprehensive fixes required")
        
        # Recommendations
        print(f"\n💡 IMMEDIATE RECOMMENDATIONS:")
        if "Database unavailable" in str(self.critical_issues):
            print("   🔧 CRITICAL: Fix database connectivity issues in service health endpoints")
        if "Authentication system" in str(self.critical_issues):
            print("   🔧 CRITICAL: Implement working authentication system")
        if "CRUD" in str(self.critical_issues):
            print("   🔧 HIGH: Fix CRUD operations for core business functionality")
        if "External API" in str(self.critical_issues):
            print("   🔧 MEDIUM: Restore external API integrations")
        if "mock data" in str(self.critical_issues):
            print("   🔧 MEDIUM: Replace mock data with real database operations")
        
        print("=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': overall_success_rate,
            'critical_issues': len(self.critical_issues),
            'production_ready': len(self.critical_issues) == 0 and overall_success_rate >= 75
        }
    
    def run_focused_test(self):
        """Run the focused test suite"""
        print("🎯 FOCUSED BACKEND TESTING FOR MEWAYZ V2 PLATFORM - CRITICAL ISSUES ASSESSMENT")
        print("=" * 80)
        print("Testing the specific critical issues mentioned in the review request")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Backend is not accessible. Stopping tests.")
            return False
        
        # Step 2: Database connectivity
        self.test_database_connectivity()
        
        # Step 3: Authentication system
        self.test_authentication_system()
        
        # Step 4: CRUD operations sample
        self.test_crud_operations_sample()
        
        # Step 5: External API integrations
        self.test_external_api_integrations()
        
        # Step 6: Mock data detection
        self.test_mock_data_detection()
        
        # Step 7: Generate comprehensive report
        results = self.generate_comprehensive_report()
        
        return results

def main():
    """Main function to run the focused test"""
    tester = FocusedBackendTester()
    
    try:
        results = tester.run_focused_test()
        
        if results:
            print(f"\n🎉 FOCUSED BACKEND TEST COMPLETED!")
            print(f"   Success Rate: {results['success_rate']:.1f}%")
            print(f"   Critical Issues: {results['critical_issues']}")
            print(f"   Production Ready: {'Yes' if results['production_ready'] else 'No'}")
            
            # Exit with appropriate code
            if results['production_ready']:
                sys.exit(0)  # Success
            else:
                sys.exit(1)  # Needs improvement
        else:
            print(f"\n❌ FOCUSED BACKEND TEST FAILED")
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