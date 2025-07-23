#!/usr/bin/env python3
"""
CRITICAL FIX: MongoDB Truth Value Testing Issue
Fixes "Database objects do not implement truth value testing" errors throughout the codebase
"""

import os
import re

def fix_database_truth_testing():
    """Fix database truth value testing throughout the codebase"""
    
    # Patterns to fix
    patterns = [
        (r'\bif\s+database\s*:', 'if database is not None:'),
        (r'\bif\s+db\s*:', 'if db is not None:'),
        (r'\bif\s+collection\s*:', 'if collection is not None:'),
        (r'\bif\s+([a-zA-Z_][a-zA-Z0-9_]*_collection)\s*:', r'if \1 is not None:'),
        (r'\bif\s+([a-zA-Z_][a-zA-Z0-9_]*_db)\s*:', r'if \1 is not None:'),
        (r'return\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+if\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+else\s+None', r'return \1 if \2 is not None else None'),
    ]
    
    # Directories to scan
    directories = ['services', 'api', 'core']
    
    files_fixed = 0
    total_replacements = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        replacements_made = 0
                        
                        # Apply all patterns
                        for pattern, replacement in patterns:
                            content, count = re.subn(pattern, replacement, content)
                            replacements_made += count
                        
                        # Only write if changes were made
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            files_fixed += 1
                            total_replacements += replacements_made
                            print(f"✅ Fixed {replacements_made} database truth testing issues in {file_path}")
                    
                    except Exception as e:
                        print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n🎯 DATABASE TRUTH TESTING FIX COMPLETE:")
    print(f"   Files Fixed: {files_fixed}")
    print(f"   Total Replacements: {total_replacements}")
    
    return files_fixed, total_replacements

if __name__ == "__main__":
    print("🔧 FIXING MONGODB TRUTH VALUE TESTING ISSUES...")
    files_fixed, total_replacements = fix_database_truth_testing()
    
    if total_replacements > 0:
        print(f"\n✅ SUCCESS: Fixed {total_replacements} database truth testing issues in {files_fixed} files")
        print("🚀 Backend should now work properly with MongoDB operations")
    else:
        print("\n ℹ️ No database truth testing issues found to fix")