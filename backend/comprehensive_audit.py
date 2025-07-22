#!/usr/bin/env python3
"""
Comprehensive Audit Script for Mewayz Platform
Identifies duplicates, missing pairs, and cleanup opportunities
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

def extract_function_names(file_path):
    """Extract function names from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Find all function definitions
        functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
        return functions
    except Exception as e:
        return []

def extract_endpoints(file_path):
    """Extract FastAPI endpoints from an API file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Find all HTTP method decorators
        endpoints = re.findall(r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)', content)
        return endpoints
    except Exception as e:
        return []

def get_file_stats(file_path):
    """Get basic file statistics"""
    try:
        stat = os.stat(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        return {
            'size': stat.st_size,
            'lines': lines,
            'modified': stat.st_mtime
        }
    except Exception:
        return {'size': 0, 'lines': 0, 'modified': 0}

def analyze_directory(base_path):
    """Analyze all Python files in the backend directory"""
    results = {
        'api_files': {},
        'service_files': {},
        'duplicates': defaultdict(list),
        'missing_pairs': [],
        'instagram_files': [],
        'random_data_files': [],
        'total_endpoints': 0
    }
    
    backend_path = Path(base_path)
    
    # Analyze API files
    api_dir = backend_path / 'api'
    if api_dir.exists():
        for file_path in api_dir.glob('*.py'):
            if file_path.name == '__init__.py':
                continue
                
            file_info = {
                'path': str(file_path),
                'stats': get_file_stats(file_path),
                'endpoints': extract_endpoints(file_path),
                'functions': extract_function_names(file_path)
            }
            results['api_files'][file_path.stem] = file_info
            results['total_endpoints'] += len(file_info['endpoints'])
            
            # Check for Instagram references
            if 'instagram' in file_path.name.lower():
                results['instagram_files'].append(str(file_path))
    
    # Analyze Service files  
    services_dir = backend_path / 'services'
    if services_dir.exists():
        for file_path in services_dir.glob('*.py'):
            if file_path.name == '__init__.py':
                continue
                
            file_info = {
                'path': str(file_path),
                'stats': get_file_stats(file_path),
                'functions': extract_function_names(file_path)
            }
            results['service_files'][file_path.stem] = file_info
            
            # Check for Instagram references
            if 'instagram' in file_path.name.lower():
                results['instagram_files'].append(str(file_path))
    
    # Identify duplicates by analyzing similar names
    all_files = list(results['api_files'].keys()) + list(results['service_files'].keys())
    
    # Group similar files
    similarity_groups = defaultdict(list)
    for filename in all_files:
        # Extract base name patterns
        base_name = re.sub(r'_(api|service)$', '', filename)
        base_name = re.sub(r'^(complete_|advanced_|real_|comprehensive_|enhanced_|professional_)', '', base_name)
        similarity_groups[base_name].append(filename)
    
    # Identify duplicates (groups with more than 1 file)
    for base_name, files in similarity_groups.items():
        if len(files) > 1:
            results['duplicates'][base_name] = files
    
    # Find missing service/API pairs
    api_names = set(results['api_files'].keys())
    service_names = set(results['service_files'].keys())
    
    # Check for APIs without services
    for api_name in api_names:
        service_variants = [
            api_name + '_service',
            api_name.replace('_api', '_service'),
            re.sub(r'^complete_', 'complete_', api_name) + '_service'
        ]
        if not any(variant in service_names for variant in service_variants):
            results['missing_pairs'].append(f"API '{api_name}' has no corresponding service")
    
    # Check for services without APIs  
    for service_name in service_names:
        api_variants = [
            service_name.replace('_service', ''),
            service_name.replace('_service', '_api'),
            re.sub(r'_service$', '', service_name)
        ]
        if not any(variant in api_names for variant in api_variants):
            results['missing_pairs'].append(f"Service '{service_name}' has no corresponding API")
    
    return results

def generate_report(results):
    """Generate a comprehensive audit report"""
    report = []
    report.append("=" * 80)
    report.append("MEWAYZ PLATFORM COMPREHENSIVE AUDIT REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary Statistics
    report.append(f"📊 SUMMARY STATISTICS:")
    report.append(f"   • API Files: {len(results['api_files'])}")
    report.append(f"   • Service Files: {len(results['service_files'])}")
    report.append(f"   • Total Endpoints: {results['total_endpoints']}")
    report.append(f"   • Duplicate Groups: {len(results['duplicates'])}")
    report.append(f"   • Missing Pairs: {len(results['missing_pairs'])}")
    report.append(f"   • Instagram Files: {len(results['instagram_files'])}")
    report.append("")
    
    # Duplicates Analysis
    if results['duplicates']:
        report.append("🔍 DUPLICATE FILES IDENTIFIED:")
        report.append("-" * 40)
        for base_name, files in results['duplicates'].items():
            report.append(f"   {base_name.upper()}:")
            for file in files:
                file_type = "API" if file in results['api_files'] else "SERVICE"
                if file in results['api_files']:
                    endpoint_count = len(results['api_files'][file]['endpoints'])
                    report.append(f"     • {file} ({file_type}) - {endpoint_count} endpoints")
                else:
                    function_count = len(results['service_files'][file]['functions'])
                    report.append(f"     • {file} ({file_type}) - {function_count} functions")
        report.append("")
    
    # Missing Pairs
    if results['missing_pairs']:
        report.append("⚠️  MISSING SERVICE/API PAIRS:")
        report.append("-" * 40)
        for missing in results['missing_pairs']:
            report.append(f"   • {missing}")
        report.append("")
    
    # Instagram Files (to be replaced with TikTok/X)
    if results['instagram_files']:
        report.append("📱 INSTAGRAM FILES TO REPLACE WITH TIKTOK/X:")
        report.append("-" * 40)
        for file in results['instagram_files']:
            report.append(f"   • {file}")
        report.append("")
    
    # Top Files by Endpoint Count
    api_by_endpoints = sorted(results['api_files'].items(), 
                             key=lambda x: len(x[1]['endpoints']), reverse=True)
    report.append("🔝 TOP API FILES BY ENDPOINT COUNT:")
    report.append("-" * 40)
    for name, info in api_by_endpoints[:10]:
        endpoint_count = len(info['endpoints'])
        report.append(f"   • {name}: {endpoint_count} endpoints")
    report.append("")
    
    # Cleanup Recommendations
    report.append("🧹 CLEANUP RECOMMENDATIONS:")
    report.append("-" * 40)
    report.append("1. MERGE DUPLICATES:")
    for base_name, files in results['duplicates'].items():
        if len(files) > 1:
            report.append(f"   • Merge {', '.join(files)} into single implementation")
    
    report.append("\n2. CREATE MISSING PAIRS:")
    for missing in results['missing_pairs']:
        report.append(f"   • {missing}")
    
    report.append("\n3. REPLACE INSTAGRAM WITH TIKTOK/X:")
    for file in results['instagram_files']:
        new_name = file.replace('instagram', 'social_media_leads')
        report.append(f"   • Replace {os.path.basename(file)} with TikTok/X variant")
    
    return "\n".join(report)

if __name__ == "__main__":
    # Run the audit
    results = analyze_directory('/app/backend')
    
    # Generate and save report
    report = generate_report(results)
    print(report)
    
    # Save detailed results as JSON for further processing
    with open('/app/backend/audit_results.json', 'w') as f:
        # Make results JSON serializable
        clean_results = {
            'summary': {
                'api_files_count': len(results['api_files']),
                'service_files_count': len(results['service_files']),
                'total_endpoints': results['total_endpoints'],
                'duplicate_groups': len(results['duplicates']),
                'missing_pairs_count': len(results['missing_pairs']),
                'instagram_files_count': len(results['instagram_files'])
            },
            'duplicates': dict(results['duplicates']),
            'missing_pairs': results['missing_pairs'],
            'instagram_files': results['instagram_files']
        }
        json.dump(clean_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend/audit_results.json")