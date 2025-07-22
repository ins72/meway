#!/usr/bin/env python3
"""
Instagram to TikTok/X Migration Script
Replaces all Instagram-specific code with TikTok/X variants
"""

import os
import re
from pathlib import Path

def find_instagram_references():
    """Find all Instagram references in the codebase"""
    instagram_refs = []
    
    # Search all Python files
    for root, dirs, files in os.walk('/app/backend'):
        # Skip backup and archive directories
        if 'backup' in root or 'archive' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                    for i, line in enumerate(lines, 1):
                        if re.search(r'instagram', line, re.IGNORECASE):
                            instagram_refs.append({
                                'file': file_path,
                                'line': i,
                                'content': line.strip()
                            })
                except Exception as e:
                    continue
    
    return instagram_refs

def remove_instagram_router_from_main():
    """Remove Instagram router import from main.py"""
    main_path = '/app/backend/main.py'
    
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Remove the Instagram router try/except block
    instagram_block = '''try:
    from api.complete_instagram_leads import router as instagram_leads_router
    app.include_router(instagram_leads_router, prefix="/api/instagram", tags=["Instagram Lead Generation"])
    included_count += 1
    print("  ✅ Included Complete Instagram Lead Generation router")
except Exception as e:
    print(f"  ❌ Failed to include Instagram Lead Generation router: {str(e)}")'''
    
    content = content.replace(instagram_block, '# Instagram router removed - replaced with TikTok/X in complete_social_media_leads')
    
    with open(main_path, 'w') as f:
        f.write(content)
    
    return "Removed Instagram router from main.py"

def check_instagram_files():
    """Check if Instagram-specific files exist and should be removed"""
    instagram_files = [
        '/app/backend/api/complete_instagram_leads.py',
        '/app/backend/services/complete_instagram_leads_service.py',
        '/app/backend/api/instagram.py',
        '/app/backend/services/instagram_service.py'
    ]
    
    existing_files = []
    for file_path in instagram_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
    
    return existing_files

def update_social_media_integrations():
    """Update social media integrations to emphasize TikTok/X over Instagram"""
    updates = []
    
    # Update external API integrator
    external_api_path = '/app/backend/core/external_apis.py'
    if os.path.exists(external_api_path):
        with open(external_api_path, 'r') as f:
            content = f.read()
        
        # Replace Instagram references with TikTok/X
        original_content = content
        content = re.sub(r'instagram[_\s]*api', 'tiktok_api', content, flags=re.IGNORECASE)
        content = re.sub(r'instagram[_\s]*integration', 'tiktok_integration', content, flags=re.IGNORECASE)
        
        if content != original_content:
            with open(external_api_path, 'w') as f:
                f.write(content)
            updates.append("Updated external_apis.py")
    
    # Update admin configuration
    admin_config_path = '/app/backend/api/admin_configuration.py'
    if os.path.exists(admin_config_path):
        with open(admin_config_path, 'r') as f:
            content = f.read()
        
        original_content = content
        # Replace Instagram with TikTok in social media APIs list
        content = re.sub(r'"Instagram[^"]*"', '"TikTok Business API", "Twitter API v2"', content)
        
        if content != original_content:
            with open(admin_config_path, 'w') as f:
                f.write(content)
            updates.append("Updated admin_configuration.py")
    
    # Update complete_social_media_leads to emphasize TikTok/X
    social_leads_api_path = '/app/backend/api/complete_social_media_leads.py'
    if os.path.exists(social_leads_api_path):
        with open(social_leads_api_path, 'r') as f:
            content = f.read()
        
        original_content = content
        # Update descriptions and comments to emphasize TikTok/X
        content = re.sub(
            r'Instagram[^,\)]*,?\s*',
            '',
            content,
            flags=re.IGNORECASE
        )
        
        # Add emphasis on TikTok/X
        if 'TikTok Lead Generation' not in content:
            content = content.replace(
                'Social Media Lead Generation',
                'Social Media Lead Generation (TikTok & Twitter/X Focus)'
            )
        
        if content != original_content:
            with open(social_leads_api_path, 'w') as f:
                f.write(content)
            updates.append("Updated complete_social_media_leads.py")
    
    # Update social media leads service
    social_leads_service_path = '/app/backend/services/complete_social_media_leads_service.py'
    if os.path.exists(social_leads_service_path):
        with open(social_leads_service_path, 'r') as f:
            content = f.read()
        
        original_content = content
        # Remove Instagram references, emphasize TikTok/X
        content = re.sub(r'instagram[_\s]*[a-zA-Z]*', 'tiktok_leads', content, flags=re.IGNORECASE)
        
        if content != original_content:
            with open(social_leads_service_path, 'w') as f:
                f.write(content)
            updates.append("Updated complete_social_media_leads_service.py")
    
    return updates

def clean_instagram_references_in_comments():
    """Clean Instagram references in comments and documentation"""
    cleaned_files = []
    
    key_files = [
        '/app/backend/core/external_api_integrator.py',
        '/app/backend/services/integrations_service.py', 
        '/app/backend/services/integration_service.py',
        '/app/backend/api/missing_endpoints_fix.py'
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Replace Instagram in comments and strings
            content = re.sub(r'Instagram Graph API', 'TikTok Business API', content)
            content = re.sub(r'Instagram[^,\n]*,?', 'TikTok & Twitter/X', content)
            content = re.sub(r'"Instagram[^"]*"', '"TikTok", "Twitter/X"', content)
            
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                cleaned_files.append(os.path.basename(file_path))
    
    return cleaned_files

def verify_tiktok_twitter_integration():
    """Verify that TikTok and Twitter integrations are properly configured"""
    verification_results = []
    
    # Check if TikTok/Twitter API keys are in use
    social_leads_service = '/app/backend/services/complete_social_media_leads_service.py'
    if os.path.exists(social_leads_service):
        with open(social_leads_service, 'r') as f:
            content = f.read()
        
        if 'TIKTOK_CLIENT_KEY' in content:
            verification_results.append("✅ TikTok API key integration found")
        else:
            verification_results.append("⚠️  TikTok API key integration missing")
        
        if 'TWITTER_API_KEY' in content or 'X_API_KEY' in content:
            verification_results.append("✅ Twitter/X API key integration found")  
        else:
            verification_results.append("⚠️  Twitter/X API key integration missing")
    
    # Check environment variables
    env_path = '/app/backend/.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        if 'TIKTOK_CLIENT_KEY' in env_content:
            verification_results.append("✅ TikTok credentials in .env")
        
        if 'TWITTER_API_KEY' in env_content:
            verification_results.append("✅ Twitter/X credentials in .env")
    
    return verification_results

def generate_migration_report(instagram_refs, updates, cleaned_files, verification):
    """Generate comprehensive migration report"""
    print("\n" + "="*70)
    print("INSTAGRAM TO TIKTOK/X MIGRATION REPORT")
    print("="*70)
    
    print(f"\n📱 INSTAGRAM REFERENCES FOUND: {len(instagram_refs)}")
    if instagram_refs:
        print("-" * 50)
        
        # Group by file
        by_file = {}
        for ref in instagram_refs:
            file_name = os.path.basename(ref['file'])
            if file_name not in by_file:
                by_file[file_name] = []
            by_file[file_name].append(ref)
        
        for file_name, refs in list(by_file.items())[:10]:  # Show first 10 files
            print(f"   📄 {file_name}: {len(refs)} references")
            for ref in refs[:2]:  # Show first 2 refs per file
                print(f"      Line {ref['line']}: {ref['content'][:50]}...")
    
    print(f"\n🔄 INTEGRATION UPDATES: {len(updates)}")
    if updates:
        print("-" * 50)
        for update in updates:
            print(f"   ✅ {update}")
    
    print(f"\n🧹 CLEANED FILES: {len(cleaned_files)}")
    if cleaned_files:
        print("-" * 50)
        for file in cleaned_files:
            print(f"   🧽 {file}")
    
    print(f"\n✅ VERIFICATION RESULTS:")
    print("-" * 50)
    for result in verification:
        print(f"   {result}")
    
    print(f"\n📋 MIGRATION SUMMARY:")
    print(f"   • Instagram references found: {len(instagram_refs)}")
    print(f"   • Files updated: {len(updates)}")
    print(f"   • Files cleaned: {len(cleaned_files)}")
    print(f"   • Verification checks: {len(verification)}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"   1. All Instagram references should be replaced with TikTok/X")
    print(f"   2. Focus on TikTok Business API and Twitter API v2")
    print(f"   3. Update frontend UI to reflect TikTok/X instead of Instagram")
    print(f"   4. Test TikTok and Twitter API integrations")

if __name__ == "__main__":
    print("🚀 STARTING INSTAGRAM TO TIKTOK/X MIGRATION")
    print("="*60)
    
    # Step 1: Find Instagram references
    print("📱 SCANNING FOR INSTAGRAM REFERENCES...")
    instagram_refs = find_instagram_references()
    
    # Step 2: Remove Instagram router from main.py
    print("🔧 REMOVING INSTAGRAM ROUTER FROM MAIN.PY...")
    main_update = remove_instagram_router_from_main()
    print(f"   ✅ {main_update}")
    
    # Step 3: Update social media integrations
    print("🔄 UPDATING SOCIAL MEDIA INTEGRATIONS...")
    updates = update_social_media_integrations()
    
    # Step 4: Clean Instagram references in comments
    print("🧹 CLEANING INSTAGRAM REFERENCES...")
    cleaned_files = clean_instagram_references_in_comments()
    
    # Step 5: Verify TikTok/Twitter integration
    print("✅ VERIFYING TIKTOK/TWITTER INTEGRATION...")
    verification = verify_tiktok_twitter_integration()
    
    # Step 6: Generate report
    generate_migration_report(instagram_refs, updates, cleaned_files, verification)
    
    print(f"\n🎉 INSTAGRAM TO TIKTOK/X MIGRATION COMPLETE!")
    print(f"   • References found: {len(instagram_refs)}")
    print(f"   • Files updated: {len(updates)}")
    print(f"   • Files cleaned: {len(cleaned_files)}")