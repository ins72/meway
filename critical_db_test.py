#!/usr/bin/env python3
"""
MEWAYZ V2 PLATFORM - CRITICAL DATABASE CONNECTIVITY ASSESSMENT - JANUARY 2025
FOCUSED ON: Database connectivity issues found in health endpoints

CRITICAL FINDING: Database objects do not implement truth value testing error
This indicates the database connectivity fixes are not yet complete.

BACKEND URL: https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class DatabaseConnectivityTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.database_errors = []
        self.working_services = []
        self.failing_services = []
        
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
    
    def test_system_health(self):
        """Test basic system health"""
        try:
            print("🔍 TESTING BASIC SYSTEM HEALTH")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("System Health", True, f"Basic system operational", data, response.status_code)
                return True
            else:
                self.log_result("System Health", False, f"System health check failed", None, response.status_code)
                return False
                
        except Exception as e:
            self.log_result("System Health", False, f"System health error: {str(e)}")
            return False
    
    def test_service_health_endpoints(self):
        """Test health endpoints across all services to identify database connectivity issues"""
        try:
            print("\n💾 TESTING SERVICE HEALTH ENDPOINTS FOR DATABASE CONNECTIVITY")
            print("=" * 80)
            
            # Get all available services from OpenAPI
            try:
                openapi_response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=30)
                if openapi_response.status_code == 200:
                    openapi_data = openapi_response.json()
                    paths = openapi_data.get('paths', {})
                    
                    # Extract health endpoints
                    health_endpoints = []
                    for path in paths.keys():
                        if '/health' in path and path.startswith('/api/'):
                            health_endpoints.append(f"{BACKEND_URL}{path}")
                    
                    print(f"Found {len(health_endpoints)} health endpoints to test")
                    
                else:
                    # Fallback to known critical services
                    health_endpoints = [
                        f"{API_BASE}/auth/health",
                        f"{API_BASE}/user/health", 
                        f"{API_BASE}/financial/health",
                        f"{API_BASE}/workspace/health",
                        f"{API_BASE}/analytics/health",
                        f"{API_BASE}/ai/health",
                        f"{API_BASE}/social-media/health",
                        f"{API_BASE}/dashboard/health",
                        f"{API_BASE}/marketing/health",
                        f"{API_BASE}/admin/health"
                    ]
                    
            except Exception as e:
                print(f"Could not fetch OpenAPI spec: {e}")
                # Use fallback endpoints
                health_endpoints = [
                    f"{API_BASE}/auth/health",
                    f"{API_BASE}/user/health", 
                    f"{API_BASE}/financial/health",
                    f"{API_BASE}/workspace/health",
                    f"{API_BASE}/analytics/health"
                ]
            
            database_error_count = 0
            working_count = 0
            total_tested = 0
            
            for endpoint in health_endpoints[:20]:  # Test first 20 to avoid timeout
                try:
                    total_tested += 1
                    service_name = endpoint.split('/')[-2]
                    
                    response = self.session.get(endpoint, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            # Check for database connectivity errors
                            error_msg = data.get('error', '')
                            if 'Database objects do not implement truth value testing' in error_msg:
                                self.log_result(f"DB Health - {service_name}", False, f"CRITICAL: Database connectivity error - {error_msg[:100]}...", data, response.status_code)
                                self.database_errors.append({
                                    'service': service_name,
                                    'endpoint': endpoint,
                                    'error': error_msg
                                })
                                database_error_count += 1
                                self.failing_services.append(service_name)
                            elif data.get('healthy', False) or data.get('success', False):
                                self.log_result(f"DB Health - {service_name}", True, "Service health check passed", data, response.status_code)
                                working_count += 1
                                self.working_services.append(service_name)
                            else:
                                self.log_result(f"DB Health - {service_name}", False, f"Service unhealthy: {error_msg}", data, response.status_code)
                                self.failing_services.append(service_name)
                                
                        except json.JSONDecodeError:
                            self.log_result(f"DB Health - {service_name}", False, "Invalid JSON response", None, response.status_code)
                            self.failing_services.append(service_name)
                    else:
                        self.log_result(f"DB Health - {service_name}", False, f"Health endpoint failed with status {response.status_code}", None, response.status_code)
                        self.failing_services.append(service_name)
                        
                except Exception as e:
                    service_name = endpoint.split('/')[-2] if '/' in endpoint else 'unknown'
                    self.log_result(f"DB Health - {service_name}", False, f"Health check error: {str(e)}")
                    self.failing_services.append(service_name)
            
            # Summary
            success_rate = (working_count / total_tested) * 100 if total_tested > 0 else 0
            db_error_rate = (database_error_count / total_tested) * 100 if total_tested > 0 else 0
            
            self.log_result("Database Connectivity Assessment", database_error_count == 0, 
                          f"DB Errors: {database_error_count}/{total_tested} ({db_error_rate:.1f}%), Working: {working_count}/{total_tested} ({success_rate:.1f}%)")
            
            return database_error_count == 0
            
        except Exception as e:
            self.log_result("Database Connectivity Assessment", False, f"Database connectivity test error: {str(e)}")
            return False
    
    def test_public_endpoints(self):
        """Test public endpoints that don't require authentication"""
        try:
            print("\n🌐 TESTING PUBLIC ENDPOINTS")
            print("=" * 60)
            
            public_endpoints = [
                f"{BACKEND_URL}/",
                f"{BACKEND_URL}/health",
                f"{BACKEND_URL}/docs",
                f"{BACKEND_URL}/openapi.json"
            ]
            
            working_public = 0
            total_public = len(public_endpoints)
            
            for endpoint in public_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=30)
                    
                    if response.status_code == 200:
                        endpoint_name = endpoint.split('/')[-1] or 'root'
                        self.log_result(f"Public - {endpoint_name}", True, "Public endpoint accessible", None, response.status_code)
                        working_public += 1
                    else:
                        endpoint_name = endpoint.split('/')[-1] or 'root'
                        self.log_result(f"Public - {endpoint_name}", False, f"Public endpoint failed with status {response.status_code}", None, response.status_code)
                        
                except Exception as e:
                    endpoint_name = endpoint.split('/')[-1] or 'root'
                    self.log_result(f"Public - {endpoint_name}", False, f"Public endpoint error: {str(e)}")
            
            public_success_rate = (working_public / total_public) * 100
            self.log_result("Public Endpoints Overall", working_public > 0, f"Public endpoints: {working_public}/{total_public} working ({public_success_rate:.1f}%)")
            
            return working_public > 0
            
        except Exception as e:
            self.log_result("Public Endpoints", False, f"Public endpoints test error: {str(e)}")
            return False
    
    def analyze_database_errors(self):
        """Analyze the specific database errors found"""
        try:
            print("\n🔍 ANALYZING DATABASE CONNECTIVITY ERRORS")
            print("=" * 60)
            
            if not self.database_errors:
                self.log_result("Database Error Analysis", True, "No database connectivity errors found")
                return True
            
            # Group errors by type
            error_types = {}
            for error_info in self.database_errors:
                error_msg = error_info['error']
                if 'Database objects do not implement truth value testing' in error_msg:
                    error_type = 'Boolean Context Error'
                elif 'database is not None' in error_msg:
                    error_type = 'None Comparison Error'
                else:
                    error_type = 'Other Database Error'
                
                if error_type not in error_types:
                    error_types[error_type] = []
                error_types[error_type].append(error_info)
            
            # Report error analysis
            for error_type, errors in error_types.items():
                affected_services = [e['service'] for e in errors]
                self.log_result(f"Error Analysis - {error_type}", False, 
                              f"Affects {len(errors)} services: {', '.join(affected_services[:5])}{'...' if len(affected_services) > 5 else ''}")
            
            # Provide specific recommendations
            if 'Boolean Context Error' in error_types:
                print("\n🔧 CRITICAL DATABASE FIX NEEDED:")
                print("   The error 'Database objects do not implement truth value testing' indicates")
                print("   that code is trying to use database objects in boolean contexts like:")
                print("   - if database: (WRONG)")
                print("   - Should be: if database is not None: (CORRECT)")
                print("   This affects database connectivity across multiple services.")
            
            return False
            
        except Exception as e:
            self.log_result("Database Error Analysis", False, f"Error analysis failed: {str(e)}")
            return False
    
    def run_comprehensive_assessment(self):
        """Run comprehensive database connectivity assessment"""
        print("🎯 MEWAYZ V2 PLATFORM - CRITICAL DATABASE CONNECTIVITY ASSESSMENT")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Focus: Database connectivity issues after fixes")
        print("=" * 80)
        
        # Test 1: Basic System Health
        system_ok = self.test_system_health()
        
        # Test 2: Service Health Endpoints (Database Connectivity)
        db_ok = self.test_service_health_endpoints()
        
        # Test 3: Public Endpoints
        public_ok = self.test_public_endpoints()
        
        # Test 4: Analyze Database Errors
        analysis_ok = self.analyze_database_errors()
        
        # Generate final assessment
        self.generate_final_assessment(system_ok, db_ok, public_ok, analysis_ok)
    
    def generate_final_assessment(self, system_ok, db_ok, public_ok, analysis_ok):
        """Generate final assessment report"""
        print("\n" + "=" * 80)
        print("🎯 CRITICAL DATABASE CONNECTIVITY ASSESSMENT RESULTS")
        print("=" * 80)
        
        # Overall Status
        total_tests = 4
        passed_tests = sum([system_ok, db_ok, public_ok, analysis_ok])
        overall_success = (passed_tests / total_tests) * 100
        
        print(f"📊 OVERALL ASSESSMENT RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Overall Success Rate: {overall_success:.1f}%")
        
        # Critical Findings
        print(f"\n🚨 CRITICAL FINDINGS:")
        if self.database_errors:
            print(f"   ❌ DATABASE CONNECTIVITY BROKEN: {len(self.database_errors)} services affected")
            print(f"   ❌ SPECIFIC ERROR: 'Database objects do not implement truth value testing'")
            print(f"   ❌ ROOT CAUSE: Improper database connection checking in service code")
            print(f"   ❌ IMPACT: All database-dependent services are failing")
        else:
            print(f"   ✅ No critical database connectivity errors found")
        
        # Service Status
        print(f"\n📋 SERVICE STATUS:")
        print(f"   ✅ Working Services: {len(self.working_services)}")
        if self.working_services:
            print(f"      {', '.join(self.working_services[:10])}{'...' if len(self.working_services) > 10 else ''}")
        
        print(f"   ❌ Failing Services: {len(self.failing_services)}")
        if self.failing_services:
            print(f"      {', '.join(self.failing_services[:10])}{'...' if len(self.failing_services) > 10 else ''}")
        
        # Improvement Status vs Review Request
        print(f"\n📈 IMPROVEMENT STATUS vs REVIEW REQUEST:")
        if len(self.database_errors) > 0:
            print(f"   ❌ DATABASE CONNECTIVITY FIXES: NOT COMPLETE")
            print(f"   ❌ Service Layer Issues: STILL PRESENT")
            print(f"   ❌ Previous 25.5% Success Rate: LIKELY STILL LOW due to DB issues")
        else:
            print(f"   ✅ DATABASE CONNECTIVITY FIXES: COMPLETE")
            print(f"   ✅ Service Layer Issues: RESOLVED")
        
        # Specific Recommendations
        print(f"\n💡 IMMEDIATE ACTION REQUIRED:")
        if self.database_errors:
            print(f"   🔧 CRITICAL: Fix database connection checking in service health endpoints")
            print(f"   🔧 CRITICAL: Replace 'if database:' with 'if database is not None:' in service code")
            print(f"   🔧 CRITICAL: Test all {len(self.failing_services)} failing services after database fix")
            print(f"   🔧 HIGH: Verify database connection initialization in service startup")
        
        if not db_ok and system_ok:
            print(f"   🔧 MEDIUM: System infrastructure is working, focus on service-level database integration")
        
        # Final Status
        print(f"\n🎯 FINAL ASSESSMENT:")
        if len(self.database_errors) > 0:
            print(f"   ❌ CRITICAL: Database connectivity fixes are NOT COMPLETE")
            print(f"   ❌ The platform still has the same database integration issues")
            print(f"   ❌ Authentication and CRUD operations will fail until database connectivity is fixed")
            print(f"   ❌ Estimated current success rate: <30% (similar to previous 25.5%)")
        else:
            print(f"   ✅ Database connectivity appears to be working")
            print(f"   ✅ Ready for authentication and CRUD testing")
            print(f"   ✅ Significant improvement expected from previous testing")
        
        print("=" * 80)
        print("🎉 CRITICAL DATABASE CONNECTIVITY ASSESSMENT COMPLETED!")
        print("=" * 80)

if __name__ == "__main__":
    tester = DatabaseConnectivityTester()
    tester.run_comprehensive_assessment()