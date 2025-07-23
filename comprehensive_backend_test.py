#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TEST FOR MEWAYZ V2 PLATFORM - JANUARY 2025
Testing ALL available endpoints to achieve 80-90%+ success rate for production readiness

This test will:
1. Discover ALL endpoints from OpenAPI specification
2. Test each endpoint systematically
3. Categorize results by service/module
4. Identify specific issues requiring fixes
5. Provide detailed recommendations for improvements

Expected: Over 1,000 endpoints to be discovered and tested
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

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.endpoint_categories = {}
        self.all_endpoints = []
        self.working_endpoints = []
        self.failing_endpoints = []
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None, status_code: int = None):
        """Log test result with detailed information"""
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
    
    def discover_all_endpoints(self):
        """Discover all endpoints from OpenAPI specification"""
        try:
            print("🔍 DISCOVERING ALL ENDPOINTS FROM OPENAPI SPECIFICATION")
            print("=" * 80)
            
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=30)
            if response.status_code != 200:
                print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
                return False
            
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            
            print(f"📊 OpenAPI Specification Analysis:")
            print(f"   Total paths discovered: {len(paths)}")
            
            # Extract all endpoints with their methods
            for path, methods in paths.items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        endpoint_info = {
                            'path': path,
                            'method': method.upper(),
                            'summary': details.get('summary', ''),
                            'tags': details.get('tags', []),
                            'parameters': details.get('parameters', []),
                            'requestBody': details.get('requestBody', {}),
                            'responses': details.get('responses', {})
                        }
                        self.all_endpoints.append(endpoint_info)
                        
                        # Categorize by tags/service
                        tags = details.get('tags', ['uncategorized'])
                        for tag in tags:
                            if tag not in self.endpoint_categories:
                                self.endpoint_categories[tag] = []
                            self.endpoint_categories[tag].append(endpoint_info)
            
            print(f"   Total endpoints discovered: {len(self.all_endpoints)}")
            print(f"   Categories found: {len(self.endpoint_categories)}")
            
            # Print category breakdown
            print(f"\n📋 ENDPOINT CATEGORIES:")
            for category, endpoints in self.endpoint_categories.items():
                print(f"   {category}: {len(endpoints)} endpoints")
            
            return True
            
        except Exception as e:
            print(f"❌ Error discovering endpoints: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            print("\n🔐 TESTING AUTHENTICATION")
            print("=" * 50)
            
            # Test login
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,  # OAuth2PasswordRequestForm expects form data
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    # Set authorization header for future requests
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_result("Authentication", True, f"Login successful - Token received", data, response.status_code)
                    return True
                else:
                    self.log_result("Authentication", False, "Login response missing access_token", None, response.status_code)
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed: {response.text}", None, response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def generate_test_data_for_endpoint(self, endpoint_info: Dict) -> Dict:
        """Generate appropriate test data for an endpoint based on its schema"""
        method = endpoint_info['method']
        path = endpoint_info['path']
        request_body = endpoint_info.get('requestBody', {})
        
        # Default test data templates
        test_data = {}
        
        # Common test data patterns based on path
        if 'user' in path.lower():
            test_data.update({
                "name": "Test User",
                "email": "testuser@example.com",
                "username": "testuser123"
            })
        
        if 'team' in path.lower():
            test_data.update({
                "name": "Test Team",
                "description": "Test team for API testing",
                "department": "Engineering"
            })
        
        if 'project' in path.lower():
            test_data.update({
                "title": "Test Project",
                "description": "Test project for API testing",
                "status": "active"
            })
        
        if 'invoice' in path.lower():
            test_data.update({
                "client_name": "Test Client",
                "amount": 1000.00,
                "currency": "USD",
                "status": "pending"
            })
        
        if 'workflow' in path.lower():
            test_data.update({
                "name": "Test Workflow",
                "description": "Test workflow for automation",
                "triggers": [{"type": "manual"}],
                "actions": [{"type": "log", "message": "test"}]
            })
        
        if 'template' in path.lower():
            test_data.update({
                "title": "Test Template",
                "description": "Test template for marketplace",
                "category": "business",
                "price": 29.99
            })
        
        # Add common fields that might be required
        test_data.update({
            "id": str(uuid.uuid4()),
            "workspace_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        
        return test_data
    
    def test_single_endpoint(self, endpoint_info: Dict) -> Tuple[bool, Dict]:
        """Test a single endpoint"""
        path = endpoint_info['path']
        method = endpoint_info['method']
        summary = endpoint_info.get('summary', '')
        
        test_name = f"{method} {path}"
        if summary:
            test_name += f" ({summary})"
        
        try:
            url = f"{BACKEND_URL}{path}"
            
            # Ensure we have authentication headers if we have a token
            headers = {"Content-Type": "application/json"}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Generate test data for POST/PUT/PATCH requests
            test_data = None
            if method in ['POST', 'PUT', 'PATCH']:
                test_data = self.generate_test_data_for_endpoint(endpoint_info)
            
            # Make the request
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
            
            # Analyze response
            if response.status_code in [200, 201, 202]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Success", data, response.status_code)
                    self.working_endpoints.append(endpoint_info)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Success (non-JSON response)", response.text[:100], response.status_code)
                    self.working_endpoints.append(endpoint_info)
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Not Found - Endpoint may not be implemented", None, response.status_code)
                self.failing_endpoints.append({**endpoint_info, 'error': 'Not Found'})
                return False, None
            elif response.status_code == 401:
                self.log_result(test_name, False, f"Unauthorized - Authentication required", None, response.status_code)
                self.failing_endpoints.append({**endpoint_info, 'error': 'Unauthorized'})
                return False, None
            elif response.status_code == 403:
                self.log_result(test_name, False, f"Forbidden - Access denied", None, response.status_code)
                self.failing_endpoints.append({**endpoint_info, 'error': 'Forbidden'})
                return False, None
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Validation error')
                    self.log_result(test_name, False, f"Validation Error: {error_msg}", None, response.status_code)
                    self.failing_endpoints.append({**endpoint_info, 'error': f'Validation Error: {error_msg}'})
                except:
                    self.log_result(test_name, False, f"Validation Error: {response.text}", None, response.status_code)
                    self.failing_endpoints.append({**endpoint_info, 'error': f'Validation Error'})
                return False, None
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Internal server error')
                    self.log_result(test_name, False, f"Server Error: {error_msg}", None, response.status_code)
                    self.failing_endpoints.append({**endpoint_info, 'error': f'Server Error: {error_msg}'})
                except:
                    self.log_result(test_name, False, f"Server Error: {response.text[:200]}", None, response.status_code)
                    self.failing_endpoints.append({**endpoint_info, 'error': 'Server Error'})
                return False, None
            else:
                self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text[:200]}", None, response.status_code)
                self.failing_endpoints.append({**endpoint_info, 'error': f'HTTP {response.status_code}'})
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            self.failing_endpoints.append({**endpoint_info, 'error': f'Request error: {str(e)}'})
            return False, None
    
    def test_all_endpoints_by_category(self):
        """Test all endpoints organized by category"""
        print(f"\n🚀 TESTING ALL {len(self.all_endpoints)} ENDPOINTS BY CATEGORY")
        print("=" * 80)
        
        category_results = {}
        
        for category, endpoints in self.endpoint_categories.items():
            print(f"\n📂 TESTING CATEGORY: {category.upper()} ({len(endpoints)} endpoints)")
            print("-" * 60)
            
            category_working = 0
            category_total = len(endpoints)
            
            for endpoint_info in endpoints:
                success, data = self.test_single_endpoint(endpoint_info)
                if success:
                    category_working += 1
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.1)
            
            category_success_rate = (category_working / category_total * 100) if category_total > 0 else 0
            category_results[category] = {
                'working': category_working,
                'total': category_total,
                'success_rate': category_success_rate
            }
            
            status_icon = "✅" if category_success_rate >= 80 else "⚠️" if category_success_rate >= 50 else "❌"
            print(f"\n{status_icon} {category}: {category_working}/{category_total} ({category_success_rate:.1f}%)")
        
        return category_results
    
    def analyze_failing_endpoints(self):
        """Analyze failing endpoints to identify common issues"""
        print(f"\n🔍 ANALYZING {len(self.failing_endpoints)} FAILING ENDPOINTS")
        print("=" * 80)
        
        # Group by error type
        error_groups = {}
        for endpoint in self.failing_endpoints:
            error = endpoint.get('error', 'Unknown error')
            if error not in error_groups:
                error_groups[error] = []
            error_groups[error].append(endpoint)
        
        print(f"📊 ERROR ANALYSIS:")
        for error_type, endpoints in error_groups.items():
            print(f"   {error_type}: {len(endpoints)} endpoints")
        
        # Detailed breakdown of most common issues
        print(f"\n🔧 DETAILED ISSUE BREAKDOWN:")
        for error_type, endpoints in sorted(error_groups.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n❌ {error_type} ({len(endpoints)} endpoints):")
            for endpoint in endpoints[:5]:  # Show first 5 examples
                print(f"   • {endpoint['method']} {endpoint['path']}")
            if len(endpoints) > 5:
                print(f"   ... and {len(endpoints) - 5} more")
        
        return error_groups
    
    def generate_recommendations(self, category_results: Dict, error_groups: Dict):
        """Generate specific recommendations for fixing issues"""
        print(f"\n💡 RECOMMENDATIONS FOR PRODUCTION READINESS")
        print("=" * 80)
        
        total_endpoints = len(self.all_endpoints)
        working_endpoints = len(self.working_endpoints)
        current_success_rate = (working_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
        
        print(f"📈 CURRENT STATUS:")
        print(f"   Total Endpoints: {total_endpoints}")
        print(f"   Working Endpoints: {working_endpoints}")
        print(f"   Current Success Rate: {current_success_rate:.1f}%")
        print(f"   Target Success Rate: 80-90%")
        print(f"   Endpoints to Fix: {int(total_endpoints * 0.8) - working_endpoints}")
        
        print(f"\n🎯 PRIORITY FIXES:")
        
        # Priority 1: Not Found errors (missing implementations)
        not_found_count = len(error_groups.get('Not Found', []))
        if not_found_count > 0:
            print(f"   🔴 CRITICAL: Fix {not_found_count} missing endpoint implementations (404 errors)")
        
        # Priority 2: Server errors
        server_error_count = len([e for e in error_groups.keys() if 'Server Error' in e])
        if server_error_count > 0:
            print(f"   🔴 CRITICAL: Fix {server_error_count} server errors (500 errors)")
        
        # Priority 3: Validation errors
        validation_error_count = len([e for e in error_groups.keys() if 'Validation Error' in e])
        if validation_error_count > 0:
            print(f"   🟡 HIGH: Fix {validation_error_count} validation schema issues (422 errors)")
        
        # Priority 4: Authentication issues
        auth_error_count = len(error_groups.get('Unauthorized', [])) + len(error_groups.get('Forbidden', []))
        if auth_error_count > 0:
            print(f"   🟡 HIGH: Fix {auth_error_count} authentication/authorization issues")
        
        print(f"\n📋 CATEGORY-SPECIFIC RECOMMENDATIONS:")
        for category, results in category_results.items():
            if results['success_rate'] < 80:
                print(f"   • {category}: {results['success_rate']:.1f}% success - Needs attention ({results['total'] - results['working']} endpoints to fix)")
        
        return {
            'total_endpoints': total_endpoints,
            'working_endpoints': working_endpoints,
            'current_success_rate': current_success_rate,
            'endpoints_to_fix': int(total_endpoints * 0.8) - working_endpoints
        }
    
    def run_comprehensive_test(self):
        """Run the comprehensive test suite"""
        print("🎯 COMPREHENSIVE BACKEND TEST FOR MEWAYZ V2 PLATFORM - JANUARY 2025")
        print("=" * 80)
        print("Testing ALL available endpoints to achieve 80-90%+ success rate for production readiness")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Discover all endpoints
        if not self.discover_all_endpoints():
            print("❌ Failed to discover endpoints. Stopping tests.")
            return False
        
        # Step 2: Authentication
        if not self.test_authentication():
            print("❌ Authentication failed. Continuing with limited testing...")
        
        # Step 3: Test all endpoints by category
        category_results = self.test_all_endpoints_by_category()
        
        # Step 4: Analyze failing endpoints
        error_groups = self.analyze_failing_endpoints()
        
        # Step 5: Generate recommendations
        recommendations = self.generate_recommendations(category_results, error_groups)
        
        # Step 6: Print final summary
        self.print_final_comprehensive_summary(category_results, error_groups, recommendations)
        
        return True
    
    def print_final_comprehensive_summary(self, category_results: Dict, error_groups: Dict, recommendations: Dict):
        """Print final comprehensive summary"""
        print(f"\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BACKEND TEST SUMMARY - MEWAYZ V2 PLATFORM")
        print("=" * 80)
        
        total_endpoints = recommendations['total_endpoints']
        working_endpoints = recommendations['working_endpoints']
        current_success_rate = recommendations['current_success_rate']
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Endpoints Discovered: {total_endpoints}")
        print(f"   Working Endpoints: {working_endpoints} ✅")
        print(f"   Failing Endpoints: {total_endpoints - working_endpoints} ❌")
        print(f"   Current Success Rate: {current_success_rate:.1f}%")
        
        # Production readiness assessment
        if current_success_rate >= 90:
            print(f"\n🟢 EXCELLENT: Platform exceeds production readiness criteria")
        elif current_success_rate >= 80:
            print(f"\n🟡 GOOD: Platform meets production readiness criteria")
        elif current_success_rate >= 70:
            print(f"\n🟠 FAIR: Platform approaching production readiness")
        elif current_success_rate >= 50:
            print(f"\n🔴 POOR: Platform needs significant work for production")
        else:
            print(f"\n🔴 CRITICAL: Platform not ready for production")
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in sorted(category_results.items(), key=lambda x: x[1]['success_rate'], reverse=True):
            status_icon = "✅" if results['success_rate'] >= 80 else "⚠️" if results['success_rate'] >= 50 else "❌"
            print(f"   {status_icon} {category}: {results['working']}/{results['total']} ({results['success_rate']:.1f}%)")
        
        print(f"\n🔧 TOP ISSUES TO FIX:")
        for error_type, endpoints in sorted(error_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"   • {error_type}: {len(endpoints)} endpoints")
        
        print("=" * 80)

def main():
    """Main function to run comprehensive backend testing"""
    tester = ComprehensiveBackendTester()
    
    try:
        success = tester.run_comprehensive_test()
        if success:
            print("\n✅ Comprehensive backend testing completed successfully!")
        else:
            print("\n❌ Comprehensive backend testing encountered issues.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
COMPREHENSIVE FULL-SCALE BACKEND TEST - MEWAYZ V2 PLATFORM
Complete Production Readiness Verification
Testing Agent: Comprehensive Backend Testing
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configuration
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = {
            "total_endpoints_tested": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "endpoints_by_category": {},
            "performance_metrics": {},
            "critical_issues": [],
            "data_quality_issues": [],
            "authentication_status": "unknown",
            "start_time": datetime.now(),
            "backend_info": {}
        }
        
        # Comprehensive endpoint mapping based on actual backend analysis
        self.endpoint_categories = {
            "System Health & Metrics": [
                "/",
                "/health", 
                "/api/health",
                "/healthz",
                "/ready",
                "/metrics"
            ],
            "Authentication System": [
                "/api/auth/login",
                "/api/auth/register", 
                "/api/auth/refresh",
                "/api/auth/logout",
                "/api/auth/profile",
                "/api/auth/change-password",
                "/api/auth/forgot-password",
                "/api/auth/reset-password",
                "/api/auth/verify-email"
            ],
            "Blog System (Working Module)": [
                "/api/blog/posts",
                "/api/blog/create",
                "/api/blog/categories",
                "/api/blog/comments",
                "/api/blog/tags",
                "/api/blog/search",
                "/api/blog/publish",
                "/api/blog/draft"
            ],
            "Content Management (Working Module)": [
                "/api/content/posts",
                "/api/content/create",
                "/api/content/edit",
                "/api/content/delete",
                "/api/content/publish",
                "/api/content/schedule",
                "/api/content/categories",
                "/api/content/tags",
                "/api/content/search"
            ],
            "Real-time Notifications (Working Module)": [
                "/api/notifications/send",
                "/api/notifications/subscribe",
                "/api/notifications/unsubscribe",
                "/api/notifications/history",
                "/api/notifications/templates",
                "/api/notifications/settings",
                "/api/notifications/status"
            ],
            "Marketing Website (Working Router)": [
                "/api/marketing-website/pages",
                "/api/marketing-website/templates",
                "/api/marketing-website/analytics",
                "/api/marketing-website/seo",
                "/api/marketing-website/content"
            ],
            "Enterprise Security (Working Router)": [
                "/api/enterprise-security/policies",
                "/api/enterprise-security/audit",
                "/api/enterprise-security/compliance",
                "/api/enterprise-security/reports",
                "/api/enterprise-security/settings"
            ],
            "Email Automation (Working Router)": [
                "/api/email-automation/campaigns",
                "/api/email-automation/templates",
                "/api/email-automation/analytics",
                "/api/email-automation/subscribers",
                "/api/email-automation/send"
            ],
            "Templates CRUD (Working Router)": [
                "/api/templates/list",
                "/api/templates/create",
                "/api/templates/update",
                "/api/templates/delete",
                "/api/templates/categories",
                "/api/templates/search"
            ],
            # Test endpoints that should exist based on main.py but may be broken
            "User Management (Expected)": [
                "/api/user/profile",
                "/api/user/update-profile",
                "/api/user/statistics",
                "/api/user/activity",
                "/api/user/preferences",
                "/api/user/notifications"
            ],
            "Dashboard (Expected)": [
                "/api/dashboard/overview",
                "/api/dashboard/analytics",
                "/api/dashboard/activity",
                "/api/dashboard/metrics",
                "/api/dashboard/widgets"
            ],
            "Analytics (Expected)": [
                "/api/analytics/overview",
                "/api/analytics/users",
                "/api/analytics/revenue",
                "/api/analytics/engagement",
                "/api/analytics/conversion"
            ],
            "AI Services (Expected)": [
                "/api/ai/generate-content",
                "/api/ai/analyze-text",
                "/api/ai/conversations",
                "/api/ai/models",
                "/api/ai/usage-statistics"
            ],
            "Social Media (Expected)": [
                "/api/social-media/posts",
                "/api/social-media/schedule",
                "/api/social-media/analytics",
                "/api/social-media/accounts"
            ],
            "E-commerce (Expected)": [
                "/api/ecommerce/products",
                "/api/ecommerce/orders",
                "/api/ecommerce/customers",
                "/api/ecommerce/inventory",
                "/api/ecommerce/payments"
            ],
            "Financial Management (Expected)": [
                "/api/financial/dashboard",
                "/api/financial/invoices",
                "/api/financial/payments",
                "/api/financial/expenses",
                "/api/financial/reports"
            ],
            "Team Management (Expected)": [
                "/api/teams/list",
                "/api/teams/create",
                "/api/teams/members",
                "/api/teams/roles",
                "/api/teams/permissions"
            ],
            "Admin Dashboard (Expected)": [
                "/api/admin/dashboard",
                "/api/admin/users",
                "/api/admin/statistics",
                "/api/admin/system-metrics",
                "/api/admin/logs"
            ]
        }

    def get_backend_info(self):
        """Get comprehensive backend information"""
        try:
            # Get system health
            health_response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if health_response.status_code == 200:
                self.test_results["backend_info"]["health"] = health_response.json()
            
            # Get system metrics
            metrics_response = self.session.get(f"{BACKEND_URL}/metrics", timeout=10)
            if metrics_response.status_code == 200:
                self.test_results["backend_info"]["metrics"] = metrics_response.json()
                
            # Get root info
            root_response = self.session.get(f"{BACKEND_URL}/", timeout=10)
            if root_response.status_code == 200:
                self.test_results["backend_info"]["root"] = root_response.json()
                
        except Exception as e:
            self.test_results["backend_info"]["error"] = str(e)

    def authenticate(self) -> bool:
        """Attempt authentication with the backend"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.test_results["authentication_status"] = "success"
                    return True
                elif "token" in data:
                    self.auth_token = data["token"]
                    self.test_results["authentication_status"] = "success"
                    return True
                else:
                    self.test_results["authentication_status"] = "failed - no token in response"
                    return False
            else:
                self.test_results["authentication_status"] = f"failed - status {response.status_code}"
                return False
                
        except Exception as e:
            self.test_results["authentication_status"] = f"error - {str(e)}"
            return False

    def test_endpoint(self, endpoint: str, method: str = "GET", data: dict = None) -> Tuple[bool, dict]:
        """Test a single endpoint and return detailed results"""
        start_time = time.time()
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            url = f"{BACKEND_URL}{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data, timeout=10)
            else:
                response = self.session.request(method, url, headers=headers, json=data, timeout=10)
            
            response_time = time.time() - start_time
            
            try:
                response_data = response.json()
                has_json = True
                response_preview = str(response_data)[:200] + "..." if len(str(response_data)) > 200 else str(response_data)
            except:
                response_data = response.text
                has_json = False
                response_preview = response_data[:200] + "..." if len(response_data) > 200 else response_data
            
            success = response.status_code in [200, 201]
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "response_time": response_time,
                "response_size": len(response.text),
                "success": success,
                "has_json": has_json,
                "response_preview": response_preview,
                "error": None if success else f"HTTP {response.status_code}"
            }
            
            # Check for mock/hardcoded data indicators
            if has_json and isinstance(response_data, dict):
                response_str = str(response_data).lower()
                mock_indicators = ["test", "mock", "fake", "dummy", "example", "placeholder", "lorem"]
                has_mock_data = any(indicator in response_str for indicator in mock_indicators)
                result["potential_mock_data"] = has_mock_data
            else:
                result["potential_mock_data"] = False
            
            return success, result
            
        except requests.exceptions.Timeout:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time": time.time() - start_time,
                "response_size": 0,
                "success": False,
                "has_json": False,
                "response_preview": "Request timed out",
                "error": "Timeout",
                "potential_mock_data": False
            }
            return False, result
            
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time": time.time() - start_time,
                "response_size": 0,
                "success": False,
                "has_json": False,
                "response_preview": f"Exception: {str(e)}",
                "error": str(e),
                "potential_mock_data": False
            }
            return False, result

    def test_category(self, category_name: str, endpoints: List[str]):
        """Test all endpoints in a category"""
        print(f"\n🔍 Testing {category_name} ({len(endpoints)} endpoints)...")
        
        category_results = {
            "total": len(endpoints),
            "successful": 0,
            "failed": 0,
            "endpoints": []
        }
        
        for endpoint in endpoints:
            success, result = self.test_endpoint(endpoint)
            category_results["endpoints"].append(result)
            
            if success:
                category_results["successful"] += 1
                self.test_results["successful_tests"] += 1
                print(f"  ✅ {endpoint} - {result['status_code']} ({result['response_time']:.3f}s) - {result['response_size']} chars")
            else:
                category_results["failed"] += 1
                self.test_results["failed_tests"] += 1
                print(f"  ❌ {endpoint} - {result['error']} ({result['response_time']:.3f}s)")
                
                # Track critical issues
                if result['status_code'] == 500:
                    self.test_results["critical_issues"].append({
                        "endpoint": endpoint,
                        "issue": "Internal Server Error",
                        "details": result['response_preview']
                    })
                elif result['status_code'] == 404:
                    self.test_results["critical_issues"].append({
                        "endpoint": endpoint,
                        "issue": "Endpoint Not Found",
                        "details": "API endpoint not implemented"
                    })
                elif result['status_code'] == 403:
                    self.test_results["critical_issues"].append({
                        "endpoint": endpoint,
                        "issue": "Authentication Required",
                        "details": "Endpoint requires authentication"
                    })
            
            # Track potential mock data
            if result.get("potential_mock_data", False):
                self.test_results["data_quality_issues"].append({
                    "endpoint": endpoint,
                    "issue": "Potential mock/hardcoded data detected",
                    "details": result['response_preview']
                })
            
            self.test_results["total_endpoints_tested"] += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        success_rate = (category_results["successful"] / category_results["total"]) * 100
        print(f"  📊 {category_name}: {category_results['successful']}/{category_results['total']} ({success_rate:.1f}% success)")
        
        self.test_results["endpoints_by_category"][category_name] = category_results

    def analyze_performance(self):
        """Analyze performance metrics across all tests"""
        print(f"\n📊 PERFORMANCE ANALYSIS")
        
        all_response_times = []
        successful_response_times = []
        
        for category_data in self.test_results["endpoints_by_category"].values():
            for endpoint_result in category_data["endpoints"]:
                all_response_times.append(endpoint_result["response_time"])
                if endpoint_result["success"]:
                    successful_response_times.append(endpoint_result["response_time"])
        
        if all_response_times:
            self.test_results["performance_metrics"] = {
                "average_response_time": sum(all_response_times) / len(all_response_times),
                "max_response_time": max(all_response_times),
                "min_response_time": min(all_response_times),
                "successful_avg_response_time": sum(successful_response_times) / len(successful_response_times) if successful_response_times else 0,
                "total_test_duration": (datetime.now() - self.test_results["start_time"]).total_seconds()
            }
        
        print(f"  📈 Average Response Time: {self.test_results['performance_metrics'].get('average_response_time', 0):.3f}s")
        print(f"  📈 Successful Endpoints Avg: {self.test_results['performance_metrics'].get('successful_avg_response_time', 0):.3f}s")
        print(f"  📈 Total Test Duration: {self.test_results['performance_metrics'].get('total_test_duration', 0):.1f}s")

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print(f"\n📋 COMPREHENSIVE FINAL REPORT")
        print("=" * 80)
        
        # Backend Information
        if "metrics" in self.test_results["backend_info"]:
            metrics = self.test_results["backend_info"]["metrics"]
            print(f"🏗️  BACKEND INFRASTRUCTURE:")
            print(f"   Platform: {metrics.get('platform', {}).get('name', 'Unknown')} v{metrics.get('platform', {}).get('version', 'Unknown')}")
            print(f"   Modules Loaded: {metrics.get('modules', {}).get('successfully_loaded', 0)}/{metrics.get('modules', {}).get('total_available', 0)} ({metrics.get('modules', {}).get('load_success_rate', '0%')})")
            print(f"   Working Modules: {', '.join(metrics.get('modules', {}).get('working_modules', []))}")
            print(f"   Database Collections: {metrics.get('database', {}).get('total_collections', 0)}")
            print(f"   API Endpoints Operational: {metrics.get('audit_status', {}).get('api_endpoints_operational', 0)}")
        
        # Calculate overall success rate
        total_tested = self.test_results["total_endpoints_tested"]
        successful = self.test_results["successful_tests"]
        success_rate = (successful / total_tested * 100) if total_tested > 0 else 0
        
        print(f"\n🎯 COMPREHENSIVE BACKEND TEST RESULTS")
        print(f"   Total Endpoints Tested: {total_tested}")
        print(f"   Successful Tests: {successful}")
        print(f"   Failed Tests: {self.test_results['failed_tests']}")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        print(f"   Authentication Status: {self.test_results['authentication_status']}")
        
        # Production readiness assessment
        print(f"\n🏭 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            print(f"   ✅ EXCELLENT - {success_rate:.1f}% success rate (≥90%)")
            readiness = "PRODUCTION READY"
        elif success_rate >= 75:
            print(f"   ✅ GOOD - {success_rate:.1f}% success rate (≥75%)")
            readiness = "MOSTLY PRODUCTION READY"
        elif success_rate >= 50:
            print(f"   ⚠️  FAIR - {success_rate:.1f}% success rate (≥50%)")
            readiness = "NEEDS IMPROVEMENT"
        else:
            print(f"   ❌ POOR - {success_rate:.1f}% success rate (<50%)")
            readiness = "NOT PRODUCTION READY"
        
        print(f"   Status: {readiness}")
        
        # Category breakdown
        print(f"\n📊 CATEGORY BREAKDOWN:")
        for category, data in self.test_results["endpoints_by_category"].items():
            cat_success_rate = (data["successful"] / data["total"] * 100) if data["total"] > 0 else 0
            status_icon = "✅" if cat_success_rate >= 75 else "⚠️" if cat_success_rate >= 50 else "❌"
            print(f"   {status_icon} {category}: {data['successful']}/{data['total']} ({cat_success_rate:.1f}%)")
        
        # Critical issues summary
        if self.test_results["critical_issues"]:
            print(f"\n🔴 CRITICAL ISSUES FOUND ({len(self.test_results['critical_issues'])}):")
            issue_counts = {}
            for issue in self.test_results["critical_issues"]:
                issue_type = issue["issue"]
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            
            for issue_type, count in issue_counts.items():
                print(f"   - {issue_type}: {count} endpoints")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND")
        
        # Data quality assessment
        if self.test_results["data_quality_issues"]:
            print(f"\n⚠️  DATA QUALITY ISSUES ({len(self.test_results['data_quality_issues'])}):")
            print(f"   - Potential mock/hardcoded data detected in {len(self.test_results['data_quality_issues'])} endpoints")
        else:
            print(f"\n✅ NO DATA QUALITY ISSUES DETECTED")
        
        # Performance summary
        perf = self.test_results["performance_metrics"]
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   - Average Response Time: {perf.get('average_response_time', 0):.3f}s")
        print(f"   - Fastest Response: {perf.get('min_response_time', 0):.3f}s")
        print(f"   - Slowest Response: {perf.get('max_response_time', 0):.3f}s")
        print(f"   - Total Test Duration: {perf.get('total_test_duration', 0):.1f}s")
        
        # Performance assessment
        avg_time = perf.get('average_response_time', 0)
        if avg_time < 1.0:
            print(f"   ✅ EXCELLENT performance (< 1s average)")
        elif avg_time < 3.0:
            print(f"   ✅ GOOD performance (< 3s average)")
        elif avg_time < 5.0:
            print(f"   ⚠️  ACCEPTABLE performance (< 5s average)")
        else:
            print(f"   ❌ POOR performance (≥ 5s average)")
        
        # Key findings and recommendations
        print(f"\n🔍 KEY FINDINGS:")
        working_modules = self.test_results["backend_info"].get("metrics", {}).get("modules", {}).get("working_modules", [])
        if len(working_modules) < 10:
            print(f"   ⚠️  Only {len(working_modules)} out of 55 API modules are working due to syntax errors")
            print(f"   🔧 RECOMMENDATION: Fix syntax errors in failed modules to unlock full API functionality")
        
        if self.test_results["authentication_status"] != "success":
            print(f"   ❌ Authentication system is not working - this blocks access to protected endpoints")
            print(f"   🔧 RECOMMENDATION: Fix authentication module to enable full endpoint testing")
        
        print("=" * 80)
        print(f"🎯 COMPREHENSIVE BACKEND TEST COMPLETED")
        print(f"   Final Assessment: {readiness}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Endpoints: {total_tested}")
        print("=" * 80)

    def run_comprehensive_test(self):
        """Run the complete comprehensive backend test"""
        print("🚀 STARTING COMPREHENSIVE FULL-SCALE BACKEND TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Target: Test ALL available API endpoints for production readiness")
        print("=" * 80)
        
        # Step 1: Get backend information
        print("\n📡 STEP 1: BACKEND INFRASTRUCTURE ANALYSIS")
        self.get_backend_info()
        
        if "metrics" in self.test_results["backend_info"]:
            metrics = self.test_results["backend_info"]["metrics"]
            print(f"   ✅ Backend Platform: {metrics.get('platform', {}).get('name', 'Unknown')} v{metrics.get('platform', {}).get('version', 'Unknown')}")
            print(f"   ✅ Modules Loaded: {metrics.get('modules', {}).get('successfully_loaded', 0)}/{metrics.get('modules', {}).get('total_available', 0)}")
            print(f"   ✅ Working Modules: {', '.join(metrics.get('modules', {}).get('working_modules', []))}")
            print(f"   ✅ Database Collections: {metrics.get('database', {}).get('total_collections', 0)}")
        
        # Step 2: Authentication
        print("\n🔐 STEP 2: AUTHENTICATION")
        auth_success = self.authenticate()
        if auth_success:
            print("   ✅ Authentication successful - Can test protected endpoints")
        else:
            print("   ❌ Authentication failed - Will test public endpoints only")
            print(f"   ⚠️  Status: {self.test_results['authentication_status']}")
        
        # Step 3: Test all endpoint categories
        print(f"\n🧪 STEP 3: COMPREHENSIVE ENDPOINT TESTING")
        total_endpoints = sum(len(endpoints) for endpoints in self.endpoint_categories.values())
        print(f"Testing {len(self.endpoint_categories)} categories with {total_endpoints} total endpoints")
        
        for category_name, endpoints in self.endpoint_categories.items():
            self.test_category(category_name, endpoints)
        
        # Step 4: Performance analysis
        self.analyze_performance()
        
        # Step 5: Generate comprehensive report
        self.generate_final_report()

def main():
    """Main test execution function"""
    tester = ComprehensiveBackendTester()
    
    try:
        tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()