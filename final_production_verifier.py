#!/usr/bin/env python3
"""
COMPREHENSIVE FINAL VERIFICATION SCRIPT
Verifies no mock data, complete CRUD operations, and service-API pairing
January 2025 - Production Readiness Check
"""

import os
import re
import json
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

class FinalProductionVerifier:
    def __init__(self, backend_path="/app/backend"):
        self.backend_path = backend_path
        self.issues = []
        self.fixes_needed = []
        self.verification_results = {
            "mock_data_scan": {},
            "crud_verification": {},
            "service_api_pairing": {},
            "missing_implementations": {},
            "summary": {}
        }
    
    def scan_for_remaining_mock_data(self):
        """Ultra-comprehensive scan for ANY remaining mock data"""
        print("🔍 SCANNING FOR ANY REMAINING MOCK DATA...")
        print("=" * 60)
        
        # Ultra-comprehensive mock patterns
        mock_patterns = [
            # Basic mock patterns
            r'mock_\w+',
            r'fake_\w+', 
            r'sample_\w+',
            r'test_\w+',
            r'dummy_\w+',
            r'placeholder\w*',
            r'example\.com',
            r'lorem ipsum',
            r'temp_\w+',
            r'demo_\w+',
            
            # Random data generators
            r'random\.\w+',
            r'uuid\.uuid4\(\)\.hex',
            r'secrets\.token_hex',
            r'random\.choice\(',
            r'random\.randint\(',
            r'random\.uniform\(',
            r'random\.sample\(',
            
            # Hardcoded sample values
            r'"User \d+"',
            r'"Sample \w+"',
            r'"Test \w+"',
            r'"Example \w+"',
            r'"Demo \w+"',
            r'"Placeholder \w+"',
            r'"Mock \w+"',
            r'"Fake \w+"',
            r'"Dummy \w+"',
            
            # Sample emails and data
            r'\w+@example\.com',
            r'\w+@test\.com',
            r'\w+@sample\.com',
            r'user\d+@\w+\.com',
            r'test\d+@\w+\.com',
            
            # Mock data structures
            r'\["Sample[^"]*"[^\]]*\]',
            r'\{"mock":[^}]*\}',
            r'\{"sample":[^}]*\}',
            r'\{"test":[^}]*\}',
            r'\{"fake":[^}]*\}',
            
            # Hardcoded return values
            r'return\s+\{[^}]*"sample"',
            r'return\s+\{[^}]*"mock"',
            r'return\s+\{[^}]*"fake"',
            r'return\s+\{[^}]*"test"',
            r'return\s+\{[^}]*"placeholder"',
            
            # Static data arrays
            r'\[[^]]*"Sample[^"]*"[^]]*\]',
            r'\[[^]]*"Mock[^"]*"[^]]*\]',
            r'\[[^]]*"Test[^"]*"[^]]*\]',
        ]
        
        mock_data_found = {}
        total_issues = 0
        critical_files = []
        
        # Scan all Python files
        for root, dirs, files in os.walk(self.backend_path):
            # Skip certain directories
            if any(skip in root for skip in ['__pycache__', '.git', 'node_modules', 'backup']):
                continue
                
            for filename in files:
                if filename.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        file_issues = []
                        line_numbers = content.split('\n')
                        
                        for i, pattern in enumerate(mock_patterns):
                            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                            for match in matches:
                                # Find line number
                                line_num = content[:match.start()].count('\n') + 1
                                line_content = line_numbers[line_num - 1] if line_num - 1 < len(line_numbers) else ""
                                
                                issue = {
                                    "pattern": pattern,
                                    "match": match.group(0),
                                    "line": line_num,
                                    "content": line_content.strip()
                                }
                                file_issues.append(issue)
                                total_issues += 1
                        
                        if file_issues:
                            relative_path = os.path.relpath(file_path, self.backend_path)
                            mock_data_found[relative_path] = {
                                "issues_count": len(file_issues),
                                "issues": file_issues
                            }
                            critical_files.append(relative_path)
                            print(f"  ❌ MOCK DATA FOUND in {relative_path}: {len(file_issues)} instances")
                            
                            # Show first few issues
                            for issue in file_issues[:3]:
                                print(f"     Line {issue['line']}: {issue['match']} in '{issue['content'][:60]}...'")
                        
                    except Exception as e:
                        print(f"  ⚠️  Error reading {filename}: {str(e)}")
        
        self.verification_results["mock_data_scan"] = {
            "total_issues": total_issues,
            "files_with_issues": len(mock_data_found),
            "critical_files": critical_files,
            "detailed_issues": mock_data_found
        }
        
        if total_issues == 0:
            print("  ✅ NO MOCK DATA FOUND - 100% CLEAN!")
        else:
            print(f"  ❌ FOUND {total_issues} MOCK DATA INSTANCES in {len(mock_data_found)} files")
            self.fixes_needed.extend(critical_files)
        
        return total_issues == 0
    
    def verify_complete_crud_operations(self):
        """Verify all entities have complete CRUD operations"""
        print("\n🔍 VERIFYING COMPLETE CRUD OPERATIONS...")
        print("=" * 60)
        
        # Define all entities that should have CRUD operations
        expected_entities = {
            "users": ["create_user", "get_user", "update_user", "delete_user"],
            "workspaces": ["create_workspace", "get_workspace", "update_workspace", "delete_workspace"],
            "templates": ["create_template", "get_template", "update_template", "delete_template"],
            "products": ["create_product", "get_product", "update_product", "delete_product"],
            "orders": ["create_order", "get_order", "update_order", "cancel_order"],
            "courses": ["create_course", "get_course", "update_course", "delete_course"],
            "contacts": ["create_contact", "get_contact", "update_contact", "delete_contact"],
            "invoices": ["create_invoice", "get_invoice", "update_invoice", "delete_invoice"],
            "bookings": ["create_booking", "get_booking", "update_booking", "cancel_booking"],
            "bio_sites": ["create_bio_site", "get_bio_site", "update_bio_site", "delete_bio_site"],
            "campaigns": ["create_campaign", "get_campaign", "update_campaign", "delete_campaign"],
            "teams": ["create_team", "get_team", "update_team", "delete_team"],
            "services": ["create_service", "get_service", "update_service", "delete_service"],
            "payments": ["create_payment", "get_payment", "update_payment", "refund_payment"],
            "social_leads": ["create_lead", "get_lead", "update_lead", "delete_lead"],
        }
        
        crud_status = {}
        missing_operations = {}
        
        # Check service files for CRUD methods
        services_path = os.path.join(self.backend_path, "services")
        for entity, required_operations in expected_entities.items():
            found_operations = []
            missing_operations[entity] = []
            
            # Search through all service files
            for filename in os.listdir(services_path):
                if filename.endswith('.py'):
                    file_path = os.path.join(services_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Look for CRUD methods
                        for operation in required_operations:
                            # Multiple patterns to catch different naming conventions
                            patterns = [
                                rf'def {operation}',
                                rf'async def {operation}',
                                rf'def {operation.replace("_", "")}',
                                rf'async def {operation.replace("_", "")}',
                            ]
                            
                            for pattern in patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    if operation not in found_operations:
                                        found_operations.append(operation)
                                    break
                    except Exception as e:
                        continue
            
            # Check what's missing
            for operation in required_operations:
                if operation not in found_operations:
                    missing_operations[entity].append(operation)
            
            # Calculate completion percentage
            completion = (len(found_operations) / len(required_operations)) * 100
            crud_status[entity] = {
                "completion": completion,
                "found": found_operations,
                "missing": missing_operations[entity]
            }
            
            if completion == 100:
                print(f"  ✅ {entity}: {completion:.0f}% CRUD complete")
            else:
                print(f"  ❌ {entity}: {completion:.0f}% CRUD complete - Missing: {missing_operations[entity]}")
                self.issues.append(f"CRUD incomplete for {entity}: missing {missing_operations[entity]}")
        
        # Check API endpoints match CRUD operations
        api_path = os.path.join(self.backend_path, "api")
        api_endpoints = {}
        
        for filename in os.listdir(api_path):
            if filename.endswith('.py'):
                file_path = os.path.join(api_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count HTTP method decorators
                    http_methods = {
                        'GET': len(re.findall(r'@router\.get|@app\.get', content)),
                        'POST': len(re.findall(r'@router\.post|@app\.post', content)),
                        'PUT': len(re.findall(r'@router\.put|@app\.put', content)),
                        'DELETE': len(re.findall(r'@router\.delete|@app\.delete', content))
                    }
                    
                    api_endpoints[filename] = http_methods
                    
                except Exception as e:
                    continue
        
        self.verification_results["crud_verification"] = {
            "entities_checked": len(expected_entities),
            "crud_status": crud_status,
            "api_endpoints": api_endpoints,
            "missing_operations": {k: v for k, v in missing_operations.items() if v}
        }
        
        complete_entities = sum(1 for status in crud_status.values() if status["completion"] == 100)
        total_entities = len(expected_entities)
        
        print(f"\n  📊 CRUD VERIFICATION SUMMARY:")
        print(f"     Complete Entities: {complete_entities}/{total_entities} ({(complete_entities/total_entities)*100:.1f}%)")
        
        return complete_entities == total_entities
    
    def verify_service_api_pairing(self):
        """Verify all service files have corresponding API files and vice versa"""
        print("\n🔍 VERIFYING SERVICE-API FILE PAIRING...")
        print("=" * 60)
        
        services_path = os.path.join(self.backend_path, "services")
        api_path = os.path.join(self.backend_path, "api")
        
        # Get all service files
        service_files = set()
        for filename in os.listdir(services_path):
            if filename.endswith('.py') and filename != '__init__.py':
                base_name = filename.replace('_service.py', '').replace('.py', '')
                service_files.add(base_name)
        
        # Get all API files
        api_files = set()
        for filename in os.listdir(api_path):
            if filename.endswith('.py') and filename != '__init__.py':
                base_name = filename.replace('.py', '')
                api_files.add(base_name)
        
        # Find mismatches
        services_without_api = service_files - api_files
        apis_without_service = api_files - service_files
        paired_files = service_files & api_files
        
        pairing_issues = []
        
        print(f"  📊 PAIRING ANALYSIS:")
        print(f"     Service Files: {len(service_files)}")
        print(f"     API Files: {len(api_files)}")
        print(f"     Properly Paired: {len(paired_files)}")
        
        if services_without_api:
            print(f"  ❌ SERVICES WITHOUT API FILES ({len(services_without_api)}):")
            for service in services_without_api:
                print(f"     - {service}_service.py → Missing {service}.py")
                pairing_issues.append(f"Service {service} missing corresponding API file")
        
        if apis_without_service:
            print(f"  ❌ API FILES WITHOUT SERVICE FILES ({len(apis_without_service)}):")
            for api in apis_without_service:
                print(f"     - {api}.py → Missing {api}_service.py")
                pairing_issues.append(f"API {api} missing corresponding service file")
        
        if not services_without_api and not apis_without_service:
            print("  ✅ ALL SERVICE-API FILES PROPERLY PAIRED!")
        
        # Verify imports in API files reference their services
        import_issues = []
        for api_file in paired_files:
            api_file_path = os.path.join(api_path, f"{api_file}.py")
            try:
                with open(api_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if service is imported
                expected_import_patterns = [
                    rf'from services\.{api_file}_service import',
                    rf'from services import {api_file}_service',
                    rf'import.*{api_file}_service',
                ]
                
                has_import = any(re.search(pattern, content) for pattern in expected_import_patterns)
                
                if not has_import:
                    import_issues.append(f"API file {api_file}.py doesn't import its service")
                    print(f"  ⚠️  {api_file}.py missing service import")
                
            except Exception as e:
                print(f"  ❌ Error checking {api_file}.py: {e}")
        
        self.verification_results["service_api_pairing"] = {
            "service_files_count": len(service_files),
            "api_files_count": len(api_files),
            "paired_count": len(paired_files),
            "services_without_api": list(services_without_api),
            "apis_without_service": list(apis_without_service),
            "import_issues": import_issues,
            "pairing_issues": pairing_issues
        }
        
        total_issues = len(services_without_api) + len(apis_without_service) + len(import_issues)
        self.issues.extend(pairing_issues + import_issues)
        
        return total_issues == 0
    
    def check_main_py_router_registration(self):
        """Verify all API routers are registered in main.py"""
        print("\n🔍 CHECKING MAIN.PY ROUTER REGISTRATION...")
        print("=" * 50)
        
        main_py_path = os.path.join(self.backend_path, "main.py")
        api_path = os.path.join(self.backend_path, "api")
        
        # Get all API files
        api_files = []
        for filename in os.listdir(api_path):
            if filename.endswith('.py') and filename != '__init__.py':
                api_files.append(filename.replace('.py', ''))
        
        try:
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
        except:
            print("  ❌ Could not read main.py")
            return False
        
        # Check which routers are registered
        registered_routers = []
        unregistered_routers = []
        
        for api_file in api_files:
            # Look for router registration patterns
            patterns = [
                rf'from api\.{api_file} import router',
                rf'include_router.*{api_file}',
                rf'{api_file}_router',
            ]
            
            is_registered = any(re.search(pattern, main_content) for pattern in patterns)
            
            if is_registered:
                registered_routers.append(api_file)
                print(f"  ✅ {api_file} router registered")
            else:
                unregistered_routers.append(api_file)
                print(f"  ❌ {api_file} router NOT registered")
        
        print(f"\n  📊 ROUTER REGISTRATION:")
        print(f"     Registered: {len(registered_routers)}/{len(api_files)}")
        print(f"     Unregistered: {len(unregistered_routers)}")
        
        if unregistered_routers:
            self.fixes_needed.extend([f"Register {router} in main.py" for router in unregistered_routers])
        
        return len(unregistered_routers) == 0
    
    def generate_fix_recommendations(self):
        """Generate specific fix recommendations for found issues"""
        print("\n🔧 GENERATING FIX RECOMMENDATIONS...")
        print("=" * 50)
        
        fixes = []
        
        # Mock data fixes
        mock_issues = self.verification_results["mock_data_scan"]
        if mock_issues["total_issues"] > 0:
            fixes.append({
                "category": "Mock Data Elimination",
                "priority": "HIGH",
                "description": f"Remove {mock_issues['total_issues']} mock data instances",
                "files": mock_issues["critical_files"],
                "action": "Replace mock data with database queries"
            })
        
        # CRUD fixes
        crud_issues = self.verification_results["crud_verification"]["missing_operations"]
        if crud_issues:
            fixes.append({
                "category": "CRUD Completion", 
                "priority": "HIGH",
                "description": f"Complete CRUD operations for {len(crud_issues)} entities",
                "entities": list(crud_issues.keys()),
                "action": "Implement missing CRUD methods in service files"
            })
        
        # Pairing fixes
        pairing_issues = self.verification_results["service_api_pairing"]["pairing_issues"]
        if pairing_issues:
            fixes.append({
                "category": "Service-API Pairing",
                "priority": "MEDIUM", 
                "description": f"Fix {len(pairing_issues)} service-API pairing issues",
                "issues": pairing_issues,
                "action": "Create missing service or API files"
            })
        
        for i, fix in enumerate(fixes, 1):
            print(f"  {i}. {fix['category']} ({fix['priority']} Priority)")
            print(f"     {fix['description']}")
            print(f"     Action: {fix['action']}")
        
        return fixes
    
    def run_comprehensive_verification(self):
        """Run complete verification suite"""
        print("🚀 STARTING COMPREHENSIVE FINAL VERIFICATION")
        print("=" * 70)
        
        # Run all verification checks
        mock_data_clean = self.scan_for_remaining_mock_data()
        crud_complete = self.verify_complete_crud_operations()
        pairing_correct = self.verify_service_api_pairing()
        routers_registered = self.check_main_py_router_registration()
        
        # Generate summary
        total_checks = 4
        passed_checks = sum([mock_data_clean, crud_complete, pairing_correct, routers_registered])
        
        self.verification_results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "success_rate": (passed_checks / total_checks) * 100,
            "mock_data_clean": mock_data_clean,
            "crud_complete": crud_complete, 
            "pairing_correct": pairing_correct,
            "routers_registered": routers_registered,
            "issues_found": len(self.issues),
            "fixes_needed": len(self.fixes_needed)
        }
        
        # Generate recommendations
        fix_recommendations = self.generate_fix_recommendations()
        
        # Print final summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE VERIFICATION SUMMARY")
        print("=" * 70)
        
        print(f"✅ Checks Passed: {passed_checks}/{total_checks} ({(passed_checks/total_checks)*100:.1f}%)")
        print(f"{'✅' if mock_data_clean else '❌'} Mock Data Eliminated: {'YES' if mock_data_clean else 'NO'}")
        print(f"{'✅' if crud_complete else '❌'} CRUD Operations Complete: {'YES' if crud_complete else 'NO'}")
        print(f"{'✅' if pairing_correct else '❌'} Service-API Pairing: {'YES' if pairing_correct else 'NO'}")
        print(f"{'✅' if routers_registered else '❌'} Router Registration: {'YES' if routers_registered else 'NO'}")
        
        if passed_checks == total_checks:
            print("\n🎉 ALL VERIFICATIONS PASSED - PRODUCTION READY!")
            print("✅ Platform ready for frontend development and native app creation")
        else:
            print(f"\n⚠️  {total_checks - passed_checks} ISSUES FOUND - FIXES NEEDED")
            print("🔧 Detailed fix recommendations generated")
        
        return self.verification_results, fix_recommendations

def main():
    verifier = FinalProductionVerifier()
    results, fixes = verifier.run_comprehensive_verification()
    
    # Save results
    with open("/app/final_verification_results.json", "w") as f:
        json.dump({"results": results, "fixes": fixes}, f, indent=2)
    
    return results, fixes

if __name__ == "__main__":
    main()