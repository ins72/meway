#!/usr/bin/env python3
"""
COMPREHENSIVE SERVICE GETTER FUNCTIONS FIX
Adds all missing getter functions based on actual class names in service files
"""

import os
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_class_name(content):
    """Extract the actual service class name from file content"""
    class_pattern = r'class (\w+Service):'
    match = re.search(class_pattern, content)
    if match:
        return match.group(1)
    return None

def get_expected_getter_name(filename):
    """Get expected getter function name from filename"""
    if filename.endswith('_service'):
        service_name = filename[:-8]  # Remove '_service'
    else:
        service_name = filename
    return f"get_{service_name}_service"

def fix_service_file(filepath):
    """Add missing getter function to service file"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract actual class name
        class_name = extract_class_name(content)
        if not class_name:
            logger.warning(f"⚠️  No service class found in {filepath}")
            return False
        
        # Get expected getter function name
        filename = Path(filepath).stem
        getter_name = get_expected_getter_name(filename)
        
        # Check if getter already exists
        if getter_name in content:
            logger.info(f"⏭️  Getter exists: {filepath}")
            return False
        
        # Template for getter function
        getter_template = f'''

# Singleton instance
_service_instance = None

def {getter_name}():
    """Get singleton instance of {class_name}"""
    global _service_instance
    if _service_instance is None:
        _service_instance = {class_name}()
    return _service_instance'''
        
        # Add getter function at the end
        content += getter_template
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Added {getter_name} to {filepath}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all service files"""
    backend_dir = Path("/app/backend")
    services_dir = backend_dir / "services"
    
    if not services_dir.exists():
        logger.error("Services directory not found!")
        return
    
    fixed_count = 0
    total_count = 0
    
    # Process all Python service files except __init__.py
    for service_file in services_dir.glob("*.py"):
        if service_file.name in ["__init__.py", "__pycache__"]:
            continue
            
        total_count += 1
        if fix_service_file(service_file):
            fixed_count += 1
    
    logger.info(f"\n🎯 SERVICE GETTERS FIX COMPLETE:")
    logger.info(f"   📊 Total files: {total_count}")
    logger.info(f"   ✅ Fixed files: {fixed_count}")
    logger.info(f"   ⏭️  Unchanged: {total_count - fixed_count}")
    
    print("\n" + "="*50)
    print("COMPREHENSIVE SERVICE GETTERS FIX")
    print("="*50)
    print(f"Total Service Files: {total_count}")
    print(f"Files Fixed: {fixed_count}")
    print(f"Files Unchanged: {total_count - fixed_count}")
    print("="*50)

if __name__ == "__main__":
    main()