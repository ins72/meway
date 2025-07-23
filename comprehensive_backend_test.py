#!/usr/bin/env python3
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
BACKEND_URL = "https://d70b9379-58ef-4e6d-9a10-f0eebb21d382.preview.emergentagent.com"
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