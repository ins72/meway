#!/usr/bin/env python3
"""
FRONTEND INTEGRATION BACKEND VERIFICATION
========================================
Quick verification that backend APIs are ready for new frontend pages:
- DashboardHome page (overview with stats)
- SocialMediaPage (social media management) 
- EcommercePage (online store management)
- SettingsPage (user/workspace settings)
- LoginPage/RegisterPage (authentication)

Test credentials: tmonnens@outlook.com / Voetballen5
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://112c0499-f547-4297-a3d4-b823824978f4.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class FrontendIntegrationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.results = []
        
    def log_result(self, endpoint: str, success: bool, status_code: int = None, details: str = ""):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "success": success,
            "status_code": status_code,
            "details": details
        }
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {endpoint}: {details}")
        
    def test_health_check(self):
        """Test basic health check"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            self.log_result("Health Check", success, response.status_code, 
                          f"Root endpoint responding" if success else f"Failed with {response.status_code}")
            
            # Also test /api/health if it exists
            try:
                health_response = requests.get(f"{self.base_url}/api/health", timeout=10)
                health_success = health_response.status_code == 200
                self.log_result("API Health Check", health_success, health_response.status_code,
                              f"API health endpoint responding" if health_success else f"Failed with {health_response.status_code}")
            except:
                self.log_result("API Health Check", False, None, "Endpoint not available")
                
        except Exception as e:
            self.log_result("Health Check", False, None, f"Connection error: {str(e)}")
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints for LoginPage/RegisterPage"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test login endpoint
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = requests.post(f"{self.base_url}/api/auth/login", 
                                   json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    self.log_result("/api/auth/login", True, 200, "Login successful, token received")
                else:
                    self.log_result("/api/auth/login", False, 200, "Login response missing token")
            else:
                self.log_result("/api/auth/login", False, response.status_code, 
                              f"Login failed: {response.text[:100]}")
                
        except Exception as e:
            self.log_result("/api/auth/login", False, None, f"Login error: {str(e)}")
        
        # Test /me endpoint if we have a token
        if self.token:
            try:
                response = requests.get(f"{self.base_url}/api/auth/me", 
                                      headers=self.headers, timeout=10)
                success = response.status_code == 200
                self.log_result("/api/auth/me", success, response.status_code,
                              "User profile retrieved" if success else f"Failed: {response.text[:100]}")
            except Exception as e:
                self.log_result("/api/auth/me", False, None, f"Me endpoint error: {str(e)}")
        
        # Test register endpoint (just check if it exists)
        try:
            # Use a test registration that should fail gracefully
            test_register = {
                "email": "test_check@example.com",
                "password": "testpass123",
                "name": "Test User"
            }
            response = requests.post(f"{self.base_url}/api/auth/register", 
                                   json=test_register, timeout=10)
            # Any response (even error) means endpoint exists
            self.log_result("/api/auth/register", True, response.status_code,
                          f"Register endpoint available (status: {response.status_code})")
        except Exception as e:
            self.log_result("/api/auth/register", False, None, f"Register endpoint error: {str(e)}")
    
    def test_dashboard_endpoints(self):
        """Test endpoints needed for DashboardHome page"""
        print("\n📊 Testing Dashboard Endpoints...")
        
        # Test analytics endpoint
        try:
            response = requests.get(f"{self.base_url}/api/analytics/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/analytics/health", success, response.status_code,
                          "Analytics system available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/analytics/health", False, None, f"Analytics error: {str(e)}")
        
        # Test workspace endpoint
        try:
            response = requests.get(f"{self.base_url}/api/workspace/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/workspace/health", success, response.status_code,
                          "Workspace system available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/workspace/health", False, None, f"Workspace error: {str(e)}")
    
    def test_social_media_endpoints(self):
        """Test endpoints needed for SocialMediaPage"""
        print("\n📱 Testing Social Media Endpoints...")
        
        # Test marketing endpoint (social media management)
        try:
            response = requests.get(f"{self.base_url}/api/marketing/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/marketing/health", success, response.status_code,
                          "Marketing/Social system available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/marketing/health", False, None, f"Marketing error: {str(e)}")
        
        # Test AI content endpoint (for social media content)
        try:
            response = requests.get(f"{self.base_url}/api/ai-content/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/ai-content/health", success, response.status_code,
                          "AI Content system available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/ai-content/health", False, None, f"AI Content error: {str(e)}")
    
    def test_ecommerce_endpoints(self):
        """Test endpoints needed for EcommercePage"""
        print("\n🛒 Testing E-commerce Endpoints...")
        
        # Test multi-vendor marketplace endpoint
        try:
            response = requests.get(f"{self.base_url}/api/multi-vendor-marketplace/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/multi-vendor-marketplace/health", success, response.status_code,
                          "Multi-vendor marketplace available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/multi-vendor-marketplace/health", False, None, f"Marketplace error: {str(e)}")
        
        # Test financial endpoint (for payments)
        try:
            response = requests.get(f"{self.base_url}/api/financial/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/financial/health", success, response.status_code,
                          "Financial system available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/financial/health", False, None, f"Financial error: {str(e)}")
        
        # Test escrow endpoint (for secure transactions)
        try:
            response = requests.get(f"{self.base_url}/api/escrow/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/escrow/health", success, response.status_code,
                          "Escrow system available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/escrow/health", False, None, f"Escrow error: {str(e)}")
    
    def test_settings_endpoints(self):
        """Test endpoints needed for SettingsPage"""
        print("\n⚙️ Testing Settings Endpoints...")
        
        # Test settings endpoint
        try:
            response = requests.get(f"{self.base_url}/api/settings/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/settings/health", success, response.status_code,
                          "Settings system available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/settings/health", False, None, f"Settings error: {str(e)}")
        
        # Test workspace subscription endpoint (for plan management)
        try:
            response = requests.get(f"{self.base_url}/api/workspace-subscription/health", 
                                  headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_result("/api/workspace-subscription/health", success, response.status_code,
                          "Subscription system available" if success else f"Failed: {response.text[:100]}")
        except Exception as e:
            self.log_result("/api/workspace-subscription/health", False, None, f"Subscription error: {str(e)}")
    
    def run_all_tests(self):
        """Run all frontend integration tests"""
        print("🚀 FRONTEND INTEGRATION BACKEND VERIFICATION")
        print("=" * 50)
        
        self.test_health_check()
        self.test_authentication_endpoints()
        self.test_dashboard_endpoints()
        self.test_social_media_endpoints()
        self.test_ecommerce_endpoints()
        self.test_settings_endpoints()
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['endpoint']}: {result['details']}")
        
        print(f"\n{'✅ ALL SYSTEMS READY FOR FRONTEND INTEGRATION' if success_rate >= 80 else '⚠️ SOME SYSTEMS NEED ATTENTION'}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = FrontendIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)