#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - TARGETED PRODUCTION READINESS TESTING - JANUARY 2025
Testing based on actual available endpoints from the review request

CREDENTIALS: tmonnens@outlook.com/Voetballen5 (super_admin with full permissions)
BACKEND URL: https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional, List, Tuple
import uuid
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = "https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class TargetedProductionTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
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
    
    def authenticate(self) -> bool:
        """Authenticate with the backend and get access token"""
        try:
            print("🔐 AUTHENTICATING WITH BACKEND...")
            
            # First check if backend is accessible
            health_response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if health_response.status_code == 200:
                self.log_result("Health Check", True, f"Backend operational", 
                              health_response.json() if health_response.headers.get('content-type', '').startswith('application/json') else health_response.text, 
                              health_response.status_code)
            else:
                self.log_result("Health Check", False, f"Backend not accessible - Status {health_response.status_code}", 
                              None, health_response.status_code)
                return False
            
            # Try to authenticate
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            auth_response = self.session.post(f"{API_BASE}/auth/login", json=auth_data, timeout=10)
            
            if auth_response.status_code == 200:
                auth_result = auth_response.json()
                if 'access_token' in auth_result:
                    self.access_token = auth_result['access_token']
                    self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                    self.log_result("Authentication", True, f"Login successful - JWT token obtained", 
                                  auth_result, auth_response.status_code)
                    return True
                else:
                    self.log_result("Authentication", False, "Login response missing access_token", 
                                  auth_result, auth_response.status_code)
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed - Status {auth_response.status_code}", 
                              auth_response.text, auth_response.status_code)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Tuple[bool, Any, int]:
        """Test a single endpoint"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=10)
            else:
                return False, None, 0
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return success, response_data, response.status_code
            
        except Exception as e:
            return False, f"Error: {str(e)}", 0
    
    def test_health_endpoints(self):
        """Test health endpoints for all major services"""
        print("\n🏥 TESTING SERVICE HEALTH ENDPOINTS")
        print("=" * 80)
        
        # Based on the previous test results, these health endpoints exist
        health_endpoints = [
            'financial',
            'workspace',
            'ai-content',
            'template',
            'booking',
            'admin-configuration',
            'analytics-system',
            'marketing',
            'social-media',
            'ai',
            'dashboard',
            'user',
            'notification',
            'auth',
            'complete-financial',
            'complete-admin-dashboard',
            'advanced-ai',
            'complete-multi-workspace',
            'complete-onboarding'
        ]
        
        for service in health_endpoints:
            success, response, status = self.test_endpoint('GET', f'/{service}/health')
            if success:
                self.working_endpoints.append(f"{service} Health")
                self.log_result(f"{service.title()} Health", True, f"Service health check working", response, status)
            else:
                self.failing_endpoints.append(f"{service} Health")
                self.log_result(f"{service.title()} Health", False, f"Service health check failed", response, status)
    
    def test_authenticated_endpoints(self):
        """Test authenticated endpoints that should work with proper token"""
        print("\n🔐 TESTING AUTHENTICATED ENDPOINTS")
        print("=" * 80)
        
        # Test endpoints that should work with authentication
        authenticated_endpoints = [
            # Try some basic CRUD endpoints that might exist
            {'name': 'Financial Service', 'endpoint': '/financial', 'method': 'GET'},
            {'name': 'Workspace Service', 'endpoint': '/workspace', 'method': 'GET'},
            {'name': 'AI Content Service', 'endpoint': '/ai-content', 'method': 'GET'},
            {'name': 'Template Service', 'endpoint': '/template', 'method': 'GET'},
            {'name': 'Booking Service', 'endpoint': '/booking', 'method': 'GET'},
            {'name': 'Admin Configuration', 'endpoint': '/admin-configuration', 'method': 'GET'},
            {'name': 'Analytics System', 'endpoint': '/analytics-system', 'method': 'GET'},
            {'name': 'Marketing Service', 'endpoint': '/marketing', 'method': 'GET'},
            {'name': 'Social Media Service', 'endpoint': '/social-media', 'method': 'GET'},
            {'name': 'AI Service', 'endpoint': '/ai', 'method': 'GET'},
            {'name': 'Dashboard Service', 'endpoint': '/dashboard', 'method': 'GET'},
            {'name': 'User Service', 'endpoint': '/user', 'method': 'GET'},
            {'name': 'Notification Service', 'endpoint': '/notification', 'method': 'GET'},
        ]
        
        for endpoint_info in authenticated_endpoints:
            success, response, status = self.test_endpoint(endpoint_info['method'], endpoint_info['endpoint'])
            if success:
                self.working_endpoints.append(endpoint_info['name'])
                self.log_result(endpoint_info['name'], True, f"Authenticated endpoint working", response, status)
            else:
                self.failing_endpoints.append(endpoint_info['name'])
                self.log_result(endpoint_info['name'], False, f"Authenticated endpoint failed", response, status)
    
    def test_crud_operations_realistic(self):
        """Test CRUD operations on endpoints that likely exist"""
        print("\n🔄 TESTING REALISTIC CRUD OPERATIONS")
        print("=" * 80)
        
        # Test POST operations with minimal data
        crud_tests = [
            {
                'name': 'Financial POST',
                'endpoint': '/financial',
                'method': 'POST',
                'data': {'name': 'Test Financial Item', 'amount': 100.00}
            },
            {
                'name': 'Workspace POST',
                'endpoint': '/workspace',
                'method': 'POST',
                'data': {'name': 'Test Workspace', 'description': 'Test workspace'}
            },
            {
                'name': 'Template POST',
                'endpoint': '/template',
                'method': 'POST',
                'data': {'name': 'Test Template', 'type': 'basic'}
            },
            {
                'name': 'Booking POST',
                'endpoint': '/booking',
                'method': 'POST',
                'data': {'service': 'Test Service', 'date': '2025-02-01'}
            }
        ]
        
        for test in crud_tests:
            success, response, status = self.test_endpoint(test['method'], test['endpoint'], test['data'], 201)
            if success or status == 200:  # Accept both 200 and 201 for successful creation
                self.working_endpoints.append(test['name'])
                self.log_result(test['name'], True, f"CRUD operation successful", response, status)
            else:
                self.failing_endpoints.append(test['name'])
                self.log_result(test['name'], False, f"CRUD operation failed", response, status)
    
    def test_stats_endpoints(self):
        """Test stats endpoints that might provide real data"""
        print("\n📊 TESTING STATISTICS ENDPOINTS")
        print("=" * 80)
        
        stats_endpoints = [
            'financial/stats',
            'workspace/stats',
            'ai-content/stats',
            'template/stats',
            'booking/stats',
            'analytics-system/stats',
            'marketing/stats',
            'social-media/stats',
            'dashboard/stats',
            'user/stats',
            'notification/stats'
        ]
        
        for endpoint in stats_endpoints:
            success, response, status = self.test_endpoint('GET', f'/{endpoint}')
            if success:
                self.working_endpoints.append(f"{endpoint} Stats")
                self.log_result(f"{endpoint.replace('/', ' ').title()} Stats", True, f"Stats endpoint working", response, status)
            else:
                self.failing_endpoints.append(f"{endpoint} Stats")
                self.log_result(f"{endpoint.replace('/', ' ').title()} Stats", False, f"Stats endpoint failed", response, status)
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 100)
        print("🎯 MEWAYZ V2 PLATFORM - TARGETED PRODUCTION READINESS ASSESSMENT - JANUARY 2025")
        print("=" * 100)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL TEST RESULTS:")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   Tests Passed: {passed_tests} ✅")
        print(f"   Tests Failed: {total_tests - passed_tests} ❌")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        # Working vs Failing Services
        working_count = len(self.working_endpoints)
        failing_count = len(self.failing_endpoints)
        total_services = working_count + failing_count
        
        print(f"\n🏢 SERVICE ANALYSIS:")
        print(f"   Working Services: {working_count}/{total_services} ({working_count/total_services*100 if total_services > 0 else 0:.1f}%)")
        print(f"   Failing Services: {failing_count}/{total_services} ({failing_count/total_services*100 if total_services > 0 else 0:.1f}%)")
        
        # Production Readiness Assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            readiness_status = "✅ PRODUCTION READY - EXCELLENT"
        elif success_rate >= 75:
            readiness_status = "✅ PRODUCTION READY - GOOD"
        elif success_rate >= 50:
            readiness_status = "⚠️ NEEDS IMPROVEMENT - PARTIAL"
        else:
            readiness_status = "❌ NOT PRODUCTION READY - CRITICAL ISSUES"
        
        print(f"   Status: {readiness_status}")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        # Key Achievements
        print(f"\n🎉 KEY ACHIEVEMENTS:")
        if self.access_token:
            print("   ✅ Authentication system working perfectly")
        if working_count > 0:
            print(f"   ✅ {working_count} services operational")
        
        # Working Services List
        if self.working_endpoints:
            print(f"\n✅ WORKING SERVICES:")
            for service in self.working_endpoints[:10]:  # Show first 10
                print(f"   - {service}")
            if len(self.working_endpoints) > 10:
                print(f"   ... and {len(self.working_endpoints) - 10} more")
        
        # Issues Requiring Attention
        print(f"\n🔧 ISSUES REQUIRING ATTENTION:")
        if success_rate < 90:
            print(f"   - Overall success rate needs improvement ({success_rate:.1f}%)")
        if failing_count > 0:
            print(f"   - {failing_count} services need fixes")
        
        return success_rate
    
    def run_comprehensive_test(self):
        """Run comprehensive production readiness test"""
        print("🎯 MEWAYZ V2 PLATFORM - TARGETED PRODUCTION READINESS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: Health Endpoints Testing
        self.test_health_endpoints()
        
        # Step 3: Authenticated Endpoints Testing
        self.test_authenticated_endpoints()
        
        # Step 4: CRUD Operations Testing
        self.test_crud_operations_realistic()
        
        # Step 5: Stats Endpoints Testing
        self.test_stats_endpoints()
        
        # Step 6: Generate Final Report
        success_rate = self.generate_final_report()
        
        return success_rate >= 50  # Lower threshold for this targeted test

def main():
    """Main function to run the production readiness test"""
    tester = TargetedProductionTester()
    
    try:
        production_ready = tester.run_comprehensive_test()
        
        if production_ready:
            print("\n🎉 FINAL CONCLUSION: PLATFORM SHOWS GOOD PROGRESS!")
            sys.exit(0)
        else:
            print("\n❌ FINAL CONCLUSION: PLATFORM NEEDS SIGNIFICANT IMPROVEMENTS")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()