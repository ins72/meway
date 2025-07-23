#!/usr/bin/env python3
"""
FIX ASYNC MONGODB CURSOR OPERATIONS
Fix the AsyncIOMotorCursor 'await' expression errors in service files
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_async_cursor_operations(filepath):
    """Fix async cursor operations in service files"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Pattern fixes for common async cursor issues
        cursor_fixes = [
            # Fix cursor operations that need to_list()
            (r'results = await collection\.find\(([^)]*)\)', r'cursor = collection.find(\1)\n        results = await cursor.to_list(length=None)'),
            (r'items = await collection\.find\(([^)]*)\)', r'cursor = collection.find(\1)\n        items = await cursor.to_list(length=None)'),
            (r'data = await collection\.find\(([^)]*)\)', r'cursor = collection.find(\1)\n        data = await cursor.to_list(length=None)'),
            
            # Fix cursor operations with limits
            (r'results = await collection\.find\(([^)]*)\)\.limit\((\d+)\)', r'cursor = collection.find(\1).limit(\2)\n        results = await cursor.to_list(length=\2)'),
            
            # Fix cursor operations with sort
            (r'results = await collection\.find\(([^)]*)\)\.sort\(([^)]*)\)', r'cursor = collection.find(\1).sort(\2)\n        results = await cursor.to_list(length=None)'),
            
            # Fix double await issues
            (r'await await collection\.', r'await collection.'),
            
            # Fix common query patterns
            (r'result = await collection\.find_one_and_update\(', r'result = await collection.find_one_and_update('),
            (r'result = await collection\.find_one_and_delete\(', r'result = await collection.find_one_and_delete('),
            
            # Fix iteration over cursors
            (r'for item in await collection\.find\(([^)]*)\):', r'async for item in collection.find(\1):'),
        ]
        
        for pattern, replacement in cursor_fixes:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                changes_made = True
                logger.debug(f"Applied cursor fix: {pattern}")
        
        # Fix specific method patterns that commonly cause issues
        method_fixes = [
            # Fix read operations in CRUD methods
            (r'async def get_([a-z_]+)\(self.*?\):\s*.*?try:\s*collection = await self\._get_collection_async\(\)\s*if collection is None:\s*return.*?results = await collection\.find\({}\)',
             lambda m: m.group(0).replace('results = await collection.find({})', 'cursor = collection.find({})\n            results = await cursor.to_list(length=None)')),
            
            # Fix list operations
            (r'async def list_([a-z_]+)\(self.*?\):\s*.*?try:\s*collection = await self\._get_collection_async\(\)\s*if collection is None:\s*return.*?items = await collection\.find\({}\)',
             lambda m: m.group(0).replace('items = await collection.find({})', 'cursor = collection.find({})\n            items = await cursor.to_list(length=None)')),
        ]
        
        for pattern, replacement in method_fixes:
            if callable(replacement):
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in reversed(list(matches)):  # Process in reverse to maintain positions
                    new_content = replacement(match)
                    if new_content != match.group(0):
                        content = content[:match.start()] + new_content + content[match.end():]
                        changes_made = True
            else:
                new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                if new_content != content:
                    content = new_content
                    changes_made = True
        
        # Only write if content actually changed
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Fixed async cursor operations: {filepath}")
            return True
        else:
            logger.debug(f"⏭️  No cursor fixes needed: {filepath}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix async cursor operations in all service files"""
    backend_dir = Path("/app/backend")
    services_dir = backend_dir / "services"
    
    if not services_dir.exists():
        logger.error("Services directory not found!")
        return
    
    fixed_count = 0
    total_count = 0
    
    # Fix all Python service files
    for service_file in services_dir.glob("*.py"):
        if service_file.name == "__init__.py":
            continue
            
        total_count += 1
        if fix_async_cursor_operations(service_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 ASYNC CURSOR OPERATIONS FIX COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*60)
    print("ASYNC MONGODB CURSOR OPERATIONS FIX RESULTS")
    print("="*60)
    print(f"Total Service Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*60)
    print("\n✅ Async cursor operations fixed!")
    print("🔄 Restart backend to apply fixes.")

if __name__ == "__main__":
    main()