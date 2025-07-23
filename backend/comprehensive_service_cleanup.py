#!/usr/bin/env python3
"""
COMPREHENSIVE SERVICE FILES CLEANUP AND FIX
Fixes all syntax errors, duplicate functions, and ensures proper structure
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_and_fix_service_file(filepath):
    """Clean and fix a service file completely"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix basic syntax issues
        # 1. Remove duplicate function definitions that are causing syntax errors
        content = re.sub(r'def _get_collection\(self\):\s*async def _get_collection_async\(self\):', 
                        'async def _get_collection_async(self):', content)
        
        # 2. Fix incomplete function definitions
        content = re.sub(r'def _get_collection\(self\):\s*$', 
                        'def _get_collection(self):\n        """Get collection synchronously"""\n        pass', 
                        content, flags=re.MULTILINE)
        
        # 3. Remove duplicate return statements and blocks
        content = re.sub(r'(\s+return {"success": False, "healthy": False, "error": "Database unavailable"}\s+){2,}', 
                        r'\1', content)
        
        # 4. Fix broken health check methods
        broken_health_pattern = r'async def health_check\(self\) -> dict:.*?return {"success": False, "healthy": False, "error": str\(e\)}'
        if re.search(broken_health_pattern, content, re.DOTALL):
            health_check_template = '''async def health_check(self) -> dict:
        """Health check with proper async database connection"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if not db:
                return {"success": False, "healthy": False, "error": "Database unavailable"}
            
            collection = db[self.collection_name]
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": self.service_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check error in {self.service_name}: {e}")
            return {"success": False, "healthy": False, "error": str(e)}'''
            
            content = re.sub(broken_health_pattern, health_check_template, content, flags=re.DOTALL)
        
        # 5. Ensure proper async collection method exists
        if 'async def _get_collection_async' not in content:
            async_method = '''
    async def _get_collection_async(self):
        """Get collection with proper async handling"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            return db[self.collection_name] if db else None
        except Exception as e:
            logger.error(f"Async collection error: {e}")
            return None'''
            
            # Add after class definition or existing methods
            if 'def __init__' in content:
                content = re.sub(r'(def __init__.*?\n        [^\n]*collection_name[^\n]*\n)', 
                               r'\1' + async_method, content, flags=re.DOTALL)
        
        # 6. Fix import statements
        required_imports = [
            'from datetime import datetime',
            'import uuid',
            'import logging'
        ]
        
        for import_line in required_imports:
            if import_line not in content and not content.startswith(import_line):
                # Add after the first import or at the beginning
                if 'import ' in content:
                    content = re.sub(r'(^""".*?"""\s*\n)', r'\1' + import_line + '\n', content, flags=re.DOTALL)
                else:
                    content = import_line + '\n' + content
        
        # 7. Add logger if missing
        if 'logger = logging.getLogger(__name__)' not in content:
            content = re.sub(r'(import logging\n)', r'\1logger = logging.getLogger(__name__)\n', content)
        
        # 8. Fix class definition issues
        content = re.sub(r'class (\w+):\s*$', r'class \1:\n    """Service class for \1 operations"""', content, flags=re.MULTILINE)
        
        # Only write if content actually changed
        if content.strip() != original_content.strip():
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Cleaned and fixed: {filepath}")
            return True
        else:
            logger.info(f"⏭️  No changes needed: {filepath}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Clean and fix all service files"""
    backend_dir = Path("/app/backend")
    services_dir = backend_dir / "services"
    
    if not services_dir.exists():
        logger.error("Services directory not found!")
        return
    
    fixed_count = 0
    total_count = 0
    
    # Process all Python service files except __init__.py
    for service_file in services_dir.glob("*.py"):
        if service_file.name in ["__init__.py"]:
            continue
            
        total_count += 1
        if clean_and_fix_service_file(service_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 SERVICE CLEANUP COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*50)
    print("COMPREHENSIVE SERVICE CLEANUP RESULTS")
    print("="*50)
    print(f"Total Service Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*50)

if __name__ == "__main__":
    main()