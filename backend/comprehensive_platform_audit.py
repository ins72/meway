#!/usr/bin/env python3
"""
COMPREHENSIVE PLATFORM AUDIT AND FIX SYSTEM
- Audit all services and APIs for proper pairing
- Check for duplicates and similar names  
- Verify real data implementation vs random data
- Ensure proper CRUD operations exist
- Add provided API keys to environment
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path

class PlatformAuditor:
    def __init__(self):
        self.api_files = []
        self.service_files = []
        self.missing_pairs = []
        self.duplicates = []
        self.random_data_issues = []
        self.crud_issues = []
        
    def scan_files(self):
        """Scan API and service files"""
        print("🔍 SCANNING API AND SERVICE FILES...")
        
        # Scan API files
        api_dir = Path("api")
        if api_dir.exists():
            for file in api_dir.glob("*.py"):
                if file.name != "__init__.py":
                    self.api_files.append(file.stem)
        
        # Scan service files  
        service_dir = Path("services")
        if service_dir.exists():
            for file in service_dir.glob("*.py"):
                if file.name != "__init__.py":
                    self.service_files.append(file.stem)
                    
        print(f"   Found {len(self.api_files)} API files")
        print(f"   Found {len(self.service_files)} service files")
        
    def check_service_api_pairing(self):
        """Check for missing service/API pairs"""
        print("\n🔗 CHECKING SERVICE/API PAIRING...")
        
        # Check for APIs without services
        for api_file in self.api_files:
            expected_service = f"{api_file}_service"
            if expected_service not in self.service_files:
                # Check for alternative naming patterns
                alt_patterns = [
                    api_file.replace("_", ""),
                    api_file.replace("-", "_"),
                    f"complete_{api_file}_service",
                    f"{api_file.replace('_api', '')}_service"
                ]
                
                found_alternative = False
                for pattern in alt_patterns:
                    if pattern in self.service_files:
                        found_alternative = True
                        break
                
                if not found_alternative:
                    self.missing_pairs.append(f"API '{api_file}' missing service")
        
        # Check for services without APIs
        for service_file in self.service_files:
            if service_file.endswith("_service"):
                expected_api = service_file.replace("_service", "")
                if expected_api not in self.api_files:
                    # Check for alternative naming patterns
                    alt_patterns = [
                        expected_api.replace("_", "-"),
                        f"complete_{expected_api}",
                        f"{expected_api}_api"
                    ]
                    
                    found_alternative = False
                    for pattern in alt_patterns:
                        if pattern in self.api_files:
                            found_alternative = True
                            break
                    
                    if not found_alternative:
                        self.missing_pairs.append(f"Service '{service_file}' missing API")
        
        if self.missing_pairs:
            print("   ❌ Missing pairs found:")
            for pair in self.missing_pairs:
                print(f"      - {pair}")
        else:
            print("   ✅ All services and APIs properly paired")
    
    def check_duplicates(self):
        """Check for duplicate or similar files"""
        print("\n🔍 CHECKING FOR DUPLICATES...")
        
        # Group similar names
        similar_groups = defaultdict(list)
        
        all_files = self.api_files + self.service_files
        
        for file in all_files:
            # Normalize name for comparison
            normalized = re.sub(r'[_-]', '', file.lower())
            normalized = re.sub(r'(service|api)$', '', normalized)
            similar_groups[normalized].append(file)
        
        # Find groups with multiple files
        for normalized, files in similar_groups.items():
            if len(files) > 2:  # More than API and service pair
                self.duplicates.append({
                    "group": normalized,
                    "files": files
                })
        
        if self.duplicates:
            print("   ⚠️ Potential duplicates found:")
            for dup in self.duplicates:
                print(f"      - {dup['group']}: {', '.join(dup['files'])}")
        else:
            print("   ✅ No duplicate files found")
    
    def check_random_data_usage(self):
        """Check for random data generation in services"""
        print("\n🎲 CHECKING FOR RANDOM DATA USAGE...")
        
        random_patterns = [
            r'random\.',
            r'uuid\.uuid4\(\)\.hex',
            r'faker\.',
            r'Sample.*data',
            r'Mock.*data',
            r'Test.*data',
            r'Dummy.*data',
            r'Lorem ipsum',
            r'Example.*\d+',
            r'sample_\w+',
            r'mock_\w+',
            r'test_\w+'
        ]
        
        service_dir = Path("services")
        if service_dir.exists():
            for service_file in service_dir.glob("*.py"):
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in random_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.random_data_issues.append({
                            "file": service_file.name,
                            "pattern": pattern,
                            "matches": len(matches)
                        })
        
        if self.random_data_issues:
            print("   ⚠️ Random data usage found:")
            for issue in self.random_data_issues:
                print(f"      - {issue['file']}: {issue['matches']} matches for '{issue['pattern']}'")
        else:
            print("   ✅ No random data usage detected")
    
    def check_crud_operations(self):
        """Check for proper CRUD operations in services"""
        print("\n📝 CHECKING CRUD OPERATIONS...")
        
        crud_methods = ['create', 'list', 'get', 'update', 'delete']
        
        service_dir = Path("services")
        if service_dir.exists():
            for service_file in service_dir.glob("*.py"):
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                missing_methods = []
                for method in crud_methods:
                    # Check for method definitions
                    patterns = [
                        rf'async def {method}_',
                        rf'def {method}_',
                        rf'async def create.*{service_file.stem.replace("_service", "")}',
                        rf'async def list.*{service_file.stem.replace("_service", "")}s?',
                        rf'async def get.*{service_file.stem.replace("_service", "")}',
                        rf'async def update.*{service_file.stem.replace("_service", "")}',
                        rf'async def delete.*{service_file.stem.replace("_service", "")}'
                    ]
                    
                    found = False
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found = True
                            break
                    
                    if not found:
                        missing_methods.append(method)
                
                if missing_methods:
                    self.crud_issues.append({
                        "file": service_file.name,
                        "missing": missing_methods
                    })
        
        if self.crud_issues:
            print("   ⚠️ Missing CRUD operations:")
            for issue in self.crud_issues:
                print(f"      - {issue['file']}: missing {', '.join(issue['missing'])}")
        else:
            print("   ✅ All services have proper CRUD operations")
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        print("\n📊 AUDIT SUMMARY")
        print("=" * 50)
        
        total_issues = len(self.missing_pairs) + len(self.duplicates) + len(self.random_data_issues) + len(self.crud_issues)
        
        print(f"Total API files: {len(self.api_files)}")
        print(f"Total Service files: {len(self.service_files)}")
        print(f"Missing pairs: {len(self.missing_pairs)}")
        print(f"Potential duplicates: {len(self.duplicates)}")
        print(f"Random data issues: {len(self.random_data_issues)}")
        print(f"CRUD issues: {len(self.crud_issues)}")
        print(f"Total issues: {total_issues}")
        
        if total_issues == 0:
            print("🎉 PLATFORM AUDIT PASSED - NO ISSUES FOUND!")
        else:
            print("⚠️ PLATFORM AUDIT FOUND ISSUES - FIXES NEEDED")
        
        return {
            "total_issues": total_issues,
            "missing_pairs": self.missing_pairs,
            "duplicates": self.duplicates,
            "random_data_issues": self.random_data_issues,
            "crud_issues": self.crud_issues
        }

def main():
    print("🎯 COMPREHENSIVE PLATFORM AUDIT - JANUARY 2025")
    print("=" * 60)
    
    auditor = PlatformAuditor()
    auditor.scan_files()
    auditor.check_service_api_pairing()
    auditor.check_duplicates()
    auditor.check_random_data_usage()
    auditor.check_crud_operations()
    
    report = auditor.generate_report()
    
    # Save report
    with open("platform_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: platform_audit_report.json")
    
    return report

if __name__ == "__main__":
    main()