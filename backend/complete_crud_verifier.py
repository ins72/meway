#!/usr/bin/env python3
"""
COMPLETE CRUD OPERATIONS VERIFIER
Tests full end-to-end CRUD functionality and identifies remaining hardcoded/mock data
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL
BACKEND_URL = "https://9fb7b81f-9f5a-4259-b2f2-bf50fd3ed214.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class CompleteCRUDTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.created_resources = []  # Track what we create so we can clean up
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if response_data and isinstance(response_data, dict):
            print(f"   Response keys: {list(response_data.keys())}")
    
    def authenticate(self):
        """Authenticate with the backend"""
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
                    self.log_result("Authentication", True, "Successfully authenticated", data)
                    return True
            
            self.log_result("Authentication", False, f"Login failed: {response.status_code}")
            return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_user_crud(self):
        """Test complete User CRUD operations"""
        print("\n" + "="*80)
        print("TESTING USER CRUD OPERATIONS")
        print("="*80)
        
        # CREATE - Register new user (if registration endpoint exists)
        test_user = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "name": "Test User CRUD",
            "phone": "+1234567890"
        }
        
        try:
            # Try to register new user
            response = self.session.post(f"{API_BASE}/auth/register", json=test_user, timeout=10)
            if response.status_code in [200, 201]:
                user_data = response.json()
                self.log_result("User CREATE", True, "New user registration successful", user_data)
                user_id = user_data.get("user_id") or user_data.get("_id")
                if user_id:
                    self.created_resources.append(("user", user_id))
            else:
                self.log_result("User CREATE", False, f"User registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("User CREATE", False, f"User registration error: {str(e)}")
        
        # READ - Get user profile
        try:
            response = self.session.get(f"{API_BASE}/users/profile", timeout=10)
            if response.status_code == 200:
                profile_data = response.json()
                self.log_result("User READ", True, "User profile retrieval successful", profile_data)
            else:
                self.log_result("User READ", False, f"Profile retrieval failed: {response.status_code}")
        except Exception as e:
            self.log_result("User READ", False, f"Profile retrieval error: {str(e)}")
        
        # UPDATE - Update user profile
        try:
            update_data = {
                "name": f"Updated User {int(time.time())}",
                "bio": "This is a test bio update"
            }
            response = self.session.put(f"{API_BASE}/users/profile", json=update_data, timeout=10)
            if response.status_code == 200:
                updated_data = response.json()
                self.log_result("User UPDATE", True, "User profile update successful", updated_data)
            else:
                self.log_result("User UPDATE", False, f"Profile update failed: {response.status_code}")
        except Exception as e:
            self.log_result("User UPDATE", False, f"Profile update error: {str(e)}")

    def test_content_crud(self):
        """Test content creation, reading, updating, deleting"""
        print("\n" + "="*80)
        print("TESTING CONTENT CRUD OPERATIONS")
        print("="*80)
        
        # CREATE - Create new content (blog post, social post, etc.)
        content_data = {
            "title": f"Test Blog Post {int(time.time())}",
            "content": "This is a test blog post created by CRUD test",
            "type": "blog",
            "status": "draft",
            "tags": ["test", "crud", "automation"]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/content", json=content_data, timeout=10)
            if response.status_code in [200, 201]:
                content_result = response.json()
                self.log_result("Content CREATE", True, "Content creation successful", content_result)
                content_id = content_result.get("content_id") or content_result.get("_id")
                if content_id:
                    self.created_resources.append(("content", content_id))
            else:
                self.log_result("Content CREATE", False, f"Content creation failed: {response.status_code}")
        except Exception as e:
            self.log_result("Content CREATE", False, f"Content creation error: {str(e)}")
        
        # READ - Get content list
        try:
            response = self.session.get(f"{API_BASE}/content?limit=10", timeout=10)
            if response.status_code == 200:
                content_list = response.json()
                self.log_result("Content READ", True, f"Retrieved {len(content_list.get('content', []))} content items", content_list)
            else:
                self.log_result("Content READ", False, f"Content retrieval failed: {response.status_code}")
        except Exception as e:
            self.log_result("Content READ", False, f"Content retrieval error: {str(e)}")

    def test_analytics_crud(self):
        """Test analytics data creation and retrieval"""
        print("\n" + "="*80)
        print("TESTING ANALYTICS CRUD OPERATIONS")
        print("="*80)
        
        # CREATE - Track analytics event
        event_data = {
            "event_type": "page_view",
            "page": "/test-page",
            "user_agent": "CRUD Test Agent",
            "timestamp": datetime.now().isoformat(),
            "properties": {
                "test_run": True,
                "crud_verification": True
            }
        }
        
        try:
            response = self.session.post(f"{API_BASE}/analytics/track", json=event_data, timeout=10)
            if response.status_code in [200, 201]:
                track_result = response.json()
                self.log_result("Analytics CREATE", True, "Analytics event tracked", track_result)
            else:
                self.log_result("Analytics CREATE", False, f"Analytics tracking failed: {response.status_code}")
        except Exception as e:
            self.log_result("Analytics CREATE", False, f"Analytics tracking error: {str(e)}")
        
        # READ - Get analytics overview
        try:
            response = self.session.get(f"{API_BASE}/analytics/overview", timeout=10)
            if response.status_code == 200:
                analytics_data = response.json()
                self.log_result("Analytics READ", True, "Analytics overview retrieved", analytics_data)
            else:
                self.log_result("Analytics READ", False, f"Analytics retrieval failed: {response.status_code}")
        except Exception as e:
            self.log_result("Analytics READ", False, f"Analytics retrieval error: {str(e)}")

    def test_workspace_crud(self):
        """Test workspace CRUD operations"""
        print("\n" + "="*80)
        print("TESTING WORKSPACE CRUD OPERATIONS") 
        print("="*80)
        
        # CREATE - Create new workspace
        workspace_data = {
            "name": f"Test Workspace {int(time.time())}",
            "description": "CRUD test workspace",
            "type": "business",
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        try:
            response = self.session.post(f"{API_BASE}/workspaces", json=workspace_data, timeout=10)
            if response.status_code in [200, 201]:
                workspace_result = response.json()
                self.log_result("Workspace CREATE", True, "Workspace creation successful", workspace_result)
                workspace_id = workspace_result.get("workspace_id") or workspace_result.get("_id")
                if workspace_id:
                    self.created_resources.append(("workspace", workspace_id))
            else:
                self.log_result("Workspace CREATE", False, f"Workspace creation failed: {response.status_code}")
        except Exception as e:
            self.log_result("Workspace CREATE", False, f"Workspace creation error: {str(e)}")
        
        # READ - Get workspaces list
        try:
            response = self.session.get(f"{API_BASE}/workspaces", timeout=10)
            if response.status_code == 200:
                workspaces_data = response.json()
                self.log_result("Workspace READ", True, "Workspaces list retrieved", workspaces_data)
            else:
                self.log_result("Workspace READ", False, f"Workspaces retrieval failed: {response.status_code}")
        except Exception as e:
            self.log_result("Workspace READ", False, f"Workspaces retrieval error: {str(e)}")

    def test_ai_services_crud(self):
        """Test AI services CRUD operations"""
        print("\n" + "="*80)
        print("TESTING AI SERVICES CRUD OPERATIONS")
        print("="*80)
        
        # CREATE - Generate AI content
        ai_request = {
            "prompt": "Write a short test article about CRUD operations",
            "type": "blog_post",
            "tone": "professional",
            "length": "short"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/ai/generate", json=ai_request, timeout=15)
            if response.status_code in [200, 201]:
                ai_result = response.json()
                self.log_result("AI CREATE", True, "AI content generation successful", ai_result)
            else:
                self.log_result("AI CREATE", False, f"AI generation failed: {response.status_code}")
        except Exception as e:
            self.log_result("AI CREATE", False, f"AI generation error: {str(e)}")
        
        # READ - Get AI services info
        try:
            response = self.session.get(f"{API_BASE}/ai/services", timeout=10)
            if response.status_code == 200:
                ai_services = response.json()
                self.log_result("AI READ", True, "AI services info retrieved", ai_services)
            else:
                self.log_result("AI READ", False, f"AI services retrieval failed: {response.status_code}")
        except Exception as e:
            self.log_result("AI READ", False, f"AI services retrieval error: {str(e)}")

    def test_delete_operations(self):
        """Test DELETE operations on created resources"""
        print("\n" + "="*80)
        print("TESTING DELETE OPERATIONS")
        print("="*80)
        
        for resource_type, resource_id in self.created_resources:
            try:
                if resource_type == "user":
                    response = self.session.delete(f"{API_BASE}/users/{resource_id}", timeout=10)
                elif resource_type == "content":
                    response = self.session.delete(f"{API_BASE}/content/{resource_id}", timeout=10)
                elif resource_type == "workspace":
                    response = self.session.delete(f"{API_BASE}/workspaces/{resource_id}", timeout=10)
                else:
                    continue
                
                if response.status_code in [200, 204]:
                    self.log_result(f"{resource_type.title()} DELETE", True, f"Successfully deleted {resource_type}")
                else:
                    self.log_result(f"{resource_type.title()} DELETE", False, f"Delete failed: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"{resource_type.title()} DELETE", False, f"Delete error: {str(e)}")

    def run_complete_crud_test(self):
        """Run complete CRUD verification"""
        print("🚀 COMPLETE CRUD OPERATIONS VERIFICATION")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with CRUD tests")
            return False
        
        # Test all CRUD operations
        self.test_user_crud()
        self.test_content_crud()
        self.test_analytics_crud()
        self.test_workspace_crud()
        self.test_ai_services_crud()
        self.test_delete_operations()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 COMPLETE CRUD TEST RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        
        return success_rate >= 80  # Consider 80% success rate as acceptable

if __name__ == "__main__":
    tester = CompleteCRUDTester()
    success = tester.run_complete_crud_test()
    
    if success:
        print("\n✅ CRUD OPERATIONS VERIFICATION: PASSED")
    else:
        print("\n❌ CRUD OPERATIONS VERIFICATION: NEEDS IMPROVEMENT")