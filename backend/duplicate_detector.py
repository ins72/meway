#!/usr/bin/env python3
"""
COMPREHENSIVE DUPLICATE FILE DETECTION AND CLEANUP SYSTEM
Identifies and resolves duplicate files, services, APIs, and conflicting routes
"""

import os
import re
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

class DuplicateDetector:
    def __init__(self):
        self.duplicate_files = []
        self.similar_files = []
        self.duplicate_services = []
        self.duplicate_apis = []
        self.conflicting_routes = []
        
    def scan_duplicate_files(self):
        """Find duplicate files by content and similar names"""
        print("🔍 SCANNING FOR DUPLICATE FILES...")
        
        # Find files by content hash
        content_hashes = defaultdict(list)
        
        # Scan API and Services directories
        for directory in ['api', 'services']:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py') and file != '__init__.py':
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    # Create hash of content
                                    content_hash = hashlib.md5(content.encode()).hexdigest()
                                    content_hashes[content_hash].append(file_path)
                            except Exception as e:
                                print(f"   Error reading {file_path}: {e}")
        
        # Find exact duplicates
        for hash_key, files in content_hashes.items():
            if len(files) > 1:
                self.duplicate_files.append({
                    'files': files,
                    'hash': hash_key,
                    'size': len(files)
                })
        
        # Find similar named files
        all_files = []
        for directory in ['api', 'services']:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py') and file != '__init__.py':
                            all_files.append(os.path.join(root, file))
        
        # Group by similar names
        name_groups = defaultdict(list)
        for file_path in all_files:
            base_name = os.path.basename(file_path)
            # Normalize name for comparison
            normalized = re.sub(r'[_-]', '', base_name.lower().replace('.py', ''))
            normalized = re.sub(r'(service|api|complete|system)$', '', normalized)
            name_groups[normalized].append(file_path)
        
        # Find similar files
        for normalized, files in name_groups.items():
            if len(files) > 1:
                self.similar_files.append({
                    'normalized_name': normalized,
                    'files': files,
                    'size': len(files)
                })
        
        print(f"   Found {len(self.duplicate_files)} exact duplicates")
        print(f"   Found {len(self.similar_files)} similar file groups")
    
    def scan_duplicate_services(self):
        """Find duplicate service classes and methods"""
        print("🔧 SCANNING FOR DUPLICATE SERVICES...")
        
        service_classes = defaultdict(list)
        service_methods = defaultdict(list)
        
        services_dir = Path('services')
        if services_dir.exists():
            for service_file in services_dir.glob('*.py'):
                if service_file.name == '__init__.py':
                    continue
                    
                try:
                    with open(service_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find service classes
                    class_matches = re.findall(r'class\s+(\w+)(?:Service)?(?:\s*\([^)]*\))?\s*:', content)
                    for class_name in class_matches:
                        service_classes[class_name].append(str(service_file))
                    
                    # Find service methods
                    method_matches = re.findall(r'(?:async\s+)?def\s+(\w+)\s*\([^)]*\)', content)
                    for method_name in method_matches:
                        if not method_name.startswith('_'):  # Skip private methods
                            service_methods[f"{service_file.stem}.{method_name}"].append(str(service_file))
                
                except Exception as e:
                    print(f"   Error reading {service_file}: {e}")
        
        # Find duplicate classes
        for class_name, files in service_classes.items():
            if len(files) > 1:
                self.duplicate_services.append({
                    'type': 'class',
                    'name': class_name,
                    'files': files,
                    'count': len(files)
                })
        
        print(f"   Found {len(self.duplicate_services)} duplicate service classes")
    
    def scan_duplicate_apis(self):
        """Find duplicate API routes and endpoints"""
        print("🌐 SCANNING FOR DUPLICATE API ROUTES...")
        
        api_routes = defaultdict(list)
        api_functions = defaultdict(list)
        
        api_dir = Path('api')
        if api_dir.exists():
            for api_file in api_dir.glob('*.py'):
                if api_file.name == '__init__.py':
                    continue
                    
                try:
                    with open(api_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find API routes
                    route_matches = re.findall(r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
                    for method, route in route_matches:
                        route_key = f"{method.upper()} {route}"
                        api_routes[route_key].append(str(api_file))
                    
                    # Find API functions
                    function_matches = re.findall(r'(?:async\s+)?def\s+(\w+)\s*\([^)]*\)', content)
                    for func_name in function_matches:
                        if not func_name.startswith('_'):
                            api_functions[func_name].append(str(api_file))
                
                except Exception as e:
                    print(f"   Error reading {api_file}: {e}")
        
        # Find conflicting routes
        for route_key, files in api_routes.items():
            if len(files) > 1:
                self.conflicting_routes.append({
                    'route': route_key,
                    'files': files,
                    'count': len(files)
                })
        
        # Find duplicate API functions
        for func_name, files in api_functions.items():
            if len(files) > 1:
                self.duplicate_apis.append({
                    'type': 'function',
                    'name': func_name,
                    'files': files,
                    'count': len(files)
                })
        
        print(f"   Found {len(self.conflicting_routes)} conflicting routes")
        print(f"   Found {len(self.duplicate_apis)} duplicate API functions")
    
    def display_results(self):
        """Display all found duplicates"""
        print("\n" + "="*80)
        print("🎯 DUPLICATE DETECTION RESULTS")
        print("="*80)
        
        total_issues = len(self.duplicate_files) + len(self.similar_files) + len(self.duplicate_services) + len(self.duplicate_apis) + len(self.conflicting_routes)
        
        if total_issues == 0:
            print("✅ NO DUPLICATES FOUND - CLEAN CODEBASE!")
            return
        
        print(f"⚠️ FOUND {total_issues} DUPLICATE ISSUES")
        
        # Exact duplicate files
        if self.duplicate_files:
            print(f"\n🚨 EXACT DUPLICATE FILES ({len(self.duplicate_files)} groups):")
            for i, dup in enumerate(self.duplicate_files, 1):
                print(f"   {i}. Duplicate group ({dup['size']} files):")
                for file in dup['files']:
                    print(f"      - {file}")
        
        # Similar named files
        if self.similar_files:
            print(f"\n⚠️ SIMILAR NAMED FILES ({len(self.similar_files)} groups):")
            for i, sim in enumerate(self.similar_files, 1):
                print(f"   {i}. Similar to '{sim['normalized_name']}' ({sim['size']} files):")
                for file in sim['files']:
                    print(f"      - {file}")
        
        # Duplicate services
        if self.duplicate_services:
            print(f"\n🔧 DUPLICATE SERVICE CLASSES ({len(self.duplicate_services)}):")
            for i, dup in enumerate(self.duplicate_services, 1):
                print(f"   {i}. Class '{dup['name']}' appears in {dup['count']} files:")
                for file in dup['files']:
                    print(f"      - {file}")
        
        # Conflicting routes
        if self.conflicting_routes:
            print(f"\n🌐 CONFLICTING API ROUTES ({len(self.conflicting_routes)}):")
            for i, conflict in enumerate(self.conflicting_routes, 1):
                print(f"   {i}. Route '{conflict['route']}' defined in {conflict['count']} files:")
                for file in conflict['files']:
                    print(f"      - {file}")
        
        # Duplicate API functions
        if self.duplicate_apis:
            print(f"\n📡 DUPLICATE API FUNCTIONS ({len(self.duplicate_apis)}):")
            for i, dup in enumerate(self.duplicate_apis, 1):
                print(f"   {i}. Function '{dup['name']}' appears in {dup['count']} files:")
                for file in dup['files']:
                    print(f"      - {file}")
    
    def generate_cleanup_recommendations(self):
        """Generate recommendations for cleaning up duplicates"""
        print("\n" + "="*80)
        print("🧹 CLEANUP RECOMMENDATIONS")
        print("="*80)
        
        recommendations = []
        
        # Exact duplicates - safe to remove
        if self.duplicate_files:
            recommendations.append("CRITICAL: Remove exact duplicate files (keep only one copy)")
            for dup in self.duplicate_files:
                recommendations.append(f"  - Keep: {dup['files'][0]}")
                for file in dup['files'][1:]:
                    recommendations.append(f"  - DELETE: {file}")
        
        # Conflicting routes - critical issue
        if self.conflicting_routes:
            recommendations.append("CRITICAL: Resolve conflicting API routes (will cause 405/500 errors)")
            for conflict in self.conflicting_routes:
                recommendations.append(f"  Route {conflict['route']} conflicts in:")
                for file in conflict['files']:
                    recommendations.append(f"    - {file}")
        
        # Similar files - review needed
        if self.similar_files:
            recommendations.append("REVIEW: Check similar named files for consolidation opportunities")
            for sim in self.similar_files:
                if sim['size'] > 3:  # More than 3 similar files
                    recommendations.append(f"  - Review {sim['normalized_name']} group ({sim['size']} files)")
        
        if recommendations:
            for rec in recommendations:
                print(rec)
        else:
            print("✅ No cleanup needed - codebase is clean!")
        
        return recommendations
    
    def run_full_scan(self):
        """Run complete duplicate detection"""
        print("🎯 COMPREHENSIVE DUPLICATE DETECTION - JANUARY 2025")
        print("="*80)
        
        self.scan_duplicate_files()
        self.scan_duplicate_services()
        self.scan_duplicate_apis()
        self.display_results()
        recommendations = self.generate_cleanup_recommendations()
        
        return {
            'duplicate_files': self.duplicate_files,
            'similar_files': self.similar_files,
            'duplicate_services': self.duplicate_services,
            'duplicate_apis': self.duplicate_apis,
            'conflicting_routes': self.conflicting_routes,
            'recommendations': recommendations,
            'total_issues': len(self.duplicate_files) + len(self.similar_files) + len(self.duplicate_services) + len(self.duplicate_apis) + len(self.conflicting_routes)
        }

def main():
    detector = DuplicateDetector()
    results = detector.run_full_scan()
    
    if results['total_issues'] > 0:
        print(f"\n🎯 SUMMARY: Found {results['total_issues']} duplicate issues")
        print("📋 Next steps:")
        print("1. Review the recommendations above")
        print("2. Remove exact duplicate files")
        print("3. Resolve conflicting API routes")
        print("4. Consolidate similar services if appropriate")
        print("5. Test the system after cleanup")
    else:
        print("\n🎉 CLEAN CODEBASE - No duplicates found!")
    
    return results

if __name__ == "__main__":
    main()