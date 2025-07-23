#!/usr/bin/env python3
"""
SERVICE GETTER FUNCTIONS FIX
Adds missing getter functions that API files expect
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_getter_function(filepath):
    """Add missing getter function to service file"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract service name from file path
        filename = Path(filepath).stem
        if filename.endswith('_service'):
            service_base_name = filename[:-8]  # Remove '_service'
        else:
            service_base_name = filename
        
        # Convert to camelCase class name
        class_name_parts = service_base_name.split('_')
        class_name = ''.join(word.capitalize() for word in class_name_parts) + 'Service'
        
        # Function name for getter
        getter_function_name = f"get_{service_base_name}_service"
        
        # Check if getter function already exists
        if getter_function_name in content:
            logger.info(f"⏭️  Getter already exists: {filepath}")
            return False
        
        # Check if service class exists
        if f"class {class_name}" not in content:
            logger.warning(f"⚠️  Service class {class_name} not found in {filepath}")
            return False
        
        # Template for getter function
        getter_template = f'''
# Singleton instance
_service_instance = None

def {getter_function_name}():
    """Get singleton instance of {class_name}"""
    global _service_instance
    if _service_instance is None:
        _service_instance = {class_name}()
    return _service_instance
'''
        
        # Add getter function at the end of the file
        content += getter_template
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Added getter to: {filepath}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Add getter functions to all service files"""
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
        if add_getter_function(service_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 GETTER FUNCTIONS FIX COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*50)
    print("SERVICE GETTER FUNCTIONS FIX RESULTS")
    print("="*50)
    print(f"Total Service Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*50)

if __name__ == "__main__":
    main()