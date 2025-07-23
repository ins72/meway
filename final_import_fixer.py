#!/usr/bin/env python3
"""
FINAL IMPORT FIXES - Fix all import and syntax errors in API files
"""

import os
import re

class FinalImportFixer:
    def __init__(self):
        self.backend_path = "/app/backend"
        self.api_path = os.path.join(self.backend_path, "api")
        self.fixes_applied = 0
    
    def fix_all_api_imports(self):
        """Fix imports in all API files"""
        print("🔧 FIXING: All API Import Issues")
        
        api_files = [
            "blog.py",
            "real_email_automation.py", 
            "enterprise_security_compliance.py"
        ]
        
        for filename in api_files:
            file_path = os.path.join(self.api_path, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Fix common import issues
                    content = self._fix_imports(content)
                    content = self._fix_auth_imports(content)
                    content = self._fix_fastapi_imports(content)
                    content = self._add_missing_imports(content)
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"  ✅ Fixed imports in {filename}")
                        self.fixes_applied += 1
                    
                except Exception as e:
                    print(f"  ❌ Error fixing {filename}: {e}")
    
    def _fix_imports(self, content: str) -> str:
        """Fix general import issues"""
        # Ensure proper import order
        imports = []
        other_content = []
        in_imports = True
        
        for line in content.split('\n'):
            if line.strip().startswith(('import ', 'from ')) and in_imports:
                imports.append(line)
            elif line.strip() == '' and in_imports:
                imports.append(line)
            else:
                in_imports = False
                other_content.append(line)
        
        # Add missing standard imports at the top
        standard_imports = [
            "from datetime import datetime",
            "import uuid",
            "import logging"
        ]
        
        for imp in standard_imports:
            if imp not in content:
                imports.insert(0, imp)
        
        return '\n'.join(imports + other_content)
    
    def _fix_auth_imports(self, content: str) -> str:
        """Fix authentication imports"""
        # Replace get_current_active_user with get_current_user
        content = re.sub(
            r'from core\.auth import get_current_active_user$',
            'from core.auth import get_current_active_user as get_current_user',
            content,
            flags=re.MULTILINE
        )
        
        # Replace usage in function parameters
        content = re.sub(
            r'Depends\(get_current_active_user\)',
            'Depends(get_current_user)',
            content
        )
        
        return content
    
    def _fix_fastapi_imports(self, content: str) -> str:
        """Fix FastAPI imports"""
        # Check if FastAPI imports are missing
        fastapi_imports = [
            "from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path",
            "from typing import List, Dict, Any, Optional"
        ]
        
        for imp in fastapi_imports:
            if "APIRouter" in content and "from fastapi import" not in content:
                content = imp + "\n" + content
                break
        
        return content
    
    def _add_missing_imports(self, content: str) -> str:
        """Add missing imports based on usage"""
        missing_imports = []
        
        # Check for logger usage
        if "logger." in content and "logger = logging.getLogger" not in content:
            missing_imports.append("logger = logging.getLogger(__name__)")
        
        # Check for router usage
        if "@router." in content and "router = APIRouter()" not in content:
            missing_imports.append("router = APIRouter()")
        
        # Add missing imports after the last import statement
        if missing_imports:
            lines = content.split('\n')
            import_end = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')) or line.strip() == '':
                    import_end = i
                else:
                    break
            
            for imp in missing_imports:
                lines.insert(import_end + 1, imp)
            
            content = '\n'.join(lines)
        
        return content
    
    def run_fixes(self):
        """Run all fixes"""
        print("🚀 STARTING FINAL IMPORT FIXES")
        print("=" * 50)
        
        self.fix_all_api_imports()
        
        print("\n" + "=" * 50)
        print(f"📊 Import fixes applied: {self.fixes_applied}")
        
        return self.fixes_applied

def main():
    fixer = FinalImportFixer()
    fixes = fixer.run_fixes()
    
    print(f"\n✅ Import fixes completed: {fixes} files fixed")
    
    return fixes

if __name__ == "__main__":
    main()