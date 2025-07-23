#!/usr/bin/env python3
"""
COMPREHENSIVE MEWAYZ PLATFORM AUDIT SCRIPT
Performs complete audit of API endpoints, services, data sources, and CRUD operations
"""

import os
import re
import ast
import json
import inspect
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, Counter

class MewayzPlatformAuditor:
    def __init__(self, base_path="/app/backend"):
        self.base_path = base_path
        self.results = {
            "summary": {},
            "api_endpoints": {},
            "services": {},
            "data_sources": {},
            "crud_operations": {},
            "duplicates": {},
            "mock_data": {},
            "missing_implementations": {}
        }
    
    def audit_api_endpoints(self):
        """Count and analyze all API endpoints in the codebase"""
        print("\n🔍 AUDITING API ENDPOINTS...")
        
        api_path = os.path.join(self.base_path, "api")
        endpoint_count = 0
        endpoints_by_file = {}
        all_endpoints = []
        
        for filename in os.listdir(api_path):
            if filename.endswith('.py') and filename != '__init__.py':
                file_path = os.path.join(api_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count HTTP method decorators
                    http_methods = ['@router.get', '@router.post', '@router.put', 
                                  '@router.delete', '@router.patch', '@app.get', 
                                  '@app.post', '@app.put', '@app.delete', '@app.patch']
                    
                    file_endpoints = []
                    for method in http_methods:
                        matches = re.findall(rf'{method}\("([^"]+)"', content)
                        for match in matches:
                            endpoint_count += 1
                            endpoint_info = {
                                "path": match,
                                "method": method.split('.')[-1],
                                "file": filename,
                                "full_path": f"{method.split('.')[-1].upper()} {match}"
                            }
                            file_endpoints.append(endpoint_info)
                            all_endpoints.append(endpoint_info)
                    
                    if file_endpoints:
                        endpoints_by_file[filename] = {
                            "count": len(file_endpoints),
                            "endpoints": file_endpoints
                        }
                        
                except Exception as e:
                    print(f"  ❌ Error reading {filename}: {str(e)}")
        
        self.results["api_endpoints"] = {
            "total_count": endpoint_count,
            "files_with_endpoints": len(endpoints_by_file),
            "endpoints_by_file": endpoints_by_file,
            "all_endpoints": all_endpoints
        }
        
        print(f"  📊 Found {endpoint_count} API endpoints across {len(endpoints_by_file)} files")
        return endpoint_count
    
    def audit_services(self):
        """Analyze all service files and their functions"""
        print("\n🔍 AUDITING SERVICES...")
        
        services_path = os.path.join(self.base_path, "services")
        service_count = 0
        services_info = {}
        
        for filename in os.listdir(services_path):
            if filename.endswith('.py') and filename != '__init__.py':
                file_path = os.path.join(services_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count functions
                    functions = re.findall(r'^def\s+(\w+)\(', content, re.MULTILINE)
                    async_functions = re.findall(r'^async def\s+(\w+)\(', content, re.MULTILINE)
                    
                    service_count += 1
                    services_info[filename] = {
                        "functions": len(functions),
                        "async_functions": len(async_functions),
                        "total_functions": len(functions) + len(async_functions),
                        "function_names": functions + async_functions
                    }
                    
                except Exception as e:
                    print(f"  ❌ Error reading {filename}: {str(e)}")
        
        total_functions = sum(info["total_functions"] for info in services_info.values())
        
        self.results["services"] = {
            "total_service_files": service_count,
            "total_functions": total_functions,
            "services_info": services_info
        }
        
        print(f"  📊 Found {service_count} service files with {total_functions} total functions")
        return service_count, total_functions
    
    def find_duplicates(self):
        """Find duplicate files and similar function names"""
        print("\n🔍 FINDING DUPLICATES...")
        
        # Find duplicate API files
        api_files = set()
        duplicate_apis = []
        
        for filename in os.listdir(os.path.join(self.base_path, "api")):
            if filename.endswith('.py'):
                # Normalize filename to find potential duplicates
                normalized = re.sub(r'(complete_|advanced_|real_)', '', filename)
                if normalized in api_files:
                    duplicate_apis.append(filename)
                api_files.add(normalized)
        
        # Find duplicate service files
        service_files = set()
        duplicate_services = []
        
        for filename in os.listdir(os.path.join(self.base_path, "services")):
            if filename.endswith('.py'):
                normalized = re.sub(r'(complete_|advanced_|real_)', '', filename)
                if normalized in service_files:
                    duplicate_services.append(filename)
                service_files.add(normalized)
        
        self.results["duplicates"] = {
            "duplicate_api_files": duplicate_apis,
            "duplicate_service_files": duplicate_services,
            "total_duplicates": len(duplicate_apis) + len(duplicate_services)
        }
        
        print(f"  📊 Found {len(duplicate_apis)} duplicate API files and {len(duplicate_services)} duplicate service files")
        return duplicate_apis, duplicate_services
    
    def scan_for_mock_data(self):
        """Scan for mock data patterns across all files"""
        print("\n🔍 SCANNING FOR MOCK DATA...")
        
        mock_patterns = [
            r'random\.',
            r'fake\.',
            r'sample_data',
            r'mock_',
            r'dummy_',
            r'test_data',
            r'placeholder',
            r'lorem ipsum',
            r'example\.com',
            r'user\d+@test\.',
            r'\["User \d+", "User \d+"\]',
            r'random\.choice',
            r'random\.randint',
            r'uuid\.uuid4\(\)\.hex',
            r'f"Sample|f"Example|f"Test'
        ]
        
        mock_data_found = {}
        total_mock_instances = 0
        
        # Scan API files
        for root, dirs, files in os.walk(self.base_path):
            for filename in files:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        file_mocks = []
                        for pattern in mock_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                file_mocks.extend(matches)
                                total_mock_instances += len(matches)
                        
                        if file_mocks:
                            relative_path = os.path.relpath(file_path, self.base_path)
                            mock_data_found[relative_path] = {
                                "instances": len(file_mocks),
                                "patterns": list(set(file_mocks))
                            }
                    
                    except Exception as e:
                        continue
        
        self.results["mock_data"] = {
            "total_instances": total_mock_instances,
            "files_with_mock_data": len(mock_data_found),
            "mock_data_by_file": mock_data_found
        }
        
        print(f"  📊 Found {total_mock_instances} mock data instances across {len(mock_data_found)} files")
        return total_mock_instances
    
    def analyze_crud_operations(self):
        """Analyze CRUD operations for all entities"""
        print("\n🔍 ANALYZING CRUD OPERATIONS...")
        
        crud_patterns = {
            "CREATE": [r'\.insert_one\(', r'\.insert_many\(', r'@router\.post'],
            "READ": [r'\.find_one\(', r'\.find\(', r'\.aggregate\(', r'@router\.get'],
            "UPDATE": [r'\.update_one\(', r'\.update_many\(', r'\.replace_one\(', r'@router\.put', r'@router\.patch'],
            "DELETE": [r'\.delete_one\(', r'\.delete_many\(', r'@router\.delete']
        }
        
        crud_by_file = {}
        total_crud_ops = 0
        
        for root, dirs, files in os.walk(self.base_path):
            for filename in files:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        file_crud = {}
                        for operation, patterns in crud_patterns.items():
                            count = 0
                            for pattern in patterns:
                                matches = re.findall(pattern, content)
                                count += len(matches)
                            
                            if count > 0:
                                file_crud[operation] = count
                                total_crud_ops += count
                        
                        if file_crud:
                            relative_path = os.path.relpath(file_path, self.base_path)
                            crud_by_file[relative_path] = file_crud
                    
                    except Exception as e:
                        continue
        
        self.results["crud_operations"] = {
            "total_crud_operations": total_crud_ops,
            "files_with_crud": len(crud_by_file),
            "crud_by_file": crud_by_file
        }
        
        print(f"  📊 Found {total_crud_ops} CRUD operations across {len(crud_by_file)} files")
        return total_crud_ops
    
    def analyze_data_sources(self):
        """Analyze data sources and external API integrations"""
        print("\n🔍 ANALYZING DATA SOURCES...")
        
        external_api_patterns = [
            r'openai\.',
            r'stripe\.',
            r'twitter\.',
            r'tiktok\.',
            r'instagram\.',
            r'facebook\.',
            r'google\.',
            r'elasticmail\.',
            r'httpx\.',
            r'requests\.',
            r'aiohttp\.'
        ]
        
        database_patterns = [
            r'db\[',
            r'collection\.',
            r'get_database\(',
            r'mongo',
            r'Motor'
        ]
        
        external_apis = {}
        database_usage = {}
        
        for root, dirs, files in os.walk(self.base_path):
            for filename in files:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for external APIs
                        api_matches = []
                        for pattern in external_api_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            api_matches.extend(matches)
                        
                        # Check for database usage
                        db_matches = []
                        for pattern in database_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            db_matches.extend(matches)
                        
                        relative_path = os.path.relpath(file_path, self.base_path)
                        
                        if api_matches:
                            external_apis[relative_path] = list(set(api_matches))
                        
                        if db_matches:
                            database_usage[relative_path] = list(set(db_matches))
                    
                    except Exception as e:
                        continue
        
        self.results["data_sources"] = {
            "external_apis": {
                "files_count": len(external_apis),
                "usage_by_file": external_apis
            },
            "database_usage": {
                "files_count": len(database_usage),
                "usage_by_file": database_usage
            }
        }
        
        print(f"  📊 Found external API usage in {len(external_apis)} files and database usage in {len(database_usage)} files")
        return len(external_apis), len(database_usage)
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        print("\n📋 GENERATING COMPREHENSIVE AUDIT REPORT...")
        
        # Run all audits
        endpoint_count = self.audit_api_endpoints()
        service_count, function_count = self.audit_services()
        duplicate_apis, duplicate_services = self.find_duplicates()
        mock_data_instances = self.scan_for_mock_data()
        crud_operations = self.analyze_crud_operations()
        api_files, db_files = self.analyze_data_sources()
        
        # Generate summary
        self.results["summary"] = {
            "platform_overview": {
                "total_api_endpoints": endpoint_count,
                "total_service_files": service_count,
                "total_service_functions": function_count,
                "total_crud_operations": crud_operations,
                "mock_data_instances": mock_data_instances,
                "duplicate_files": len(duplicate_apis) + len(duplicate_services),
                "files_with_external_apis": api_files,
                "files_with_database_usage": db_files
            },
            "data_quality": {
                "mock_data_status": "NEEDS ATTENTION" if mock_data_instances > 0 else "CLEAN",
                "duplicate_files_status": "NEEDS CLEANUP" if (len(duplicate_apis) + len(duplicate_services)) > 0 else "CLEAN",
                "crud_completeness": "PARTIAL" if crud_operations < endpoint_count else "COMPLETE"
            },
            "recommendations": []
        }
        
        # Add recommendations
        if mock_data_instances > 0:
            self.results["summary"]["recommendations"].append(f"Eliminate {mock_data_instances} mock data instances")
        
        if len(duplicate_apis) + len(duplicate_services) > 0:
            self.results["summary"]["recommendations"].append(f"Remove {len(duplicate_apis) + len(duplicate_services)} duplicate files")
        
        if crud_operations < endpoint_count:
            self.results["summary"]["recommendations"].append(f"Implement missing CRUD operations (have {crud_operations}, need ~{endpoint_count})")
        
        return self.results
    
    def save_report(self, filename="comprehensive_audit_report.json"):
        """Save audit report to JSON file"""
        output_path = os.path.join("/app", filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Audit report saved to {output_path}")
        return output_path

def main():
    """Main audit execution"""
    print("🚀 STARTING COMPREHENSIVE MEWAYZ PLATFORM AUDIT")
    print("=" * 60)
    
    auditor = MewayzPlatformAuditor()
    results = auditor.generate_report()
    report_path = auditor.save_report()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE AUDIT SUMMARY")
    print("=" * 60)
    
    summary = results["summary"]["platform_overview"]
    print(f"📍 Total API Endpoints: {summary['total_api_endpoints']}")
    print(f"📁 Service Files: {summary['total_service_files']}")
    print(f"⚙️  Service Functions: {summary['total_service_functions']}")
    print(f"🔄 CRUD Operations: {summary['total_crud_operations']}")
    print(f"🎭 Mock Data Instances: {summary['mock_data_instances']}")
    print(f"📋 Duplicate Files: {summary['duplicate_files']}")
    print(f"🌐 External API Usage: {summary['files_with_external_apis']} files")
    print(f"💾 Database Usage: {summary['files_with_database_usage']} files")
    
    print(f"\n📝 Report saved to: {report_path}")
    
    return results

if __name__ == "__main__":
    main()