#!/usr/bin/env python3
"""
MONGODB MOTOR TRUTH VALUE TESTING FIX
Fixes the critical "Database objects do not implement truth value testing" error
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_mongo_truth_testing(filepath):
    """Fix MongoDB Motor truth value testing issues in service files"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Pattern replacements for MongoDB Motor truth value testing fixes
        fixes = [
            # Fix direct database truth testing
            (r'if\s+db\s*:', 'if db is not None:'),
            (r'if\s+database\s*:', 'if database is not None:'),
            (r'if\s+collection\s*:', 'if collection is not None:'),
            
            # Fix negated truth testing
            (r'if\s+not\s+db\s*:', 'if db is None:'),
            (r'if\s+not\s+database\s*:', 'if database is None:'),
            (r'if\s+not\s+collection\s*:', 'if collection is None:'),
            
            # Fix return conditions
            (r'return\s+db\s+if\s+db\s+else\s+None', 'return db if db is not None else None'),
            (r'return\s+database\s+if\s+database\s+else\s+None', 'return database if database is not None else None'),
            (r'return\s+collection\s+if\s+collection\s+else\s+None', 'return collection if collection is not None else None'),
            
            # Fix conditional expressions
            (r'db\[([^\]]+)\]\s+if\s+db\s+else\s+None', r'db[\1] if db is not None else None'),
            (r'database\[([^\]]+)\]\s+if\s+database\s+else\s+None', r'database[\1] if database is not None else None'),
        ]
        
        for pattern, replacement in fixes:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                changes_made = True
                logger.debug(f"Applied fix: {pattern} -> {replacement}")
        
        # Specific fix for common health check patterns
        health_check_patterns = [
            # Fix database unavailable checks
            (r'if\s+not\s+db\s*:\s*return\s+{"success":\s*False,\s*"healthy":\s*False,\s*"error":\s*"Database unavailable"}',
             'if db is None:\n                return {"success": False, "healthy": False, "error": "Database unavailable"}'),
            
            (r'if\s+not\s+collection\s*:\s*return\s+{"success":\s*False,\s*"healthy":\s*False,\s*"error":\s*"Database unavailable"}',
             'if collection is None:\n                return {"success": False, "healthy": False, "error": "Database unavailable"}'),
        ]
        
        for pattern, replacement in health_check_patterns:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                content = new_content
                changes_made = True
                logger.debug(f"Applied health check fix: {pattern}")
        
        # Only write if content changed
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Fixed MongoDB truth testing: {filepath}")
            return True
        else:
            logger.debug(f"⏭️  No MongoDB truth testing issues: {filepath}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix MongoDB Motor truth value testing in all service files"""
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
        if fix_mongo_truth_testing(service_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 MONGODB TRUTH TESTING FIX COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*60)
    print("MONGODB MOTOR TRUTH VALUE TESTING FIX RESULTS")
    print("="*60)
    print(f"Total Service Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*60)
    print("\n✅ MongoDB Motor compatibility issues resolved!")
    print("🔄 Restart backend to apply changes.")

if __name__ == "__main__":
    main()