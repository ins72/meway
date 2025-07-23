#!/usr/bin/env python3
"""
Final syntax fix for all API files
"""

import os
import re

def fix_api_file(file_path):
    """Fix remaining syntax issues in API file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Fix duplicate parameter names
        content = re.sub(r'item: item:', 'item:', content)
        content = re.sub(r'items: items:', 'items:', content)
        
        # Fix malformed parameter lines
        content = re.sub(r'item_id: str = Path\([^)]+\),\s*item: \w+Update = Body\(\.\.\.\),\s*\n\s*\n\s*current_user:', 
                        'item_id: str = Path(..., description="ID to update"),\n    item: Update = Body(...),\n    current_user:', content)
        
        # Fix specific pattern issues
        content = re.sub(r'(\w+Update = Body\(\.\.\.\),)\s*\n\s*\n\s*current_user:', r'\1\n    current_user:', content)
        
        # Fix incomplete lines
        content = re.sub(r'items: List\[\w+\] = Bod$', 'items: List[Create] = Body(...)', content)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Fixed syntax in {os.path.basename(file_path)}")
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