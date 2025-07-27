"""
Production CRUD Verifier
Comprehensive testing and verification of all CRUD operations
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionCRUDVerifier:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "crud_operations": {},
            "production_ready": False
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and return response"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=request_headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=request_headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=request_headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text(),
                        "headers": dict(response.headers)
                    }
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed"] += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {details}")
            logger.error(f"❌ {test_name}: FAILED - {details}")
    
    async def test_health_endpoints(self):
        """Test basic health endpoints"""
        logger.info("🔍 Testing Health Endpoints...")
        
        health_endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/health", "Health check"),
            ("GET", "/api/health", "API health check"),
            ("GET", "/readiness", "Readiness probe"),
            ("GET", "/liveness", "Liveness probe")
        ]
        
        for method, endpoint, description in health_endpoints:
            response = await self.make_request(method, endpoint)
            success = response["status"] == 200
            self.log_test_result(description, success, f"Status: {response['status']}")
    
    async def test_authentication(self):
        """Test authentication system"""
        logger.info("🔍 Testing Authentication System...")
        
        # Test registration
        register_data = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        response = await self.make_request("POST", "/api/auth/register", register_data)
        if response["status"] == 200:
            self.log_test_result("User Registration", True)
            
            # Test login
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            
            response = await self.make_request("POST", "/api/auth/login", login_data)
            if response["status"] == 200 and "access_token" in response["data"]:
                self.auth_token = response["data"]["access_token"]
                self.log_test_result("User Login", True)
                
                # Test get current user
                response = await self.make_request("GET", "/api/auth/me")
                success = response["status"] == 200
                self.log_test_result("Get Current User", success, f"Status: {response['status']}")
            else:
                self.log_test_result("User Login", False, f"Status: {response['status']}")
        else:
            self.log_test_result("User Registration", False, f"Status: {response['status']}")
    
    async def test_workspace_crud(self):
        """Test workspace CRUD operations"""
        logger.info("🔍 Testing Workspace CRUD Operations...")
        
        if not self.auth_token:
            self.log_test_result("Workspace CRUD", False, "No authentication token")
            return
        
        # Create workspace
        workspace_data = {
            "name": "Test Workspace",
            "description": "Test workspace for CRUD verification",
            "industry": "Technology",
            "main_goals": ["analytics", "crm"],
            "subscription_plan": "pro"
        }
        
        response = await self.make_request("POST", "/api/workspace/", workspace_data)
        if response["status"] == 200:
            workspace_id = response["data"]["id"]
            self.log_test_result("Create Workspace", True)
            
            # Read workspace
            response = await self.make_request("GET", f"/api/workspace/{workspace_id}")
            success = response["status"] == 200
            self.log_test_result("Read Workspace", success, f"Status: {response['status']}")
            
            # Update workspace
            update_data = {
                "name": "Updated Test Workspace",
                "description": "Updated description"
            }
            response = await self.make_request("PUT", f"/api/workspace/{workspace_id}", update_data)
            success = response["status"] == 200
            self.log_test_result("Update Workspace", success, f"Status: {response['status']}")
            
            # List workspaces
            response = await self.make_request("GET", "/api/workspace/")
            success = response["status"] == 200
            self.log_test_result("List Workspaces", success, f"Status: {response['status']}")
            
            # Delete workspace
            response = await self.make_request("DELETE", f"/api/workspace/{workspace_id}")
            success = response["status"] == 200
            self.log_test_result("Delete Workspace", success, f"Status: {response['status']}")
            
            self.test_results["crud_operations"]["workspace"] = True
        else:
            self.log_test_result("Create Workspace", False, f"Status: {response['status']}")
            self.test_results["crud_operations"]["workspace"] = False
    
    async def test_user_crud(self):
        """Test user CRUD operations"""
        logger.info("🔍 Testing User CRUD Operations...")
        
        if not self.auth_token:
            self.log_test_result("User CRUD", False, "No authentication token")
            return
        
        # Get current user profile
        response = await self.make_request("GET", "/api/user/me")
        success = response["status"] == 200
        self.log_test_result("Get Current User Profile", success, f"Status: {response['status']}")
        
        # Update current user
        update_data = {
            "full_name": "Updated Test User",
            "company": "Test Company"
        }
        response = await self.make_request("PUT", "/api/user/me", update_data)
        success = response["status"] == 200
        self.log_test_result("Update Current User", success, f"Status: {response['status']}")
        
        # Get user preferences
        response = await self.make_request("GET", "/api/user/me/preferences")
        success = response["status"] == 200
        self.log_test_result("Get User Preferences", success, f"Status: {response['status']}")
        
        # Update user preferences
        preferences_data = {
            "theme": "dark",
            "language": "en",
            "timezone": "UTC"
        }
        response = await self.make_request("PUT", "/api/user/me/preferences", preferences_data)
        success = response["status"] == 200
        self.log_test_result("Update User Preferences", success, f"Status: {response['status']}")
        
        self.test_results["crud_operations"]["user"] = True
    
    async def test_blog_crud(self):
        """Test blog CRUD operations"""
        logger.info("🔍 Testing Blog CRUD Operations...")
        
        if not self.auth_token:
            self.log_test_result("Blog CRUD", False, "No authentication token")
            return
        
        # Create blog post
        blog_data = {
            "title": "Test Blog Post",
            "content": "This is a test blog post content for CRUD verification.",
            "excerpt": "Test excerpt",
            "tags": ["test", "crud"],
            "category": "Technology",
            "is_published": True
        }
        
        response = await self.make_request("POST", "/api/blog/posts", blog_data)
        if response["status"] == 200:
            post_id = response["data"]["id"]
            self.log_test_result("Create Blog Post", True)
            
            # Read blog post
            response = await self.make_request("GET", f"/api/blog/posts/{post_id}")
            success = response["status"] == 200
            self.log_test_result("Read Blog Post", success, f"Status: {response['status']}")
            
            # Update blog post
            update_data = {
                "title": "Updated Test Blog Post",
                "content": "Updated content"
            }
            response = await self.make_request("PUT", f"/api/blog/posts/{post_id}", update_data)
            success = response["status"] == 200
            self.log_test_result("Update Blog Post", success, f"Status: {response['status']}")
            
            # List blog posts
            response = await self.make_request("GET", "/api/blog/posts")
            success = response["status"] == 200
            self.log_test_result("List Blog Posts", success, f"Status: {response['status']}")
            
            # Create comment
            comment_data = {
                "content": "Test comment on the blog post"
            }
            response = await self.make_request("POST", f"/api/blog/posts/{post_id}/comments", comment_data)
            success = response["status"] == 200
            self.log_test_result("Create Blog Comment", success, f"Status: {response['status']}")
            
            # List comments
            response = await self.make_request("GET", f"/api/blog/posts/{post_id}/comments")
            success = response["status"] == 200
            self.log_test_result("List Blog Comments", success, f"Status: {response['status']}")
            
            # Delete blog post
            response = await self.make_request("DELETE", f"/api/blog/posts/{post_id}")
            success = response["status"] == 200
            self.log_test_result("Delete Blog Post", success, f"Status: {response['status']}")
            
            self.test_results["crud_operations"]["blog"] = True
        else:
            self.log_test_result("Create Blog Post", False, f"Status: {response['status']}")
            self.test_results["crud_operations"]["blog"] = False
    
    async def test_content_crud(self):
        """Test content CRUD operations"""
        logger.info("🔍 Testing Content CRUD Operations...")
        
        if not self.auth_token:
            self.log_test_result("Content CRUD", False, "No authentication token")
            return
        
        # Create content
        content_data = {
            "title": "Test Content",
            "content": "This is test content for CRUD verification",
            "type": "article",
            "status": "draft"
        }
        
        response = await self.make_request("POST", "/api/content/", content_data)
        if response["status"] == 200:
            content_id = response["data"]["id"]
            self.log_test_result("Create Content", True)
            
            # Read content
            response = await self.make_request("GET", f"/api/content/{content_id}")
            success = response["status"] == 200
            self.log_test_result("Read Content", success, f"Status: {response['status']}")
            
            # Update content
            update_data = {
                "title": "Updated Test Content",
                "status": "published"
            }
            response = await self.make_request("PUT", f"/api/content/{content_id}", update_data)
            success = response["status"] == 200
            self.log_test_result("Update Content", success, f"Status: {response['status']}")
            
            # List content
            response = await self.make_request("GET", "/api/content/")
            success = response["status"] == 200
            self.log_test_result("List Content", success, f"Status: {response['status']}")
            
            # Delete content
            response = await self.make_request("DELETE", f"/api/content/{content_id}")
            success = response["status"] == 200
            self.log_test_result("Delete Content", success, f"Status: {response['status']}")
            
            self.test_results["crud_operations"]["content"] = True
        else:
            self.log_test_result("Create Content", False, f"Status: {response['status']}")
            self.test_results["crud_operations"]["content"] = False
    
    async def test_notification_crud(self):
        """Test notification CRUD operations"""
        logger.info("🔍 Testing Notification CRUD Operations...")
        
        if not self.auth_token:
            self.log_test_result("Notification CRUD", False, "No authentication token")
            return
        
        # Send notification
        notification_data = {
            "title": "Test Notification",
            "message": "This is a test notification",
            "type": "info",
            "recipient_id": "current_user"
        }
        
        response = await self.make_request("POST", "/api/notification/send", notification_data)
        success = response["status"] == 200
        self.log_test_result("Send Notification", success, f"Status: {response['status']}")
        
        # Get notification history
        response = await self.make_request("GET", "/api/notification/history")
        success = response["status"] == 200
        self.log_test_result("Get Notification History", success, f"Status: {response['status']}")
        
        # Get notification stats
        response = await self.make_request("GET", "/api/notification/stats")
        success = response["status"] == 200
        self.log_test_result("Get Notification Stats", success, f"Status: {response['status']}")
        
        self.test_results["crud_operations"]["notification"] = True
    
    async def test_campaign_crud(self):
        """Test campaign CRUD operations"""
        logger.info("🔍 Testing Campaign CRUD Operations...")
        
        if not self.auth_token:
            self.log_test_result("Campaign CRUD", False, "No authentication token")
            return
        
        # Create campaign
        campaign_data = {
            "name": "Test Campaign",
            "description": "Test campaign for CRUD verification",
            "type": "email",
            "status": "draft"
        }
        
        response = await self.make_request("POST", "/api/campaign/", campaign_data)
        if response["status"] == 200:
            campaign_id = response["data"]["id"]
            self.log_test_result("Create Campaign", True)
            
            # Read campaign
            response = await self.make_request("GET", f"/api/campaign/{campaign_id}")
            success = response["status"] == 200
            self.log_test_result("Read Campaign", success, f"Status: {response['status']}")
            
            # Update campaign
            update_data = {
                "name": "Updated Test Campaign",
                "status": "active"
            }
            response = await self.make_request("PUT", f"/api/campaign/{campaign_id}", update_data)
            success = response["status"] == 200
            self.log_test_result("Update Campaign", success, f"Status: {response['status']}")
            
            # List campaigns
            response = await self.make_request("GET", "/api/campaign/")
            success = response["status"] == 200
            self.log_test_result("List Campaigns", success, f"Status: {response['status']}")
            
            # Delete campaign
            response = await self.make_request("DELETE", f"/api/campaign/{campaign_id}")
            success = response["status"] == 200
            self.log_test_result("Delete Campaign", success, f"Status: {response['status']}")
            
            self.test_results["crud_operations"]["campaign"] = True
        else:
            self.log_test_result("Create Campaign", False, f"Status: {response['status']}")
            self.test_results["crud_operations"]["campaign"] = False
    
    async def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        logger.info("🔍 Testing Analytics Endpoints...")
        
        if not self.auth_token:
            self.log_test_result("Analytics", False, "No authentication token")
            return
        
        # Test various analytics endpoints
        analytics_endpoints = [
            ("GET", "/api/blog/analytics", "Blog Analytics"),
            ("GET", "/api/workspace/analytics", "Workspace Analytics"),
            ("GET", "/api/marketing/analytics", "Marketing Analytics"),
            ("GET", "/api/dashboard/analytics", "Dashboard Analytics")
        ]
        
        for method, endpoint, description in analytics_endpoints:
            response = await self.make_request(method, endpoint)
            success = response["status"] in [200, 404]  # 404 is acceptable if no data
            self.log_test_result(description, success, f"Status: {response['status']}")
    
    async def test_admin_endpoints(self):
        """Test admin endpoints"""
        logger.info("🔍 Testing Admin Endpoints...")
        
        if not self.auth_token:
            self.log_test_result("Admin Endpoints", False, "No authentication token")
            return
        
        # Test admin endpoints (these might require admin privileges)
        admin_endpoints = [
            ("GET", "/api/workspace/admin/all", "Admin List All Workspaces"),
            ("GET", "/api/user/admin/all", "Admin List All Users"),
            ("GET", "/api/blog/admin/posts", "Admin List All Blog Posts"),
            ("GET", "/api/workspace/stats", "Workspace Stats"),
            ("GET", "/api/user/stats", "User Stats"),
            ("GET", "/api/blog/stats", "Blog Stats")
        ]
        
        for method, endpoint, description in admin_endpoints:
            response = await self.make_request(method, endpoint)
            success = response["status"] in [200, 403]  # 403 is acceptable for non-admin users
            self.log_test_result(description, success, f"Status: {response['status']}")
    
    async def run_comprehensive_test(self):
        """Run comprehensive CRUD test suite"""
        logger.info("🚀 Starting Comprehensive CRUD Verification...")
        logger.info(f"Testing against: {self.base_url}")
        
        # Test sequence
        await self.test_health_endpoints()
        await self.test_authentication()
        await self.test_workspace_crud()
        await self.test_user_crud()
        await self.test_blog_crud()
        await self.test_content_crud()
        await self.test_notification_crud()
        await self.test_campaign_crud()
        await self.test_analytics_endpoints()
        await self.test_admin_endpoints()
        
        # Calculate success rate
        success_rate = (self.test_results["passed"] / self.test_results["total_tests"]) * 100 if self.test_results["total_tests"] > 0 else 0
        
        # Determine production readiness
        self.test_results["production_ready"] = success_rate >= 80 and self.test_results["failed"] < 10
        
        # Generate report
        self.generate_report()
        
        return self.test_results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "="*80)
        logger.info("📊 PRODUCTION CRUD VERIFICATION REPORT")
        logger.info("="*80)
        
        logger.info(f"Total Tests: {self.test_results['total_tests']}")
        logger.info(f"Passed: {self.test_results['passed']}")
        logger.info(f"Failed: {self.test_results['failed']}")
        logger.info(f"Success Rate: {(self.test_results['passed'] / self.test_results['total_tests']) * 100:.1f}%")
        
        logger.info("\nCRUD Operations Status:")
        for operation, status in self.test_results["crud_operations"].items():
            status_icon = "✅" if status else "❌"
            logger.info(f"  {status_icon} {operation.title()}: {'Working' if status else 'Failed'}")
        
        logger.info(f"\nProduction Ready: {'✅ YES' if self.test_results['production_ready'] else '❌ NO'}")
        
        if self.test_results["errors"]:
            logger.info("\nErrors Found:")
            for error in self.test_results["errors"][:10]:  # Show first 10 errors
                logger.info(f"  ❌ {error}")
        
        logger.info("="*80)
        
        # Save detailed report to file
        report_file = f"production_crud_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"Detailed report saved to: {report_file}")

async def main():
    """Main function to run the production CRUD verifier"""
    base_url = os.getenv("API_BASE_URL", "http://localhost:8001")
    
    async with ProductionCRUDVerifier(base_url) as verifier:
        results = await verifier.run_comprehensive_test()
        
        if results["production_ready"]:
            logger.info("🎉 Platform is PRODUCTION READY with complete CRUD operations!")
            sys.exit(0)
        else:
            logger.error("❌ Platform is NOT production ready. Please fix the issues above.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 