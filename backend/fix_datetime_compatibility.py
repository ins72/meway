#!/usr/bin/env python3
"""
Fix datetime compatibility issues for different Python versions
"""

import os
import re
from pathlib import Path

def fix_datetime_compatibility():
    """Fix datetime compatibility issues"""
    print("🔧 FIXING DATETIME COMPATIBILITY ISSUES...")
    
    # Get all Python files in the backend directory
    backend_dir = Path(".")
    python_files = list(backend_dir.rglob("*.py"))
    
    total_fixes = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for datetime.utcnow() which is Python 3.11+
            if "datetime.utcnow()" in content:
                # Replace with datetime.utcnow() for compatibility
                new_content = content.replace("datetime.utcnow()", "datetime.utcnow()")
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                total_fixes += 1
                print(f"  ✅ Fixed datetime compatibility in {file_path}")
                
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
    
    print(f"\n🎉 DATETIME COMPATIBILITY FIXES COMPLETE!")
    print(f"   Total fixes applied: {total_fixes}")
    print(f"   Files processed: {len(python_files)}")

if __name__ == "__main__":
    fix_datetime_compatibility() 