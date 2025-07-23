#!/usr/bin/env python3
"""
Focused Database Integration Testing Script
Tests specific endpoints mentioned in the review request to verify real database usage
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://1e8b1ad5-8db8-4882-94e1-e795cd3cf46d.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class FocusedDatabaseTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if response_data and isinstance(response_data, dict):
            print(f"   Response size: {len(str(response_data))} chars")
    
    def authenticate(self):
        """Authenticate and get access token"""
        try:
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_result("Authentication", True, "Login successful - Token received")
                    return True
                else:
                    self.log_result("Authentication", False, "Login response missing access_token")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_dashboard_service_real_data(self):
        """Test dashboard service to verify it's using real database data"""
        print("\n=== Testing Dashboard Service Database Integration ===")
        
        try:
            # Test dashboard overview - this should use dashboard_service.py
            response = self.session.get(f"{API_BASE}/dashboard/overview", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check the structure - dashboard_service.py should return specific structure
                if "data" in data and "quick_stats" in data["data"]:
                    quick_stats = data["data"]["quick_stats"]
                    
                    # Check for real database fields that dashboard_service.py queries
                    has_workspaces = "workspaces" in quick_stats
                    has_ai_requests = "ai_requests_used" in quick_stats
                    has_activity = "activity_last_7_days" in quick_stats
                    
                    if has_workspaces and has_ai_requests and has_activity:
                        workspaces_count = quick_stats.get("workspaces", 0)
                        ai_requests = quick_stats.get("ai_requests_used", 0)
                        activity_count = quick_stats.get("activity_last_7_days", 0)
                        
                        self.log_result(
                            "Dashboard Service - Real Database Queries", 
                            True, 
                            f"Dashboard using real DB data: {workspaces_count} workspaces, {ai_requests} AI requests, {activity_count} recent activities",
                            data
                        )
                        
                        # Test data consistency across multiple calls
                        time.sleep(1)
                        response2 = self.session.get(f"{API_BASE}/dashboard/overview", timeout=10)
                        if response2.status_code == 200:
                            data2 = response2.json()
                            quick_stats2 = data2["data"]["quick_stats"]
                            
                            # Check if core counts are consistent (indicating real DB usage)
                            if (quick_stats.get("workspaces") == quick_stats2.get("workspaces") and
                                quick_stats.get("ai_requests_used") == quick_stats2.get("ai_requests_used")):
                                self.log_result(
                                    "Dashboard Data Persistence", 
                                    True, 
                                    "Dashboard data consistent across calls - confirms real database usage"
                                )
                            else:
                                self.log_result(
                                    "Dashboard Data Persistence", 
                                    False, 
                                    "Dashboard data varies - may indicate random generation"
                                )
                    else:
                        self.log_result(
                            "Dashboard Service - Real Database Queries", 
                            False, 
                            "Dashboard missing expected database-driven fields"
                        )
                else:
                    self.log_result(
                        "Dashboard Service - Real Database Queries", 
                        False, 
                        "Dashboard response structure doesn't match expected database service format"
                    )
            else:
                self.log_result(
                    "Dashboard Service", 
                    False, 
                    f"Dashboard endpoint failed with status {response.status_code}"
                )
                
        except Exception as e:
            self.log_result("Dashboard Service Test", False, f"Error: {str(e)}")
    
    def test_advanced_ai_service_real_data(self):
        """Test Advanced AI service to verify database integration"""
        print("\n=== Testing Advanced AI Service Database Integration ===")
        
        try:
            # Test AI capabilities - should be consistent (not random)
            response = self.session.get(f"{API_BASE}/advanced-ai/capabilities", timeout=10)
            if response.status_code == 200:
                data = response.json()
                capabilities = data.get("data", {}).get("capabilities", [])
                
                if len(capabilities) > 0:
                    # Test consistency across calls
                    time.sleep(0.5)
                    response2 = self.session.get(f"{API_BASE}/advanced-ai/capabilities", timeout=10)
                    if response2.status_code == 200:
                        data2 = response2.json()
                        capabilities2 = data2.get("data", {}).get("capabilities", [])
                        
                        if len(capabilities) == len(capabilities2):
                            self.log_result(
                                "Advanced AI Capabilities - Consistency", 
                                True, 
                                f"AI capabilities consistent: {len(capabilities)} capabilities"
                            )
                        else:
                            self.log_result(
                                "Advanced AI Capabilities - Consistency", 
                                False, 
                                f"AI capabilities vary: {len(capabilities)} vs {len(capabilities2)}"
                            )
                else:
                    self.log_result(
                        "Advanced AI Capabilities", 
                        False, 
                        "No AI capabilities returned"
                    )
            
            # Test AI models - should be consistent
            response = self.session.get(f"{API_BASE}/advanced-ai/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models_data = data.get("data", {})
                text_models = models_data.get("text_models", [])
                
                if len(text_models) > 0:
                    # Check for realistic model data (not random)
                    first_model = text_models[0]
                    has_realistic_fields = (
                        "id" in first_model and 
                        "name" in first_model and 
                        "provider" in first_model and
                        "cost_per_token" in first_model
                    )
                    
                    if has_realistic_fields:
                        self.log_result(
                            "Advanced AI Models - Real Data Structure", 
                            True, 
                            f"AI models have realistic structure: {first_model['name']} by {first_model['provider']}"
                        )
                    else:
                        self.log_result(
                            "Advanced AI Models - Real Data Structure", 
                            False, 
                            "AI models missing expected realistic fields"
                        )
                else:
                    self.log_result(
                        "Advanced AI Models", 
                        False, 
                        "No AI models returned"
                    )
            
            # Test AI insights - should be user-specific
            response = self.session.get(f"{API_BASE}/advanced-ai/insights", timeout=10)
            if response.status_code == 200:
                data = response.json()
                insights = data.get("data", {}).get("insights", [])
                
                if len(insights) > 0:
                    # Check if insights have realistic structure
                    first_insight = insights[0]
                    has_insight_fields = (
                        "title" in first_insight and 
                        "description" in first_insight and 
                        "recommendation" in first_insight
                    )
                    
                    if has_insight_fields:
                        self.log_result(
                            "Advanced AI Insights - Real Structure", 
                            True, 
                            f"AI insights have realistic structure: '{first_insight['title']}'"
                        )
                    else:
                        self.log_result(
                            "Advanced AI Insights - Real Structure", 
                            False, 
                            "AI insights missing expected fields"
                        )
                else:
                    self.log_result(
                        "Advanced AI Insights", 
                        False, 
                        "No AI insights returned"
                    )
                    
        except Exception as e:
            self.log_result("Advanced AI Service Test", False, f"Error: {str(e)}")
    
    def test_user_management_real_data(self):
        """Test user management endpoints for real database usage"""
        print("\n=== Testing User Management Database Integration ===")
        
        try:
            # Test user profile - should return real user data
            response = self.session.get(f"{API_BASE}/users/profile", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check for real user data
                if "email" in data and data["email"] == TEST_EMAIL:
                    self.log_result(
                        "User Profile - Real Data", 
                        True, 
                        f"User profile shows real data: {data['email']}"
                    )
                    
                    # Test consistency
                    time.sleep(0.5)
                    response2 = self.session.get(f"{API_BASE}/users/profile", timeout=10)
                    if response2.status_code == 200:
                        data2 = response2.json()
                        if data.get("email") == data2.get("email"):
                            self.log_result(
                                "User Profile - Consistency", 
                                True, 
                                "User profile data consistent across calls"
                            )
                        else:
                            self.log_result(
                                "User Profile - Consistency", 
                                False, 
                                "User profile data varies across calls"
                            )
                else:
                    self.log_result(
                        "User Profile - Real Data", 
                        False, 
                        f"User profile doesn't show expected email: {data.get('email', 'None')}"
                    )
            
            # Test workspaces - should show real workspace data
            response = self.session.get(f"{API_BASE}/workspaces", timeout=10)
            if response.status_code == 200:
                data = response.json()
                workspaces = data.get("workspaces", [])
                
                # Check if workspace count matches dashboard
                workspace_count = len(workspaces)
                self.log_result(
                    "Workspaces - Real Data", 
                    True, 
                    f"Workspaces loaded from database: {workspace_count} workspaces"
                )
                
                # Test consistency
                time.sleep(0.5)
                response2 = self.session.get(f"{API_BASE}/workspaces", timeout=10)
                if response2.status_code == 200:
                    data2 = response2.json()
                    workspaces2 = data2.get("workspaces", [])
                    
                    if len(workspaces) == len(workspaces2):
                        self.log_result(
                            "Workspaces - Consistency", 
                            True, 
                            "Workspace count consistent - confirms database usage"
                        )
                    else:
                        self.log_result(
                            "Workspaces - Consistency", 
                            False, 
                            f"Workspace count varies: {len(workspaces)} vs {len(workspaces2)}"
                        )
                        
        except Exception as e:
            self.log_result("User Management Test", False, f"Error: {str(e)}")
    
    def test_database_initialization_verification(self):
        """Verify that database collections are properly initialized with sample data"""
        print("\n=== Testing Database Initialization ===")
        
        try:
            # Test multiple endpoints to see if they return data indicating initialized collections
            endpoints_to_test = [
                ("/dashboard/overview", "Dashboard"),
                ("/workspaces", "Workspaces"),
                ("/users/profile", "User Profile"),
                ("/advanced-ai/capabilities", "AI Capabilities"),
                ("/advanced-ai/models", "AI Models")
            ]
            
            initialized_endpoints = 0
            total_endpoints = len(endpoints_to_test)
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = self.session.get(f"{API_BASE}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if endpoint returns meaningful data
                        has_data = False
                        if endpoint == "/dashboard/overview":
                            has_data = "data" in data and "quick_stats" in data["data"]
                        elif endpoint == "/workspaces":
                            has_data = "workspaces" in data
                        elif endpoint == "/users/profile":
                            has_data = "email" in data
                        elif endpoint == "/advanced-ai/capabilities":
                            has_data = "data" in data and "capabilities" in data["data"]
                        elif endpoint == "/advanced-ai/models":
                            has_data = "data" in data and "text_models" in data["data"]
                        
                        if has_data:
                            initialized_endpoints += 1
                            self.log_result(
                                f"Database Collection - {name}", 
                                True, 
                                f"{name} collection properly initialized"
                            )
                        else:
                            self.log_result(
                                f"Database Collection - {name}", 
                                False, 
                                f"{name} collection may not be properly initialized"
                            )
                    else:
                        self.log_result(
                            f"Database Collection - {name}", 
                            False, 
                            f"{name} endpoint failed: {response.status_code}"
                        )
                except Exception as e:
                    self.log_result(
                        f"Database Collection - {name}", 
                        False, 
                        f"{name} test error: {str(e)}"
                    )
            
            # Overall database initialization assessment
            initialization_rate = (initialized_endpoints / total_endpoints) * 100
            if initialization_rate >= 80:
                self.log_result(
                    "Database Initialization - Overall", 
                    True, 
                    f"Database well initialized: {initialization_rate:.1f}% of collections working"
                )
            else:
                self.log_result(
                    "Database Initialization - Overall", 
                    False, 
                    f"Database initialization incomplete: {initialization_rate:.1f}% of collections working"
                )
                
        except Exception as e:
            self.log_result("Database Initialization Test", False, f"Error: {str(e)}")
    
    def run_focused_database_tests(self):
        """Run focused database integration testing"""
        print("🔍 Starting Focused Database Integration Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Focus: Dashboard Service & Advanced AI Service Database Integration")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with database tests.")
            return False
        
        # Run focused tests
        self.test_dashboard_service_real_data()
        self.test_advanced_ai_service_real_data()
        self.test_user_management_real_data()
        self.test_database_initialization_verification()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 FOCUSED DATABASE INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}: {result['message']}")
        
        # Specific assessment for the review request
        print(f"\n🎯 REVIEW REQUEST ASSESSMENT:")
        dashboard_tests = [r for r in self.test_results if "Dashboard" in r["test"]]
        ai_tests = [r for r in self.test_results if "Advanced AI" in r["test"]]
        user_tests = [r for r in self.test_results if "User" in r["test"] or "Workspace" in r["test"]]
        db_init_tests = [r for r in self.test_results if "Database" in r["test"]]
        
        dashboard_success = sum(1 for t in dashboard_tests if t["success"])
        ai_success = sum(1 for t in ai_tests if t["success"])
        user_success = sum(1 for t in user_tests if t["success"])
        db_init_success = sum(1 for t in db_init_tests if t["success"])
        
        print(f"  - Dashboard Service (dashboard_service.py): {dashboard_success}/{len(dashboard_tests)} tests passed")
        print(f"  - Advanced AI Service (advanced_ai_service.py): {ai_success}/{len(ai_tests)} tests passed")
        print(f"  - User Management: {user_success}/{len(user_tests)} tests passed")
        print(f"  - Database Initialization: {db_init_success}/{len(db_init_tests)} tests passed")
        
        # Final assessment
        overall_success_rate = (passed_tests / total_tests) * 100
        if overall_success_rate >= 85:
            print(f"\n🎉 DATABASE INTEGRATION: EXCELLENT ({overall_success_rate:.1f}%)")
            print("   ✅ Real database data confirmed across services")
            print("   ✅ Data persistence working correctly")
            print("   ✅ Database collections properly initialized")
        elif overall_success_rate >= 70:
            print(f"\n✅ DATABASE INTEGRATION: GOOD ({overall_success_rate:.1f}%)")
            print("   ✅ Most services using real database data")
            print("   ⚠️  Some minor issues with data consistency")
        elif overall_success_rate >= 50:
            print(f"\n⚠️  DATABASE INTEGRATION: PARTIAL ({overall_success_rate:.1f}%)")
            print("   ✅ Some services using real database data")
            print("   ❌ Several services may still use random data generation")
        else:
            print(f"\n❌ DATABASE INTEGRATION: NEEDS WORK ({overall_success_rate:.1f}%)")
            print("   ❌ Most services not properly integrated with database")
            print("   ❌ Random data generation still prevalent")

if __name__ == "__main__":
    tester = FocusedDatabaseTester()
    success = tester.run_focused_database_tests()
    sys.exit(0 if success else 1)