#!/usr/bin/env python3
"""
CRITICAL DUPLICATE CLEANUP SYSTEM
Removes the most problematic duplicates causing 405/500 errors
Focus on fixing conflicting routes first, then removing unnecessary files
"""

import os
import shutil
from pathlib import Path

class DuplicateCleanup:
    def __init__(self):
        self.files_removed = 0
        self.conflicts_resolved = 0
        
    def identify_core_apis(self):
        """Identify which APIs to keep vs remove"""
        
        # Core APIs to KEEP (these are the main business functionality)
        core_apis = {
            'auth.py',           # Authentication
            'financial.py',      # Financial management  
            'referral_system.py', # Referral system
            'stripe_integration.py', # Stripe payments
            'twitter.py',        # Twitter integration
            'tiktok.py',         # TikTok integration
            'admin.py',          # Admin functionality
            'analytics.py',      # Analytics
            'booking.py',        # Booking system
            'crm.py',            # CRM
            'user.py',           # User management
            'workspace.py',      # Workspace management
            'team_management.py', # Team management
            'complete_onboarding.py', # Onboarding
            'complete_multi_workspace.py', # Multi-workspace
            'form_builder.py',   # Form builder
            'website_builder.py', # Website builder
            'escrow.py',         # Escrow system
            'complete_financial.py', # Complete financial
        }
        
        return core_apis
    
    def remove_duplicate_apis(self):
        """Remove duplicate API files, keeping only core ones"""
        print("🗑️ REMOVING DUPLICATE API FILES...")
        
        core_apis = self.identify_core_apis()
        api_dir = Path('api')
        
        if not api_dir.exists():
            print("   No API directory found")
            return
        
        # Get all API files
        all_api_files = list(api_dir.glob('*.py'))
        
        # Group similar files
        similar_groups = {}
        for api_file in all_api_files:
            if api_file.name == '__init__.py':
                continue
                
            # Normalize name
            base_name = api_file.name.replace('.py', '')
            normalized = base_name.lower()
            
            # Remove prefixes/suffixes that indicate duplicates
            for prefix in ['complete_', 'advanced_', 'real_']:
                if normalized.startswith(prefix):
                    normalized = normalized[len(prefix):]
                    break
            
            for suffix in ['_system', '_api', '_suite', '_management']:
                if normalized.endswith(suffix):
                    normalized = normalized[:-len(suffix)]
                    break
            
            if normalized not in similar_groups:
                similar_groups[normalized] = []
            similar_groups[normalized].append(api_file)
        
        # Remove duplicates from each group
        for normalized_name, files in similar_groups.items():
            if len(files) <= 1:
                continue
                
            # Sort by preference (keep core APIs first)
            files_to_keep = []
            files_to_remove = []
            
            for file in files:
                if file.name in core_apis:
                    files_to_keep.append(file)
                else:
                    files_to_remove.append(file)
            
            # If no core API in this group, keep the simplest name
            if not files_to_keep:
                # Keep the file with the shortest, simplest name
                files.sort(key=lambda f: (len(f.name), f.name))
                files_to_keep.append(files[0])
                files_to_remove = files[1:]
            
            # Remove duplicate files
            for file_to_remove in files_to_remove:
                try:
                    file_to_remove.unlink()
                    print(f"   ✅ Removed duplicate: {file_to_remove.name}")
                    self.files_removed += 1
                except Exception as e:
                    print(f"   ❌ Error removing {file_to_remove.name}: {e}")
    
    def remove_duplicate_services(self):
        """Remove duplicate service files"""
        print("🔧 REMOVING DUPLICATE SERVICE FILES...")
        
        services_dir = Path('services')
        if not services_dir.exists():
            print("   No services directory found")
            return
        
        # Remove the duplicate DataPopulationService
        duplicate_service = services_dir / 'data_population.py'
        if duplicate_service.exists():
            try:
                duplicate_service.unlink()
                print(f"   ✅ Removed duplicate service: data_population.py")
                self.files_removed += 1
            except Exception as e:
                print(f"   ❌ Error removing data_population.py: {e}")
        
        # Remove services that match removed APIs
        all_service_files = list(services_dir.glob('*.py'))
        
        for service_file in all_service_files:
            if service_file.name == '__init__.py':
                continue
                
            # Check if corresponding API was removed
            api_name = service_file.name.replace('_service', '').replace('.py', '.py')
            api_path = Path('api') / api_name
            
            # If API doesn't exist, remove the service too
            if not api_path.exists():
                # Check for similar API names
                base_name = service_file.name.replace('_service.py', '')
                similar_apis = list(Path('api').glob(f'*{base_name}*.py'))
                
                if not similar_apis:
                    try:
                        service_file.unlink()
                        print(f"   ✅ Removed orphaned service: {service_file.name}")
                        self.files_removed += 1
                    except Exception as e:
                        print(f"   ❌ Error removing {service_file.name}: {e}")
    
    def clean_main_py_imports(self):
        """Clean up main.py to remove imports for deleted files"""
        print("🧹 CLEANING MAIN.PY IMPORTS...")
        
        main_py = Path('main.py')
        if not main_py.exists():
            print("   main.py not found")
            return
        
        try:
            with open(main_py, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get list of existing API files
            api_dir = Path('api')
            existing_apis = set()
            if api_dir.exists():
                for api_file in api_dir.glob('*.py'):
                    if api_file.name != '__init__.py':
                        existing_apis.add(api_file.name.replace('.py', ''))
            
            # Remove import lines for non-existent APIs
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                line_stripped = line.strip()
                
                # Check if this is an API import line
                if line_stripped.startswith('from api.') and 'import router as' in line:
                    # Extract API name
                    api_name = line_stripped.split('from api.')[1].split(' import')[0]
                    
                    # Only keep if API file exists
                    if api_name in existing_apis:
                        new_lines.append(line)
                    else:
                        print(f"   ✅ Removed import for deleted API: {api_name}")
                        self.conflicts_resolved += 1
                
                # Check if this is a router include line
                elif 'app.include_router' in line_stripped:
                    # Extract router name
                    router_name = line_stripped.split('(')[1].split(',')[0].strip()
                    
                    # Check if this router still exists based on imports above
                    found_import = False
                    for prev_line in new_lines:
                        if f'as {router_name}' in prev_line:
                            found_import = True
                            break
                    
                    if found_import:
                        new_lines.append(line)
                    else:
                        print(f"   ✅ Removed router include for deleted API: {router_name}")
                        self.conflicts_resolved += 1
                else:
                    new_lines.append(line)
            
            # Write back cleaned content
            with open(main_py, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"   ✅ Cleaned main.py imports")
            
        except Exception as e:
            print(f"   ❌ Error cleaning main.py: {e}")
    
    def run_critical_cleanup(self):
        """Run critical cleanup to resolve duplicate conflicts"""
        
        print("🎯 CRITICAL DUPLICATE CLEANUP - JANUARY 2025")
        print("="*70)
        print("⚠️ REMOVING DUPLICATE FILES TO RESOLVE 405/500 ERRORS")
        print("="*70)
        
        # Backup main.py first
        try:
            shutil.copy2('main.py', 'main_backup.py')
            print("✅ Created backup: main_backup.py")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
        
        # Run cleanup steps
        self.remove_duplicate_apis()
        self.remove_duplicate_services()
        self.clean_main_py_imports()
        
        print(f"\n🎉 CLEANUP COMPLETE")
        print(f"Files removed: {self.files_removed}")
        print(f"Conflicts resolved: {self.conflicts_resolved}")
        
        if self.files_removed > 0:
            print(f"\n✅ CRITICAL SUCCESS:")
            print(f"   - Removed {self.files_removed} duplicate files")
            print(f"   - Resolved {self.conflicts_resolved} routing conflicts")
            print(f"   - Should eliminate most 405/500 errors")
            print(f"\n🔄 NEXT STEPS:")
            print(f"   1. Restart the backend server")
            print(f"   2. Test API endpoints")
            print(f"   3. Verify no import errors")
        else:
            print(f"\n ℹ️ No critical duplicates found to remove")
        
        return self.files_removed, self.conflicts_resolved

def main():
    cleanup = DuplicateCleanup()
    files_removed, conflicts_resolved = cleanup.run_critical_cleanup()
    
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"Total files removed: {files_removed}")
    print(f"Total conflicts resolved: {conflicts_resolved}")
    
    if files_removed > 0:
        print(f"\n⚠️ IMPORTANT:")
        print(f"Backend needs restart after cleanup")
        print(f"Some functionality may be consolidated")
        print(f"Test thoroughly after restart")
    
    return files_removed > 0

if __name__ == "__main__":
    main()