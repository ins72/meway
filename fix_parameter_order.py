#!/usr/bin/env python3
import os
import re
import glob

def fix_parameter_order():
    # Find all Python files in the api directory
    api_files = glob.glob('/app/backend/api/*.py')
    
    for file_path in api_files:
        print(f"Processing {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix parameter order issues in update functions
        # Pattern: current_user: dict = Depends(get_current_user),\n    item: SomeUpdate,
        pattern = r'(\s+current_user: dict = Depends\(get_current_user\),)\n(\s+item: \w+Update,)'
        replacement = r'\2 = Body(...),\n\1'
        content = re.sub(pattern, replacement, content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_parameter_order()
    print("All parameter order issues fixed!")