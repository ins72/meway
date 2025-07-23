#!/usr/bin/env python3
"""
FIX SYNC/ASYNC COLLECTION USAGE
Replace _get_collection() with _get_collection_async() in async methods
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_sync_async_collection_usage(filepath):
    """Fix sync/async collection usage in service files"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Find all async methods that use self._get_collection()
        # Replace with self._get_collection_async()
        async_method_pattern = r'(async def [^:]+:.*?)self\._get_collection\(\)'
        
        matches = list(re.finditer(async_method_pattern, content, re.DOTALL))
        
        for match in reversed(matches):  # Process in reverse to maintain positions
            method_content = match.group(0)
            # Replace _get_collection() with await _get_collection_async()
            updated_method = method_content.replace('self._get_collection()', 'await self._get_collection_async()')
            content = content[:match.start()] + updated_method + content[match.end():]
            changes_made = True
        
        # Also fix any cases where collection assignment is not awaited
        content = re.sub(
            r'(async def [^:]+:.*?)collection = await self\._get_collection_async\(\)',
            r'\1collection = await self._get_collection_async()',
            content,
            flags=re.DOTALL
        )
        
        # Fix cursor operations - replace direct await on find() with to_list()
        cursor_patterns = [
            (r'results = await collection\.find\(([^)]*)\)(?!\s*\.)', r'cursor = collection.find(\1)\n            results = await cursor.to_list(length=None)'),
            (r'items = await collection\.find\(([^)]*)\)(?!\s*\.)', r'cursor = collection.find(\1)\n            items = await cursor.to_list(length=None)'),
            (r'data = await collection\.find\(([^)]*)\)(?!\s*\.)', r'cursor = collection.find(\1)\n            data = await cursor.to_list(length=None)'),
        ]
        
        for pattern, replacement in cursor_patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                changes_made = True
        
        # Only write if content actually changed
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Fixed sync/async collection usage: {filepath}")
            return True
        else:
            logger.debug(f"⏭️  No sync/async fixes needed: {filepath}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix sync/async collection usage in all service files"""
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
        if fix_sync_async_collection_usage(service_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 SYNC/ASYNC COLLECTION USAGE FIX COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*60)
    print("SYNC/ASYNC COLLECTION USAGE FIX RESULTS")
    print("="*60)
    print(f"Total Service Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*60)
    print("\n✅ Collection usage synchronized!")
    print("🔄 Restart backend to apply fixes.")

if __name__ == "__main__":
    main()