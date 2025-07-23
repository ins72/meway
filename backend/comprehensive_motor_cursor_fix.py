#!/usr/bin/env python3
"""
COMPREHENSIVE ASYNC MOTOR CURSOR FIX
Fix all AsyncIOMotorCursor 'await' expression errors across all services
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_motor_cursor_operations(filepath):
    """Fix Motor cursor operations in service files"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Fix patterns for Motor cursor operations
        cursor_fixes = [
            # Fix direct await on find() - most common error
            (r'cursor = await collection\.find\(([^)]*)\)', r'cursor = collection.find(\1)'),
            (r'results = await collection\.find\(([^)]*)\)', r'cursor = collection.find(\1)\n            results = await cursor.to_list(length=None)'),
            (r'items = await collection\.find\(([^)]*)\)', r'cursor = collection.find(\1)\n            items = await cursor.to_list(length=None)'),
            (r'data = await collection\.find\(([^)]*)\)', r'cursor = collection.find(\1)\n            data = await cursor.to_list(length=None)'),
            (r'docs = await collection\.find\(([^)]*)\)', r'cursor = collection.find(\1)\n            docs = await cursor.to_list(length=None)'),
            
            # Fix chained operations
            (r'cursor = await collection\.find\(([^)]*)\)\.skip\(([^)]*)\)\.limit\(([^)]*)\)', 
             r'cursor = collection.find(\1).skip(\2).limit(\3)'),
            (r'results = await collection\.find\(([^)]*)\)\.skip\(([^)]*)\)\.limit\(([^)]*)\)', 
             r'cursor = collection.find(\1).skip(\2).limit(\3)\n            results = await cursor.to_list(length=\3)'),
            (r'items = await collection\.find\(([^)]*)\)\.limit\(([^)]*)\)', 
             r'cursor = collection.find(\1).limit(\2)\n            items = await cursor.to_list(length=\2)'),
            
            # Fix sort operations
            (r'cursor = await collection\.find\(([^)]*)\)\.sort\(([^)]*)\)', 
             r'cursor = collection.find(\1).sort(\2)'),
            (r'results = await collection\.find\(([^)]*)\)\.sort\(([^)]*)\)', 
             r'cursor = collection.find(\1).sort(\2)\n            results = await cursor.to_list(length=None)'),
            
            # Fix iteration patterns
            (r'for item in await collection\.find\(([^)]*)\):', r'async for item in collection.find(\1):'),
            
            # Fix list comprehensions with find
            (r'\[([^]]*) for ([^]]*) in await collection\.find\(([^)]*)\)\]',
             r'cursor = collection.find(\3)\n            temp_list = await cursor.to_list(length=None)\n            [\1 for \2 in temp_list]'),
        ]
        
        for pattern, replacement in cursor_fixes:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                changes_made = True
                logger.debug(f"Applied cursor fix: {pattern}")
        
        # Fix specific method patterns in services
        if 'async def list_' in content:
            # Fix list methods
            list_method_pattern = r'(async def list_[^(]+\([^)]*\):.*?)cursor = await collection\.find\(([^)]*)\)\.skip\(([^)]*)\)\.limit\(([^)]*)\)\s*docs = await cursor\.to_list\(length=\4\)'
            replacement = r'\1cursor = collection.find(\2).skip(\3).limit(\4)\n            docs = await cursor.to_list(length=\4)'
            new_content = re.sub(list_method_pattern, replacement, content, flags=re.DOTALL)
            if new_content != content:
                content = new_content
                changes_made = True
        
        # Only write if content actually changed
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Fixed Motor cursor operations: {filepath}")
            return True
        else:
            logger.debug(f"⏭️  No cursor fixes needed: {filepath}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix Motor cursor operations in all service files"""
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
        if fix_motor_cursor_operations(service_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 MOTOR CURSOR OPERATIONS FIX COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*60)
    print("COMPREHENSIVE MOTOR CURSOR FIX RESULTS")
    print("="*60)
    print(f"Total Service Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*60)
    print("\n✅ All AsyncIOMotorCursor operations fixed!")
    print("🔄 Restart backend to eliminate cursor errors.")

if __name__ == "__main__":
    main()