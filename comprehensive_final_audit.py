#!/usr/bin/env python3
"""
COMPREHENSIVE FINAL AUDIT - MEWAYZ V2 PLATFORM
June 2025 - Complete audit for CRUD operations, mock data, duplicates, and missing pairs
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple
import glob

class ComprehensiveFinalAudit:
    def __init__(self):
        self.backend_path = "/app/backend"
        self.api_path = os.path.join(self.backend_path, "api")
        self.services_path = os.path.join(self.backend_path, "services") 
        self.models_path = os.path.join(self.backend_path, "models")
        
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "missing_crud_operations": [],
            "mock_hardcoded_data": [],
            "duplicate_files": [],
            "missing_pairs": {
                "services_without_apis": [],
                "apis_without_services": []
            },
            "statistics": {
                "total_api_files": 0,
                "total_service_files": 0,
                "crud_completeness": 0,
                "mock_data_instances": 0,
                "duplicate_file_sets": 0
            }
        }
        
    def audit_crud_operations(self):
        """Audit all services for missing CRUD operations"""
        print("🔍 AUDITING: CRUD Operations Completeness")
        
        # Get all service files
        service_files = glob.glob(os.path.join(self.services_path, "*.py"))
        self.audit_results["statistics"]["total_service_files"] = len(service_files)
        
        crud_operations = ["create", "read", "get", "update", "delete", "list"]
        
        for service_file in service_files:
            service_name = os.path.basename(service_file)[:-3]  # Remove .py
            
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for CRUD operations
                found_operations = {}
                for operation in crud_operations:
                    # Look for method definitions with CRUD operations
                    patterns = [
                        rf"async def {operation}_",
                        rf"def {operation}_",
                        rf"async def.*{operation}.*\(",
                        rf"def.*{operation}.*\("
                    ]
                    
                    found = False
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found = True
                            break
                    
                    found_operations[operation] = found
                
                # Identify missing operations
                missing_ops = [op for op, found in found_operations.items() if not found]
                
                if missing_ops:
                    self.audit_results["missing_crud_operations"].append({
                        "service": service_name,
                        "file_path": service_file,
                        "missing_operations": missing_ops,
                        "found_operations": [op for op, found in found_operations.items() if found],
                        "completeness_percentage": (len([op for op in found_operations.values() if op]) / len(crud_operations)) * 100
                    })
                
            except Exception as e:
                print(f"  ❌ Error reading {service_file}: {e}")
        
        print(f"  📊 Found {len(self.audit_results['missing_crud_operations'])} services with incomplete CRUD operations")
    
    def audit_mock_hardcoded_data(self):
        """Audit for mock, random, or hardcoded data"""
        print("🔍 AUDITING: Mock/Random/Hardcoded Data")
        
        # Patterns to look for
        mock_patterns = [
            r"mock_\w+",
            r"fake_\w+", 
            r"dummy_\w+",
            r"sample_\w+",
            r"test_\w+",
            r"random\.\w+",
            r"randint\(",
            r"choice\(",
            r"uuid\.uuid4\(\).*str\(",
            r"\"example\.com\"",
            r"\"test@.*\.com\"",
            r"\"dummy.*\"",
            r"\"sample.*\"",
            r"\"mock.*\"",
            r"lorem ipsum",
            r"Lorem Ipsum",
            r"placeholder",
            r"hardcoded",
            r"temp_\w+",
            r"default_\w+.*=.*\".*\"",
        ]
        
        # Search in all Python files
        all_py_files = []
        for root, dirs, files in os.walk(self.backend_path):
            for file in files:
                if file.endswith('.py'):
                    all_py_files.append(os.path.join(root, file))
        
        total_mock_instances = 0
        
        for py_file in all_py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                file_mock_instances = []
                
                for i, line in enumerate(lines, 1):
                    for pattern in mock_patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            file_mock_instances.append({
                                "line_number": i,
                                "line_content": line.strip(),
                                "pattern_matched": pattern,
                                "match_text": match.group()
                            })
                
                if file_mock_instances:
                    self.audit_results["mock_hardcoded_data"].append({
                        "file_path": py_file,
                        "relative_path": os.path.relpath(py_file, self.backend_path),
                        "instances": file_mock_instances,
                        "count": len(file_mock_instances)
                    })
                    
                    total_mock_instances += len(file_mock_instances)
                
            except Exception as e:
                print(f"  ❌ Error reading {py_file}: {e}")
        
        self.audit_results["statistics"]["mock_data_instances"] = total_mock_instances
        print(f"  📊 Found {total_mock_instances} mock/hardcoded data instances in {len(self.audit_results['mock_hardcoded_data'])} files")
    
    def audit_duplicate_files(self):
        """Audit for duplicate or very similar files"""
        print("🔍 AUDITING: Duplicate and Similar Files")
        
        # Get all Python files
        all_py_files = []
        for root, dirs, files in os.walk(self.backend_path):
            for file in files:
                if file.endswith('.py'):
                    all_py_files.append(os.path.join(root, file))
        
        # Group files by similar names
        name_groups = {}
        
        for file_path in all_py_files:
            basename = os.path.basename(file_path)[:-3]  # Remove .py
            
            # Create normalized name for grouping
            normalized = re.sub(r'_?(complete|advanced|enhanced|improved|new|v2|final)_?', '', basename.lower())
            normalized = re.sub(r'_?(service|api|router|controller|manager)_?', '', normalized)
            
            if normalized not in name_groups:
                name_groups[normalized] = []
            name_groups[normalized].append(file_path)
        
        # Find groups with multiple files (potential duplicates)
        duplicate_groups = []
        for normalized_name, files in name_groups.items():
            if len(files) > 1:
                # Analyze file similarity
                file_data = []
                for file_path in files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        file_data.append({
                            "path": file_path,
                            "relative_path": os.path.relpath(file_path, self.backend_path),
                            "size": len(content),
                            "lines": len(content.split('\n')),
                            "functions": len(re.findall(r'def \w+', content)),
                            "classes": len(re.findall(r'class \w+', content)),
                            "async_functions": len(re.findall(r'async def \w+', content))
                        })
                    except Exception as e:
                        print(f"  ❌ Error reading {file_path}: {e}")
                
                if file_data:
                    duplicate_groups.append({
                        "normalized_name": normalized_name,
                        "files": file_data,
                        "similarity_score": self._calculate_similarity_score(file_data)
                    })
        
        self.audit_results["duplicate_files"] = duplicate_groups
        self.audit_results["statistics"]["duplicate_file_sets"] = len(duplicate_groups)
        print(f"  📊 Found {len(duplicate_groups)} sets of potentially duplicate files")
    
    def audit_missing_pairs(self):
        """Audit for services without APIs and APIs without services"""
        print("🔍 AUDITING: Missing Service-API Pairs")
        
        # Get all API files
        api_files = glob.glob(os.path.join(self.api_path, "*.py"))
        api_names = set()
        for api_file in api_files:
            basename = os.path.basename(api_file)[:-3]  # Remove .py
            # Normalize API name
            normalized = re.sub(r'_?(api|router|controller)_?', '', basename.lower())
            api_names.add(normalized)
        
        # Get all service files
        service_files = glob.glob(os.path.join(self.services_path, "*.py"))
        service_names = set()
        for service_file in service_files:
            basename = os.path.basename(service_file)[:-3]  # Remove .py
            # Normalize service name
            normalized = re.sub(r'_?(service|manager)_?', '', basename.lower())
            service_names.add(normalized)
        
        self.audit_results["statistics"]["total_api_files"] = len(api_files)
        
        # Find services without corresponding APIs
        services_without_apis = []
        for service_name in service_names:
            if service_name not in api_names:
                # Find the actual service file
                matching_files = [f for f in service_files if service_name in os.path.basename(f).lower()]
                if matching_files:
                    services_without_apis.append({
                        "service_name": service_name,
                        "service_file": matching_files[0],
                        "relative_path": os.path.relpath(matching_files[0], self.backend_path)
                    })
        
        # Find APIs without corresponding services
        apis_without_services = []
        for api_name in api_names:
            if api_name not in service_names:
                # Find the actual API file
                matching_files = [f for f in api_files if api_name in os.path.basename(f).lower()]
                if matching_files:
                    apis_without_services.append({
                        "api_name": api_name,
                        "api_file": matching_files[0],
                        "relative_path": os.path.relpath(matching_files[0], self.backend_path)
                    })
        
        self.audit_results["missing_pairs"]["services_without_apis"] = services_without_apis
        self.audit_results["missing_pairs"]["apis_without_services"] = apis_without_services
        
        print(f"  📊 Found {len(services_without_apis)} services without APIs")
        print(f"  📊 Found {len(apis_without_services)} APIs without services")
    
    def _calculate_similarity_score(self, file_data: List[Dict]) -> float:
        """Calculate similarity score between files"""
        if len(file_data) < 2:
            return 0.0
        
        # Simple similarity based on size, lines, functions, classes
        metrics = ['size', 'lines', 'functions', 'classes', 'async_functions']
        total_similarity = 0
        comparisons = 0
        
        for i in range(len(file_data)):
            for j in range(i + 1, len(file_data)):
                file1, file2 = file_data[i], file_data[j]
                file_similarity = 0
                
                for metric in metrics:
                    val1, val2 = file1.get(metric, 0), file2.get(metric, 0)
                    if val1 + val2 > 0:
                        similarity = 1 - abs(val1 - val2) / max(val1, val2, 1)
                        file_similarity += similarity
                
                total_similarity += file_similarity / len(metrics)
                comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0.0
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        report_path = "/app/comprehensive_final_audit_report.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        # Generate summary report
        summary_path = "/app/audit_summary_report.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# Comprehensive Final Audit Report\n")
            f.write(f"**Generated:** {self.audit_results['timestamp']}\n\n")
            
            f.write("## 📊 Statistics Summary\n")
            stats = self.audit_results['statistics']
            f.write(f"- **Total API Files:** {stats['total_api_files']}\n")
            f.write(f"- **Total Service Files:** {stats['total_service_files']}\n")
            f.write(f"- **Mock Data Instances:** {stats['mock_data_instances']}\n")
            f.write(f"- **Duplicate File Sets:** {stats['duplicate_file_sets']}\n\n")
            
            f.write("## 🔧 Issues Found\n")
            f.write(f"- **Incomplete CRUD Operations:** {len(self.audit_results['missing_crud_operations'])} services\n")
            f.write(f"- **Mock/Hardcoded Data:** {len(self.audit_results['mock_hardcoded_data'])} files\n")
            f.write(f"- **Services without APIs:** {len(self.audit_results['missing_pairs']['services_without_apis'])}\n")
            f.write(f"- **APIs without Services:** {len(self.audit_results['missing_pairs']['apis_without_services'])}\n\n")
            
            # Top issues by category
            if self.audit_results['missing_crud_operations']:
                f.write("### Most Incomplete CRUD Services\n")
                sorted_crud = sorted(self.audit_results['missing_crud_operations'], 
                                   key=lambda x: x['completeness_percentage'])
                for service in sorted_crud[:5]:
                    f.write(f"- **{service['service']}:** {service['completeness_percentage']:.1f}% complete\n")
                f.write("\n")
            
            if self.audit_results['mock_hardcoded_data']:
                f.write("### Files with Most Mock Data\n")
                sorted_mock = sorted(self.audit_results['mock_hardcoded_data'], 
                                   key=lambda x: x['count'], reverse=True)
                for file_info in sorted_mock[:5]:
                    f.write(f"- **{file_info['relative_path']}:** {file_info['count']} instances\n")
                f.write("\n")
        
        print(f"\n📁 Audit reports generated:")
        print(f"  📊 Detailed report: {report_path}")
        print(f"  📝 Summary report: {summary_path}")
        
        return report_path, summary_path
    
    def run_comprehensive_audit(self):
        """Run complete audit process"""
        print("🚀 STARTING COMPREHENSIVE FINAL AUDIT")
        print("=" * 60)
        
        self.audit_crud_operations()
        self.audit_mock_hardcoded_data() 
        self.audit_duplicate_files()
        self.audit_missing_pairs()
        
        report_paths = self.generate_audit_report()
        
        print("\n" + "=" * 60)
        print("📋 AUDIT SUMMARY")
        print("=" * 60)
        
        stats = self.audit_results['statistics']
        print(f"🗃️  Files Analyzed: {stats['total_api_files']} APIs, {stats['total_service_files']} Services")
        print(f"🔧 CRUD Issues: {len(self.audit_results['missing_crud_operations'])} services need completion")
        print(f"🎭 Mock Data: {stats['mock_data_instances']} instances in {len(self.audit_results['mock_hardcoded_data'])} files")
        print(f"📁 Duplicates: {stats['duplicate_file_sets']} sets of similar files found")
        print(f"🔗 Missing Pairs: {len(self.audit_results['missing_pairs']['services_without_apis'])} services without APIs")
        print(f"🔗 Missing Pairs: {len(self.audit_results['missing_pairs']['apis_without_services'])} APIs without services")
        
        return self.audit_results

def main():
    auditor = ComprehensiveFinalAudit()
    results = auditor.run_comprehensive_audit()
    
    print(f"\n✅ Comprehensive audit completed")
    print(f"🔍 Found {len(results['missing_crud_operations']) + len(results['mock_hardcoded_data']) + len(results['duplicate_files']) + len(results['missing_pairs']['services_without_apis']) + len(results['missing_pairs']['apis_without_services'])} total issues to address")
    
    return results

if __name__ == "__main__":
    main()