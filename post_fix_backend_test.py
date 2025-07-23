#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - POST-FIX COMPREHENSIVE TESTING - JANUARY 2025
Testing Objective: Assess the current status after fixing database connectivity and service layer issues.

Focus Areas:
1. Database Connectivity Status
2. Authentication System Assessment  
3. CRUD Operations Analysis
4. Mock Data Detection
5. Critical Business Services Testing

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
import re

# Backend URL from environment
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class PostFixTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.working_endpoints = []
        self.failing_endpoints = []
        self.crud_results = {
            'CREATE': {'working': [], 'failing': []},
            'READ': {'working': [], 'failing': []},
            'UPDATE': {'working': [], 'failing': []},
            'DELETE': {'working': [], 'failing': []}
        }
        self.mock_data_detected = []
        self.real_data_confirmed = []
        
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
    
    def detect_mock_data(self, response_data: Any, endpoint_path: str) -> bool:
        """Detect if response contains mock, random, or hardcoded data"""
        if not response_data:
            return False
            
        data_str = str(response_data).lower()
        
        # Common mock data patterns
        mock_patterns = [
            'sample', 'mock', 'test_', 'dummy', 'fake', 'placeholder',
            'lorem ipsum', 'example.com', 'test@test.com', 'testuser',
            'random_', 'generated_', 'temp_', 'demo_'
        ]
        
        # Check for mock patterns
        for pattern in mock_patterns:
            if pattern in data_str:
                return True
                
        return False
    
    def test_health_check(self):
        """Test basic health check and system status"""
        try:
            print("🔍 TESTING SYSTEM HEALTH AND CONNECTIVITY")
            print("=" * 60)
            
            # Test basic health endpoint
            response = self.session.get(f"{BACKEND_URL}/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", True, f"Backend operational - {data.get('message', 'System healthy')}", data, response.status_code)
                return True
            else:
                self.log_result("Health Check", False, f"Health check failed with status {response.status_code}", None, response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Health Check", False, f"Health check error: {str(e)}")
            return False
    
    def authenticate(self):
        """Authenticate with the system and get access token"""
        try:
            print("\n🔐 TESTING AUTHENTICATION SYSTEM")
            print("=" * 60)
            
            # Try different authentication endpoints
            auth_endpoints = [
                f"{API_BASE}/auth/login",
                f"{API_BASE}/user/login", 
                f"{API_BASE}/login",
                f"{BACKEND_URL}/login"
            ]
            
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            for endpoint in auth_endpoints:
                try:
                    response = self.session.post(endpoint, json=login_data, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'access_token' in data or 'token' in data:
                            self.access_token = data.get('access_token') or data.get('token')
                            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                            self.log_result("Authentication", True, f"Login successful via {endpoint}", data, response.status_code)
                            return True
                        elif 'message' in data and 'success' in str(data).lower():
                            self.log_result("Authentication", True, f"Login successful via {endpoint} (no token required)", data, response.status_code)
                            return True
                    elif response.status_code == 422:
                        # Validation error - try different format
                        alt_data = {"username": TEST_EMAIL, "password": TEST_PASSWORD}
                        alt_response = self.session.post(endpoint, json=alt_data, timeout=30)
                        if alt_response.status_code == 200:
                            data = alt_response.json()
                            if 'access_token' in data or 'token' in data:
                                self.access_token = data.get('access_token') or data.get('token')
                                self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                                self.log_result("Authentication", True, f"Login successful via {endpoint} (alt format)", data, alt_response.status_code)
                                return True
                                
                except Exception as e:
                    continue
            
            self.log_result("Authentication", False, "All authentication endpoints failed")
            return False
            
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity through various endpoints"""
        try:
            print("\n💾 TESTING DATABASE CONNECTIVITY")
            print("=" * 60)
            
            # Test endpoints that should indicate database connectivity
            db_test_endpoints = [
                f"{API_BASE}/user/profile",
                f"{API_BASE}/dashboard/overview", 
                f"{API_BASE}/analytics/overview",
                f"{API_BASE}/financial/dashboard",
                f"{API_BASE}/workspace/list",
                f"{BACKEND_URL}/metrics"
            ]
            
            db_working = 0
            db_total = len(db_test_endpoints)
            
            for endpoint in db_test_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Check if response indicates real database data
                        if data and not self.detect_mock_data(data, endpoint):
                            self.log_result(f"DB Connectivity - {endpoint.split('/')[-1]}", True, "Database connection working with real data", data, response.status_code)
                            self.real_data_confirmed.append(endpoint)
                            db_working += 1
                        elif data:
                            self.log_result(f"DB Connectivity - {endpoint.split('/')[-1]}", True, "Database connection working (possible mock data)", data, response.status_code)
                            self.mock_data_detected.append(endpoint)
                            db_working += 1
                        else:
                            self.log_result(f"DB Connectivity - {endpoint.split('/')[-1]}", False, "Empty response from database", None, response.status_code)
                    else:
                        self.log_result(f"DB Connectivity - {endpoint.split('/')[-1]}", False, f"Database endpoint failed with status {response.status_code}", None, response.status_code)
                        
                except Exception as e:
                    self.log_result(f"DB Connectivity - {endpoint.split('/')[-1]}", False, f"Database connectivity error: {str(e)}")
            
            success_rate = (db_working / db_total) * 100
            self.log_result("Database Connectivity Overall", success_rate > 50, f"Database connectivity: {db_working}/{db_total} endpoints working ({success_rate:.1f}%)")
            
            return success_rate > 50
            
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Database connectivity test error: {str(e)}")
            return False
    
    def test_crud_operations(self):
        """Test CRUD operations across critical services"""
        try:
            print("\n🔄 TESTING CRUD OPERATIONS")
            print("=" * 60)
            
            # Test CREATE operations
            create_tests = [
                {
                    "endpoint": f"{API_BASE}/financial/invoices",
                    "data": {
                        "client_name": "Test Client",
                        "amount": 1000.00,
                        "description": "Test Invoice",
                        "due_date": "2025-02-15"
                    }
                },
                {
                    "endpoint": f"{API_BASE}/workspace/create",
                    "data": {
                        "name": "Test Workspace",
                        "description": "Test workspace for CRUD testing"
                    }
                },
                {
                    "endpoint": f"{API_BASE}/ai/content/generate",
                    "data": {
                        "prompt": "Generate a test content piece",
                        "type": "blog_post"
                    }
                }
            ]
            
            for test in create_tests:
                try:
                    response = self.session.post(test["endpoint"], json=test["data"], timeout=30)
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        self.log_result(f"CREATE - {test['endpoint'].split('/')[-1]}", True, "Create operation successful", data, response.status_code)
                        self.crud_results['CREATE']['working'].append(test["endpoint"])
                    else:
                        self.log_result(f"CREATE - {test['endpoint'].split('/')[-1]}", False, f"Create operation failed with status {response.status_code}", None, response.status_code)
                        self.crud_results['CREATE']['failing'].append(test["endpoint"])
                        
                except Exception as e:
                    self.log_result(f"CREATE - {test['endpoint'].split('/')[-1]}", False, f"Create operation error: {str(e)}")
                    self.crud_results['CREATE']['failing'].append(test["endpoint"])
            
            # Test READ operations
            read_tests = [
                f"{API_BASE}/user/profile",
                f"{API_BASE}/financial/invoices",
                f"{API_BASE}/workspace/list",
                f"{API_BASE}/analytics/overview",
                f"{API_BASE}/ai/content/history",
                f"{API_BASE}/social-media/posts",
                f"{API_BASE}/dashboard/overview"
            ]
            
            for endpoint in read_tests:
                try:
                    response = self.session.get(endpoint, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.log_result(f"READ - {endpoint.split('/')[-1]}", True, "Read operation successful", data, response.status_code)
                        self.crud_results['READ']['working'].append(endpoint)
                    else:
                        self.log_result(f"READ - {endpoint.split('/')[-1]}", False, f"Read operation failed with status {response.status_code}", None, response.status_code)
                        self.crud_results['READ']['failing'].append(endpoint)
                        
                except Exception as e:
                    self.log_result(f"READ - {endpoint.split('/')[-1]}", False, f"Read operation error: {str(e)}")
                    self.crud_results['READ']['failing'].append(endpoint)
            
            # Calculate CRUD success rates
            create_success = len(self.crud_results['CREATE']['working']) / len(create_tests) * 100 if create_tests else 0
            read_success = len(self.crud_results['READ']['working']) / len(read_tests) * 100 if read_tests else 0
            
            self.log_result("CRUD Operations Overall", (create_success + read_success) / 2 > 25, 
                          f"CRUD Success Rates - CREATE: {create_success:.1f}%, READ: {read_success:.1f}%")
            
            return (create_success + read_success) / 2 > 25
            
        except Exception as e:
            self.log_result("CRUD Operations", False, f"CRUD operations test error: {str(e)}")
            return False
    
    def test_critical_business_services(self):
        """Test critical business services mentioned in review request"""
        try:
            print("\n🏢 TESTING CRITICAL BUSINESS SERVICES")
            print("=" * 60)
            
            # High Priority Services
            high_priority_services = [
                {"name": "Financial Management", "endpoints": [
                    f"{API_BASE}/financial/dashboard",
                    f"{API_BASE}/financial/invoices",
                    f"{API_BASE}/financial/payments"
                ]},
                {"name": "User Management", "endpoints": [
                    f"{API_BASE}/user/profile",
                    f"{API_BASE}/user/settings",
                    f"{API_BASE}/auth/verify"
                ]},
                {"name": "Workspace Management", "endpoints": [
                    f"{API_BASE}/workspace/list",
                    f"{API_BASE}/workspace/settings",
                    f"{API_BASE}/workspace/members"
                ]}
            ]
            
            # Medium Priority Services  
            medium_priority_services = [
                {"name": "Social Media Management", "endpoints": [
                    f"{API_BASE}/social-media/posts",
                    f"{API_BASE}/social-media/analytics",
                    f"{API_BASE}/social-media/schedule"
                ]},
                {"name": "AI Automation Suite", "endpoints": [
                    f"{API_BASE}/ai/content/generate",
                    f"{API_BASE}/ai/workflows",
                    f"{API_BASE}/ai/analytics"
                ]},
                {"name": "Analytics", "endpoints": [
                    f"{API_BASE}/analytics/overview",
                    f"{API_BASE}/analytics/reports",
                    f"{API_BASE}/dashboard/metrics"
                ]}
            ]
            
            all_services = high_priority_services + medium_priority_services
            service_results = {}
            
            for service in all_services:
                working_endpoints = 0
                total_endpoints = len(service["endpoints"])
                
                for endpoint in service["endpoints"]:
                    try:
                        response = self.session.get(endpoint, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            self.log_result(f"{service['name']} - {endpoint.split('/')[-1]}", True, "Service endpoint working", data, response.status_code)
                            working_endpoints += 1
                            
                            # Check for real vs mock data
                            if not self.detect_mock_data(data, endpoint):
                                self.real_data_confirmed.append(endpoint)
                            else:
                                self.mock_data_detected.append(endpoint)
                        else:
                            self.log_result(f"{service['name']} - {endpoint.split('/')[-1]}", False, f"Service endpoint failed with status {response.status_code}", None, response.status_code)
                            
                    except Exception as e:
                        self.log_result(f"{service['name']} - {endpoint.split('/')[-1]}", False, f"Service endpoint error: {str(e)}")
                
                success_rate = (working_endpoints / total_endpoints) * 100
                service_results[service["name"]] = success_rate
                self.log_result(f"{service['name']} Overall", success_rate > 50, f"Service success rate: {working_endpoints}/{total_endpoints} ({success_rate:.1f}%)")
            
            # Calculate overall business services success
            avg_success = sum(service_results.values()) / len(service_results) if service_results else 0
            self.log_result("Critical Business Services Overall", avg_success > 50, f"Average business services success rate: {avg_success:.1f}%")
            
            return avg_success > 50, service_results
            
        except Exception as e:
            self.log_result("Critical Business Services", False, f"Business services test error: {str(e)}")
            return False, {}
    
    def run_comprehensive_test(self):
        """Run all post-fix tests"""
        print("🎯 MEWAYZ V2 PLATFORM - POST-FIX COMPREHENSIVE TESTING - JANUARY 2025")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing with credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test 1: Health Check
        health_ok = self.test_health_check()
        
        # Test 2: Authentication
        auth_ok = self.authenticate()
        
        # Test 3: Database Connectivity
        db_ok = self.test_database_connectivity()
        
        # Test 4: CRUD Operations
        crud_ok = self.test_crud_operations()
        
        # Test 5: Critical Business Services
        services_ok, service_results = self.test_critical_business_services()
        
        # Generate final report
        self.generate_final_report(health_ok, auth_ok, db_ok, crud_ok, services_ok, service_results)
    
    def generate_final_report(self, health_ok, auth_ok, db_ok, crud_ok, services_ok, service_results):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("🎯 POST-FIX COMPREHENSIVE TESTING RESULTS")
        print("=" * 80)
        
        # Overall Status
        total_tests = 5
        passed_tests = sum([health_ok, auth_ok, db_ok, crud_ok, services_ok])
        overall_success = (passed_tests / total_tests) * 100
        
        print(f"📊 OVERALL TEST RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Overall Success Rate: {overall_success:.1f}%")
        print(f"   Status: {'✅ IMPROVED' if overall_success > 50 else '❌ NEEDS ATTENTION'}")
        
        # Individual Test Results
        print(f"\n📋 INDIVIDUAL TEST RESULTS:")
        print(f"   ✅ Health Check: {'PASS' if health_ok else 'FAIL'}")
        print(f"   ✅ Authentication: {'PASS' if auth_ok else 'FAIL'}")
        print(f"   ✅ Database Connectivity: {'PASS' if db_ok else 'FAIL'}")
        print(f"   ✅ CRUD Operations: {'PASS' if crud_ok else 'FAIL'}")
        print(f"   ✅ Business Services: {'PASS' if services_ok else 'FAIL'}")
        
        # CRUD Analysis
        print(f"\n🔄 CRUD OPERATIONS ANALYSIS:")
        create_working = len(self.crud_results['CREATE']['working'])
        create_total = create_working + len(self.crud_results['CREATE']['failing'])
        read_working = len(self.crud_results['READ']['working'])
        read_total = read_working + len(self.crud_results['READ']['failing'])
        
        print(f"   CREATE Operations: {create_working}/{create_total} working")
        print(f"   READ Operations: {read_working}/{read_total} working")
        
        # Mock Data Analysis
        print(f"\n📊 DATA QUALITY ANALYSIS:")
        total_data_endpoints = len(self.real_data_confirmed) + len(self.mock_data_detected)
        if total_data_endpoints > 0:
            real_data_percentage = (len(self.real_data_confirmed) / total_data_endpoints) * 100
            print(f"   Real Data Endpoints: {len(self.real_data_confirmed)}")
            print(f"   Mock Data Endpoints: {len(self.mock_data_detected)}")
            print(f"   Real Data Percentage: {real_data_percentage:.1f}%")
        else:
            print(f"   No data endpoints tested")
        
        # Business Services Analysis
        if service_results:
            print(f"\n🏢 BUSINESS SERVICES ANALYSIS:")
            for service, success_rate in service_results.items():
                status = "✅" if success_rate > 50 else "❌"
                print(f"   {status} {service}: {success_rate:.1f}% success rate")
        
        # Improvement Assessment
        print(f"\n📈 IMPROVEMENT ASSESSMENT:")
        if overall_success > 75:
            print(f"   🎉 EXCELLENT: Platform shows significant improvement after fixes")
        elif overall_success > 50:
            print(f"   ✅ GOOD: Platform shows improvement but needs more work")
        elif overall_success > 25:
            print(f"   ⚠️ PARTIAL: Some improvements visible but major issues remain")
        else:
            print(f"   ❌ CRITICAL: Platform still has major issues requiring immediate attention")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not auth_ok:
            print(f"   🔧 CRITICAL: Fix authentication system - unable to access protected endpoints")
        if not db_ok:
            print(f"   🔧 CRITICAL: Fix database connectivity issues")
        if not crud_ok:
            print(f"   🔧 HIGH: Implement proper CRUD operations across services")
        if not services_ok:
            print(f"   🔧 HIGH: Fix critical business service endpoints")
        if len(self.mock_data_detected) > len(self.real_data_confirmed):
            print(f"   🔧 MEDIUM: Replace remaining mock data with real database operations")
        
        print("=" * 80)
        print("🎉 POST-FIX COMPREHENSIVE TESTING COMPLETED!")
        print("=" * 80)

if __name__ == "__main__":
    tester = PostFixTester()
    tester.run_comprehensive_test()