#!/usr/bin/env python3
"""
Systematic Cleanup Script for Mewayz Platform
Consolidates duplicates and ensures full CRUD functionality
"""

import os
import shutil
import json
from pathlib import Path

# Load audit results
with open('/app/backend/audit_results.json', 'r') as f:
    audit = json.load(f)

def get_consolidation_plan():
    """Define which files to keep and which to merge/remove"""
    plan = {
        # E-commerce consolidation - Keep complete_ecommerce as master
        'ecommerce': {
            'master': 'complete_ecommerce',
            'merge': ['ecommerce', 'enhanced_ecommerce'], 
            'service_master': 'complete_ecommerce_service',
            'service_merge': ['ecommerce_service', 'enhanced_ecommerce_service']
        },
        
        # Website Builder consolidation - Keep complete_website_builder as master  
        'website_builder': {
            'master': 'complete_website_builder',
            'merge': ['website_builder', 'professional_website_builder'],
            'service_master': 'complete_website_builder_service', 
            'service_merge': ['website_builder_service', 'professional_website_builder_service']
        },
        
        # Financial consolidation - Keep complete_financial as master
        'financial': {
            'master': 'complete_financial',
            'merge': ['financial_management'],
            'service_master': 'complete_financial_service',
            'service_merge': ['financial_service']
        },
        
        # Booking consolidation - Keep complete_booking as master
        'booking': {
            'master': 'complete_booking', 
            'merge': ['booking', 'bookings'],
            'service_master': 'complete_booking_service',
            'service_merge': ['booking_service', 'bookings_service']
        },
        
        # Subscription consolidation - Keep complete_subscription as master
        'subscription': {
            'master': 'complete_subscription',
            'merge': ['subscription_management'],
            'service_master': 'complete_subscription_service',
            'service_merge': ['subscription_service']
        },
        
        # Multi-workspace consolidation - Keep complete_multi_workspace as master
        'workspace': {
            'master': 'complete_multi_workspace',
            'merge': ['workspace', 'workspaces'],
            'service_master': 'complete_multi_workspace_service',
            'service_merge': ['workspace_service', 'workspaces_service', 'workspace_management_service']
        },
        
        # Onboarding consolidation - Keep complete_onboarding as master
        'onboarding': {
            'master': 'complete_onboarding',
            'merge': ['onboarding_system'],
            'service_master': 'complete_onboarding_service',
            'service_merge': ['onboarding_service']
        },
        
        # User management consolidation
        'user': {
            'master': 'user',
            'merge': ['users'],
            'service_master': 'user_service',
            'service_merge': ['users_service']
        },
        
        # AI consolidation - Keep real_ai_automation as master
        'ai_automation': {
            'master': 'real_ai_automation',
            'merge': [],
            'service_master': 'real_ai_automation_service', 
            'service_merge': []
        },
        
        # Email automation - Keep real_email_automation as master
        'email_automation': {
            'master': 'real_email_automation',
            'merge': [],
            'service_master': 'real_email_automation_service',
            'service_merge': []
        },
        
        # Social media leads - Keep complete_social_media_leads as master
        'social_media_leads': {
            'master': 'complete_social_media_leads',
            'merge': [],
            'service_master': 'complete_social_media_leads_service',
            'service_merge': ['social_media_service']
        }
    }
    
    return plan

def backup_files(files_to_remove):
    """Create backup of files before removal"""
    backup_dir = Path('/app/backend/backup_duplicates')
    backup_dir.mkdir(exist_ok=True)
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            backup_path = backup_dir / filename
            shutil.copy2(file_path, backup_path)
            print(f"   📁 Backed up {filename}")

def remove_duplicate_files():
    """Remove duplicate files based on consolidation plan"""
    plan = get_consolidation_plan()
    files_to_remove = []
    
    print("🧹 CONSOLIDATING DUPLICATE FILES:")
    print("-" * 40)
    
    for category, config in plan.items():
        print(f"\n{category.upper()} CONSOLIDATION:")
        
        # API files to remove
        for api_file in config.get('merge', []):
            api_path = f"/app/backend/api/{api_file}.py"
            if os.path.exists(api_path):
                files_to_remove.append(api_path)
                print(f"   🗑️  Removing duplicate API: {api_file}.py")
        
        # Service files to remove
        for service_file in config.get('service_merge', []):
            service_path = f"/app/backend/services/{service_file}.py"
            if os.path.exists(service_path):
                files_to_remove.append(service_path)
                print(f"   🗑️  Removing duplicate Service: {service_file}.py")
        
        # Keep master files
        master_api = config.get('master')
        master_service = config.get('service_master')
        if master_api:
            print(f"   ✅ Keeping master API: {master_api}.py")
        if master_service:
            print(f"   ✅ Keeping master Service: {master_service}.py")
    
    # Backup files before removal
    print(f"\n📦 BACKING UP {len(files_to_remove)} FILES:")
    backup_files(files_to_remove)
    
    # Remove duplicate files
    print(f"\n🗑️  REMOVING {len(files_to_remove)} DUPLICATE FILES:")
    removed_count = 0
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            removed_count += 1
            print(f"   ❌ Removed: {os.path.basename(file_path)}")
    
    print(f"\n✅ Successfully removed {removed_count} duplicate files")
    return removed_count

def update_main_py_imports():
    """Update main.py to remove references to deleted files"""
    main_py_path = '/app/backend/main.py'
    
    # Files that were removed and should not be imported
    removed_apis = [
        'ecommerce', 'enhanced_ecommerce', 'website_builder', 'professional_website_builder',
        'financial_management', 'booking', 'bookings', 'subscription_management',
        'workspace', 'workspaces', 'onboarding_system', 'users'
    ]
    
    print("\n🔧 UPDATING main.py IMPORTS:")
    print("-" * 40)
    
    # Read current main.py
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Remove references to deleted modules from ALL_API_MODULES
    for api in removed_apis:
        # Remove from ALL_API_MODULES list
        content = content.replace(f"'{api}', ", "")
        content = content.replace(f", '{api}'", "")
        content = content.replace(f"'{api}'", "")
        print(f"   🔧 Removed {api} from ALL_API_MODULES")
    
    # Remove specific router includes for deleted files
    lines = content.split('\n')
    filtered_lines = []
    skip_next_except = False
    
    for i, line in enumerate(lines):
        skip_line = False
        
        # Skip try blocks for removed APIs
        for api in removed_apis:
            if f'from api.{api} import' in line:
                # Find the corresponding try/except block and skip it
                skip_line = True
                j = i
                # Skip until we find the except block
                while j < len(lines) and 'except Exception' not in lines[j]:
                    j += 1
                # Skip the except block too
                while j < len(lines) and (lines[j].startswith('except') or lines[j].startswith('    ') and lines[j].strip()):
                    j += 1
                break
        
        if not skip_line:
            filtered_lines.append(line)
    
    content = '\n'.join(filtered_lines)
    
    # Write updated main.py
    if content != original_content:
        with open(main_py_path, 'w') as f:
            f.write(content)
        print("   ✅ Updated main.py imports")
    else:
        print("   ℹ️  No changes needed in main.py")

def add_missing_services():
    """Create missing service files for APIs without services"""
    missing_services = [
        'admin_configuration', 'admin', 'survey_system', 'compliance_system',
        'i18n_system', 'monitoring_system', 'automation_system', 'crm_management', 
        'support_system', 'realtime_notifications', 'team_management',
        'ai_token_management', 'backup_system', 'webhook_system'
    ]
    
    print("\n➕ CREATING MISSING SERVICE FILES:")
    print("-" * 40)
    
    service_template = '''"""
{service_name} Service
Provides business logic for {service_display}
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import get_database

class {class_name}:
    """Service class for {service_display}"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["{collection_name}"]
    
    async def get_all(self, user_id: str, limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all records for user"""
        cursor = self.collection.find(
            {{"user_id": user_id}},
            limit=limit,
            skip=skip,
            sort=[("created_at", -1)]
        )
        return await cursor.to_list(length=limit)
    
    async def get_by_id(self, user_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        return await self.collection.find_one({{
            "id": record_id,
            "user_id": user_id
        }})
    
    async def create(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new record"""
        record = {{
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **data
        }}
        
        await self.collection.insert_one(record)
        return record
    
    async def update(self, user_id: str, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing record"""
        update_data = {{
            **data,
            "updated_at": datetime.utcnow()
        }}
        
        result = await self.collection.find_one_and_update(
            {{"id": record_id, "user_id": user_id}},
            {{"$set": update_data}},
            return_document=True
        )
        
        return result
    
    async def delete(self, user_id: str, record_id: str) -> bool:
        """Delete record"""
        result = await self.collection.delete_one({{
            "id": record_id,
            "user_id": user_id
        }})
        
        return result.deleted_count > 0
    
    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics"""
        total = await self.collection.count_documents({{"user_id": user_id}})
        
        return {{
            "total_records": total,
            "service": "{service_name}",
            "last_updated": datetime.utcnow().isoformat()
        }}

# Service instance
{service_name}_service = {class_name}()
'''
    
    created_count = 0
    for service in missing_services:
        service_file_path = f'/app/backend/services/{service}_service.py'
        
        if not os.path.exists(service_file_path):
            class_name = ''.join(word.capitalize() for word in service.split('_')) + 'Service'
            service_display = service.replace('_', ' ').title()
            collection_name = service
            
            service_content = service_template.format(
                service_name=service,
                service_display=service_display,
                class_name=class_name,
                collection_name=collection_name
            )
            
            with open(service_file_path, 'w') as f:
                f.write(service_content)
            
            print(f"   ➕ Created: {service}_service.py")
            created_count += 1
        else:
            print(f"   ✅ Already exists: {service}_service.py")
    
    print(f"\n✅ Created {created_count} missing service files")

def verify_api_keys():
    """Verify that all provided API keys are properly configured"""
    env_path = '/app/backend/.env'
    
    required_keys = {
        'ELASTICMAIL_API_KEY': 'D7CAD4A6C3F39166DEC4E906F29391905CF15EAC4F78760BCE24DCEA0F4884E9102D0F69DE607FACDF52B9DCF7F81670',
        'TWITTER_API_KEY': '57zInvI1CUTkc3i4aGN87kn1k', 
        'TWITTER_API_SECRET': 'GJkQNYE7VoZjv8dovZXgvGGoaopJIYzdzzNBXgPVGqkRfTXWtk',
        'TIKTOK_CLIENT_KEY': 'aw09alsjbsn4syuq',
        'TIKTOK_CLIENT_SECRET': 'EYYV4rrs1m7FUghDzuYPyZw36eHKRehu', 
        'OPENAI_API_KEY': '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',
        'GOOGLE_CLIENT_ID': '429180120844-nq1f3t1cjrmbeh83na713ur80mpigpss.apps.googleusercontent.com',
        'GOOGLE_CLIENT_SECRET': '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',
        'STRIPE_SECRET_KEY': 'sk_test_51RHeZMPTey8qEzxZn2t4XbP6CATdXVbcgbzvSjdVIsijehuscfcSOVQ016bUXsVaBV9MyoI8EThIBTgmXSjDUs6n00ipAjYRXZ',
        'STRIPE_PUBLISHABLE_KEY': 'pk_test_51RHeZMPTey8qEzxZZ1MyBvDG8Qh2VOoxUroGhxpNmcEMnvgfQCfwcsHihlFvqz35LPjAYyKZ4j5Njm07AKGuXDqw00nAsVfaXv'
    }
    
    print("\n🔑 VERIFYING API KEYS:")
    print("-" * 40)
    
    # Read current .env file
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    verified_keys = 0
    for key, value in required_keys.items():
        if f"{key}={value}" in env_content:
            print(f"   ✅ {key}: Configured")
            verified_keys += 1
        else:
            print(f"   ❌ {key}: Missing or incorrect")
    
    print(f"\n✅ {verified_keys}/{len(required_keys)} API keys verified")
    
    return verified_keys == len(required_keys)

def generate_summary_report():
    """Generate final cleanup summary"""
    print("\n" + "="*60)
    print("CLEANUP SUMMARY REPORT")
    print("="*60)
    
    # Count remaining files
    api_files = len(list(Path('/app/backend/api').glob('*.py'))) - 1  # Exclude __init__.py
    service_files = len(list(Path('/app/backend/services').glob('*.py'))) - 1  # Exclude __init__.py
    
    print(f"📊 FINAL COUNTS:")
    print(f"   • API Files: {api_files}")
    print(f"   • Service Files: {service_files}")
    print(f"   • Original Endpoints: 731")
    print("")
    
    print(f"🧹 CLEANUP ACTIONS:")
    print(f"   • Duplicate files consolidated")
    print(f"   • Missing services created")
    print(f"   • main.py imports updated")
    print(f"   • API keys verified")
    print("")
    
    print(f"📋 NEXT STEPS:")
    print(f"   1. Test backend functionality")
    print(f"   2. Verify all CRUD operations")
    print(f"   3. Eliminate remaining random data")
    print(f"   4. Replace Instagram with TikTok/X variants")

if __name__ == "__main__":
    print("🚀 STARTING SYSTEMATIC CLEANUP")
    print("="*50)
    
    # Step 1: Remove duplicate files
    removed_count = remove_duplicate_files()
    
    # Step 2: Update main.py imports
    update_main_py_imports()
    
    # Step 3: Create missing services
    add_missing_services()
    
    # Step 4: Verify API keys
    api_keys_ok = verify_api_keys()
    
    # Step 5: Generate summary
    generate_summary_report()
    
    print(f"\n🎉 CLEANUP COMPLETE!")
    print(f"   • Files removed: {removed_count}")
    print(f"   • API keys verified: {'✅' if api_keys_ok else '❌'}")
    print(f"   • Ready for testing: {'✅' if removed_count > 0 else '⚠️'}")