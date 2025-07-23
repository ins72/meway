#!/usr/bin/env python3
import os
import re
import glob

def fix_syntax_errors():
    # Find all Python files in the api directory
    api_files = glob.glob('/app/backend/api/*.py')
    
    for file_path in api_files:
        print(f"Processing {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix duplicate parameter names like "item: item:" -> "item:"
        content = re.sub(r'(\s+)(\w+): \2:', r'\1\2:', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_syntax_errors()
    print("All syntax errors fixed!")