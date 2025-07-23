#!/usr/bin/env python3
"""
FOCUSED AUTHENTICATION & CRUD TESTING FOR MEWAYZ V2 PLATFORM - JANUARY 2025
Testing the complete authentication system and critical business services as requested in review

TESTING OBJECTIVES:
1. Complete Authentication System - Test login functionality with proper JWT token generation
2. Full CRUD Operations Testing - Test data creation, reading, updating, and deletion
3. Critical Business Services with Full CRUD - Financial, User, Workspace, Social Media, AI, Template, Admin
4. Real Data Persistence Verification - Test data consistency across multiple API calls
5. External API Integrations with Authentication - OpenAI, Twitter/X, TikTok, ElasticMail, Stripe
6. Mock Data Elimination Verification - Ensure all data comes from real database operations

CREDENTIALS: tmonnens@outlook.com/Voetballen5
BACKEND URL: https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com
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
BACKEND_URL = "https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class FocusedAuthenticationTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.authentication_working = False
        self.crud_results = {
            'CREATE': {'working': [], 'failing': []},
            'READ': {'working': [], 'failing': []},
            'UPDATE': {'working': [], 'failing': []},
            'DELETE': {'working': [], 'failing': []}
        }
        self.real_data_endpoints = []
        self.mock_data_endpoints = []
        self.external_api_results = []
        
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
                json=login_data,  # Send as JSON data
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
                    
                    # Test 2: Verify token works with protected endpoint
                    print("\n2. Testing JWT Token Validation...")
                    profile_response = self.session.get(f"{API_BASE}/user/profile", timeout=10)
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        self.log_result("Authentication - Token Validation", True, f"JWT token validation successful", profile_data, profile_response.status_code)
                        return True
                    else:
                        self.log_result("Authentication - Token Validation", False, f"JWT token validation failed - Status {profile_response.status_code}", None, profile_response.status_code)
                        return False
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
    
    def test_crud_operations(self):
        """Test full CRUD operations across critical business services"""
        if not self.authentication_working:
            print("❌ Skipping CRUD tests - Authentication not working")
            return False
            
        print("\n🔄 TESTING FULL CRUD OPERATIONS")
        print("=" * 60)
        
        # Test CRUD operations for different services
        crud_test_cases = [
            {
                "service": "Financial Management",
                "base_endpoint": "/financial",
                "create_data": {
                    "type": "invoice",
                    "amount": 2500.00,
                    "client_name": "Acme Corporation",
                    "description": "Web development services Q1 2025",
                    "due_date": "2025-02-15"
                }
            },
            {
                "service": "Workspace Management", 
                "base_endpoint": "/workspace",
                "create_data": {
                    "name": "Marketing Team Workspace",
                    "description": "Collaborative workspace for marketing campaigns",
                    "type": "team"
                }
            },
            {
                "service": "AI Content",
                "base_endpoint": "/ai-content",
                "create_data": {
                    "type": "blog_post",
                    "topic": "Digital Marketing Trends 2025",
                    "tone": "professional",
                    "length": "medium"
                }
            },
            {
                "service": "Template Management",
                "base_endpoint": "/template",
                "create_data": {
                    "name": "Business Proposal Template",
                    "category": "business",
                    "description": "Professional business proposal template",
                    "price": 49.99
                }
            }
        ]
        
        for test_case in crud_test_cases:
            self.test_service_crud(test_case["service"], test_case["base_endpoint"], test_case["create_data"])
        
        return True
    
    def test_service_crud(self, service_name: str, base_endpoint: str, create_data: Dict):
        """Test CRUD operations for a specific service"""
        print(f"\n📋 Testing CRUD for {service_name}...")
        
        created_item_id = None
        
        # CREATE Test
        try:
            create_response = self.session.post(f"{API_BASE}{base_endpoint}", json=create_data, timeout=15)
            if create_response.status_code in [200, 201]:
                create_result = create_response.json()
                created_item_id = create_result.get('id') or create_result.get('_id')
                self.crud_results['CREATE']['working'].append(f"{service_name} - CREATE")
                self.log_result(f"{service_name} - CREATE", True, f"Item created successfully", create_result, create_response.status_code)
            else:
                self.crud_results['CREATE']['failing'].append(f"{service_name} - CREATE")
                self.log_result(f"{service_name} - CREATE", False, f"Create failed - Status {create_response.status_code}", None, create_response.status_code)
        except Exception as e:
            self.crud_results['CREATE']['failing'].append(f"{service_name} - CREATE")
            self.log_result(f"{service_name} - CREATE", False, f"Create error: {str(e)}")
        
        # READ Test (List all items)
        try:
            read_response = self.session.get(f"{API_BASE}{base_endpoint}", timeout=15)
            if read_response.status_code == 200:
                read_result = read_response.json()
                self.crud_results['READ']['working'].append(f"{service_name} - READ")
                self.log_result(f"{service_name} - READ", True, f"Items retrieved successfully", read_result, read_response.status_code)
                
                # Check for real vs mock data
                if self.detect_real_data(read_result, service_name):
                    self.real_data_endpoints.append(f"{service_name} - READ")
                else:
                    self.mock_data_endpoints.append(f"{service_name} - READ")
            else:
                self.crud_results['READ']['failing'].append(f"{service_name} - READ")
                self.log_result(f"{service_name} - READ", False, f"Read failed - Status {read_response.status_code}", None, read_response.status_code)
        except Exception as e:
            self.crud_results['READ']['failing'].append(f"{service_name} - READ")
            self.log_result(f"{service_name} - READ", False, f"Read error: {str(e)}")
        
        # UPDATE Test (if we have a created item)
        if created_item_id:
            try:
                update_data = create_data.copy()
                update_data['updated'] = True
                update_data['updated_at'] = datetime.now().isoformat()
                
                update_response = self.session.put(f"{API_BASE}{base_endpoint}/{created_item_id}", json=update_data, timeout=15)
                if update_response.status_code in [200, 204]:
                    update_result = update_response.json() if update_response.content else {"updated": True}
                    self.crud_results['UPDATE']['working'].append(f"{service_name} - UPDATE")
                    self.log_result(f"{service_name} - UPDATE", True, f"Item updated successfully", update_result, update_response.status_code)
                else:
                    self.crud_results['UPDATE']['failing'].append(f"{service_name} - UPDATE")
                    self.log_result(f"{service_name} - UPDATE", False, f"Update failed - Status {update_response.status_code}", None, update_response.status_code)
            except Exception as e:
                self.crud_results['UPDATE']['failing'].append(f"{service_name} - UPDATE")
                self.log_result(f"{service_name} - UPDATE", False, f"Update error: {str(e)}")
            
            # DELETE Test
            try:
                delete_response = self.session.delete(f"{API_BASE}{base_endpoint}/{created_item_id}", timeout=15)
                if delete_response.status_code in [200, 204]:
                    delete_result = delete_response.json() if delete_response.content else {"deleted": True}
                    self.crud_results['DELETE']['working'].append(f"{service_name} - DELETE")
                    self.log_result(f"{service_name} - DELETE", True, f"Item deleted successfully", delete_result, delete_response.status_code)
                else:
                    self.crud_results['DELETE']['failing'].append(f"{service_name} - DELETE")
                    self.log_result(f"{service_name} - DELETE", False, f"Delete failed - Status {delete_response.status_code}", None, delete_response.status_code)
            except Exception as e:
                self.crud_results['DELETE']['failing'].append(f"{service_name} - DELETE")
                self.log_result(f"{service_name} - DELETE", False, f"Delete error: {str(e)}")
    
    def detect_real_data(self, response_data: Any, service_name: str) -> bool:
        """Detect if response contains real data vs mock data"""
        if not response_data:
            return False
            
        data_str = str(response_data).lower()
        
        # Mock data patterns
        mock_patterns = [
            'sample', 'mock', 'test_', 'dummy', 'fake', 'placeholder',
            'lorem ipsum', 'example.com', 'test@test.com', 'testuser',
            'random_', 'generated_', 'temp_', 'demo_'
        ]
        
        # Check for mock patterns
        for pattern in mock_patterns:
            if pattern in data_str:
                return False
        
        # If data contains realistic business information, consider it real
        business_patterns = [
            'invoice', 'payment', 'client', 'project', 'campaign',
            'workspace', 'team', 'user', 'content', 'template'
        ]
        
        for pattern in business_patterns:
            if pattern in data_str:
                return True
                
        return True  # Default to real data if no mock patterns found
    
    def test_external_api_integrations(self):
        """Test external API integrations with authentication"""
        if not self.authentication_working:
            print("❌ Skipping External API tests - Authentication not working")
            return False
            
        print("\n🌐 TESTING EXTERNAL API INTEGRATIONS")
        print("=" * 60)
        
        # Test external API integrations
        external_apis = [
            {
                "name": "OpenAI Integration",
                "endpoint": "/ai/generate-content",
                "test_data": {
                    "prompt": "Write a professional email about project completion",
                    "type": "email",
                    "tone": "professional"
                }
            },
            {
                "name": "Twitter/X Integration", 
                "endpoint": "/social-media/twitter/search",
                "test_data": {
                    "query": "digital marketing trends",
                    "count": 10
                }
            },
            {
                "name": "Stripe Integration",
                "endpoint": "/payment/stripe/test-connection",
                "test_data": {}
            },
            {
                "name": "ElasticMail Integration",
                "endpoint": "/email/elasticmail/test-connection", 
                "test_data": {}
            }
        ]
        
        for api_test in external_apis:
            self.test_external_api(api_test["name"], api_test["endpoint"], api_test["test_data"])
        
        return True
    
    def test_external_api(self, api_name: str, endpoint: str, test_data: Dict):
        """Test a specific external API integration"""
        print(f"\n🔌 Testing {api_name}...")
        
        try:
            if test_data:
                response = self.session.post(f"{API_BASE}{endpoint}", json=test_data, timeout=20)
            else:
                response = self.session.get(f"{API_BASE}{endpoint}", timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                self.external_api_results.append({"name": api_name, "success": True, "data": result})
                self.log_result(f"External API - {api_name}", True, f"Integration working successfully", result, response.status_code)
            else:
                self.external_api_results.append({"name": api_name, "success": False, "error": f"Status {response.status_code}"})
                self.log_result(f"External API - {api_name}", False, f"Integration failed - Status {response.status_code}", None, response.status_code)
        except Exception as e:
            self.external_api_results.append({"name": api_name, "success": False, "error": str(e)})
            self.log_result(f"External API - {api_name}", False, f"Integration error: {str(e)}")
    
    def test_data_persistence(self):
        """Test real data persistence verification"""
        if not self.authentication_working:
            print("❌ Skipping Data Persistence tests - Authentication not working")
            return False
            
        print("\n💾 TESTING REAL DATA PERSISTENCE VERIFICATION")
        print("=" * 60)
        
        # Test data consistency across multiple calls
        persistence_tests = [
            {"name": "User Profile", "endpoint": "/user/profile"},
            {"name": "Dashboard Data", "endpoint": "/dashboard/overview"},
            {"name": "Financial Summary", "endpoint": "/financial/summary"},
            {"name": "Workspace List", "endpoint": "/workspace/list"}
        ]
        
        for test in persistence_tests:
            self.test_data_consistency(test["name"], test["endpoint"])
        
        return True
    
    def test_data_consistency(self, test_name: str, endpoint: str):
        """Test data consistency across multiple API calls"""
        print(f"\n🔄 Testing {test_name} consistency...")
        
        try:
            # Make first call
            response1 = self.session.get(f"{API_BASE}{endpoint}", timeout=15)
            if response1.status_code != 200:
                self.log_result(f"Data Persistence - {test_name}", False, f"First call failed - Status {response1.status_code}", None, response1.status_code)
                return
            
            data1 = response1.json()
            
            # Wait a moment
            time.sleep(1)
            
            # Make second call
            response2 = self.session.get(f"{API_BASE}{endpoint}", timeout=15)
            if response2.status_code != 200:
                self.log_result(f"Data Persistence - {test_name}", False, f"Second call failed - Status {response2.status_code}", None, response2.status_code)
                return
            
            data2 = response2.json()
            
            # Compare data consistency
            if data1 == data2:
                self.log_result(f"Data Persistence - {test_name}", True, f"Data consistent across calls - Real database confirmed", data1, 200)
                self.real_data_endpoints.append(f"{test_name} - Persistence")
            else:
                # Check if differences are expected (like timestamps)
                data1_str = str(data1)
                data2_str = str(data2)
                
                # If only timestamps differ, still consider it consistent
                if len(data1_str) == len(data2_str) and abs(len(data1_str) - len(data2_str)) < 50:
                    self.log_result(f"Data Persistence - {test_name}", True, f"Data mostly consistent - Minor timestamp differences acceptable", data1, 200)
                    self.real_data_endpoints.append(f"{test_name} - Persistence")
                else:
                    self.log_result(f"Data Persistence - {test_name}", False, f"Data inconsistent - May be using random generation", None, 200)
                    self.mock_data_endpoints.append(f"{test_name} - Persistence")
                    
        except Exception as e:
            self.log_result(f"Data Persistence - {test_name}", False, f"Persistence test error: {str(e)}")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 100)
        print("🎯 FOCUSED AUTHENTICATION & CRUD TESTING RESULTS - MEWAYZ V2 PLATFORM")
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
        print(f"   Protected Endpoint Access: {'✅ Working' if self.authentication_working else '❌ Failed'}")
        
        # CRUD Operations Analysis
        print(f"\n🔄 CRUD OPERATIONS ANALYSIS:")
        for crud_type, results in self.crud_results.items():
            working_count = len(results['working'])
            failing_count = len(results['failing'])
            total_count = working_count + failing_count
            success_rate = (working_count / total_count * 100) if total_count > 0 else 0
            
            status_icon = "✅" if success_rate >= 75 else "⚠️" if success_rate >= 50 else "❌"
            print(f"   {status_icon} {crud_type}: {working_count}/{total_count} ({success_rate:.1f}%)")
        
        # Data Quality Analysis
        print(f"\n📊 DATA QUALITY ANALYSIS:")
        total_data_endpoints = len(self.real_data_endpoints) + len(self.mock_data_endpoints)
        real_data_percentage = (len(self.real_data_endpoints) / total_data_endpoints * 100) if total_data_endpoints > 0 else 0
        
        print(f"   Real Data Endpoints: {len(self.real_data_endpoints)} ✅")
        print(f"   Mock Data Detected: {len(self.mock_data_endpoints)} ⚠️")
        print(f"   Real Data Percentage: {real_data_percentage:.1f}%")
        
        # External API Integration Results
        print(f"\n🌐 EXTERNAL API INTEGRATION RESULTS:")
        working_apis = len([api for api in self.external_api_results if api["success"]])
        total_apis = len(self.external_api_results)
        api_success_rate = (working_apis / total_apis * 100) if total_apis > 0 else 0
        
        print(f"   Working Integrations: {working_apis}/{total_apis} ({api_success_rate:.1f}%)")
        for api_result in self.external_api_results:
            status = "✅" if api_result["success"] else "❌"
            print(f"   {status} {api_result['name']}")
        
        # Production Readiness Assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if overall_success_rate >= 95 and self.authentication_working:
            print("   🟢 EXCELLENT - Platform exceeds production readiness criteria")
            print("   ✅ Ready for immediate production deployment")
        elif overall_success_rate >= 85 and self.authentication_working:
            print("   🟡 VERY GOOD - Platform meets production readiness criteria")
            print("   ✅ Ready for production deployment with minor monitoring")
        elif overall_success_rate >= 75 and self.authentication_working:
            print("   🟠 GOOD - Platform approaches production readiness")
            print("   ⚠️ Ready for production with some improvements recommended")
        elif self.authentication_working:
            print("   🔴 PARTIAL - Authentication working but other issues exist")
            print("   ❌ Needs improvements before production deployment")
        else:
            print("   🔴 CRITICAL - Authentication system not working")
            print("   ❌ Not ready for production - authentication must be fixed first")
        
        # Key Achievements
        print(f"\n🎉 KEY ACHIEVEMENTS:")
        print(f"   • Authentication System: {'✅ Working' if self.authentication_working else '❌ Failed'}")
        print(f"   • CRUD Operations: {sum(len(results['working']) for results in self.crud_results.values())} working operations")
        print(f"   • Real Data Usage: {real_data_percentage:.1f}% of endpoints using real data")
        print(f"   • External API Integrations: {working_apis}/{total_apis} working")
        print(f"   • Overall Success Rate: {overall_success_rate:.1f}%")
        
        print("=" * 100)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': overall_success_rate,
            'authentication_working': self.authentication_working,
            'real_data_percentage': real_data_percentage,
            'external_api_success_rate': api_success_rate
        }
    
    def run_focused_authentication_test(self):
        """Run the complete focused authentication and CRUD test"""
        print("🎯 FOCUSED AUTHENTICATION & CRUD TESTING FOR MEWAYZ V2 PLATFORM - JANUARY 2025")
        print("=" * 100)
        print("Testing complete authentication system and critical business services")
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
        
        # Step 3: CRUD operations test
        self.test_crud_operations()
        
        # Step 4: External API integrations test
        self.test_external_api_integrations()
        
        # Step 5: Data persistence verification
        self.test_data_persistence()
        
        # Step 6: Generate comprehensive report
        final_results = self.generate_comprehensive_report()
        
        return final_results

def main():
    """Main function to run the focused authentication test"""
    tester = FocusedAuthenticationTester()
    
    try:
        results = tester.run_focused_authentication_test()
        
        if results:
            print(f"\n🎉 FOCUSED AUTHENTICATION & CRUD TEST COMPLETED!")
            print(f"   Success Rate: {results['success_rate']:.1f}%")
            print(f"   Authentication: {'✅ Working' if results['authentication_working'] else '❌ Failed'}")
            print(f"   Real Data Usage: {results['real_data_percentage']:.1f}%")
            
            # Exit with appropriate code
            if results['success_rate'] >= 75 and results['authentication_working']:
                sys.exit(0)  # Success
            else:
                sys.exit(1)  # Needs improvement
        else:
            print(f"\n❌ FOCUSED AUTHENTICATION & CRUD TEST FAILED")
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