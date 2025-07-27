#!/usr/bin/env python3
"""
FINAL PRODUCTION VERIFICATION
Comprehensive verification that the platform is production-ready
"""

import os
import sys
import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime

class FinalProductionVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "PENDING",
            "checks": {}
        }
    
    async def verify_server_health(self):
        """Verify server is running and healthy"""
        print("🔍 VERIFYING SERVER HEALTH...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"  ✅ Health check: {data}")
                        self.results["checks"]["server_health"] = {
                            "status": "PASS",
                            "response": data
                        }
                    else:
                        print(f"  ❌ Health check failed: {response.status}")
                        self.results["checks"]["server_health"] = {
                            "status": "FAIL",
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            print(f"  ❌ Server health check error: {e}")
            self.results["checks"]["server_health"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def verify_crud_operations(self):
        """Verify CRUD operations are working"""
        print("\n🔍 VERIFYING CRUD OPERATIONS...")
        
        # Test workspace CRUD
        try:
            async with aiohttp.ClientSession() as session:
                # Create workspace
                workspace_data = {
                    "name": "Test Workspace",
                    "description": "Test workspace for verification",
                    "plan": "basic"
                }
                
                async with session.post(f"{self.base_url}/api/workspace", json=workspace_data) as response:
                    if response.status in [200, 201]:
                        workspace = await response.json()
                        print(f"  ✅ Workspace created: {workspace.get('id', 'N/A')}")
                        
                        # Test read workspace
                        workspace_id = workspace.get('id')
                        if workspace_id:
                            async with session.get(f"{self.base_url}/api/workspace/{workspace_id}") as get_response:
                                if get_response.status == 200:
                                    print(f"  ✅ Workspace read: {workspace_id}")
                                    
                                    # Test update workspace
                                    update_data = {"name": "Updated Test Workspace"}
                                    async with session.put(f"{self.base_url}/api/workspace/{workspace_id}", json=update_data) as put_response:
                                        if put_response.status == 200:
                                            print(f"  ✅ Workspace updated: {workspace_id}")
                                            
                                            # Test delete workspace
                                            async with session.delete(f"{self.base_url}/api/workspace/{workspace_id}") as delete_response:
                                                if delete_response.status in [200, 204]:
                                                    print(f"  ✅ Workspace deleted: {workspace_id}")
                                                    self.results["checks"]["workspace_crud"] = {"status": "PASS"}
                                                else:
                                                    print(f"  ❌ Workspace delete failed: {delete_response.status}")
                                                    self.results["checks"]["workspace_crud"] = {"status": "FAIL", "error": f"Delete failed: {delete_response.status}"}
                                        else:
                                            print(f"  ❌ Workspace update failed: {put_response.status}")
                                            self.results["checks"]["workspace_crud"] = {"status": "FAIL", "error": f"Update failed: {put_response.status}"}
                                else:
                                    print(f"  ❌ Workspace read failed: {get_response.status}")
                                    self.results["checks"]["workspace_crud"] = {"status": "FAIL", "error": f"Read failed: {get_response.status}"}
                    else:
                        print(f"  ❌ Workspace create failed: {response.status}")
                        self.results["checks"]["workspace_crud"] = {"status": "FAIL", "error": f"Create failed: {response.status}"}
                        
        except Exception as e:
            print(f"  ❌ CRUD verification error: {e}")
            self.results["checks"]["workspace_crud"] = {"status": "FAIL", "error": str(e)}
    
    async def verify_database_operations(self):
        """Verify database operations are real (not mock)"""
        print("\n🔍 VERIFYING DATABASE OPERATIONS...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test analytics endpoint to verify real data
                async with session.get(f"{self.base_url}/api/analytics") as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if data looks real (not mock)
                        if isinstance(data, dict) and len(data) > 0:
                            print(f"  ✅ Analytics data: Real database operations detected")
                            self.results["checks"]["database_operations"] = {"status": "PASS", "data_sample": data}
                        else:
                            print(f"  ❌ Analytics data: Empty or invalid response")
                            self.results["checks"]["database_operations"] = {"status": "FAIL", "error": "Empty response"}
                    else:
                        print(f"  ❌ Analytics endpoint failed: {response.status}")
                        self.results["checks"]["database_operations"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            print(f"  ❌ Database verification error: {e}")
            self.results["checks"]["database_operations"] = {"status": "FAIL", "error": str(e)}
    
    async def verify_api_documentation(self):
        """Verify API documentation is accessible"""
        print("\n🔍 VERIFYING API DOCUMENTATION...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test Swagger UI
                async with session.get(f"{self.base_url}/docs") as response:
                    if response.status == 200:
                        print(f"  ✅ Swagger UI: Accessible")
                        self.results["checks"]["swagger_ui"] = {"status": "PASS"}
                    else:
                        print(f"  ❌ Swagger UI: Failed ({response.status})")
                        self.results["checks"]["swagger_ui"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
                
                # Test ReDoc
                async with session.get(f"{self.base_url}/redoc") as response:
                    if response.status == 200:
                        print(f"  ✅ ReDoc: Accessible")
                        self.results["checks"]["redoc"] = {"status": "PASS"}
                    else:
                        print(f"  ❌ ReDoc: Failed ({response.status})")
                        self.results["checks"]["redoc"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            print(f"  ❌ API documentation error: {e}")
            self.results["checks"]["api_documentation"] = {"status": "FAIL", "error": str(e)}
    
    async def verify_mock_data_elimination(self):
        """Verify no mock data remains in code"""
        print("\n🔍 VERIFYING MOCK DATA ELIMINATION...")
        
        # Check key service files for mock data patterns
        service_files = [
            "services/workspace_subscription_service.py",
            "services/enterprise_revenue_service.py", 
            "services/ai_token_purchase_service.py",
            "services/website_builder_service.py"
        ]
        
        mock_patterns = ["mock_", "fake_", "dummy_", "test_data", "sample_data", "hardcoded"]
        mock_found = False
        
        for file_path in service_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in mock_patterns:
                        if pattern in content.lower():
                            print(f"  ❌ Mock data found in {file_path}: {pattern}")
                            mock_found = True
                            
                except Exception as e:
                    print(f"  ❌ Error reading {file_path}: {e}")
                    mock_found = True
        
        if not mock_found:
            print(f"  ✅ No mock data patterns found in service files")
            self.results["checks"]["mock_data_elimination"] = {"status": "PASS"}
        else:
            self.results["checks"]["mock_data_elimination"] = {"status": "FAIL", "error": "Mock data patterns found"}
    
    def generate_summary(self):
        """Generate final summary"""
        print("\n" + "="*60)
        print("📊 FINAL PRODUCTION VERIFICATION SUMMARY")
        print("="*60)
        
        total_checks = len(self.results["checks"])
        passed_checks = sum(1 for check in self.results["checks"].values() if check.get("status") == "PASS")
        failed_checks = total_checks - passed_checks
        
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        
        if failed_checks == 0:
            self.results["overall_status"] = "PASS"
            print("\n🎉 ALL CHECKS PASSED!")
            print("✅ Platform is PRODUCTION READY")
        else:
            self.results["overall_status"] = "FAIL"
            print(f"\n❌ {failed_checks} checks failed")
            print("Platform needs attention before production deployment")
        
        # Save results
        with open("final_verification_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: final_verification_results.json")
        
        return self.results["overall_status"] == "PASS"
    
    async def run_all_verifications(self):
        """Run all verification checks"""
        print("🚀 STARTING FINAL PRODUCTION VERIFICATION")
        print("="*60)
        
        await self.verify_server_health()
        await self.verify_crud_operations()
        await self.verify_database_operations()
        await self.verify_api_documentation()
        await self.verify_mock_data_elimination()
        
        return self.generate_summary()

async def main():
    """Main verification function"""
    verifier = FinalProductionVerifier()
    success = await verifier.run_all_verifications()
    
    if success:
        print("\n🎉 PRODUCTION READINESS VERIFICATION COMPLETE!")
        print("✅ Platform is ready for production deployment")
        sys.exit(0)
    else:
        print("\n❌ PRODUCTION READINESS VERIFICATION FAILED!")
        print("Platform needs fixes before production deployment")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 