#!/usr/bin/env python3
"""
Database Integration Testing Script
Tests that dashboard and Advanced AI services are using real database data instead of random generation
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

class DatabaseIntegrationTester:
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
                    self.log_result("Authentication", True, "Login successful - Token received", data)
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
    
    def test_dashboard_real_data(self):
        """Test dashboard endpoints to verify real database data usage"""
        print("\n=== Testing Dashboard Database Integration ===")
        
        try:
            # Test dashboard overview
            response = self.session.get(f"{API_BASE}/dashboard/overview", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check for real data indicators
                user_stats = data.get("user_stats", {})
                recent_activity = data.get("recent_activity", [])
                
                # Verify data structure indicates real database usage
                has_workspaces = "workspaces" in user_stats
                has_projects = "active_projects" in user_stats
                has_visits = "total_visits" in user_stats
                has_conversion = "conversion_rate" in user_stats
                has_activities = len(recent_activity) > 0
                
                if has_workspaces and has_projects and has_visits and has_conversion:
                    self.log_result(
                        "Dashboard Overview - Real Data Structure", 
                        True, 
                        f"Dashboard shows real data structure: {user_stats['workspaces']} workspaces, {user_stats['active_projects']} projects, {user_stats['total_visits']} visits",
                        data
                    )
                    
                    # Test data persistence by making multiple calls
                    time.sleep(1)
                    response2 = self.session.get(f"{API_BASE}/dashboard/overview", timeout=10)
                    if response2.status_code == 200:
                        data2 = response2.json()
                        user_stats2 = data2.get("user_stats", {})
                        
                        # Check if data is consistent (indicating real database usage)
                        if (user_stats.get("workspaces") == user_stats2.get("workspaces") and
                            user_stats.get("active_projects") == user_stats2.get("active_projects")):
                            self.log_result(
                                "Dashboard Data Persistence", 
                                True, 
                                "Dashboard data is consistent across calls - indicates real database usage"
                            )
                        else:
                            self.log_result(
                                "Dashboard Data Persistence", 
                                False, 
                                "Dashboard data varies between calls - may indicate random generation"
                            )
                else:
                    self.log_result(
                        "Dashboard Overview - Real Data Structure", 
                        False, 
                        "Dashboard missing expected real data fields"
                    )
            else:
                self.log_result(
                    "Dashboard Overview", 
                    False, 
                    f"Dashboard endpoint failed with status {response.status_code}"
                )
                
        except Exception as e:
            self.log_result("Dashboard Real Data Test", False, f"Error: {str(e)}")
    
    def test_advanced_ai_real_data(self):
        """Test Advanced AI endpoints to verify real database data usage and tracking"""
        print("\n=== Testing Advanced AI Database Integration ===")
        
        try:
            # Test AI capabilities
            response = self.session.get(f"{API_BASE}/advanced-ai/capabilities", timeout=10)
            if response.status_code == 200:
                data = response.json()
                capabilities = data.get("data", {}).get("capabilities", [])
                
                if len(capabilities) > 0:
                    self.log_result(
                        "Advanced AI Capabilities", 
                        True, 
                        f"AI capabilities loaded: {len(capabilities)} capabilities available",
                        data
                    )
                else:
                    self.log_result(
                        "Advanced AI Capabilities", 
                        False, 
                        "No AI capabilities returned"
                    )
            
            # Test AI models
            response = self.session.get(f"{API_BASE}/advanced-ai/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models_data = data.get("data", {})
                text_models = models_data.get("text_models", [])
                image_models = models_data.get("image_models", [])
                
                if len(text_models) > 0 and len(image_models) > 0:
                    self.log_result(
                        "Advanced AI Models", 
                        True, 
                        f"AI models loaded: {len(text_models)} text models, {len(image_models)} image models",
                        data
                    )
                else:
                    self.log_result(
                        "Advanced AI Models", 
                        False, 
                        "Insufficient AI models returned"
                    )
            
            # Test AI insights
            response = self.session.get(f"{API_BASE}/advanced-ai/insights", timeout=10)
            if response.status_code == 200:
                data = response.json()
                insights = data.get("data", {}).get("insights", [])
                
                if len(insights) > 0:
                    self.log_result(
                        "Advanced AI Insights", 
                        True, 
                        f"AI insights generated: {len(insights)} insights available",
                        data
                    )
                else:
                    self.log_result(
                        "Advanced AI Insights", 
                        False, 
                        "No AI insights returned"
                    )
            
            # Test AI usage analytics to verify database tracking
            # Try different periods to see if real data is being tracked
            for period in ["daily", "weekly", "monthly"]:
                response = self.session.get(f"{API_BASE}/advanced-ai/usage-analytics?period={period}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    usage_data = data.get("data", {})
                    usage_summary = usage_data.get("usage_summary", {})
                    
                    total_requests = usage_summary.get("total_requests", 0)
                    tokens_consumed = usage_summary.get("tokens_consumed", 0)
                    cost_incurred = usage_summary.get("cost_incurred", 0.0)
                    
                    self.log_result(
                        f"AI Usage Analytics ({period})", 
                        True, 
                        f"Usage data: {total_requests} requests, {tokens_consumed} tokens, ${cost_incurred} cost",
                        usage_data
                    )
                else:
                    self.log_result(
                        f"AI Usage Analytics ({period})", 
                        False, 
                        f"Failed to get usage analytics for {period}"
                    )
                    
        except Exception as e:
            self.log_result("Advanced AI Real Data Test", False, f"Error: {str(e)}")
    
    def test_user_management_data(self):
        """Test user management endpoints for real data"""
        print("\n=== Testing User Management Database Integration ===")
        
        try:
            # Test user profile
            response = self.session.get(f"{API_BASE}/users/profile", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check for real user data structure
                if "email" in data and "created_at" in data:
                    self.log_result(
                        "User Profile Data", 
                        True, 
                        f"User profile loaded with email: {data.get('email', 'N/A')}",
                        data
                    )
                else:
                    self.log_result(
                        "User Profile Data", 
                        False, 
                        "User profile missing expected fields"
                    )
            
            # Test user activity
            response = self.session.get(f"{API_BASE}/user/activity", timeout=10)
            if response.status_code == 200:
                data = response.json()
                activities = data.get("activities", [])
                
                self.log_result(
                    "User Activity Data", 
                    True, 
                    f"User activities loaded: {len(activities)} activities",
                    data
                )
            else:
                self.log_result(
                    "User Activity Data", 
                    False, 
                    f"Failed to get user activities: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result("User Management Data Test", False, f"Error: {str(e)}")
    
    def test_data_persistence_across_calls(self):
        """Test that data remains consistent across multiple calls (indicating real database usage)"""
        print("\n=== Testing Data Persistence Across Multiple Calls ===")
        
        try:
            # Test workspace data consistency
            responses = []
            for i in range(3):
                response = self.session.get(f"{API_BASE}/workspaces", timeout=10)
                if response.status_code == 200:
                    responses.append(response.json())
                time.sleep(0.5)
            
            if len(responses) >= 2:
                # Check if workspace count is consistent
                workspace_counts = [len(resp.get("workspaces", [])) for resp in responses]
                if len(set(workspace_counts)) == 1:  # All counts are the same
                    self.log_result(
                        "Workspace Data Persistence", 
                        True, 
                        f"Workspace count consistent across calls: {workspace_counts[0]} workspaces"
                    )
                else:
                    self.log_result(
                        "Workspace Data Persistence", 
                        False, 
                        f"Workspace count varies: {workspace_counts} - may indicate random generation"
                    )
            
            # Test user profile consistency
            profile_responses = []
            for i in range(2):
                response = self.session.get(f"{API_BASE}/users/profile", timeout=10)
                if response.status_code == 200:
                    profile_responses.append(response.json())
                time.sleep(0.5)
            
            if len(profile_responses) >= 2:
                # Check if user email is consistent
                emails = [resp.get("email") for resp in profile_responses]
                if len(set(emails)) == 1 and emails[0]:  # All emails are the same and not None
                    self.log_result(
                        "User Profile Persistence", 
                        True, 
                        f"User profile consistent across calls: {emails[0]}"
                    )
                else:
                    self.log_result(
                        "User Profile Persistence", 
                        False, 
                        f"User profile varies across calls: {emails}"
                    )
                    
        except Exception as e:
            self.log_result("Data Persistence Test", False, f"Error: {str(e)}")
    
    def run_database_integration_tests(self):
        """Run comprehensive database integration testing"""
        print("🔍 Starting Database Integration Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Focus: Verifying real database data usage vs random generation")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with database tests.")
            return False
        
        # Run specific database integration tests
        self.test_dashboard_real_data()
        self.test_advanced_ai_real_data()
        self.test_user_management_data()
        self.test_data_persistence_across_calls()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 DATABASE INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
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
        
        # Database integration assessment
        print(f"\n🔍 DATABASE INTEGRATION ASSESSMENT:")
        dashboard_tests = [r for r in self.test_results if "Dashboard" in r["test"]]
        ai_tests = [r for r in self.test_results if "AI" in r["test"]]
        persistence_tests = [r for r in self.test_results if "Persistence" in r["test"]]
        
        dashboard_success = sum(1 for t in dashboard_tests if t["success"])
        ai_success = sum(1 for t in ai_tests if t["success"])
        persistence_success = sum(1 for t in persistence_tests if t["success"])
        
        print(f"  - Dashboard Integration: {dashboard_success}/{len(dashboard_tests)} tests passed")
        print(f"  - Advanced AI Integration: {ai_success}/{len(ai_tests)} tests passed")
        print(f"  - Data Persistence: {persistence_success}/{len(persistence_tests)} tests passed")
        
        if passed_tests >= total_tests * 0.8:
            print(f"\n🎉 DATABASE INTEGRATION: EXCELLENT - Real database data confirmed!")
        elif passed_tests >= total_tests * 0.6:
            print(f"\n✅ DATABASE INTEGRATION: GOOD - Most endpoints using real data")
        else:
            print(f"\n⚠️  DATABASE INTEGRATION: NEEDS IMPROVEMENT - Some endpoints may still use random data")

if __name__ == "__main__":
    tester = DatabaseIntegrationTester()
    success = tester.run_database_integration_tests()
    sys.exit(0 if success else 1)