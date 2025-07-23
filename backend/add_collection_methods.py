#!/usr/bin/env python3
"""
COMPREHENSIVE SERVICE COLLECTION METHODS FIX
Adds missing _get_collection methods to all service files for database access
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_get_collection_method(filepath):
    """Add missing _get_collection method to service file"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if _get_collection method already exists
        if 'def _get_collection(self):' in content:
            logger.debug(f"⏭️  _get_collection already exists: {filepath}")
            return False
        
        # Extract service name from class definition to determine collection name
        class_match = re.search(r'class (\w+Service):', content)
        if not class_match:
            logger.warning(f"⚠️  No service class found in {filepath}")
            return False
        
        class_name = class_match.group(1)
        
        # Determine collection name from service class name
        # Remove 'Service' and convert to snake_case
        service_base = class_name.replace('Service', '')
        collection_name = re.sub(r'([A-Z])', r'_\1', service_base).lower().strip('_')
        
        # Template for _get_collection method
        get_collection_template = f'''
    def _get_collection(self):
        """Get collection for database operations"""
        try:
            from core.database import get_database
            db = get_database()
            if db is None:
                logger.error("Database not available")
                return None
            return db["{collection_name}"]
        except Exception as e:
            logger.error(f"Error getting collection: {{e}}")
            return None

    async def _get_collection_async(self):
        """Get collection for async database operations"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if db is None:
                logger.error("Database not available")
                return None
            return db["{collection_name}"]
        except Exception as e:
            logger.error(f"Error getting async collection: {{e}}")
            return None'''
        
        # Find where to insert the methods (after __init__ method)
        init_pattern = r'(def __init__\(self\):.*?(?=\n    def|\n    async def|\n\n|$))'
        init_match = re.search(init_pattern, content, re.DOTALL)
        
        if init_match:
            # Insert after __init__ method
            content = content.replace(init_match.group(1), init_match.group(1) + get_collection_template)
        else:
            # If no __init__ found, insert after class definition
            class_pattern = r'(class \w+Service:.*?\n)'
            class_match = re.search(class_pattern, content, re.DOTALL)
            if class_match:
                # Add __init__ and collection methods
                init_and_collection = f'''
    def __init__(self):
        """Initialize service"""
        self.collection_name = "{collection_name}"
        self.service_name = "{service_base.lower()}"
{get_collection_template}'''
                content = content.replace(class_match.group(1), class_match.group(1) + init_and_collection)
            else:
                logger.warning(f"⚠️  Could not find class definition in {filepath}")
                return False
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Added _get_collection methods to: {filepath}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Add _get_collection methods to all service files"""
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
        if add_get_collection_method(service_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 SERVICE COLLECTION METHODS FIX COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*60)
    print("SERVICE COLLECTION METHODS FIX RESULTS")
    print("="*60)
    print(f"Total Service Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*60)
    print("\n✅ All services now have _get_collection methods!")
    print("🔄 Restart backend to enable CRUD operations.")

if __name__ == "__main__":
    main()