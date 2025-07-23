#!/usr/bin/env python3
"""
Fix FastAPI parameter annotations to resolve syntax errors
"""

import os
import re

def fix_api_file(file_path):
    """Fix FastAPI parameter annotations in API file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Fix pattern: parameter without default after parameter with default
        # Pattern 1: item: Model, after Path(...) parameter
        pattern1 = r'(item_id: str = Path\([^)]+\),\s*)(item: \w+,)(\s*current_user: dict = Depends\(get_current_user\))'
        replacement1 = r'\1item: \2.replace(", ", " = Body(...),") \3'
        
        # More specific fix for the exact patterns
        content = re.sub(r'(item: \w+),(\s*current_user: dict = Depends\(get_current_user\))', r'item: \1 = Body(...),\2', content)
        content = re.sub(r'(items: List\[\w+\]),(\s*current_user: dict = Depends\(get_current_user\))', r'items: \1 = Body(...),\2', content)
        
        # Fix permanent parameter
        content = re.sub(r'(permanent: bool = Query\([^)]+\),\s*)(current_user: dict = Depends\(get_current_user\))', r'\2,\n    \1', content)
        
        # Ensure all Body imports are present
        if 'from fastapi import' in content and 'Body' not in content:
            content = content.replace('from fastapi import', 'from fastapi import Body,')
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Fixed FastAPI parameters in {os.path.basename(file_path)}")
            return True
        
        return False
        
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