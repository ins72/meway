#!/usr/bin/env python3
"""
COMPREHENSIVE 600+ ENDPOINT AUDIT FOR MEWAYZ V2 PLATFORM
=======================================================

This script conducts a complete audit of ALL services, APIs, models, and endpoints
to identify missing CRUD operations, mock data, duplicate files, and service/API pairs.

Target: Audit 600-700+ API endpoints across the entire platform
"""

import os
import json
import ast
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional
from datetime import datetime
import inspect
import importlib.util

class ComprehensiveEndpointAuditor:
    def __init__(self):
        self.backend_path = Path("/app/backend")
        self.api_path = self.backend_path / "api"
        self.services_path = self.backend_path / "services"
        self.models_path = self.backend_path / "models"
        
        # Audit results storage
        self.audit_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_files_scanned": 0,
            "endpoints_discovered": {},
            "services_discovered": {},
            "models_discovered": {},
            "missing_crud_operations": [],
            "mock_data_instances": [],
            "duplicate_files": [],
            "service_api_pairs": {},
            "missing_service_api_pairs": [],
            "summary": {}
        }
        
        # Track all discovered endpoints
        self.all_endpoints = {}
        self.all_services = {}
        self.all_models = {}
        
        print("🔍 COMPREHENSIVE 600+ ENDPOINT AUDIT INITIALIZED")
        print("=" * 60)

    async def run_comprehensive_audit(self):
        """Execute the complete audit process"""
        print("🚀 Starting comprehensive audit of Mewayz v2 platform...")
        
        # Step 1: Discover all API endpoints
        await self.discover_all_api_endpoints()
        
        # Step 2: Discover all services
        await self.discover_all_services()
        
        # Step 3: Discover all models
        await self.discover_all_models()
        
        # Step 4: Audit for missing CRUD operations
        await self.audit_missing_crud_operations()
        
        # Step 5: Audit for mock/random data
        await self.audit_mock_data()
        
        # Step 6: Audit for duplicate files
        await self.audit_duplicate_files()
        
        # Step 7: Audit service/API pairs
        await self.audit_service_api_pairs()
        
        # Step 8: Generate comprehensive summary
        await self.generate_audit_summary()
        
        # Step 9: Save results
        await self.save_audit_results()
        
        print("✅ COMPREHENSIVE AUDIT COMPLETED")
        return self.audit_results

    async def discover_all_api_endpoints(self):
        """Discover all API endpoints across all API files"""
        print("\n📊 PHASE 1: Discovering All API Endpoints...")
        
        api_files = list(self.api_path.glob("*.py"))
        endpoint_count = 0
        
        for api_file in api_files:
            if api_file.name.startswith("__"):
                continue
                
            try:
                # Read and parse the file
                content = api_file.read_text(encoding='utf-8')
                self.audit_results["total_files_scanned"] += 1
                
                # Extract module name
                module_name = api_file.stem
                
                # Find all HTTP method decorators and endpoints
                endpoints = self.extract_endpoints_from_file(content, module_name)
                
                if endpoints:
                    self.all_endpoints[module_name] = endpoints
                    self.audit_results["endpoints_discovered"][module_name] = endpoints
                    endpoint_count += len(endpoints)
                    
                    print(f"  📁 {module_name}: {len(endpoints)} endpoints")
                    
            except Exception as e:
                print(f"  ❌ Error scanning {api_file.name}: {str(e)}")
                continue
        
        print(f"\n🎯 DISCOVERED {endpoint_count} API ENDPOINTS across {len(self.all_endpoints)} API modules")

    def extract_endpoints_from_file(self, content: str, module_name: str) -> List[Dict]:
        """Extract all HTTP endpoints from a Python file"""
        endpoints = []
        
        # HTTP method patterns
        http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
        
        # Find all route decorators
        patterns = [
            r'@router\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']',
            r'@app\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']',
            r'@router\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\'].*?\)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)
                
                # Extract function name (look for the next function definition)
                func_match = re.search(r'def\s+(\w+)\s*\(', content[match.end():])
                func_name = func_match.group(1) if func_match else "unknown"
                
                endpoint = {
                    "method": method,
                    "path": path,
                    "function": func_name,
                    "module": module_name,
                    "full_path": f"/api/{path.lstrip('/')}" if not path.startswith('/api') else path
                }
                endpoints.append(endpoint)
        
        return endpoints

    async def discover_all_services(self):
        """Discover all service files and their methods"""
        print("\n⚙️ PHASE 2: Discovering All Services...")
        
        service_files = list(self.services_path.glob("*.py"))
        service_count = 0
        
        for service_file in service_files:
            if service_file.name.startswith("__"):
                continue
                
            try:
                content = service_file.read_text(encoding='utf-8')
                self.audit_results["total_files_scanned"] += 1
                
                module_name = service_file.stem
                
                # Extract service methods
                methods = self.extract_service_methods(content, module_name)
                
                if methods:
                    self.all_services[module_name] = methods
                    self.audit_results["services_discovered"][module_name] = methods
                    service_count += len(methods)
                    
                    print(f"  🔧 {module_name}: {len(methods)} methods")
                    
            except Exception as e:
                print(f"  ❌ Error scanning {service_file.name}: {str(e)}")
                continue
        
        print(f"\n🎯 DISCOVERED {service_count} SERVICE METHODS across {len(self.all_services)} service modules")

    def extract_service_methods(self, content: str, module_name: str) -> List[Dict]:
        """Extract all methods from a service file"""
        methods = []
        
        # Find all function definitions
        func_pattern = r'(?:async\s+)?def\s+(\w+)\s*\([^)]*\):'
        matches = re.finditer(func_pattern, content, re.MULTILINE)
        
        for match in matches:
            func_name = match.group(1)
            
            # Skip private methods and common patterns
            if func_name.startswith('_') and not func_name.startswith('__'):
                continue
                
            # Determine CRUD operation type
            crud_type = self.determine_crud_type(func_name)
            
            method = {
                "name": func_name,
                "crud_type": crud_type,
                "module": module_name
            }
            methods.append(method)
        
        return methods

    def determine_crud_type(self, func_name: str) -> str:
        """Determine CRUD operation type from function name"""
        func_lower = func_name.lower()
        
        if any(word in func_lower for word in ['create', 'add', 'insert', 'post']):
            return 'CREATE'
        elif any(word in func_lower for word in ['get', 'find', 'list', 'fetch', 'read', 'retrieve']):
            return 'READ'
        elif any(word in func_lower for word in ['update', 'modify', 'edit', 'patch', 'put']):
            return 'UPDATE'
        elif any(word in func_lower for word in ['delete', 'remove', 'destroy']):
            return 'DELETE'
        else:
            return 'OTHER'

    async def discover_all_models(self):
        """Discover all model definitions"""
        print("\n📋 PHASE 3: Discovering All Models...")
        
        model_files = list(self.models_path.glob("*.py"))
        model_count = 0
        
        for model_file in model_files:
            if model_file.name.startswith("__"):
                continue
                
            try:
                content = model_file.read_text(encoding='utf-8')
                self.audit_results["total_files_scanned"] += 1
                
                module_name = model_file.stem
                
                # Extract model classes
                models = self.extract_model_classes(content, module_name)
                
                if models:
                    self.all_models[module_name] = models
                    self.audit_results["models_discovered"][module_name] = models
                    model_count += len(models)
                    
                    print(f"  📄 {module_name}: {len(models)} models")
                    
            except Exception as e:
                print(f"  ❌ Error scanning {model_file.name}: {str(e)}")
                continue
        
        print(f"\n🎯 DISCOVERED {model_count} MODEL CLASSES across {len(self.all_models)} model modules")

    def extract_model_classes(self, content: str, module_name: str) -> List[Dict]:
        """Extract all model classes from a file"""
        models = []
        
        # Find all class definitions
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
        matches = re.finditer(class_pattern, content, re.MULTILINE)
        
        for match in matches:
            class_name = match.group(1)
            
            # Find class fields
            class_start = match.end()
            # Find the next class or end of file
            next_class = re.search(r'\nclass\s+\w+', content[class_start:])
            class_end = class_start + next_class.start() if next_class else len(content)
            
            class_content = content[class_start:class_end]
            fields = self.extract_model_fields(class_content)
            
            model = {
                "name": class_name,
                "module": module_name,
                "fields": fields,
                "field_count": len(fields)
            }
            models.append(model)
        
        return models

    def extract_model_fields(self, class_content: str) -> List[str]:
        """Extract field names from a model class"""
        fields = []
        
        # Find field definitions (various patterns)
        patterns = [
            r'(\w+)\s*:\s*\w+',  # Type annotations
            r'(\w+)\s*=\s*Field\(',  # Pydantic fields
            r'(\w+)\s*=\s*[^=\n]+',  # Assignment patterns
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, class_content, re.MULTILINE)
            for match in matches:
                field_name = match.group(1)
                if not field_name.startswith('_') and field_name not in fields:
                    fields.append(field_name)
        
        return fields

    async def audit_missing_crud_operations(self):
        """Audit for missing CRUD operations in services"""
        print("\n🔍 PHASE 4: Auditing Missing CRUD Operations...")
        
        missing_crud = []
        
        for service_name, methods in self.all_services.items():
            # Count CRUD operations
            crud_counts = {'CREATE': 0, 'READ': 0, 'UPDATE': 0, 'DELETE': 0}
            
            for method in methods:
                crud_type = method['crud_type']
                if crud_type in crud_counts:
                    crud_counts[crud_type] += 1
            
            # Identify missing operations
            missing_ops = [op for op, count in crud_counts.items() if count == 0]
            
            if missing_ops:
                missing_crud.append({
                    "service": service_name,
                    "missing_operations": missing_ops,
                    "current_operations": crud_counts,
                    "severity": "HIGH" if len(missing_ops) >= 3 else "MEDIUM"
                })
                
                print(f"  ⚠️ {service_name}: Missing {missing_ops}")
        
        self.audit_results["missing_crud_operations"] = missing_crud
        print(f"\n🎯 FOUND {len(missing_crud)} SERVICES WITH MISSING CRUD OPERATIONS")

    async def audit_mock_data(self):
        """Audit for mock, random, or hardcoded data"""
        print("\n🎲 PHASE 5: Auditing Mock/Random Data...")
        
        mock_data_instances = []
        
        # Patterns that indicate mock or random data  
        mock_patterns = [
            r'random\.',
            r'fake\.',
            r'mock_',
            r'dummy_',
            r'sample_data',
            r'test_data',
            r'fake_\w+',
            r'random_\w+',
            r'mock\w*Data',
            r'generateFake',
            r'createMock',
            r'randint\(',
            r'choice\(',
            r'uuid4\(\).*random',
            r'Lorem ipsum',
            r'example\.com',
            r'test@example',
        ]
        
        all_files = list(self.api_path.glob("*.py")) + list(self.services_path.glob("*.py"))
        
        for file_path in all_files:
            if file_path.name.startswith("__"):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in mock_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            mock_data_instances.append({
                                "file": str(file_path.relative_to(self.backend_path)),
                                "line": i,
                                "code": line.strip(),
                                "pattern": pattern,
                                "severity": "HIGH" if any(p in pattern for p in ['random', 'fake', 'mock']) else "MEDIUM"
                            })
                            
            except Exception as e:
                print(f"  ❌ Error scanning {file_path.name}: {str(e)}")
                continue
        
        self.audit_results["mock_data_instances"] = mock_data_instances
        print(f"\n🎯 FOUND {len(mock_data_instances)} MOCK DATA INSTANCES")

    async def audit_duplicate_files(self):
        """Audit for duplicate or very similar files"""
        print("\n📁 PHASE 6: Auditing Duplicate Files...")
        
        duplicate_files = []
        
        # Check for backup files
        backup_patterns = ['.backup', '.bak', '.old', '.orig', '_backup', '_old']
        
        all_files = list(self.backend_path.rglob("*.py"))
        
        for file_path in all_files:
            filename = file_path.name
            
            # Check for backup patterns
            for pattern in backup_patterns:
                if pattern in filename:
                    original_name = filename.replace(pattern, '')
                    original_file = file_path.parent / original_name
                    
                    if original_file.exists():
                        duplicate_files.append({
                            "original": str(original_file.relative_to(self.backend_path)),
                            "duplicate": str(file_path.relative_to(self.backend_path)),
                            "type": "backup_file",
                            "action": "REMOVE_DUPLICATE"
                        })
        
        # Check for similarly named files
        file_groups = {}
        for file_path in all_files:
            base_name = file_path.stem.lower()
            # Remove common suffixes for grouping
            for suffix in ['_service', '_api', '_router', '_handler', '_controller']:
                if base_name.endswith(suffix):
                    base_name = base_name[:-len(suffix)]
                    break
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(file_path)
        
        # Find groups with multiple files
        for base_name, files in file_groups.items():
            if len(files) > 2:  # More than API + Service is suspicious
                # Check for potential duplicates by content similarity
                for i, file1 in enumerate(files):
                    for file2 in files[i+1:]:
                        if self.files_are_similar(file1, file2):
                            duplicate_files.append({
                                "original": str(file1.relative_to(self.backend_path)),
                                "duplicate": str(file2.relative_to(self.backend_path)),
                                "type": "similar_content",
                                "action": "REVIEW_AND_MERGE"
                            })
        
        self.audit_results["duplicate_files"] = duplicate_files
        print(f"\n🎯 FOUND {len(duplicate_files)} DUPLICATE/SIMILAR FILES")

    def files_are_similar(self, file1: Path, file2: Path, threshold: float = 0.8) -> bool:
        """Check if two files have similar content"""
        try:
            content1 = set(file1.read_text(encoding='utf-8').split())
            content2 = set(file2.read_text(encoding='utf-8').split())
            
            if not content1 or not content2:
                return False
            
            intersection = len(content1.intersection(content2))
            union = len(content1.union(content2))
            
            similarity = intersection / union if union > 0 else 0
            return similarity > threshold
            
        except Exception:
            return False

    async def audit_service_api_pairs(self):
        """Audit for missing service/API pairs"""
        print("\n🔗 PHASE 7: Auditing Service/API Pairs...")
        
        service_api_pairs = {}
        missing_pairs = []
        
        # Match services with APIs
        for service_name in self.all_services.keys():
            # Clean service name (remove _service suffix)
            clean_name = service_name.replace('_service', '')
            
            # Look for corresponding API
            corresponding_apis = []
            for api_name in self.all_endpoints.keys():
                if clean_name in api_name or api_name in clean_name:
                    corresponding_apis.append(api_name)
            
            service_api_pairs[service_name] = {
                "service": service_name,
                "corresponding_apis": corresponding_apis,
                "has_api": len(corresponding_apis) > 0
            }
            
            if not corresponding_apis:
                missing_pairs.append({
                    "service": service_name,
                    "expected_api_name": clean_name,
                    "action": "CREATE_API_ENDPOINTS"
                })
        
        # Check APIs without services
        for api_name in self.all_endpoints.keys():
            corresponding_services = []
            for service_name in self.all_services.keys():
                clean_service = service_name.replace('_service', '')
                if api_name in clean_service or clean_service in api_name:
                    corresponding_services.append(service_name)
            
            if not corresponding_services:
                missing_pairs.append({
                    "api": api_name,
                    "expected_service_name": f"{api_name}_service",
                    "action": "CREATE_SERVICE_METHODS"
                })
        
        self.audit_results["service_api_pairs"] = service_api_pairs
        self.audit_results["missing_service_api_pairs"] = missing_pairs
        print(f"\n🎯 FOUND {len(missing_pairs)} MISSING SERVICE/API PAIRS")

    async def generate_audit_summary(self):
        """Generate comprehensive audit summary"""
        print("\n📊 PHASE 8: Generating Audit Summary...")
        
        total_endpoints = sum(len(endpoints) for endpoints in self.all_endpoints.values())
        total_services = sum(len(methods) for methods in self.all_services.values())
        total_models = sum(len(models) for models in self.all_models.values())
        
        summary = {
            "overview": {
                "total_files_scanned": self.audit_results["total_files_scanned"],
                "total_api_modules": len(self.all_endpoints),
                "total_service_modules": len(self.all_services), 
                "total_model_modules": len(self.all_models),
                "total_endpoints_discovered": total_endpoints,
                "total_service_methods": total_services,
                "total_model_classes": total_models
            },
            "issues_found": {
                "missing_crud_operations": len(self.audit_results["missing_crud_operations"]),
                "mock_data_instances": len(self.audit_results["mock_data_instances"]),
                "duplicate_files": len(self.audit_results["duplicate_files"]),
                "missing_service_api_pairs": len(self.audit_results["missing_service_api_pairs"])
            },
            "crud_analysis": {
                "services_with_complete_crud": 0,
                "services_with_partial_crud": 0,
                "services_with_no_crud": 0
            },
            "priority_actions": []
        }
        
        # Analyze CRUD completeness
        for item in self.audit_results["missing_crud_operations"]:
            if len(item["missing_operations"]) == 4:
                summary["crud_analysis"]["services_with_no_crud"] += 1
            elif len(item["missing_operations"]) > 0:
                summary["crud_analysis"]["services_with_partial_crud"] += 1
            else:
                summary["crud_analysis"]["services_with_complete_crud"] += 1
        
        # Generate priority actions
        if self.audit_results["missing_crud_operations"]:
            summary["priority_actions"].append({
                "action": "Implement missing CRUD operations",
                "priority": "HIGH",
                "count": len(self.audit_results["missing_crud_operations"])
            })
        
        if self.audit_results["mock_data_instances"]:
            summary["priority_actions"].append({
                "action": "Eliminate mock/random data",
                "priority": "HIGH",
                "count": len(self.audit_results["mock_data_instances"])
            })
        
        if self.audit_results["duplicate_files"]:
            summary["priority_actions"].append({
                "action": "Remove duplicate files",
                "priority": "MEDIUM",
                "count": len(self.audit_results["duplicate_files"])
            })
        
        if self.audit_results["missing_service_api_pairs"]:
            summary["priority_actions"].append({
                "action": "Create missing service/API pairs",
                "priority": "HIGH",
                "count": len(self.audit_results["missing_service_api_pairs"])
            })
        
        self.audit_results["summary"] = summary
        
        print("✅ AUDIT SUMMARY GENERATED")

    async def save_audit_results(self):
        """Save comprehensive audit results"""
        print("\n💾 PHASE 9: Saving Audit Results...")
        
        # Save detailed results
        results_file = self.backend_path / "comprehensive_600_endpoint_audit_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
        
        # Generate markdown report
        await self.generate_markdown_report()
        
        print(f"✅ AUDIT RESULTS SAVED TO: {results_file}")

    async def generate_markdown_report(self):
        """Generate a comprehensive markdown report"""
        report_file = self.backend_path / "COMPREHENSIVE_600_ENDPOINT_AUDIT_REPORT.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# COMPREHENSIVE 600+ ENDPOINT AUDIT REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"**Audit Date:** {self.audit_results['timestamp']}\n")
            f.write(f"**Platform:** Mewayz v2\n")
            f.write(f"**Scope:** Complete backend audit (APIs, Services, Models)\n\n")
            
            # Overview
            summary = self.audit_results["summary"]["overview"]
            f.write("## 📊 AUDIT OVERVIEW\n\n")
            f.write(f"- **Files Scanned:** {summary['total_files_scanned']}\n")
            f.write(f"- **API Modules:** {summary['total_api_modules']}\n")
            f.write(f"- **Service Modules:** {summary['total_service_modules']}\n")
            f.write(f"- **Model Modules:** {summary['total_model_modules']}\n")
            f.write(f"- **Total Endpoints:** {summary['total_endpoints_discovered']}\n")
            f.write(f"- **Total Service Methods:** {summary['total_service_methods']}\n")
            f.write(f"- **Total Model Classes:** {summary['total_model_classes']}\n\n")
            
            # Issues Summary
            issues = self.audit_results["summary"]["issues_found"]
            f.write("## 🚨 ISSUES SUMMARY\n\n")
            f.write(f"- **Missing CRUD Operations:** {issues['missing_crud_operations']}\n")
            f.write(f"- **Mock Data Instances:** {issues['mock_data_instances']}\n")
            f.write(f"- **Duplicate Files:** {issues['duplicate_files']}\n")
            f.write(f"- **Missing Service/API Pairs:** {issues['missing_service_api_pairs']}\n\n")
            
            # Priority Actions
            f.write("## 🎯 PRIORITY ACTIONS\n\n")
            for action in self.audit_results["summary"]["priority_actions"]:
                f.write(f"- **{action['priority']}:** {action['action']} ({action['count']} items)\n")
            f.write("\n")
            
            # Detailed findings...
            if self.audit_results["missing_crud_operations"]:
                f.write("## 🔍 MISSING CRUD OPERATIONS\n\n")
                for item in self.audit_results["missing_crud_operations"][:10]:  # Top 10
                    f.write(f"### {item['service']}\n")
                    f.write(f"- **Missing:** {', '.join(item['missing_operations'])}\n")
                    f.write(f"- **Severity:** {item['severity']}\n\n")
            
            # Mock data findings
            if self.audit_results["mock_data_instances"]:
                f.write("## 🎲 MOCK DATA INSTANCES\n\n")
                for item in self.audit_results["mock_data_instances"][:15]:  # Top 15
                    f.write(f"- **File:** {item['file']}\n")
                    f.write(f"  - **Line {item['line']}:** `{item['code']}`\n")
                    f.write(f"  - **Pattern:** {item['pattern']}\n\n")
        
        print(f"✅ MARKDOWN REPORT GENERATED: {report_file}")

async def main():
    """Main execution function"""
    print("🚀 MEWAYZ V2 COMPREHENSIVE 600+ ENDPOINT AUDIT")
    print("=" * 60)
    print("🎯 Target: Audit all services, APIs, models, and endpoints")
    print("🔍 Scope: CRUD operations, mock data, duplicates, service/API pairs")
    print("=" * 60)
    
    auditor = ComprehensiveEndpointAuditor()
    results = await auditor.run_comprehensive_audit()
    
    print("\n" + "=" * 60)
    print("📊 AUDIT COMPLETION SUMMARY")
    print("=" * 60)
    
    summary = results["summary"]["overview"]
    issues = results["summary"]["issues_found"]
    
    print(f"✅ Total Files Scanned: {summary['total_files_scanned']}")
    print(f"✅ Total Endpoints Found: {summary['total_endpoints_discovered']}")
    print(f"✅ Total Service Methods: {summary['total_service_methods']}")
    print(f"✅ Total Model Classes: {summary['total_model_classes']}")
    print()
    print(f"⚠️ Missing CRUD Operations: {issues['missing_crud_operations']}")
    print(f"⚠️ Mock Data Instances: {issues['mock_data_instances']}")
    print(f"⚠️ Duplicate Files: {issues['duplicate_files']}")
    print(f"⚠️ Missing Service/API Pairs: {issues['missing_service_api_pairs']}")
    
    total_issues = sum(issues.values())
    print(f"\n🎯 TOTAL ISSUES TO FIX: {total_issues}")
    
    if total_issues == 0:
        print("🎉 PLATFORM IS AUDIT-COMPLIANT!")
    else:
        print("🔧 REMEDIATION REQUIRED")
    
    print("\n📁 Results saved to:")
    print("  - comprehensive_600_endpoint_audit_results.json")
    print("  - COMPREHENSIVE_600_ENDPOINT_AUDIT_REPORT.md")

if __name__ == "__main__":
    asyncio.run(main())