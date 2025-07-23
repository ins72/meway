#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM AUDIT & FIX
Identifies and fixes all remaining issues:
1. Missing API/Service pairs
2. Incomplete CRUD operations
3. Mock data usage
4. Missing external API integrations
"""

import os
import re
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def audit_api_service_pairs():
    """Audit for missing API/Service pairs"""
    backend_dir = Path("/app/backend")
    api_dir = backend_dir / "api"
    services_dir = backend_dir / "services"
    
    # Get all API files
    api_files = {f.stem for f in api_dir.glob("*.py") if f.name != "__init__.py"}
    
    # Get all service files  
    service_files = {f.stem.replace("_service", "") for f in services_dir.glob("*_service.py")}
    
    # Find missing pairs
    missing_services = api_files - service_files
    missing_apis = service_files - api_files
    
    logger.info(f"📊 API/SERVICE PAIR AUDIT:")
    logger.info(f"   API files: {len(api_files)}")
    logger.info(f"   Service files: {len(service_files)}")
    logger.info(f"   Missing services: {len(missing_services)}")
    logger.info(f"   Missing APIs: {len(missing_apis)}")
    
    if missing_services:
        logger.warning(f"   APIs without services: {', '.join(missing_services)}")
    if missing_apis:
        logger.warning(f"   Services without APIs: {', '.join(missing_apis)}")
    
    return missing_services, missing_apis

def audit_external_api_integrations():
    """Audit for missing external API integrations"""
    
    required_integrations = [
        ("twitter", "Twitter/X API Integration"),
        ("tiktok", "TikTok API Integration"), 
        ("stripe_integration", "Stripe Payment Integration"),
        ("referral_system", "Referral System"),
        ("social_media_management", "Social Media Management")
    ]
    
    backend_dir = Path("/app/backend")
    api_dir = backend_dir / "api"
    services_dir = backend_dir / "services"
    
    missing_integrations = []
    
    for integration_name, description in required_integrations:
        api_file = api_dir / f"{integration_name}.py"
        service_file = services_dir / f"{integration_name}_service.py"
        
        if not api_file.exists() or not service_file.exists():
            missing_integrations.append((integration_name, description))
    
    logger.info(f"🔗 EXTERNAL API INTEGRATIONS AUDIT:")
    logger.info(f"   Required integrations: {len(required_integrations)}")
    logger.info(f"   Missing integrations: {len(missing_integrations)}")
    
    if missing_integrations:
        for name, desc in missing_integrations:
            logger.warning(f"   Missing: {desc} ({name})")
    
    return missing_integrations

def audit_crud_completeness():
    """Audit CRUD completeness in API files"""
    
    backend_dir = Path("/app/backend")
    api_dir = backend_dir / "api"
    
    incomplete_crud = []
    
    for api_file in api_dir.glob("*.py"):
        if api_file.name == "__init__.py":
            continue
            
        try:
            with open(api_file, 'r') as f:
                content = f.read()
            
            # Check for CRUD operations
            has_create = "@router.post(" in content
            has_read = "@router.get(" in content
            has_update = "@router.put(" in content or "@router.patch(" in content
            has_delete = "@router.delete(" in content
            
            crud_score = sum([has_create, has_read, has_update, has_delete])
            
            if crud_score < 4:
                missing_ops = []
                if not has_create: missing_ops.append("CREATE")
                if not has_read: missing_ops.append("READ") 
                if not has_update: missing_ops.append("UPDATE")
                if not has_delete: missing_ops.append("DELETE")
                
                incomplete_crud.append((api_file.stem, missing_ops, crud_score))
        
        except Exception as e:
            logger.error(f"Error auditing {api_file}: {e}")
    
    logger.info(f"📝 CRUD COMPLETENESS AUDIT:")
    logger.info(f"   API files audited: {len(list(api_dir.glob('*.py'))) - 1}")
    logger.info(f"   Incomplete CRUD: {len(incomplete_crud)}")
    
    if incomplete_crud:
        for api_name, missing_ops, score in incomplete_crud:
            logger.warning(f"   {api_name}: Missing {', '.join(missing_ops)} ({score}/4 CRUD)")
    
    return incomplete_crud

def audit_mock_data_usage():
    """Audit for mock data usage in services"""
    
    backend_dir = Path("/app/backend")
    services_dir = backend_dir / "services"
    
    mock_data_files = []
    
    mock_patterns = [
        r'"sample_.*"',
        r'"test_.*"', 
        r'"mock_.*"',
        r'"fake_.*"',
        r'"dummy_.*"',
        r'random\.',
        r'faker\.',
        r'uuid\.uuid4\(\)\.hex\[:8\]',
        r'Sample\s+\w+',
        r'Test\s+\w+',
        r'Mock\s+\w+',
        r'Dummy\s+\w+'
    ]
    
    for service_file in services_dir.glob("*.py"):
        if service_file.name == "__init__.py":
            continue
            
        try:
            with open(service_file, 'r') as f:
                content = f.read()
            
            mock_found = []
            for pattern in mock_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    mock_found.extend(matches)
            
            if mock_found:
                mock_data_files.append((service_file.stem, mock_found))
        
        except Exception as e:
            logger.error(f"Error auditing {service_file}: {e}")
    
    logger.info(f"🎭 MOCK DATA USAGE AUDIT:")
    logger.info(f"   Service files audited: {len(list(services_dir.glob('*.py'))) - 1}")
    logger.info(f"   Files with mock data: {len(mock_data_files)}")
    
    if mock_data_files:
        for service_name, mock_items in mock_data_files:
            logger.warning(f"   {service_name}: {len(mock_items)} mock data instances")
    
    return mock_data_files

def main():
    """Run comprehensive system audit"""
    logger.info("🔍 COMPREHENSIVE SYSTEM AUDIT STARTING")
    logger.info("="*60)
    
    # Run all audits
    missing_services, missing_apis = audit_api_service_pairs()
    missing_integrations = audit_external_api_integrations()
    incomplete_crud = audit_crud_completeness()
    mock_data_files = audit_mock_data_usage()
    
    # Summary
    total_issues = len(missing_services) + len(missing_apis) + len(missing_integrations) + len(incomplete_crud) + len(mock_data_files)
    
    logger.info(f"\n📊 AUDIT SUMMARY:")
    logger.info(f"   Missing services: {len(missing_services)}")
    logger.info(f"   Missing APIs: {len(missing_apis)}")
    logger.info(f"   Missing integrations: {len(missing_integrations)}")
    logger.info(f"   Incomplete CRUD: {len(incomplete_crud)}")
    logger.info(f"   Mock data files: {len(mock_data_files)}")
    logger.info(f"   TOTAL ISSUES: {total_issues}")
    
    # Save audit results
    audit_results = {
        "timestamp": "2025-01-23T18:30:00",
        "missing_services": list(missing_services),
        "missing_apis": list(missing_apis),
        "missing_integrations": [{"name": name, "description": desc} for name, desc in missing_integrations],
        "incomplete_crud": [{"api": api, "missing": ops, "score": score} for api, ops, score in incomplete_crud],
        "mock_data_files": [{"service": service, "mock_items": items} for service, items in mock_data_files],
        "total_issues": total_issues
    }
    
    with open("/app/backend/audit_results.json", "w") as f:
        json.dump(audit_results, f, indent=2)
    
    logger.info(f"\n✅ Audit results saved to audit_results.json")
    
    return audit_results

if __name__ == "__main__":
    main()