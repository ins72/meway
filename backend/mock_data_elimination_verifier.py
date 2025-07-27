#!/usr/bin/env python3
"""
MOCK DATA ELIMINATION VERIFIER
Verifies that all mock data has been replaced with real database operations
"""

import os
import re
import asyncio
import aiohttp
from typing import List, Dict, Any
from datetime import datetime

class MockDataEliminationVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.mock_patterns = [
            r"mock_",
            r"fake_",
            r"dummy_",
            r"test_data",
            r"sample_data",
            r"hardcoded",
            r"hard-coded",
            r"Mock.*data",
            r"Fake.*data",
            r"Sample.*data",
            r"TODO.*mock",
            r"#.*mock",
            r"#.*fake",
            r"#.*dummy"
        ]
        
    async def verify_no_mock_data_in_code(self) -> Dict[str, Any]:
        """Verify no mock data patterns exist in code files"""
        print("🔍 VERIFYING NO MOCK DATA IN CODE FILES...")
        
        backend_files = []
        for root, dirs, files in os.walk("."):
            if "node_modules" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    backend_files.append(os.path.join(root, file))
        
        mock_data_found = []
        
        for file_path in backend_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in self.mock_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        mock_data_found.append({
                            "file": file_path,
                            "pattern": pattern,
                            "matches": len(matches)
                        })
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
        
        return {
            "success": len(mock_data_found) == 0,
            "files_checked": len(backend_files),
            "mock_data_found": mock_data_found
        }
    
    async def verify_database_operations(self) -> Dict[str, Any]:
        """Verify that endpoints return real database data"""
        print("🔍 VERIFYING DATABASE OPERATIONS...")
        
        test_endpoints = [
            ("/api/workspace", "GET", "Workspace listing"),
            ("/api/user", "GET", "User listing"),
            ("/api/blog", "GET", "Blog posts"),
            ("/api/workspace/subscription/usage", "GET", "Usage data"),
            ("/api/analytics/revenue", "GET", "Revenue analytics"),
            ("/api/ai-tokens/balance", "GET", "Token balance"),
            ("/api/notifications", "GET", "Notifications"),
            ("/api/campaigns", "GET", "Campaigns")
        ]
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for endpoint, method, description in test_endpoints:
                try:
                    if method == "GET":
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            data = await response.json()
                            
                            # Check if response contains real data indicators
                            is_real_data = self._check_real_data_indicators(data)
                            
                            results.append({
                                "endpoint": endpoint,
                                "description": description,
                                "status_code": response.status,
                                "is_real_data": is_real_data,
                                "success": response.status == 200 and is_real_data
                            })
                            
                            print(f"  ✅ {description}: {'Real data' if is_real_data else 'Mock data'}")
                            
                except Exception as e:
                    results.append({
                        "endpoint": endpoint,
                        "description": description,
                        "status_code": 0,
                        "is_real_data": False,
                        "success": False,
                        "error": str(e)
                    })
                    print(f"  ❌ {description}: Error - {e}")
        
        return {
            "success": all(r["success"] for r in results),
            "endpoints_tested": len(results),
            "results": results
        }
    
    def _check_real_data_indicators(self, data: Any) -> bool:
        """Check if data contains indicators of real database data"""
        if isinstance(data, dict):
            # Check for real data indicators
            real_indicators = [
                "id", "_id", "created_at", "updated_at", "workspace_id", "user_id",
                "status", "type", "amount", "count", "total"
            ]
            
            # Check if data has real structure
            has_real_structure = any(key in data for key in real_indicators)
            
            # Check for mock data indicators
            mock_indicators = [
                "mock", "fake", "dummy", "test", "sample", "example"
            ]
            
            has_mock_indicators = any(
                mock_indicator in str(data).lower() 
                for mock_indicator in mock_indicators
            )
            
            return has_real_structure and not has_mock_indicators
            
        elif isinstance(data, list):
            # Check if list contains real data
            if len(data) == 0:
                return True  # Empty list is fine
            
            # Check first item for real data indicators
            return self._check_real_data_indicators(data[0])
        
        return True
    
    async def verify_service_layer_operations(self) -> Dict[str, Any]:
        """Verify service layer uses real database operations"""
        print("🔍 VERIFYING SERVICE LAYER OPERATIONS...")
        
        service_files = [
            "services/workspace_service.py",
            "services/user_service.py", 
            "services/blog_service.py",
            "services/workspace_subscription_service.py",
            "services/enterprise_revenue_service.py",
            "services/ai_token_purchase_service.py",
            "services/website_builder_service.py",
            "services/template_marketplace_access_service.py"
        ]
        
        results = []
        
        for service_file in service_files:
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for database operations
                db_operations = [
                    r"self\.db\.",
                    r"collection\.",
                    r"await.*find",
                    r"await.*insert",
                    r"await.*update",
                    r"await.*delete",
                    r"await.*aggregate"
                ]
                
                has_db_operations = any(
                    re.search(pattern, content) 
                    for pattern in db_operations
                )
                
                # Check for mock data patterns
                has_mock_data = any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in self.mock_patterns
                )
                
                results.append({
                    "service": service_file,
                    "has_db_operations": has_db_operations,
                    "has_mock_data": has_mock_data,
                    "success": has_db_operations and not has_mock_data
                })
                
                status = "✅" if has_db_operations and not has_mock_data else "❌"
                print(f"  {status} {service_file}: {'Real DB ops' if has_db_operations else 'No DB ops'} {'+ Mock data' if has_mock_data else ''}")
                
            except Exception as e:
                results.append({
                    "service": service_file,
                    "has_db_operations": False,
                    "has_mock_data": False,
                    "success": False,
                    "error": str(e)
                })
                print(f"  ❌ {service_file}: Error - {e}")
        
        return {
            "success": all(r["success"] for r in results),
            "services_checked": len(results),
            "results": results
        }
    
    async def verify_crud_operations(self) -> Dict[str, Any]:
        """Verify CRUD operations work with real data"""
        print("🔍 VERIFYING CRUD OPERATIONS...")
        
        # Test creating real data
        test_workspace = {
            "name": f"Test Workspace {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "Test workspace for mock data verification",
            "type": "business",
            "settings": {
                "timezone": "UTC",
                "language": "en"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                # Create workspace
                async with session.post(
                    f"{self.base_url}/api/workspace",
                    json=test_workspace
                ) as response:
                    if response.status == 200:
                        workspace_data = await response.json()
                        workspace_id = workspace_data.get("id")
                        
                        if workspace_id:
                            # Read workspace
                            async with session.get(f"{self.base_url}/api/workspace/{workspace_id}") as get_response:
                                if get_response.status == 200:
                                    # Update workspace
                                    update_data = {"description": "Updated description"}
                                    async with session.put(
                                        f"{self.base_url}/api/workspace/{workspace_id}",
                                        json=update_data
                                    ) as update_response:
                                        if update_response.status == 200:
                                            # Delete workspace
                                            async with session.delete(f"{self.base_url}/api/workspace/{workspace_id}") as delete_response:
                                                return {
                                                    "success": delete_response.status in [200, 204],
                                                    "crud_operations": {
                                                        "create": response.status == 200,
                                                        "read": get_response.status == 200,
                                                        "update": update_response.status == 200,
                                                        "delete": delete_response.status in [200, 204]
                                                    },
                                                    "workspace_id": workspace_id
                                                }
                
                return {"success": False, "error": "CRUD operations failed"}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run comprehensive verification of mock data elimination"""
        print("🚀 STARTING COMPREHENSIVE MOCK DATA ELIMINATION VERIFICATION")
        print("=" * 60)
        
        results = {}
        
        # 1. Verify no mock data in code
        results["code_verification"] = await self.verify_no_mock_data_in_code()
        
        # 2. Verify database operations
        results["database_operations"] = await self.verify_database_operations()
        
        # 3. Verify service layer operations
        results["service_layer"] = await self.verify_service_layer_operations()
        
        # 4. Verify CRUD operations
        results["crud_operations"] = await self.verify_crud_operations()
        
        # Calculate overall success
        overall_success = all(
            result.get("success", False) 
            for result in results.values()
        )
        
        results["overall_success"] = overall_success
        results["verification_timestamp"] = datetime.now().isoformat()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            if test_name == "overall_success" or test_name == "verification_timestamp":
                continue
                
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
            
            if not result.get("success", False):
                if "mock_data_found" in result:
                    print(f"   Found {len(result['mock_data_found'])} mock data instances")
                if "error" in result:
                    print(f"   Error: {result['error']}")
        
        print(f"\n🎯 OVERALL RESULT: {'✅ PRODUCTION READY' if overall_success else '❌ NEEDS FIXES'}")
        
        return results

async def main():
    """Main verification function"""
    verifier = MockDataEliminationVerifier()
    results = await verifier.run_comprehensive_verification()
    
    # Save results to file
    import json
    with open("mock_data_elimination_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: mock_data_elimination_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 