#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for Mewayz Platform
Focus: Advanced Monitoring & Observability System (Eighteenth Wave)
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com/api"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class MonitoringSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, response_data=None, error=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response_size": len(str(response_data)) if response_data else 0,
            "error": str(error) if error else None
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")
        if response_data and success:
            print(f"   Response size: {result['response_size']} chars")
    
    def authenticate(self):
        """Authenticate with the backend"""
        try:
            auth_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
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
    
    def test_system_health(self):
        """Test GET /api/monitoring/system-health"""
        try:
            response = self.session.get(f"{BACKEND_URL}/monitoring/system-health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("System Health Monitoring", True, data)
                return True
            else:
                self.log_test("System Health Monitoring", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("System Health Monitoring", False, error=str(e))
            return False
    
    def test_real_time_metrics(self):
        """Test GET /api/monitoring/real-time-metrics"""
        try:
            response = self.session.get(f"{BACKEND_URL}/monitoring/real-time-metrics")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Real-time Metrics", True, data)
                return True
            else:
                self.log_test("Real-time Metrics", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Real-time Metrics", False, error=str(e))
            return False
    
    def test_performance_analytics(self):
        """Test GET /api/monitoring/performance-analytics with different timeframes"""
        timeframes = ["1h", "24h", "7d", "30d"]
        success_count = 0
        
        for timeframe in timeframes:
            try:
                response = self.session.get(f"{BACKEND_URL}/monitoring/performance-analytics?timeframe={timeframe}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Performance Analytics ({timeframe})", True, data)
                    success_count += 1
                else:
                    self.log_test(f"Performance Analytics ({timeframe})", False, error=f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Performance Analytics ({timeframe})", False, error=str(e))
        
        return success_count == len(timeframes)
    
    def test_alerting_rules(self):
        """Test GET /api/monitoring/alerting-rules"""
        try:
            response = self.session.get(f"{BACKEND_URL}/monitoring/alerting-rules")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Alerting Rules", True, data)
                return True
            else:
                self.log_test("Alerting Rules", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Alerting Rules", False, error=str(e))
            return False
    
    def test_service_status(self):
        """Test GET /api/monitoring/service-status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/monitoring/service-status")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Service Status", True, data)
                return True
            else:
                self.log_test("Service Status", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Service Status", False, error=str(e))
            return False
    
    def test_uptime_stats(self):
        """Test GET /api/monitoring/uptime-stats with various day parameters"""
        day_params = [7, 30, 90]
        success_count = 0
        
        for days in day_params:
            try:
                response = self.session.get(f"{BACKEND_URL}/monitoring/uptime-stats?days={days}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Uptime Statistics ({days} days)", True, data)
                    success_count += 1
                else:
                    self.log_test(f"Uptime Statistics ({days} days)", False, error=f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Uptime Statistics ({days} days)", False, error=str(e))
        
        return success_count == len(day_params)
    
    def test_resource_utilization(self):
        """Test GET /api/monitoring/resource-utilization"""
        try:
            response = self.session.get(f"{BACKEND_URL}/monitoring/resource-utilization")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Resource Utilization", True, data)
                return True
            else:
                self.log_test("Resource Utilization", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Resource Utilization", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all monitoring system tests"""
        print("🌊 EIGHTEENTH WAVE - ADVANCED MONITORING & OBSERVABILITY SYSTEM TESTING")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n📊 TESTING MONITORING SYSTEM ENDPOINTS:")
        print("-" * 50)
        
        # Test all monitoring endpoints
        tests = [
            self.test_system_health,
            self.test_real_time_metrics,
            self.test_performance_analytics,
            self.test_alerting_rules,
            self.test_service_status,
            self.test_uptime_stats,
            self.test_resource_utilization
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("🌊 EIGHTEENTH WAVE MONITORING SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ALL MONITORING SYSTEM TESTS PASSED!")
            print("✅ Advanced Monitoring & Observability System is fully operational")
        elif success_rate >= 80:
            print("⚠️  Most tests passed with some issues")
        else:
            print("❌ Multiple test failures detected")
        
        # Print detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        print("-" * 50)
        
        total_response_size = 0
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["response_size"]:
                print(f"   📊 Response: {result['response_size']} chars")
                total_response_size += result["response_size"]
            if result["error"]:
                print(f"   ❌ Error: {result['error']}")
        
        print(f"\n📊 Total Data Processed: {total_response_size:,} bytes")
        print(f"⏱️  Test Duration: {datetime.now().isoformat()}")
        
        return success_rate == 100

def main():
    """Main test execution"""
    print("🚀 Starting Advanced Monitoring & Observability System Tests...")
    
    tester = MonitoringSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 CONCLUSION: EIGHTEENTH WAVE MONITORING SYSTEM FULLY OPERATIONAL")
        sys.exit(0)
    else:
        print("\n⚠️  CONCLUSION: SOME MONITORING SYSTEM ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()