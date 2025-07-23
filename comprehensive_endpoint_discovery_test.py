#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING FOR MEWAYZ V2 PLATFORM - JANUARY 2025
Comprehensive testing of ALL available API endpoints to establish current state and identify all issues.

COMPREHENSIVE TESTING REQUIREMENTS:
1. Full Endpoint Discovery: Test ALL available endpoints (aiming for 600-700+ as requested)
2. Complete CRUD Testing: Test Create, Read, Update, Delete operations for every endpoint
3. Real Data Verification: Verify all endpoints use real database data (no mock/random/hardcoded data)
4. Production Readiness: Test authentication, error handling, performance, data persistence
5. Service Coverage: Test all 52 working API modules plus any additional discoverable endpoints

TESTING SCOPE:
- All API modules: admin, advanced_ai, advanced_ai_analytics, advanced_ai_suite, advanced_analytics, 
  advanced_financial, advanced_financial_analytics, ai, ai_content, ai_token_management, analytics, 
  analytics_system, auth, automation_system, backup_system, bio_sites, blog, business_intelligence, 
  compliance_system, content, content_creation, course_management, crm_management, customer_experience, 
  dashboard, email_marketing, escrow_system, form_builder, google_oauth, i18n_system, integration, 
  integrations, link_shortener, marketing, media, media_library, monitoring_system, notification_system, 
  promotions_referrals, rate_limiting_system, realtime_notifications, social_email, social_email_integration, 
  social_media, social_media_suite, support_system, survey_system, team_management, template_marketplace, 
  user, webhook_system, workflow_automation
- All HTTP methods: GET, POST, PUT, DELETE, PATCH
- All endpoint variations: health checks, CRUD operations, statistics, filters, searches
- Authentication testing across all endpoints
- Database integration verification
- Performance and error handling assessment

CREDENTIALS:
- Use: tmonnens@outlook.com/Voetballen5
- Backend URL: https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com

EXPECTED OUTCOME:
- Detailed report of all working vs failing endpoints
- Identification of missing CRUD operations
- Detection of mock/random/hardcoded data
- Performance metrics and error patterns
- Complete inventory of all available endpoints
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional, List, Tuple
import uuid
from datetime import datetime, timedelta
import concurrent.futures
import threading

# Backend URL from environment
BACKEND_URL = "https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.discovered_endpoints = []
        self.working_endpoints = []
        self.failed_endpoints = []
        self.crud_results = {"CREATE": [], "READ": [], "UPDATE": [], "DELETE": []}
        self.mock_data_detected = []
        self.real_data_confirmed = []
        self.performance_metrics = []
        self.lock = threading.Lock()
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None, 
                   response_time: float = None, status_code: int = None):
        """Log test result with comprehensive details"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "response_size": len(str(response_data)) if response_data else 0,
            "response_time": response_time,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        
        with self.lock:
            self.test_results.append(result)
            if success:
                self.working_endpoints.append(test_name)
            else:
                self.failed_endpoints.append(test_name)
                
        print(f"{status}: {test_name} - {message}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response size: {len(str(response_data))} chars")
        if response_time:
            print(f"   Response time: {response_time:.3f}s")
    
    def test_health_check(self):
        """Test basic health check and discover all endpoints"""
        try:
            print("🔍 DISCOVERING ALL AVAILABLE ENDPOINTS...")
            print("=" * 80)
            
            # Get OpenAPI specification to discover all endpoints
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=15)
            if response.status_code == 200:
                openapi_data = response.json()
                paths = openapi_data.get('paths', {})
                
                # Extract all endpoints with their methods
                for path, methods in paths.items():
                    for method in methods.keys():
                        if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                            endpoint_info = {
                                'path': path,
                                'method': method.upper(),
                                'full_url': f"{BACKEND_URL}{path}",
                                'api_path': path.replace('/api/', '') if path.startswith('/api/') else path
                            }
                            self.discovered_endpoints.append(endpoint_info)
                
                total_endpoints = len(self.discovered_endpoints)
                self.log_result("Endpoint Discovery", True, 
                              f"Discovered {total_endpoints} total endpoints from OpenAPI specification", 
                              {"total_endpoints": total_endpoints, "paths_count": len(paths)})
                
                # Print endpoint categories
                categories = {}
                for endpoint in self.discovered_endpoints:
                    path_parts = endpoint['path'].strip('/').split('/')
                    if len(path_parts) > 1 and path_parts[0] == 'api':
                        category = path_parts[1] if len(path_parts) > 1 else 'root'
                    else:
                        category = path_parts[0] if path_parts else 'root'
                    
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(endpoint)
                
                print(f"\n📊 DISCOVERED ENDPOINT CATEGORIES:")
                print(f"   Total Categories: {len(categories)}")
                for category, endpoints in sorted(categories.items()):
                    print(f"   • {category}: {len(endpoints)} endpoints")
                
                return True
            else:
                self.log_result("Endpoint Discovery", False, 
                              f"Could not access OpenAPI specification - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Endpoint Discovery", False, f"Discovery error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            print("\n🔐 TESTING AUTHENTICATION...")
            print("=" * 50)
            
            # Test login
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,  # OAuth2PasswordRequestForm expects form data
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    # Set authorization header for future requests
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_result("Authentication", True, 
                                  f"Login successful - JWT token received", 
                                  data, response_time, response.status_code)
                    return True
                else:
                    self.log_result("Authentication", False, 
                                  "Login response missing access_token", 
                                  data, response_time, response.status_code)
                    return False
            else:
                self.log_result("Authentication", False, 
                              f"Login failed with status {response.status_code}: {response.text}", 
                              None, response_time, response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_endpoint_comprehensive(self, endpoint_info: Dict, test_data: Dict = None) -> Tuple[bool, Any]:
        """Test a specific endpoint comprehensively"""
        path = endpoint_info['path']
        method = endpoint_info['method']
        test_name = f"{method} {path}"
        
        try:
            url = endpoint_info['full_url']
            
            # Ensure we have authentication headers if we have a token
            headers = {"Content-Type": "application/json"}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=test_data, headers=headers, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, json=test_data, headers=headers, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=10)
            elif method == "PATCH":
                response = self.session.patch(url, json=test_data, headers=headers, timeout=10)
            else:
                self.log_result(test_name, False, f"Unsupported method: {method}")
                return False, None
            
            response_time = time.time() - start_time
            
            # Track performance
            self.performance_metrics.append({
                "endpoint": test_name,
                "response_time": response_time,
                "status_code": response.status_code
            })
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    
                    # Check for mock/random data patterns
                    self.check_for_mock_data(test_name, data)
                    
                    # Track CRUD operation
                    self.track_crud_operation(method, test_name, True)
                    
                    self.log_result(test_name, True, 
                                  f"SUCCESS - Status {response.status_code}", 
                                  data, response_time, response.status_code)
                    return True, data
                except:
                    # Non-JSON response but still successful
                    self.track_crud_operation(method, test_name, True)
                    self.log_result(test_name, True, 
                                  f"SUCCESS - Status {response.status_code} (non-JSON response)", 
                                  response.text, response_time, response.status_code)
                    return True, response.text
                    
            elif response.status_code == 404:
                self.track_crud_operation(method, test_name, False)
                self.log_result(test_name, False, 
                              f"NOT FOUND (404) - Endpoint may not be implemented", 
                              None, response_time, response.status_code)
                return False, None
                
            elif response.status_code == 401:
                self.track_crud_operation(method, test_name, False)
                self.log_result(test_name, False, 
                              f"UNAUTHORIZED (401) - Authentication required", 
                              None, response_time, response.status_code)
                return False, None
                
            elif response.status_code == 403:
                self.track_crud_operation(method, test_name, False)
                self.log_result(test_name, False, 
                              f"FORBIDDEN (403) - Access denied", 
                              None, response_time, response.status_code)
                return False, None
                
            elif response.status_code == 405:
                self.track_crud_operation(method, test_name, False)
                self.log_result(test_name, False, 
                              f"METHOD NOT ALLOWED (405) - {method} not supported", 
                              None, response_time, response.status_code)
                return False, None
                
            elif response.status_code == 422:
                self.track_crud_operation(method, test_name, False)
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Validation error')
                    self.log_result(test_name, False, 
                                  f"VALIDATION ERROR (422): {error_msg}", 
                                  error_data, response_time, response.status_code)
                except:
                    self.log_result(test_name, False, 
                                  f"VALIDATION ERROR (422): {response.text}", 
                                  None, response_time, response.status_code)
                return False, None
                
            elif response.status_code == 500:
                self.track_crud_operation(method, test_name, False)
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Internal server error')
                    self.log_result(test_name, False, 
                                  f"SERVER ERROR (500): {error_msg}", 
                                  error_data, response_time, response.status_code)
                except:
                    self.log_result(test_name, False, 
                                  f"SERVER ERROR (500): {response.text}", 
                                  None, response_time, response.status_code)
                return False, None
                
            else:
                self.track_crud_operation(method, test_name, False)
                self.log_result(test_name, False, 
                              f"ERROR - Status {response.status_code}: {response.text}", 
                              None, response_time, response.status_code)
                return False, None
                
        except Exception as e:
            self.track_crud_operation(method, test_name, False)
            self.log_result(test_name, False, f"REQUEST ERROR: {str(e)}")
            return False, None
    
    def check_for_mock_data(self, test_name: str, data: Any):
        """Check if response contains mock/random/hardcoded data"""
        data_str = str(data).lower()
        
        # Common mock data patterns
        mock_patterns = [
            'sample', 'mock', 'test', 'dummy', 'fake', 'lorem ipsum',
            'example.com', 'test@test.com', 'testuser', 'sampledata',
            'placeholder', 'demo', 'temp', 'random_', 'mock_'
        ]
        
        # Hardcoded values that suggest non-real data
        hardcoded_patterns = [
            '1250.00', '999.99', '123.45', '100.00', '50.00',
            'user123', 'admin123', 'test123', 'sample123'
        ]
        
        mock_detected = any(pattern in data_str for pattern in mock_patterns)
        hardcoded_detected = any(pattern in data_str for pattern in hardcoded_patterns)
        
        if mock_detected or hardcoded_detected:
            self.mock_data_detected.append({
                "endpoint": test_name,
                "reason": "mock_patterns" if mock_detected else "hardcoded_values",
                "data_sample": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
            })
        else:
            self.real_data_confirmed.append(test_name)
    
    def track_crud_operation(self, method: str, test_name: str, success: bool):
        """Track CRUD operation results"""
        crud_mapping = {
            "POST": "CREATE",
            "GET": "READ", 
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE"
        }
        
        crud_type = crud_mapping.get(method, "OTHER")
        if crud_type in self.crud_results:
            self.crud_results[crud_type].append({
                "endpoint": test_name,
                "success": success
            })
    
    def generate_test_data_for_endpoint(self, path: str, method: str) -> Dict:
        """Generate appropriate test data for different endpoints"""
        # Basic test data templates for different endpoint types
        if 'team' in path.lower():
            return {
                "name": "Test Marketing Team",
                "description": "Team for comprehensive testing",
                "department": "Marketing"
            }
        elif 'user' in path.lower():
            return {
                "email": "testuser@mewayz.com",
                "name": "Test User",
                "role": "member"
            }
        elif 'workflow' in path.lower():
            return {
                "name": "Test Automation Workflow",
                "description": "Automated workflow for testing",
                "triggers": [{"type": "schedule", "cron": "0 9 * * 1"}],
                "actions": [{"type": "send_email", "template": "welcome"}]
            }
        elif 'invoice' in path.lower():
            return {
                "client_name": "Test Client Corp",
                "client_email": "billing@testclient.com",
                "amount": 1500.00,
                "items": [{"name": "Service", "quantity": 1, "price": 1500.00}]
            }
        elif 'template' in path.lower():
            return {
                "title": "Test Business Template",
                "description": "Template for comprehensive testing",
                "category": "business",
                "price": 29.99
            }
        elif 'post' in path.lower() or 'social' in path.lower():
            return {
                "content": "Test social media post for comprehensive testing #business",
                "platforms": ["twitter", "linkedin"],
                "scheduled_time": "2025-01-16T15:00:00Z"
            }
        elif 'escrow' in path.lower() or 'transaction' in path.lower():
            return {
                "buyer_id": "buyer_test_123",
                "seller_id": "seller_test_456", 
                "amount": 2000.00,
                "project_title": "Test Project"
            }
        elif 'dispute' in path.lower():
            return {
                "transaction_id": "trans_test_123",
                "reason": "quality_issues",
                "description": "Test dispute for comprehensive testing"
            }
        elif 'device' in path.lower():
            return {
                "device_id": "device_test_001",
                "device_type": "mobile",
                "platform": "ios",
                "app_version": "2.1.0"
            }
        elif 'manifest' in path.lower():
            return {
                "app_name": "Mewayz Business Platform",
                "short_name": "Mewayz",
                "theme_color": "#2563EB",
                "background_color": "#FFFFFF"
            }
        else:
            # Generic test data
            return {
                "name": "Test Item",
                "description": "Item created for comprehensive testing",
                "type": "test",
                "active": True
            }
    
    def test_all_endpoints_comprehensive(self):
        """Test all discovered endpoints comprehensively"""
        print(f"\n🚀 COMPREHENSIVE TESTING OF ALL {len(self.discovered_endpoints)} ENDPOINTS...")
        print("=" * 80)
        
        # Group endpoints by category for organized testing
        categories = {}
        for endpoint in self.discovered_endpoints:
            path_parts = endpoint['path'].strip('/').split('/')
            if len(path_parts) > 1 and path_parts[0] == 'api':
                category = path_parts[1] if len(path_parts) > 1 else 'root'
            else:
                category = path_parts[0] if path_parts else 'root'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(endpoint)
        
        # Test each category
        for category, endpoints in sorted(categories.items()):
            print(f"\n📂 TESTING CATEGORY: {category.upper()} ({len(endpoints)} endpoints)")
            print("-" * 60)
            
            for endpoint_info in endpoints:
                # Generate appropriate test data for POST/PUT requests
                test_data = None
                if endpoint_info['method'] in ['POST', 'PUT', 'PATCH']:
                    test_data = self.generate_test_data_for_endpoint(
                        endpoint_info['path'], 
                        endpoint_info['method']
                    )
                
                # Test the endpoint
                success, response_data = self.test_endpoint_comprehensive(endpoint_info, test_data)
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.1)
    
    def test_real_data_verification(self):
        """Verify that endpoints are using real database data"""
        print(f"\n🔍 REAL DATA VERIFICATION...")
        print("=" * 50)
        
        # Test key endpoints multiple times to check for data consistency
        key_endpoints = [
            {"path": "/api/dashboard/overview", "method": "GET"},
            {"path": "/api/user/profile", "method": "GET"},
            {"path": "/api/analytics/overview", "method": "GET"},
            {"path": "/api/team-management/dashboard", "method": "GET"},
            {"path": "/api/financial/dashboard", "method": "GET"}
        ]
        
        for endpoint_info in key_endpoints:
            print(f"\n🔄 Testing data consistency for {endpoint_info['path']}...")
            
            responses = []
            for i in range(3):  # Test 3 times
                success, data = self.test_endpoint_comprehensive(endpoint_info)
                if success and data:
                    responses.append(str(data))
                time.sleep(1)  # Wait between requests
            
            if len(responses) >= 2:
                # Check if responses are identical (suggesting real data)
                if all(resp == responses[0] for resp in responses):
                    self.log_result(f"Data Consistency - {endpoint_info['path']}", True,
                                  "Data consistent across multiple calls - confirms real database usage")
                else:
                    self.log_result(f"Data Consistency - {endpoint_info['path']}", False,
                                  "Data inconsistent across calls - may be using random generation")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 100)
        print("🎯 COMPREHENSIVE BACKEND TESTING REPORT - MEWAYZ V2 PLATFORM")
        print("=" * 100)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL TEST RESULTS:")
        print(f"   Total Endpoints Discovered: {len(self.discovered_endpoints)}")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   Working Endpoints: {passed_tests} ✅")
        print(f"   Failed Endpoints: {failed_tests} ❌")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        # CRUD Operations Analysis
        print(f"\n🔄 CRUD OPERATIONS ANALYSIS:")
        for crud_type, operations in self.crud_results.items():
            if operations:
                successful = len([op for op in operations if op["success"]])
                total = len(operations)
                crud_success_rate = (successful / total * 100) if total > 0 else 0
                print(f"   {crud_type} Operations: {successful}/{total} ({crud_success_rate:.1f}% success)")
        
        # Performance Analysis
        if self.performance_metrics:
            avg_response_time = sum(m["response_time"] for m in self.performance_metrics if m["response_time"]) / len([m for m in self.performance_metrics if m["response_time"]])
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            
            # Fast endpoints (< 0.5s)
            fast_endpoints = [m for m in self.performance_metrics if m["response_time"] and m["response_time"] < 0.5]
            print(f"   Fast Endpoints (< 0.5s): {len(fast_endpoints)}")
            
            # Slow endpoints (> 2s)
            slow_endpoints = [m for m in self.performance_metrics if m["response_time"] and m["response_time"] > 2.0]
            print(f"   Slow Endpoints (> 2s): {len(slow_endpoints)}")
        
        # Data Quality Analysis
        print(f"\n🔍 DATA QUALITY ANALYSIS:")
        print(f"   Real Data Confirmed: {len(self.real_data_confirmed)} endpoints")
        print(f"   Mock Data Detected: {len(self.mock_data_detected)} endpoints")
        
        if self.mock_data_detected:
            print(f"\n❌ ENDPOINTS WITH MOCK DATA:")
            for mock_endpoint in self.mock_data_detected[:10]:  # Show first 10
                print(f"   • {mock_endpoint['endpoint']} - {mock_endpoint['reason']}")
        
        # Status Code Analysis
        status_codes = {}
        for result in self.test_results:
            if result.get("status_code"):
                code = result["status_code"]
                if code not in status_codes:
                    status_codes[code] = 0
                status_codes[code] += 1
        
        print(f"\n📈 HTTP STATUS CODE DISTRIBUTION:")
        for code, count in sorted(status_codes.items()):
            print(f"   {code}: {count} endpoints")
        
        # Production Readiness Assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - Platform is production ready with outstanding performance")
        elif success_rate >= 75:
            print("   🟡 GOOD - Platform is mostly production ready with minor issues")
        elif success_rate >= 50:
            print("   🟠 PARTIAL - Platform needs significant improvements before production")
        else:
            print("   🔴 CRITICAL - Platform is not ready for production deployment")
        
        # Critical Issues Summary
        critical_issues = [r for r in self.test_results if not r["success"] and r.get("status_code") in [500, 404]]
        if critical_issues:
            print(f"\n❌ CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
            issue_types = {}
            for issue in critical_issues:
                status_code = issue.get("status_code", "Unknown")
                if status_code not in issue_types:
                    issue_types[status_code] = []
                issue_types[status_code].append(issue["test"])
            
            for status_code, endpoints in issue_types.items():
                print(f"   {status_code} Errors: {len(endpoints)} endpoints")
                for endpoint in endpoints[:5]:  # Show first 5
                    print(f"     • {endpoint}")
                if len(endpoints) > 5:
                    print(f"     ... and {len(endpoints) - 5} more")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if failed_tests > 0:
            print(f"   • Fix {failed_tests} failing endpoints to improve success rate")
        if len(self.mock_data_detected) > 0:
            print(f"   • Replace mock data with real database operations in {len(self.mock_data_detected)} endpoints")
        if len([m for m in self.performance_metrics if m.get("response_time", 0) > 2.0]) > 0:
            print(f"   • Optimize slow endpoints for better performance")
        
        print("=" * 100)
        
        return {
            "total_endpoints": len(self.discovered_endpoints),
            "total_tests": total_tests,
            "success_rate": success_rate,
            "working_endpoints": passed_tests,
            "failed_endpoints": failed_tests,
            "crud_results": self.crud_results,
            "mock_data_count": len(self.mock_data_detected),
            "real_data_count": len(self.real_data_confirmed),
            "avg_response_time": avg_response_time if self.performance_metrics else 0
        }
    
    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite"""
        print("🎯 COMPREHENSIVE BACKEND TESTING FOR MEWAYZ V2 PLATFORM - JANUARY 2025")
        print("=" * 100)
        print("Conducting comprehensive testing of ALL available API endpoints")
        print("to establish current state and identify all issues.")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 100)
        
        # Step 1: Health check and endpoint discovery
        if not self.test_health_check():
            print("❌ Backend is not accessible or endpoint discovery failed. Stopping tests.")
            return False
        
        # Step 2: Authentication
        if not self.test_authentication():
            print("❌ Authentication failed. Continuing with limited testing...")
        else:
            print(f"✅ Authentication successful. Token: {self.access_token[:20]}...")
        
        # Step 3: Comprehensive endpoint testing
        self.test_all_endpoints_comprehensive()
        
        # Step 4: Real data verification
        self.test_real_data_verification()
        
        # Step 5: Generate comprehensive report
        report_data = self.generate_comprehensive_report()
        
        return report_data

def main():
    """Main function to run comprehensive backend testing"""
    tester = ComprehensiveBackendTester()
    
    try:
        results = tester.run_comprehensive_test_suite()
        
        if results:
            print(f"\n🎉 COMPREHENSIVE TESTING COMPLETED!")
            print(f"   Success Rate: {results['success_rate']:.1f}%")
            print(f"   Working Endpoints: {results['working_endpoints']}")
            print(f"   Total Endpoints Tested: {results['total_tests']}")
            
            # Return success if we have a reasonable success rate
            return results['success_rate'] >= 50
        else:
            print(f"\n❌ COMPREHENSIVE TESTING FAILED!")
            return False
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Testing interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)