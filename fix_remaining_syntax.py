#!/usr/bin/env python3
import os
import re
import glob

def fix_remaining_syntax_errors():
    # Find all Python files in the api directory
    api_files = glob.glob('/app/backend/api/*.py')
    
    for file_path in api_files:
        print(f"Processing {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix the specific pattern: "item: SomeUpdate, = Body(...)"
        content = re.sub(r'(\w+): (\w+), = Body\(\.\.\.\),', r'\1: \2 = Body(...),', content)
        
        # Fix malformed function parameter blocks
        # Pattern: function definition with malformed parameters
        pattern = r'(@router\.put\([^)]+\)\s*\n)(async def \w+\(\s*\n)(\s+item_id: str = Path\([^)]+\),\s+item: \w+, = Body\(\.\.\.\),\s*\n\s*\n\s*\n\s+current_user: dict = Depends\(get_current_user\),\s*\n\):)'
        
        def fix_function_params(match):
            decorator = match.group(1)
            func_def = match.group(2)
            params = match.group(3)
            
            # Extract the parameters
            item_id_match = re.search(r'item_id: str = Path\([^)]+\)', params)
            item_match = re.search(r'item: (\w+), = Body\(\.\.\.\)', params)
            current_user_match = re.search(r'current_user: dict = Depends\(get_current_user\)', params)
            
            if item_id_match and item_match and current_user_match:
                item_id_param = item_id_match.group(0)
                item_type = item_match.group(1)
                current_user_param = current_user_match.group(0)
                
                # Reconstruct properly formatted parameters
                new_params = f"""    {item_id_param},
    item: {item_type} = Body(...),
    {current_user_param}
):"""
                
                return decorator + func_def + new_params
            
            return match.group(0)
        
        content = re.sub(pattern, fix_function_params, content, flags=re.MULTILINE | re.DOTALL)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_remaining_syntax_errors()
    print("All remaining syntax errors fixed!")