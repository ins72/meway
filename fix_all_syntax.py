#!/usr/bin/env python3
import os
import re
import glob

def fix_all_syntax_issues():
    # Find all Python files in the api directory
    api_files = glob.glob('/app/backend/api/*.py')
    
    for file_path in api_files:
        print(f"Processing {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix malformed parameter lines like "item: SomeUpdate, = Body(...)"
        content = re.sub(r'(\w+): (\w+), = Body\(\.\.\.\),', r'\1: \2 = Body(...),', content)
        
        # Fix lines with extra commas and spaces
        content = re.sub(r',\s*,', ',', content)
        
        # Fix empty lines with just spaces/commas
        content = re.sub(r'\n\s*,?\s*\n', '\n', content)
        
        # Fix function parameter formatting issues
        lines = content.split('\n')
        fixed_lines = []
        in_function_def = False
        function_params = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if we're starting a function definition
            if re.match(r'^async def \w+\(', line):
                in_function_def = True
                function_params = [line]
                i += 1
                continue
            
            # If we're in a function definition, collect parameters
            if in_function_def:
                if line.strip() == ')':
                    # End of function definition
                    in_function_def = False
                    # Process and fix the parameters
                    fixed_params = fix_function_parameters(function_params)
                    fixed_lines.extend(fixed_params)
                    fixed_lines.append(line)
                elif line.strip().startswith('):'):
                    # End of function definition with docstring
                    in_function_def = False
                    fixed_params = fix_function_parameters(function_params)
                    fixed_lines.extend(fixed_params)
                    fixed_lines.append(line)
                else:
                    function_params.append(line)
                i += 1
                continue
            
            fixed_lines.append(line)
            i += 1
        
        content = '\n'.join(fixed_lines)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

def fix_function_parameters(param_lines):
    """Fix function parameter ordering and syntax"""
    if not param_lines:
        return param_lines
    
    # Join all parameter lines
    full_params = '\n'.join(param_lines)
    
    # Extract individual parameters
    params = []
    current_param = ""
    
    for line in param_lines[1:]:  # Skip the function definition line
        stripped = line.strip()
        if stripped and not stripped.startswith(')'):
            if stripped.endswith(','):
                current_param += stripped
                params.append(current_param.strip())
                current_param = ""
            else:
                current_param += stripped
    
    if current_param.strip():
        params.append(current_param.strip())
    
    # Separate parameters with defaults from those without
    params_with_defaults = []
    params_without_defaults = []
    
    for param in params:
        if '=' in param and 'Body(...)' in param:
            params_with_defaults.append(param)
        elif '=' in param:
            params_with_defaults.append(param)
        else:
            # Add Body(...) to parameters without defaults that look like request bodies
            if any(word in param.lower() for word in ['create', 'update']) and ':' in param:
                param = param.rstrip(',') + ' = Body(...),'
                params_with_defaults.append(param)
            else:
                params_without_defaults.append(param)
    
    # Reconstruct the function definition
    result = [param_lines[0]]  # Function definition line
    
    # Add parameters without defaults first
    for param in params_without_defaults:
        result.append(f"    {param}")
    
    # Add parameters with defaults
    for param in params_with_defaults:
        result.append(f"    {param}")
    
    return result

if __name__ == "__main__":
    fix_all_syntax_issues()
    print("All syntax issues fixed!")