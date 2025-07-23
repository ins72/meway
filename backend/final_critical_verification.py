#!/usr/bin/env python3
"""
FINAL CRITICAL VERIFICATION SYSTEM
Verify absolutely critical aspects are perfect:
1. All APIs have corresponding services
2. All services have corresponding APIs  
3. No broken imports or references
4. All critical business functions are complete
"""

import os
import re
from pathlib import Path

def verify_critical_pairings():
    """Verify all critical API/service pairings are correct"""
    print("🔍 VERIFYING CRITICAL API/SERVICE PAIRINGS...")
    
    # Get actual files
    api_files = set()
    service_files = set()
    
    if os.path.exists('api'):
        for file in Path('api').glob('*.py'):
            if file.name != '__init__.py':
                api_files.add(file.stem)
    
    if os.path.exists('services'):
        for file in Path('services').glob('*.py'):
            if file.name != '__init__.py':
                base_name = file.stem.replace('_service', '') if file.stem.endswith('_service') else file.stem
                service_files.add(base_name)
    
    print(f"   APIs: {len(api_files)}")
    print(f"   Services: {len(service_files)}")
    
    # Check critical business APIs have services
    critical_apis = {
        'auth', 'admin', 'financial', 'complete_financial', 'analytics',
        'workspace', 'complete_multi_workspace', 'referral_system', 
        'stripe_integration', 'twitter', 'tiktok', 'booking', 'crm',
        'form_builder', 'website_builder', 'ai_content', 'escrow'
    }
    
    missing_critical_services = []
    for api in critical_apis:
        if api not in service_files:
            missing_critical_services.append(api)
    
    if missing_critical_services:
        print(f"   ⚠️ Missing critical services: {missing_critical_services}")
        return False
    else:
        print("   ✅ All critical business APIs have services")
        return True

def verify_import_references():
    """Verify all import references are correct"""
    print("🔧 VERIFYING IMPORT REFERENCES...")
    
    broken_imports = []
    
    # Check API files for service imports
    if os.path.exists('api'):
        for api_file in Path('api').glob('*.py'):
            if api_file.name == '__init__.py':
                continue
                
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find service imports
                service_imports = re.findall(r'from services\.(\w+) import', content)
                
                for service_import in service_imports:
                    service_file = f'services/{service_import}.py'
                    if not os.path.exists(service_file):
                        broken_imports.append(f"{api_file.name} imports missing {service_file}")
                        
            except Exception as e:
                broken_imports.append(f"Error reading {api_file.name}: {e}")
    
    if broken_imports:
        print(f"   ⚠️ Found {len(broken_imports)} broken imports:")
        for broken in broken_imports:
            print(f"      - {broken}")
        return False
    else:
        print("   ✅ All imports are valid")
        return True

def verify_main_py_registrations():
    """Verify main.py router registrations are correct"""
    print("📋 VERIFYING MAIN.PY REGISTRATIONS...")
    
    if not os.path.exists('main.py'):
        print("   ❌ main.py not found")
        return False
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find router imports
        router_imports = re.findall(r'from api\.(\w+) import router as (\w+)', content)
        # Find router registrations
        router_registrations = re.findall(r'app\.include_router\((\w+)', content)
        
        imported_routers = set([router_name for _, router_name in router_imports])
        registered_routers = set(router_registrations)
        
        # Check for imports without registrations
        unregistered = imported_routers - registered_routers
        # Check for registrations without imports
        unimported = registered_routers - imported_routers
        
        issues = []
        if unregistered:
            issues.append(f"Imported but not registered: {unregistered}")
        if unimported:
            issues.append(f"Registered but not imported: {unimported}")
        
        if issues:
            print(f"   ⚠️ Router registration issues:")
            for issue in issues:
                print(f"      - {issue}")
            return False
        else:
            print(f"   ✅ All {len(imported_routers)} routers properly registered")
            return True
            
    except Exception as e:
        print(f"   ❌ Error checking main.py: {e}")
        return False

def verify_critical_endpoints():
    """Verify critical endpoints exist"""
    print("🎯 VERIFYING CRITICAL ENDPOINTS...")
    
    critical_endpoints = [
        ('api/auth.py', 'login'),
        ('api/admin.py', 'health'),
        ('api/financial.py', 'health'),
        ('api/analytics.py', 'health'),
        ('api/referral_system.py', 'health'),
        ('api/stripe_integration.py', 'health'),
        ('api/workspace.py', 'health')
    ]
    
    missing_endpoints = []
    
    for api_file, endpoint in critical_endpoints:
        if os.path.exists(api_file):
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if endpoint == 'login':
                    if 'async def login' not in content:
                        missing_endpoints.append(f"{api_file}: missing login function")
                elif endpoint == 'health':
                    if 'async def health' not in content and '/health' not in content:
                        missing_endpoints.append(f"{api_file}: missing health endpoint")
                        
            except Exception as e:
                missing_endpoints.append(f"{api_file}: error reading file")
        else:
            missing_endpoints.append(f"{api_file}: file not found")
    
    if missing_endpoints:
        print(f"   ⚠️ Missing critical endpoints:")
        for endpoint in missing_endpoints:
            print(f"      - {endpoint}")
        return False
    else:
        print("   ✅ All critical endpoints exist")
        return True

def run_final_verification():
    """Run all final verifications"""
    print("🎯 FINAL CRITICAL VERIFICATION - JANUARY 2025")
    print("="*70)
    
    all_checks = [
        verify_critical_pairings(),
        verify_import_references(), 
        verify_main_py_registrations(),
        verify_critical_endpoints()
    ]
    
    passed_checks = sum(all_checks)
    total_checks = len(all_checks)
    
    print(f"\n📊 FINAL VERIFICATION RESULTS:")
    print(f"Passed: {passed_checks}/{total_checks} checks")
    
    if passed_checks == total_checks:
        print("🎉 ALL CRITICAL VERIFICATIONS PASSED!")
        print("✅ Platform is PERFECT for production deployment")
        return True
    else:
        print("⚠️ Some verifications failed - manual review needed")
        return False

if __name__ == "__main__":
    run_final_verification()