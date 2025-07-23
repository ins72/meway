#!/usr/bin/env python3
"""
Fix misplaced ObjectId imports in service files
"""

import os
import re

def fix_misplaced_imports():
    """Fix misplaced ObjectId imports throughout service files"""
    
    files_fixed = 0
    
    # Scan services directory
    for root, dirs, files in os.walk('services'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Find and remove misplaced imports like "from bson import ObjectId" in the middle of functions
                    # Pattern: spaces/tabs followed by "from bson import ObjectId" not at the beginning of a line after imports
                    lines = content.split('\n')
                    new_lines = []
                    in_imports_section = True
                    has_objectid_import = False
                    
                    for i, line in enumerate(lines):
                        # Check if we're still in the imports section
                        if in_imports_section:
                            if line.strip().startswith(('import ', 'from ')) and 'import' in line:
                                if 'from bson import ObjectId' in line:
                                    has_objectid_import = True
                            elif line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                                if not line.strip().startswith(('import ', 'from ')):
                                    in_imports_section = False
                        
                        # Remove misplaced ObjectId imports (not in imports section)
                        if not in_imports_section and line.strip() == 'from bson import ObjectId':
                            print(f"Removing misplaced import from line {i+1} in {file_path}")
                            continue  # Skip this line
                        
                        new_lines.append(line)
                    
                    # Add ObjectId import at the top if needed and not present
                    if not has_objectid_import:
                        # Find the last import line
                        last_import_idx = -1
                        for i, line in enumerate(new_lines):
                            if line.strip().startswith(('import ', 'from ')) and 'import' in line:
                                last_import_idx = i
                        
                        if last_import_idx >= 0:
                            new_lines.insert(last_import_idx + 1, 'from bson import ObjectId')
                            print(f"Added ObjectId import to {file_path}")
                    
                    new_content = '\n'.join(new_lines)
                    
                    # Only write if changes were made
                    if new_content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        files_fixed += 1
                        print(f"✅ Fixed imports in {file_path}")
                
                except Exception as e:
                    print(f"❌ Error processing {file_path}: {e}")
    
    return files_fixed

if __name__ == "__main__":
    print("🔧 FIXING MISPLACED OBJECTID IMPORTS...")
    files_fixed = fix_misplaced_imports()
    print(f"\n✅ Fixed {files_fixed} files")