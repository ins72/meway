#!/usr/bin/env python3
"""
Fix syntax errors in API files
"""

import os
import re

def fix_api_file(file_path):
    """Fix syntax errors in API file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix the argument order issue
        # Pattern: item_id with Path(...) followed by item without default
        pattern = r'(async def update_\w+\(\s*item_id: str = Path\([^)]+\),\s*)(item: \w+,)(\s*current_user: dict = Depends\(get_current_user\))'
        replacement = r'\1\3,\n    \2'
        
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Also fix delete methods with similar pattern
        pattern = r'(async def delete_\w+\(\s*item_id: str = Path\([^)]+\),\s*)(permanent: bool = Query\([^)]+\),)(\s*current_user: dict = Depends\(get_current_user\))'
        replacement = r'\1\3,\n    \2'
        
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed syntax errors in {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def fix_all_api_files():
    """Fix all API files"""
    api_dir = '/app/backend/api'
    fixed_count = 0
    
    for file_name in os.listdir(api_dir):
        if file_name.endswith('.py') and not file_name.startswith('__'):
            file_path = os.path.join(api_dir, file_name)
            if fix_api_file(file_path):
                fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} API files")
    return fixed_count

if __name__ == "__main__":
    fix_all_api_files()