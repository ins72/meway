#!/usr/bin/env python3
"""
COMPREHENSIVE AUTHENTICATED BACKEND TEST
Test all endpoints with proper authentication
"""

import requests
import json
import time
from datetime import datetime

class AuthenticatedEndpointTest:
    def __init__(self):
        self.base_url = "https://d70b9379-58ef-4e6d-9a10-f0eebb21d382.preview.emergentagent.com"
        self.session = requests.Session()
        self.auth_token = None
        
        # All actual endpoints from OpenAPI
        self.endpoints = [
            ("/", "GET"),
            ("/api/automation/status", "GET"),
            ("/api/blog/analytics", "GET"),
            ("/api/blog/posts", "GET"),
            ("/api/blog/posts", "POST"),
            ("/api/content/api/content/", "GET"),
            ("/api/content/api/content/analytics/performance", "GET"),
            ("/api/content/api/content/categories/list", "GET"),
            ("/api/content/api/content/search", "GET"),
            ("/api/device/offline/sync", "POST"),
            ("/api/device/register", "POST"),
            ("/api/disputes/initiate", "POST"),
            ("/api/disputes/list", "GET"),
            ("/api/email-automation/analytics/overview", "GET"),
            ("/api/email-automation/automation-sequence", "POST"),
            ("/api/email-automation/bulk-email", "POST"),
            ("/api/email-automation/campaigns", "GET"),
            ("/api/email-automation/email-logs", "GET"),
            ("/api/email-automation/send-email", "POST"),
            ("/api/email-automation/subscribers", "GET"),
            ("/api/email-automation/templates", "GET"),
            ("/api/enterprise-security/audit/log", "POST"),
            ("/api/enterprise-security/audit/logs", "GET"),
            ("/api/enterprise-security/compliance/frameworks", "GET"),
            ("/api/enterprise-security/compliance/report", "POST"),
            ("/api/enterprise-security/compliance/reports", "GET"),
            ("/api/enterprise-security/security/dashboard", "GET"),
            ("/api/enterprise-security/threat-detection/alerts", "GET"),
            ("/api/enterprise-security/threat-detection/setup", "POST"),
            ("/api/enterprise-security/vulnerability-assessment", "POST"),
            ("/api/enterprise-security/vulnerability-assessments", "GET"),
            ("/api/escrow/transactions/list", "GET"),
            ("/api/escrow/transactions/milestone", "POST"),
            ("/api/health", "GET"),
            ("/api/instagram/profiles", "GET"),
            ("/api/instagram/search", "POST"),
            ("/api/integration/available", "GET"),
            ("/api/integration/connected", "GET"),
            ("/api/integration/status", "GET"),
            ("/api/marketing-website/ab-tests", "GET"),
            ("/api/marketing-website/analytics/overview", "GET"),
            ("/api/marketing-website/pages", "GET"),
            ("/api/marketing-website/templates/marketplace", "GET"),
            ("/api/marketing/analytics", "GET"),
            ("/api/marketing/campaigns", "GET"),
            ("/api/marketing/contacts", "GET"),
            ("/api/notifications/api/notifications/connection-status", "GET"),
            ("/api/notifications/api/notifications/history", "GET"),
            ("/api/notifications/api/notifications/mark-all-read", "POST"),
            ("/api/notifications/api/notifications/send", "POST"),
            ("/api/notifications/api/notifications/send-bulk", "POST"),
            ("/api/notifications/api/notifications/stats", "GET"),
            ("/api/posts/schedule", "POST"),
            ("/api/posts/scheduled", "GET"),
            ("/api/pwa/manifest/current", "GET"),
            ("/api/pwa/manifest/generate", "POST"),
            ("/api/team-management/activity", "GET"),
            ("/api/team-management/dashboard", "GET"),
            ("/api/team-management/members", "GET"),
            ("/api/team-management/teams", "POST"),
            ("/api/template-marketplace/browse", "GET"),
            ("/api/template-marketplace/creator-earnings", "GET"),
            ("/api/workflows/create", "POST"),
            ("/api/workflows/list", "GET"),
            ("/api/workspaces", "GET"),
            ("/health", "GET"),
            ("/healthz", "GET"),
            ("/metrics", "GET"),
            ("/ready", "GET")
        ]
        
        self.results = {
            "total_endpoints": len(self.endpoints),
            "successful": 0,
            "failed": 0,
            "endpoints": []
        }
    
    def authenticate(self):
        """Get authentication token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                data={
                    "username": "tmonnens@outlook.com",
                    "password": "Voetballen5"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_endpoint(self, endpoint: str, method: str):
        """Test a single endpoint with proper method"""
        try:
            url = f"{self.base_url}{endpoint}"
            start_time = time.time()
            
            # Prepare test data for POST requests
            test_data = {
                "test": True,
                "data": "test data for endpoint validation"
            }
            
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=test_data, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, json=test_data, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=10)
            else:
                response = self.session.get(url, timeout=10)
            
            response_time = time.time() - start_time
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code in [200, 201, 202],
                "error": None,
                "data_size": 0,
                "has_real_data": False,
                "response_format": "unknown"
            }
            
            if response.status_code in [200, 201, 202]:
                try:
                    data = response.json()
                    result["data_size"] = len(str(data))
                    result["response_format"] = "json"
                    
                    # Check for real data vs mock data
                    data_str = str(data).lower()
                    real_data_indicators = ["user_id", "created_at", "updated_at", "_id", "success"]
                    mock_data_indicators = ["sample", "mock", "test", "dummy", "fake", "example"]
                    
                    has_real_indicators = any(indicator in data_str for indicator in real_data_indicators)
                    has_mock_indicators = any(indicator in data_str for indicator in mock_data_indicators)
                    
                    result["has_real_data"] = has_real_indicators and not has_mock_indicators
                    
                except:
                    result["data_size"] = len(response.text)
                    result["response_format"] = "text"
            else:
                result["error"] = response.text[:200] if response.text else "No error message"
            
            return result
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "url": f"{self.base_url}{endpoint}",
                "status_code": 0,
                "response_time": 0,
                "success": False,
                "error": str(e),
                "data_size": 0,
                "has_real_data": False,
                "response_format": "error"
            }
    
    def run_comprehensive_test(self):
        """Test all endpoints with authentication"""
        print("🚀 STARTING COMPREHENSIVE AUTHENTICATED BACKEND TEST")
        print(f"Testing {len(self.endpoints)} endpoints with proper authentication...")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return self.results
        
        # Test all endpoints
        for i, (endpoint, method) in enumerate(self.endpoints, 1):
            print(f"[{i:2d}/{len(self.endpoints)}] {method:4} {endpoint}")
            
            result = self.test_endpoint(endpoint, method)
            self.results["endpoints"].append(result)
            
            if result["success"]:
                self.results["successful"] += 1
                status = "✅ PASS"
                if result["has_real_data"]:
                    status += " (real data)"
                else:
                    status += " (basic response)"
            else:
                self.results["failed"] += 1
                status = f"❌ FAIL ({result['status_code']})"
            
            print(f"    {status} - {result['response_time']:.3f}s - {result['data_size']} bytes")
            
            time.sleep(0.1)  # Small delay
        
        # Print detailed summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE AUTHENTICATED TEST SUMMARY")
        print("=" * 80)
        print(f"Total Endpoints Tested: {self.results['total_endpoints']}")
        print(f"Authentication: ✅ SUCCESS")
        print(f"Successful Responses: {self.results['successful']}")
        print(f"Failed Responses: {self.results['failed']}")
        print(f"Success Rate: {(self.results['successful']/self.results['total_endpoints']*100):.1f}%")
        
        # Categorize responses
        success_endpoints = [r for r in self.results["endpoints"] if r["success"]]
        real_data_endpoints = [r for r in success_endpoints if r["has_real_data"]]
        failed_endpoints = [r for r in self.results["endpoints"] if not r["success"]]
        
        print(f"\n✅ WORKING ENDPOINTS ({len(success_endpoints)}):")
        for result in success_endpoints[:10]:  # Show first 10
            print(f"  {result['method']:4} {result['endpoint']} - {result['status_code']} - {result['data_size']} bytes")
        if len(success_endpoints) > 10:
            print(f"  ... and {len(success_endpoints) - 10} more")
        
        print(f"\n📊 ENDPOINTS WITH REAL DATA ({len(real_data_endpoints)}):")
        for result in real_data_endpoints[:5]:  # Show first 5
            print(f"  {result['method']:4} {result['endpoint']}")
        
        if failed_endpoints:
            print(f"\n❌ FAILING ENDPOINTS ({len(failed_endpoints)}):")
            for result in failed_endpoints[:10]:  # Show first 10
                error_msg = result['error'][:50] if result['error'] else 'No error'
                print(f"  {result['method']:4} {result['endpoint']} - {result['status_code']} - {error_msg}")
        
        return self.results

def main():
    tester = AuthenticatedEndpointTest()
    results = tester.run_comprehensive_test()
    
    # Save results
    with open("/app/authenticated_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Authenticated test completed - Results saved to authenticated_test_results.json")
    print(f"🎯 Success Rate: {(results['successful']/results['total_endpoints']*100):.1f}%")
    
    return results

if __name__ == "__main__":
    main()