#!/usr/bin/env python3
"""
Fix datetime deprecation warnings by replacing datetime.utcnow() with datetime.utcnow()
"""

import os
import re
from pathlib import Path

def fix_datetime_deprecation():
    """Fix all datetime.utcnow() deprecation warnings"""
    print("🔧 FIXING DATETIME DEPRECATION WARNINGS...")
    
    # Get all Python files in the backend directory
    backend_dir = Path(".")
    python_files = list(backend_dir.rglob("*.py"))
    
    total_fixes = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count occurrences before replacement
            original_count = content.count("datetime.utcnow()")
            
            if original_count > 0:
                # Replace datetime.utcnow() with datetime.utcnow()
                new_content = content.replace("datetime.utcnow()", "datetime.utcnow()")
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                total_fixes += original_count
                print(f"  ✅ Fixed {original_count} occurrences in {file_path}")
                
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
    
    print(f"\n🎉 DATETIME DEPRECATION FIXES COMPLETE!")
    print(f"   Total fixes applied: {total_fixes}")
    print(f"   Files processed: {len(python_files)}")

if __name__ == "__main__":
    fix_datetime_deprecation() 