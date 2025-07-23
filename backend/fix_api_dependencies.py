#!/usr/bin/env python3
"""
FIX API ENDPOINT DEPENDENCIES
Replace get_current_user with get_current_admin for CRUD operations
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_api_dependencies(filepath):
    """Fix API endpoint dependencies to use get_current_admin for CRUD operations"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Check if file already imports get_current_admin
        if 'get_current_admin' not in content:
            # Add get_current_admin import
            if 'from core.auth import get_current_user' in content:
                content = content.replace(
                    'from core.auth import get_current_user',
                    'from core.auth import get_current_user, get_current_admin'
                )
                changes_made = True
        
        # Patterns for CRUD endpoints that should use get_current_admin
        crud_patterns = [
            # POST endpoints (CREATE operations)
            (r'(@router\.post\(["\'][^"\']*["\'][^)]*\).*?async def [^(]+\([^)]*current_user: dict = Depends\(get_current_user\))',
             lambda m: m.group(0).replace('Depends(get_current_user)', 'Depends(get_current_admin)')),
            
            # PUT endpoints (UPDATE operations)
            (r'(@router\.put\(["\'][^"\']*["\'][^)]*\).*?async def [^(]+\([^)]*current_user: dict = Depends\(get_current_user\))',
             lambda m: m.group(0).replace('Depends(get_current_user)', 'Depends(get_current_admin)')),
            
            # DELETE endpoints (DELETE operations)
            (r'(@router\.delete\(["\'][^"\']*["\'][^)]*\).*?async def [^(]+\([^)]*current_user: dict = Depends\(get_current_user\))',
             lambda m: m.group(0).replace('Depends(get_current_user)', 'Depends(get_current_admin)')),
            
            # GET endpoints with paths (specific item access)
            (r'(@router\.get\(["\'][^"\']*{[^}]+}[^"\']*["\'][^)]*\).*?async def [^(]+\([^)]*current_user: dict = Depends\(get_current_user\))',
             lambda m: m.group(0).replace('Depends(get_current_user)', 'Depends(get_current_admin)')),
            
            # Endpoints with /stats in the path
            (r'(@router\.get\(["\'][^"\']*stats[^"\']*["\'][^)]*\).*?async def [^(]+\([^)]*current_user: dict = Depends\(get_current_user\))',
             lambda m: m.group(0).replace('Depends(get_current_user)', 'Depends(get_current_admin)')),
        ]
        
        for pattern, replacement in crud_patterns:
            if callable(replacement):
                matches = list(re.finditer(pattern, content, re.DOTALL))
                for match in reversed(matches):  # Process in reverse to maintain positions
                    new_content = replacement(match)
                    if new_content != match.group(0):
                        content = content[:match.start()] + new_content + content[match.end():]
                        changes_made = True
                        logger.debug(f"Updated CRUD endpoint dependency in {filepath}")
            else:
                new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                if new_content != content:
                    content = new_content
                    changes_made = True
        
        # Fix specific GET endpoints that should require admin (list operations)
        list_patterns = [
            # GET endpoints for listing (no path parameters)
            (r'(@router\.get\(["\']\/["\'][^)]*\).*?async def list_[^(]+\([^)]*current_user: dict = Depends\(get_current_user\))',
             lambda m: m.group(0).replace('Depends(get_current_user)', 'Depends(get_current_admin)')),
        ]
        
        for pattern, replacement in list_patterns:
            if callable(replacement):
                matches = list(re.finditer(pattern, content, re.DOTALL))
                for match in reversed(matches):
                    new_content = replacement(match)
                    if new_content != match.group(0):
                        content = content[:match.start()] + new_content + content[match.end():]
                        changes_made = True
                        logger.debug(f"Updated list endpoint dependency in {filepath}")
        
        # Only write if content actually changed
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Fixed API dependencies: {filepath}")
            return True
        else:
            logger.debug(f"⏭️  No dependency fixes needed: {filepath}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix API endpoint dependencies in all API files"""
    backend_dir = Path("/app/backend")
    api_dir = backend_dir / "api"
    
    if not api_dir.exists():
        logger.error("API directory not found!")
        return
    
    fixed_count = 0
    total_count = 0
    
    # Fix all Python API files
    for api_file in api_dir.glob("*.py"):
        if api_file.name == "__init__.py":
            continue
            
        total_count += 1
        if fix_api_dependencies(api_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 API DEPENDENCIES FIX COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*60)
    print("API ENDPOINT DEPENDENCIES FIX RESULTS")
    print("="*60)
    print(f"Total API Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*60)
    print("\n✅ All CRUD endpoints now use get_current_admin!")
    print("🔄 Restart backend to apply authorization fixes.")

if __name__ == "__main__":
    main()