#!/usr/bin/env python3
"""
Rate Limiting & Throttling System Backend Test
Testing comprehensive API rate limiting and analytics functionality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

class RateLimitingSystemTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, response_data: Any = None, error: str = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response_size": len(str(response_data)) if response_data else 0,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if error:
            print(f"   Error: {error}")
        if response_data and success:
            print(f"   Response size: {result['response_size']} chars")
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        try:
            auth_data = {
                "username": email,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_test("Authentication", True, token_data)
                return True
            else:
                self.log_test("Authentication", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, error=str(e))
            return False
    
    def test_rate_limit_status(self) -> bool:
        """Test GET /rate-limits/status - Get rate limit status"""
        try:
            response = self.session.get(f"{self.base_url}/api/rate-limits/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["success", "data"]
                if all(field in data for field in required_fields):
                    rate_data = data["data"]
                    
                    # Check for essential rate limit fields
                    essential_fields = ["user_id", "subscription_tier", "user_limits", "workspace_limits"]
                    if all(field in rate_data for field in essential_fields):
                        self.log_test("Rate Limit Status", True, data)
                        return True
                    else:
                        self.log_test("Rate Limit Status", False, error="Missing essential rate limit fields")
                        return False
                else:
                    self.log_test("Rate Limit Status", False, error="Invalid response structure")
                    return False
            else:
                self.log_test("Rate Limit Status", False, error=f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Rate Limit Status", False, error=str(e))
            return False
    
    def test_rate_limit_metrics(self) -> bool:
        """Test GET /rate-limits/metrics - Get metrics and analytics"""
        try:
            # Test with different timeframes
            timeframes = ["1h", "24h", "7d"]
            
            for timeframe in timeframes:
                response = self.session.get(
                    f"{self.base_url}/api/rate-limits/metrics",
                    params={"timeframe": timeframe}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and "data" in data:
                        metrics_data = data["data"]
                        
                        # Check for essential metrics fields
                        essential_fields = ["timeframe", "usage_patterns", "top_endpoints", "summary"]
                        if all(field in metrics_data for field in essential_fields):
                            self.log_test(f"Rate Limit Metrics ({timeframe})", True, data)
                        else:
                            self.log_test(f"Rate Limit Metrics ({timeframe})", False, error="Missing essential metrics fields")
                            return False
                    else:
                        self.log_test(f"Rate Limit Metrics ({timeframe})", False, error="Invalid response structure")
                        return False
                else:
                    self.log_test(f"Rate Limit Metrics ({timeframe})", False, error=f"Status: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("Rate Limit Metrics", False, error=str(e))
            return False
    
    def test_api_usage_statistics(self) -> bool:
        """Test GET /rate-limits/usage - Get API usage statistics"""
        try:
            # Test with different parameters
            test_cases = [
                {"timeframe": "24h", "endpoint": "all"},
                {"timeframe": "1h", "endpoint": "/api/dashboard/overview"},
                {"timeframe": "7d", "endpoint": "all"}
            ]
            
            for case in test_cases:
                response = self.session.get(
                    f"{self.base_url}/api/rate-limits/usage",
                    params=case
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and "data" in data:
                        usage_data = data["data"]
                        
                        # Check for essential usage fields
                        essential_fields = ["timeframe", "endpoint_filter", "endpoints", "summary"]
                        if all(field in usage_data for field in essential_fields):
                            test_name = f"API Usage Statistics ({case['timeframe']}, {case['endpoint']})"
                            self.log_test(test_name, True, data)
                        else:
                            self.log_test("API Usage Statistics", False, error="Missing essential usage fields")
                            return False
                    else:
                        self.log_test("API Usage Statistics", False, error="Invalid response structure")
                        return False
                else:
                    self.log_test("API Usage Statistics", False, error=f"Status: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("API Usage Statistics", False, error=str(e))
            return False
    
    def test_rate_limit_check(self) -> bool:
        """Test POST /rate-limits/check - Check rate limits"""
        try:
            # Test rate limit checking for different endpoints
            test_endpoints = [
                "/api/dashboard/overview",
                "/api/analytics/data",
                "/api/users/profile"
            ]
            
            for endpoint in test_endpoints:
                response = self.session.post(
                    f"{self.base_url}/api/rate-limits/check",
                    params={
                        "endpoint": endpoint,
                        "action": "api_call"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and "data" in data:
                        check_data = data["data"]
                        
                        # Check for essential rate limit check fields
                        essential_fields = ["allowed", "endpoint", "subscription_tier", "checks"]
                        if all(field in check_data for field in essential_fields):
                            test_name = f"Rate Limit Check ({endpoint})"
                            self.log_test(test_name, True, data)
                        else:
                            self.log_test("Rate Limit Check", False, error="Missing essential check fields")
                            return False
                    else:
                        self.log_test("Rate Limit Check", False, error="Invalid response structure")
                        return False
                else:
                    self.log_test("Rate Limit Check", False, error=f"Status: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("Rate Limit Check", False, error=str(e))
            return False
    
    def test_user_quotas(self) -> bool:
        """Test GET /rate-limits/quotas - Get user quotas"""
        try:
            response = self.session.get(f"{self.base_url}/api/rate-limits/quotas")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    quota_data = data["data"]
                    
                    # Check for essential quota fields
                    essential_fields = ["user_id", "subscription_tier", "quotas", "features"]
                    if all(field in quota_data for field in essential_fields):
                        self.log_test("User Quotas", True, data)
                        return True
                    else:
                        self.log_test("User Quotas", False, error="Missing essential quota fields")
                        return False
                else:
                    self.log_test("User Quotas", False, error="Invalid response structure")
                    return False
            else:
                self.log_test("User Quotas", False, error=f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Quotas", False, error=str(e))
            return False
    
    def test_rate_limit_alerts(self) -> bool:
        """Test GET /rate-limits/alerts - Get rate limit alerts"""
        try:
            response = self.session.get(f"{self.base_url}/api/rate-limits/alerts")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    alert_data = data["data"]
                    
                    # Check for essential alert fields
                    essential_fields = ["alerts", "total_alerts", "severity_breakdown"]
                    if all(field in alert_data for field in essential_fields):
                        self.log_test("Rate Limit Alerts", True, data)
                        return True
                    else:
                        self.log_test("Rate Limit Alerts", False, error="Missing essential alert fields")
                        return False
                else:
                    self.log_test("Rate Limit Alerts", False, error="Invalid response structure")
                    return False
            else:
                self.log_test("Rate Limit Alerts", False, error=f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Rate Limit Alerts", False, error=str(e))
            return False
    
    def test_top_endpoints(self) -> bool:
        """Test GET /rate-limits/top-endpoints - Get top endpoints"""
        try:
            # Test with different parameters
            test_cases = [
                {"limit": 5, "timeframe": "24h"},
                {"limit": 10, "timeframe": "1h"},
                {"limit": 3, "timeframe": "7d"}
            ]
            
            for case in test_cases:
                response = self.session.get(
                    f"{self.base_url}/api/rate-limits/top-endpoints",
                    params=case
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and "data" in data:
                        endpoint_data = data["data"]
                        
                        # Check for essential top endpoints fields
                        essential_fields = ["timeframe", "limit", "endpoints", "total_requests"]
                        if all(field in endpoint_data for field in essential_fields):
                            test_name = f"Top Endpoints (limit={case['limit']}, {case['timeframe']})"
                            self.log_test(test_name, True, data)
                        else:
                            self.log_test("Top Endpoints", False, error="Missing essential endpoint fields")
                            return False
                    else:
                        self.log_test("Top Endpoints", False, error="Invalid response structure")
                        return False
                else:
                    self.log_test("Top Endpoints", False, error=f"Status: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("Top Endpoints", False, error=str(e))
            return False
    
    def test_performance_metrics(self) -> bool:
        """Test GET /rate-limits/performance - Get performance metrics"""
        try:
            timeframes = ["1h", "24h", "7d"]
            
            for timeframe in timeframes:
                response = self.session.get(
                    f"{self.base_url}/api/rate-limits/performance",
                    params={"timeframe": timeframe}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and "data" in data:
                        perf_data = data["data"]
                        
                        # Check for essential performance fields
                        essential_fields = ["timeframe", "response_time", "throughput", "error_rates"]
                        if all(field in perf_data for field in essential_fields):
                            self.log_test(f"Performance Metrics ({timeframe})", True, data)
                        else:
                            self.log_test("Performance Metrics", False, error="Missing essential performance fields")
                            return False
                    else:
                        self.log_test("Performance Metrics", False, error="Invalid response structure")
                        return False
                else:
                    self.log_test("Performance Metrics", False, error=f"Status: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("Performance Metrics", False, error=str(e))
            return False
    
    def test_optimization_suggestions(self) -> bool:
        """Test GET /rate-limits/optimization - Get optimization suggestions"""
        try:
            response = self.session.get(f"{self.base_url}/api/rate-limits/optimization")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    opt_data = data["data"]
                    
                    # Check for essential optimization fields
                    essential_fields = ["suggestions", "total_potential_savings"]
                    if all(field in opt_data for field in essential_fields):
                        self.log_test("Optimization Suggestions", True, data)
                        return True
                    else:
                        self.log_test("Optimization Suggestions", False, error="Missing essential optimization fields")
                        return False
                else:
                    self.log_test("Optimization Suggestions", False, error="Invalid response structure")
                    return False
            else:
                self.log_test("Optimization Suggestions", False, error=f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Optimization Suggestions", False, error=str(e))
            return False
    
    def test_system_health(self) -> bool:
        """Test GET /rate-limits/health - Get system health"""
        try:
            response = self.session.get(f"{self.base_url}/api/rate-limits/health")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "data" in data:
                    health_data = data["data"]
                    
                    # Check for essential health fields
                    essential_fields = ["status", "uptime", "response_time", "components"]
                    if all(field in health_data for field in essential_fields):
                        self.log_test("System Health", True, data)
                        return True
                    else:
                        self.log_test("System Health", False, error="Missing essential health fields")
                        return False
                else:
                    self.log_test("System Health", False, error="Invalid response structure")
                    return False
            else:
                self.log_test("System Health", False, error=f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("System Health", False, error=str(e))
            return False
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive rate limiting system test"""
        print("🌊 STARTING COMPREHENSIVE RATE LIMITING & THROTTLING SYSTEM TEST")
        print("=" * 80)
        
        # Authentication
        print("\n📋 AUTHENTICATION TEST")
        auth_success = self.authenticate("tmonnens@outlook.com", "Voetballen5")
        
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with tests")
            return self.generate_summary()
        
        # Core Rate Limiting Tests
        print("\n📋 CORE RATE LIMITING TESTS")
        tests = [
            ("Rate Limit Status", self.test_rate_limit_status),
            ("Rate Limit Metrics", self.test_rate_limit_metrics),
            ("API Usage Statistics", self.test_api_usage_statistics),
            ("Rate Limit Check", self.test_rate_limit_check),
            ("User Quotas", self.test_user_quotas),
            ("Rate Limit Alerts", self.test_rate_limit_alerts),
            ("Top Endpoints", self.test_top_endpoints),
            ("Performance Metrics", self.test_performance_metrics),
            ("Optimization Suggestions", self.test_optimization_suggestions),
            ("System Health", self.test_system_health)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            test_func()
            time.sleep(0.1)  # Small delay between tests
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate total response data processed
        total_data_processed = sum(result["response_size"] for result in self.test_results if result["success"])
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": round(success_rate, 1),
            "total_data_processed": total_data_processed,
            "test_results": self.test_results
        }
        
        print("\n" + "=" * 80)
        print("🌊 RATE LIMITING & THROTTLING SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate}%")
        print(f"📦 Total Data Processed: {total_data_processed:,} characters")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['error']}")
        
        return summary

def main():
    """Main test execution"""
    # Get backend URL from environment
    backend_url = "https://d70b9379-58ef-4e6d-9a10-f0eebb21d382.preview.emergentagent.com"
    
    print(f"🌊 RATE LIMITING & THROTTLING SYSTEM BACKEND TEST")
    print(f"🔗 Backend URL: {backend_url}")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize tester
    tester = RateLimitingSystemTester(backend_url)
    
    # Run comprehensive test
    summary = tester.run_comprehensive_test()
    
    # Final status
    if summary["success_rate"] >= 90:
        print(f"\n🎉 RATE LIMITING SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print(f"✅ {summary['passed']}/{summary['total_tests']} tests passed ({summary['success_rate']}%)")
    else:
        print(f"\n⚠️ RATE LIMITING SYSTEM TEST COMPLETED WITH ISSUES")
        print(f"❌ {summary['failed']}/{summary['total_tests']} tests failed")
    
    return summary

if __name__ == "__main__":
    main()