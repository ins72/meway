#!/usr/bin/env python3
"""
FOCUSED PLAN CHANGE IMPACT ANALYSIS SYSTEM TEST
===============================================
Testing the 5 previously failing endpoints with detailed error analysis:
1. POST /api/plan-change-impact/analyze-feature-change (400 error)
2. POST /api/plan-change-impact/analyze-plan-disable (400 error)  
3. POST /api/plan-change-impact/simulate-change (500 error)
4. POST /api/plan-change-impact/execute-migration-plan/{migration_id} (400 error)
5. POST /api/plan-change-impact/rollback-plan-change (400 error)

Also testing the working endpoints to ensure they still function.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://eff6f53c-47df-43a1-9962-4d20b26f6dc5.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class PlanChangeImpactTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        
    def authenticate(self):
        """Authenticate and get token"""
        try:
            login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def log_result(self, endpoint: str, method: str, success: bool, status_code: int, details: str, response_data: dict = None):
        """Log detailed test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "success": success,
            "status_code": status_code,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {method} {endpoint} - Status {status_code} - {details}")
        
        if not success and response_data:
            print(f"   Error details: {json.dumps(response_data, indent=2)}")
    
    def test_working_endpoints(self):
        """Test the endpoints that should be working"""
        print(f"\n🟢 TESTING WORKING ENDPOINTS")
        print("=" * 50)
        
        # 1. Health Check
        try:
            response = requests.get(f"{self.base_url}/api/plan-change-impact/health", timeout=30)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else {}
            details = f"Service healthy: {data.get('healthy', False)}" if success else "Health check failed"
            self.log_result("/api/plan-change-impact/health", "GET", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/health", "GET", False, 0, str(e))
        
        # 2. Analyze Pricing Change
        try:
            test_data = {
                "plan_name": "creator",
                "pricing_changes": {
                    "monthly_price": 39.99,
                    "yearly_price": 399.99
                }
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/analyze-pricing-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Pricing analysis: {data.get('impact_summary', {}).get('affected_subscriptions', 0)} subscriptions" if success else "Pricing analysis failed"
            self.log_result("/api/plan-change-impact/analyze-pricing-change", "POST", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/analyze-pricing-change", "POST", False, 0, str(e))
        
        # 3. Analyze Limit Change
        try:
            test_data = {
                "plan_name": "creator",
                "limit_changes": {
                    "ai_content_generation": 2000,
                    "instagram_searches": 1000
                }
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/analyze-limit-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Limit analysis: {data.get('impact_summary', {}).get('affected_subscriptions', 0)} subscriptions" if success else "Limit analysis failed"
            self.log_result("/api/plan-change-impact/analyze-limit-change", "POST", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/analyze-limit-change", "POST", False, 0, str(e))
        
        # 4. Get Affected Subscriptions
        try:
            response = requests.get(f"{self.base_url}/api/plan-change-impact/affected-subscriptions/creator?change_type=pricing&limit=50", headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Affected subscriptions: {data.get('total_affected', 0)} found" if success else "Failed to get affected subscriptions"
            self.log_result("/api/plan-change-impact/affected-subscriptions/creator", "GET", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/affected-subscriptions/creator", "GET", False, 0, str(e))
        
        # 5. Create Migration Plan
        try:
            test_data = {
                "source_plan": "education",
                "target_plan": "business",
                "migration_strategy": "gradual"
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/create-migration-plan", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Migration plan created: {data.get('migration_plan', {}).get('_id', 'Unknown ID')}" if success else "Failed to create migration plan"
            self.log_result("/api/plan-change-impact/create-migration-plan", "POST", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/create-migration-plan", "POST", False, 0, str(e))
        
        # 6. Get Impact History
        try:
            response = requests.get(f"{self.base_url}/api/plan-change-impact/impact-history?plan_name=creator&days_back=30&limit=20", headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Impact history: {len(data.get('impact_history', []))} records" if success else "Failed to get impact history"
            self.log_result("/api/plan-change-impact/impact-history", "GET", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/impact-history", "GET", False, 0, str(e))
        
        # 7. Get Risk Assessment
        try:
            response = requests.get(f"{self.base_url}/api/plan-change-impact/risk-assessment/creator?change_type=pricing", headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Risk assessment: {data.get('risk_assessment', {}).get('current_risk', {}).get('level', 'Unknown')} risk" if success else "Failed to get risk assessment"
            self.log_result("/api/plan-change-impact/risk-assessment/creator", "GET", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/risk-assessment/creator", "GET", False, 0, str(e))
    
    def test_failing_endpoints(self):
        """Test the 5 previously failing endpoints with detailed error analysis"""
        print(f"\n🔴 TESTING PREVIOUSLY FAILING ENDPOINTS")
        print("=" * 50)
        
        # 1. Analyze Feature Change (400 error)
        try:
            test_data = {
                "plan_name": "business",
                "feature_changes": {
                    "features_added": ["advanced_analytics", "priority_support"],
                    "features_removed": ["basic_reporting"]
                }
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/analyze-feature-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Feature analysis: {data.get('impact_summary', {}).get('features_added', 0)} added, {data.get('impact_summary', {}).get('features_removed', 0)} removed" if success else f"Feature analysis failed: {data.get('error', 'Unknown error')}"
            self.log_result("/api/plan-change-impact/analyze-feature-change", "POST", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/analyze-feature-change", "POST", False, 0, str(e))
        
        # 2. Analyze Plan Disable (400 error)
        try:
            test_data = {
                "plan_name": "education",
                "disable_date": "2025-08-01T00:00:00Z",
                "sunset_date": "2025-09-01T00:00:00Z"
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/analyze-plan-disable", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Plan disable analysis: {data.get('impact_summary', {}).get('affected_subscriptions', 0)} subscriptions affected" if success else f"Plan disable analysis failed: {data.get('error', 'Unknown error')}"
            self.log_result("/api/plan-change-impact/analyze-plan-disable", "POST", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/analyze-plan-disable", "POST", False, 0, str(e))
        
        # 3. Simulate Change (500 error)
        try:
            test_data = {
                "plan_name": "creator",
                "changes": {
                    "pricing": {"monthly_price": 34.99},
                    "features": {"features_added": ["advanced_templates"]},
                    "limits": {"ai_content_generation": 1500}
                }
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/simulate-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Plan simulation: {data.get('simulation', {}).get('overall_risk', 'Unknown')} risk level" if success else f"Plan simulation failed: {data.get('error', 'Unknown error')}"
            self.log_result("/api/plan-change-impact/simulate-change", "POST", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/simulate-change", "POST", False, 0, str(e))
        
        # 4. Execute Migration Plan (400 error)
        try:
            test_migration_id = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID format
            test_data = {
                "dry_run": True,
                "batch_size": 10
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/execute-migration-plan/{test_migration_id}", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Migration execution: {data.get('execution_record', {}).get('status', 'Unknown')}" if success else f"Migration execution failed: {data.get('error', 'Unknown error')}"
            self.log_result(f"/api/plan-change-impact/execute-migration-plan/{test_migration_id}", "POST", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result(f"/api/plan-change-impact/execute-migration-plan/{test_migration_id}", "POST", False, 0, str(e))
        
        # 5. Rollback Plan Change (400 error)
        try:
            test_data = {
                "plan_name": "creator",
                "rollback_to_version": "1.0",
                "reason": "Test rollback functionality"
            }
            response = requests.post(f"{self.base_url}/api/plan-change-impact/rollback-plan-change", json=test_data, headers=self.headers, timeout=30)
            success = response.status_code == 200
            data = response.json()
            details = f"Plan rollback: {data.get('rollback_record', {}).get('status', 'Unknown')}" if success else f"Plan rollback failed: {data.get('error', 'Unknown error')}"
            self.log_result("/api/plan-change-impact/rollback-plan-change", "POST", success, response.status_code, details, data if not success else None)
        except Exception as e:
            self.log_result("/api/plan-change-impact/rollback-plan-change", "POST", False, 0, str(e))
    
    def run_comprehensive_test(self):
        """Run comprehensive test of Plan Change Impact Analysis System"""
        print(f"🚀 PLAN CHANGE IMPACT ANALYSIS SYSTEM - FOCUSED TEST")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        
        # Authenticate
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test working endpoints
        self.test_working_endpoints()
        
        # Test failing endpoints
        self.test_failing_endpoints()
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 PLAN CHANGE IMPACT ANALYSIS SYSTEM TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        working_endpoints = [r for r in self.test_results if r["success"]]
        failing_endpoints = [r for r in self.test_results if not r["success"]]
        
        if working_endpoints:
            print(f"\n✅ WORKING ENDPOINTS ({len(working_endpoints)}):")
            for result in working_endpoints:
                print(f"   • {result['method']} {result['endpoint']} - {result['details']}")
        
        if failing_endpoints:
            print(f"\n❌ FAILING ENDPOINTS ({len(failing_endpoints)}):")
            for result in failing_endpoints:
                print(f"   • {result['method']} {result['endpoint']} - {result['details']}")
                if result.get('response_data'):
                    error_msg = result['response_data'].get('error', 'No error message')
                    print(f"     Error: {error_msg}")
        
        # Save detailed results
        with open('/app/plan_change_impact_test_results.json', 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate
                },
                "test_results": self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: /app/plan_change_impact_test_results.json")
        
        return success_rate >= 70

def main():
    tester = PlanChangeImpactTester()
    success = tester.run_comprehensive_test()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()