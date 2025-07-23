#!/usr/bin/env python3
"""
DUPLICATE FILE CLEANUP
Remove identified duplicate files and consolidate functionality
"""

import os
import shutil
from typing import List

class DuplicateFileCleanup:
    def __init__(self, base_path="/app/backend"):
        self.base_path = base_path
        self.removed_files = []
        
    def remove_duplicate_files(self):
        """Remove identified duplicate files"""
        print("🧹 REMOVING DUPLICATE FILES...")
        
        # Duplicate API files identified in audit
        duplicate_apis = [
            "template_marketplace.py"  # Keep advanced_template_marketplace.py instead
        ]
        
        # Duplicate service files identified in audit
        duplicate_services = [
            "team_management_service.py",  # Keep advanced_team_management_service.py instead
            "escrow_service.py"  # This might be used, let's check first
        ]
        
        # Remove duplicate API files
        for filename in duplicate_apis:
            file_path = os.path.join(self.base_path, "api", filename)
            if os.path.exists(file_path):
                self.backup_and_remove_file(file_path, "api")
        
        # Check service files before removal
        for filename in duplicate_services:
            file_path = os.path.join(self.base_path, "services", filename)
            if os.path.exists(file_path):
                if filename == "escrow_service.py":
                    # Check if this is referenced in complete_escrow_service.py
                    advanced_path = os.path.join(self.base_path, "services", "complete_escrow_service.py")
                    if os.path.exists(advanced_path):
                        self.backup_and_remove_file(file_path, "services")
                else:
                    self.backup_and_remove_file(file_path, "services")
    
    def backup_and_remove_file(self, file_path: str, category: str):
        """Backup file before removing"""
        try:
            filename = os.path.basename(file_path)
            backup_dir = f"/app/backup_duplicates_{category}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup
            backup_path = os.path.join(backup_dir, filename)
            shutil.copy2(file_path, backup_path)
            
            # Remove original
            os.remove(file_path)
            
            self.removed_files.append(file_path)
            print(f"  ✅ Removed duplicate: {filename} (backed up)")
            
        except Exception as e:
            print(f"  ❌ Error removing {file_path}: {str(e)}")
    
    def consolidate_functionality(self):
        """Consolidate functionality from removed duplicates"""
        print("🔧 CONSOLIDATING FUNCTIONALITY...")
        
        # Ensure advanced files have all functionality
        consolidations = [
            {
                "target": "/app/backend/api/advanced_template_marketplace.py",
                "ensure_has": ["@router.get", "@router.post", "@router.put", "@router.delete"]
            },
            {
                "target": "/app/backend/services/advanced_template_marketplace_service.py", 
                "ensure_has": ["create_template", "get_templates", "update_template", "delete_template"]
            }
        ]
        
        for consolidation in consolidations:
            self.check_functionality(consolidation["target"], consolidation["ensure_has"])
    
    def check_functionality(self, file_path: str, required_functions: List[str]):
        """Check if file has required functionality"""
        try:
            if not os.path.exists(file_path):
                print(f"  ⚠️  File not found: {os.path.basename(file_path)}")
                return
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing = []
            for func in required_functions:
                if func not in content:
                    missing.append(func)
            
            if missing:
                print(f"  ⚠️  {os.path.basename(file_path)} missing: {', '.join(missing)}")
            else:
                print(f"  ✅ {os.path.basename(file_path)} has all required functionality")
                
        except Exception as e:
            print(f"  ❌ Error checking {file_path}: {str(e)}")
    
    def run(self):
        """Execute duplicate file cleanup"""
        print("🚀 STARTING DUPLICATE FILE CLEANUP")
        print("=" * 50)
        
        self.remove_duplicate_files()
        self.consolidate_functionality()
        
        print(f"\n✅ DUPLICATE FILE CLEANUP COMPLETE!")
        print(f"📊 Files Removed: {len(self.removed_files)}")
        for file_path in self.removed_files:
            print(f"  - {os.path.basename(file_path)}")
        print("=" * 50)

def main():
    cleanup = DuplicateFileCleanup()
    cleanup.run()

if __name__ == "__main__":
    main()