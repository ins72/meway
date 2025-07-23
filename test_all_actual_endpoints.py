#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TEST - ALL ACTUAL ENDPOINTS
Test all 74 actual endpoints for production readiness
"""

import requests
import json
import time
from datetime import datetime

class ComprehensiveActualEndpointTest:
    def __init__(self):
        self.base_url = "https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com"
        self.session = requests.Session()
        self.auth_token = None
        self.results = {
            "total_endpoints": 0,
            "successful": 0,
            "failed": 0,
            "endpoints": []
        }
        
        # All actual endpoints from OpenAPI
        self.endpoints = [
            "/",
            "/api/automation/status",
            "/api/blog/analytics",
            "/api/blog/posts",
            "/api/blog/posts/slug/test-slug",
            "/api/blog/posts/test-id",
            "/api/content/api/content/",
            "/api/content/api/content/analytics/performance", 
            "/api/content/api/content/categories/list",
            "/api/content/api/content/search",
            "/api/content/api/content/test-id",
            "/api/device/offline/sync",
            "/api/device/register",
            "/api/disputes/initiate",
            "/api/disputes/list",
            "/api/email-automation/analytics/overview",
            "/api/email-automation/automation-sequence",
            "/api/email-automation/bulk-email",
            "/api/email-automation/campaigns",
            "/api/email-automation/campaigns/test-id/statistics",
            "/api/email-automation/email-logs",
            "/api/email-automation/send-email",
            "/api/email-automation/subscribers",
            "/api/email-automation/templates",
            "/api/enterprise-security/audit/log",
            "/api/enterprise-security/audit/logs",
            "/api/enterprise-security/compliance/frameworks",
            "/api/enterprise-security/compliance/report",
            "/api/enterprise-security/compliance/reports",
            "/api/enterprise-security/security/dashboard",
            "/api/enterprise-security/threat-detection/alerts",
            "/api/enterprise-security/threat-detection/setup",
            "/api/enterprise-security/vulnerability-assessment",
            "/api/enterprise-security/vulnerability-assessments",
            "/api/escrow/transactions/list",
            "/api/escrow/transactions/milestone",
            "/api/health",
            "/api/instagram/profiles",
            "/api/instagram/search",
            "/api/integration/available",
            "/api/integration/connected",
            "/api/integration/status",
            "/api/marketing-website/ab-tests",
            "/api/marketing-website/analytics/overview",
            "/api/marketing-website/pages",
            "/api/marketing-website/seo/analysis/test-id",
            "/api/marketing-website/templates/marketplace",
            "/api/marketing/analytics",
            "/api/marketing/campaigns",
            "/api/marketing/contacts",
            "/api/notifications/api/notifications/connection-status",
            "/api/notifications/api/notifications/history",
            "/api/notifications/api/notifications/mark-all-read",
            "/api/notifications/api/notifications/mark-read/test-id",
            "/api/notifications/api/notifications/send",
            "/api/notifications/api/notifications/send-bulk",
            "/api/notifications/api/notifications/stats",
            "/api/posts/schedule",
            "/api/posts/scheduled",
            "/api/pwa/manifest/current",
            "/api/pwa/manifest/generate",
            "/api/team-management/activity",
            "/api/team-management/dashboard",
            "/api/team-management/members",
            "/api/team-management/teams",
            "/api/template-marketplace/browse",
            "/api/template-marketplace/creator-earnings",
            "/api/workflows/create",
            "/api/workflows/list",
            "/api/workspaces",
            "/health",
            "/healthz",
            "/metrics",
            "/ready"
        ]
    
    def authenticate(self):
        """Get authentication token"""
        try:
            # Try different auth endpoints
            auth_endpoints = [
                "/api/auth/login",
                "/auth/login", 
                "/login"
            ]
            
            for endpoint in auth_endpoints:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        data={
                            "username": "tmonnens@outlook.com",
                            "password": "Voetballen5"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("access_token"):
                            self.auth_token = data["access_token"]
                            self.session.headers.update({
                                "Authorization": f"Bearer {self.auth_token}"
                            })
                            print(f"✅ Authentication successful via {endpoint}")
                            return True
                except:
                    continue
            
            print("⚠️  Authentication failed - proceeding without token")
            return False
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_endpoint(self, endpoint: str):
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            start_time = time.time()
            
            # Try GET request first
            response = self.session.get(url, timeout=10)
            response_time = time.time() - start_time
            
            result = {
                "endpoint": endpoint,
                "url": url,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code in [200, 201],
                "error": None,
                "data_size": 0,
                "has_mock_data": False
            }
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    result["data_size"] = len(str(data))
                    
                    # Check for mock data
                    data_str = str(data).lower()
                    mock_indicators = ["sample", "mock", "test", "dummy", "fake", "example"]
                    result["has_mock_data"] = any(indicator in data_str for indicator in mock_indicators)
                    
                except:
                    result["data_size"] = len(response.text)
            else:
                result["error"] = response.text[:200] if response.text else "No error message"
            
            return result
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "url": f"{self.base_url}{endpoint}",
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": str(e),
                "data_size": 0,
                "has_mock_data": False
            }
    
    def run_comprehensive_test(self):
        """Test all endpoints"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TEST")
        print(f"Testing {len(self.endpoints)} actual endpoints...")
        print("=" * 60)
        
        # Authenticate first
        self.authenticate()
        
        # Test all endpoints
        for i, endpoint in enumerate(self.endpoints, 1):
            print(f"[{i}/{len(self.endpoints)}] Testing {endpoint}")
            
            result = self.test_endpoint(endpoint)
            self.results["endpoints"].append(result)
            
            if result["success"]:
                self.results["successful"] += 1
                status = "✅ PASS"
                if result["has_mock_data"]:
                    status += " (has mock data)"
            else:
                self.results["failed"] += 1
                status = f"❌ FAIL ({result['status_code']})"
            
            print(f"    {status} - {result['response_time']:.3f}s")
            
            time.sleep(0.1)  # Small delay to prevent overwhelming
        
        self.results["total_endpoints"] = len(self.endpoints)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        print(f"Total Endpoints Tested: {self.results['total_endpoints']}")
        print(f"Successful: {self.results['successful']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['successful']/self.results['total_endpoints']*100):.1f}%")
        
        # Show failing endpoints
        failing_endpoints = [r for r in self.results["endpoints"] if not r["success"]]
        if failing_endpoints:
            print(f"\n❌ FAILING ENDPOINTS ({len(failing_endpoints)}):")
            for result in failing_endpoints:
                print(f"  {result['endpoint']} - {result['status_code']} - {result['error'][:50] if result['error'] else 'No error'}")
        
        # Show endpoints with mock data
        mock_endpoints = [r for r in self.results["endpoints"] if r["has_mock_data"]]
        if mock_endpoints:
            print(f"\n🎭 ENDPOINTS WITH MOCK DATA ({len(mock_endpoints)}):")
            for result in mock_endpoints:
                print(f"  {result['endpoint']}")
        
        return self.results

def main():
    tester = ComprehensiveActualEndpointTest()
    results = tester.run_comprehensive_test()
    
    # Save results
    with open("/app/comprehensive_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Test completed - Results saved to comprehensive_test_results.json")
    return results

if __name__ == "__main__":
    main()