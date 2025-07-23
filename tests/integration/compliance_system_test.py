#!/usr/bin/env python3
"""
Advanced Compliance & Audit System Testing
TWENTIETH WAVE MIGRATION - Final System Testing
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
LOGIN_EMAIL = "tmonnens@outlook.com"
LOGIN_PASSWORD = "Voetballen5"

class ComplianceSystemTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.session = requests.Session()
        self.test_results = []
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            print("🔐 Authenticating admin user...")
            
            # Login with form data
            login_data = {
                "username": LOGIN_EMAIL,
                "password": LOGIN_PASSWORD
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    print(f"✅ Authentication successful - Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"❌ No access token in response: {result}")
                    return False
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, method, endpoint, data=None, params=None, description=""):
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}/api/compliance{endpoint}"
            print(f"\n🧪 Testing {method} {endpoint} - {description}")
            
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                if data:
                    response = self.session.post(url, data=data)
                else:
                    response = self.session.post(url, json=data)
            else:
                print(f"❌ Unsupported method: {method}")
                return False
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    data_size = len(json.dumps(result))
                    print(f"✅ SUCCESS - Response size: {data_size} chars")
                    
                    # Log key information
                    if "data" in result:
                        data_content = result["data"]
                        if isinstance(data_content, dict):
                            print(f"📋 Data keys: {list(data_content.keys())}")
                        elif isinstance(data_content, list):
                            print(f"📋 Data items: {len(data_content)}")
                    
                    self.test_results.append({
                        "endpoint": endpoint,
                        "method": method,
                        "status": "SUCCESS",
                        "response_size": data_size,
                        "description": description
                    })
                    return True
                    
                except json.JSONDecodeError:
                    print(f"✅ SUCCESS - Non-JSON response: {response.text[:200]}")
                    self.test_results.append({
                        "endpoint": endpoint,
                        "method": method,
                        "status": "SUCCESS",
                        "response_size": len(response.text),
                        "description": description
                    })
                    return True
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"📄 Response: {response.text[:500]}")
                self.test_results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "status": "FAILED",
                    "error": f"Status {response.status_code}: {response.text[:200]}",
                    "description": description
                })
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.test_results.append({
                "endpoint": endpoint,
                "method": method,
                "status": "ERROR",
                "error": str(e),
                "description": description
            })
            return False
    
    def run_compliance_tests(self):
        """Run comprehensive compliance system tests"""
        print("🌊 TWENTIETH WAVE - ADVANCED COMPLIANCE & AUDIT SYSTEM TESTING")
        print("=" * 80)
        
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        print(f"\n🎯 Testing Advanced Compliance & Audit System endpoints...")
        
        # Test 1: Framework Status
        self.test_endpoint(
            "GET", "/framework-status",
            description="Comprehensive compliance framework status"
        )
        
        # Test 2: Audit Logs (default)
        self.test_endpoint(
            "GET", "/audit-logs",
            description="Default audit logs (100 entries)"
        )
        
        # Test 3: Audit Logs with filters
        self.test_endpoint(
            "GET", "/audit-logs",
            params={"event_type": "security", "limit": 50},
            description="Security audit logs (50 entries)"
        )
        
        # Test 4: Audit Logs with date range
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        self.test_endpoint(
            "GET", "/audit-logs",
            params={"start_date": start_date, "end_date": end_date, "limit": 25},
            description="Audit logs for last 7 days (25 entries)"
        )
        
        # Test 5: Create Compliance Report - GDPR
        self.test_endpoint(
            "POST", "/create-report",
            data={"framework": "gdpr", "report_type": "summary"},
            description="GDPR compliance report creation (summary)"
        )
        
        # Test 6: Create Compliance Report - SOC2
        self.test_endpoint(
            "POST", "/create-report",
            data={"framework": "soc2", "report_type": "detailed"},
            description="SOC2 compliance report creation (detailed)"
        )
        
        # Test 7: Create Compliance Report - All frameworks
        self.test_endpoint(
            "POST", "/create-report",
            data={"framework": "all", "report_type": "executive"},
            description="All frameworks compliance report (executive)"
        )
        
        # Test 8: Policy Management
        self.test_endpoint(
            "GET", "/policy-management",
            description="Policy management information"
        )
        
        # Test 9: Risk Register
        self.test_endpoint(
            "GET", "/risk-register",
            description="Comprehensive risk register"
        )
        
        # Test 10: Compliance Dashboard
        self.test_endpoint(
            "GET", "/compliance-dashboard",
            description="Comprehensive compliance dashboard data"
        )
        
        # Test 11: Framework Details - GDPR
        self.test_endpoint(
            "GET", "/framework/gdpr",
            description="GDPR framework details"
        )
        
        # Test 12: Framework Details - ISO27001
        self.test_endpoint(
            "GET", "/framework/iso27001",
            description="ISO27001 framework details"
        )
        
        # Test 13: Framework Details - HIPAA
        self.test_endpoint(
            "GET", "/framework/hipaa",
            description="HIPAA framework details"
        )
        
        # Test 14: Compliance Certificates
        self.test_endpoint(
            "GET", "/certificates",
            description="All compliance certificates"
        )
        
        # Test 15: Training Status
        self.test_endpoint(
            "GET", "/training-status",
            description="Compliance training status"
        )
        
        # Test 16: Initiate Audit - Internal GDPR
        self.test_endpoint(
            "POST", "/initiate-audit",
            data={"framework": "gdpr", "audit_type": "internal", "scope": "full"},
            description="Initiate internal GDPR audit (full scope)"
        )
        
        # Test 17: Initiate Audit - External SOC2
        self.test_endpoint(
            "POST", "/initiate-audit",
            data={"framework": "soc2", "audit_type": "external", "scope": "partial"},
            description="Initiate external SOC2 audit (partial scope)"
        )
        
        # Test 18: Initiate Audit - Certification ISO27001
        self.test_endpoint(
            "POST", "/initiate-audit",
            data={"framework": "iso27001", "audit_type": "certification", "scope": "focused"},
            description="Initiate ISO27001 certification audit (focused scope)"
        )
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🌊 TWENTIETH WAVE COMPLIANCE SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["status"] == "SUCCESS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAILED"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print("\n🎉 ALL COMPLIANCE SYSTEM TESTS PASSED! 🎉")
            print("🌊 TWENTIETH WAVE MIGRATION - COMPLETE SUCCESS!")
        else:
            print(f"\n⚠️  {failed_tests + error_tests} tests need attention")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            print(f"{status_icon} {result['method']} {result['endpoint']} - {result['description']}")
            if result["status"] == "SUCCESS" and "response_size" in result:
                print(f"   📊 Response size: {result['response_size']} chars")
            elif result["status"] != "SUCCESS":
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        total_data = sum(r.get("response_size", 0) for r in self.test_results if r["status"] == "SUCCESS")
        print(f"\n📊 Total data processed: {total_data:,} bytes")
        
        return successful_tests == total_tests

def main():
    """Main test execution"""
    print("🌊 TWENTIETH WAVE - ADVANCED COMPLIANCE & AUDIT SYSTEM TESTING")
    print("🎯 Testing comprehensive compliance management and audit functionality")
    print("🔧 Backend URL:", BACKEND_URL)
    print("👤 Test User:", LOGIN_EMAIL)
    print("=" * 80)
    
    tester = ComplianceSystemTester()
    
    try:
        success = tester.run_compliance_tests()
        if success:
            tester.print_summary()
            return tester.print_summary()
        else:
            print("❌ Testing failed during execution")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)