#!/usr/bin/env python3
"""
Comprehensive Backup & Disaster Recovery System Test
Tests all 11 endpoints of the NINETEENTH WAVE backup system
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
LOGIN_EMAIL = "tmonnens@outlook.com"
LOGIN_PASSWORD = "Voetballen5"

class BackupSystemTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
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
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print(f"✅ Authentication successful - Token obtained")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, method, endpoint, data=None, description=""):
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}/api/backup{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, data=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == 200
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status_code": response.status_code,
                "success": success,
                "response_size": len(response.text),
                "timestamp": datetime.now().isoformat()
            }
            
            if success:
                try:
                    json_data = response.json()
                    result["has_data"] = "data" in json_data
                    result["data_keys"] = list(json_data.get("data", {}).keys()) if isinstance(json_data.get("data"), dict) else []
                except:
                    result["has_data"] = False
                    result["data_keys"] = []
                
                print(f"✅ {method} {endpoint} - {description} ({response.status_code}) - {len(response.text)} chars")
            else:
                print(f"❌ {method} {endpoint} - {description} ({response.status_code}) - {response.text[:200]}")
            
            self.test_results.append(result)
            return success, response
            
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {str(e)}")
            result = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return False, None
    
    def run_comprehensive_tests(self):
        """Run all backup system tests"""
        print("🌊 NINETEENTH WAVE - COMPREHENSIVE BACKUP & DISASTER RECOVERY SYSTEM TESTING")
        print("=" * 80)
        
        if not self.authenticate():
            return False
        
        print("\n📋 Testing Backup System Endpoints:")
        print("-" * 50)
        
        # Test 1: Comprehensive Backup Status
        self.test_endpoint(
            "GET", "/comprehensive-status",
            description="Complete backup system status with disaster recovery info"
        )
        
        # Test 2: Disaster Recovery Initiation
        dr_data = {
            "scenario": "data_corruption",
            "target_location": "secondary_datacenter",
            "recovery_point": "2025-01-15T10:00:00Z",
            "notify_stakeholders": True
        }
        self.test_endpoint(
            "POST", "/initiate-disaster-recovery",
            data=dr_data,
            description="Initiate disaster recovery procedure"
        )
        
        # Test 3: Backup History (default 30 days)
        self.test_endpoint(
            "GET", "/history",
            description="Backup history for default 30 days"
        )
        
        # Test 4: Backup History (7 days)
        self.test_endpoint(
            "GET", "/history?days=7",
            description="Backup history for 7 days"
        )
        
        # Test 5: Backup History (90 days)
        self.test_endpoint(
            "GET", "/history?days=90",
            description="Backup history for 90 days"
        )
        
        # Test 6: Manual Backup Creation (Full)
        full_backup_data = {
            "backup_type": "full",
            "description": "Manual full backup for testing",
            "include_databases": True,
            "include_files": True,
            "storage_location": "primary_s3"
        }
        self.test_endpoint(
            "POST", "/create-manual-backup",
            data=full_backup_data,
            description="Create manual full backup"
        )
        
        # Test 7: Manual Backup Creation (Incremental)
        incremental_backup_data = {
            "backup_type": "incremental",
            "description": "Manual incremental backup for testing",
            "include_databases": True,
            "include_files": False,
            "storage_location": "secondary_azure"
        }
        self.test_endpoint(
            "POST", "/create-manual-backup",
            data=incremental_backup_data,
            description="Create manual incremental backup"
        )
        
        # Test 8: Recovery Options
        self.test_endpoint(
            "GET", "/recovery-options",
            description="Available recovery options and restore points"
        )
        
        # Test 9: Storage Analytics
        self.test_endpoint(
            "GET", "/storage-analytics",
            description="Storage utilization and analytics"
        )
        
        # Test 10: System Health
        self.test_endpoint(
            "GET", "/system-health",
            description="Backup system health status"
        )
        
        # Test 11: Schedule Information
        self.test_endpoint(
            "GET", "/schedule-info",
            description="Backup schedule information"
        )
        
        # Test 12: Recovery Testing (Full System)
        recovery_test_data = {
            "recovery_type": "full_system_restore",
            "test_location": "secondary_datacenter"
        }
        self.test_endpoint(
            "POST", "/test-recovery",
            data=recovery_test_data,
            description="Test disaster recovery - full system restore"
        )
        
        # Test 13: Recovery Testing (Selective)
        selective_test_data = {
            "recovery_type": "selective_restore",
            "test_location": "cloud_failover"
        }
        self.test_endpoint(
            "POST", "/test-recovery",
            data=selective_test_data,
            description="Test disaster recovery - selective restore"
        )
        
        # Test 14: Compliance Report
        self.test_endpoint(
            "GET", "/compliance-report",
            description="Backup compliance and audit report"
        )
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🌊 NINETEENTH WAVE BACKUP SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - successful_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['method']} {result['endpoint']} - {result['description']}")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            size_info = f"({result.get('response_size', 0)} chars)" if result["success"] else ""
            print(f"   {status} {result['method']} {result['endpoint']} - {result['description']} {size_info}")
        
        # Calculate total data processed
        total_data = sum(r.get("response_size", 0) for r in self.test_results if r["success"])
        print(f"\n📊 Total Data Processed: {total_data:,} bytes")
        
        return successful_tests, total_tests

def main():
    """Main test execution"""
    print("🚀 Starting Comprehensive Backup & Disaster Recovery System Tests")
    print(f"🌐 Backend URL: {BASE_URL}")
    print(f"👤 Test User: {LOGIN_EMAIL}")
    print(f"⏰ Test Time: {datetime.now().isoformat()}")
    
    tester = BackupSystemTester()
    
    if tester.run_comprehensive_tests():
        successful, total = tester.print_summary()
        
        if successful == total:
            print(f"\n🎉 ALL TESTS PASSED! Backup system is fully operational.")
            sys.exit(0)
        else:
            print(f"\n⚠️  {total - successful} tests failed. Check the details above.")
            sys.exit(1)
    else:
        print(f"\n💥 Test execution failed. Check authentication and connectivity.")
        sys.exit(1)

if __name__ == "__main__":
    main()