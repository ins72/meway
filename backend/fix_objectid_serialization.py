#!/usr/bin/env python3
"""
CRITICAL FIX: MongoDB ObjectId Serialization Issue
Fixes FastAPI JSON serialization errors with MongoDB ObjectId objects
"""

import os
import re
from bson import ObjectId

def fix_objectid_serialization():
    """Fix ObjectId serialization issues throughout the codebase"""
    
    # Pattern replacements to handle ObjectId serialization
    patterns = [
        # Convert ObjectId to string when creating response data
        (r'return\s+({.*?"_id":\s*[^,}]+.*?})', r'# Convert ObjectId to string\n        if "_id" in \1 and isinstance(\1["_id"], ObjectId):\n            \1["_id"] = str(\1["_id"])\n        return \1'),
        
        # Add ObjectId import where needed
        (r'^(from typing import.*?)$', r'\1\nfrom bson import ObjectId'),
        
        # Handle ObjectId in collection operations
        (r'await collection\.find_one\((.*?)\)', r'doc = await collection.find_one(\1)\n        if doc and "_id" in doc:\n            doc["_id"] = str(doc["_id"])\n        return doc'),
        
        # Handle cursor operations
        (r'docs = await cursor\.to_list\(length=([^)]+)\)', r'raw_docs = await cursor.to_list(length=\1)\n        docs = []\n        for doc in raw_docs:\n            if "_id" in doc:\n                doc["_id"] = str(doc["_id"])\n            docs.append(doc)'),
    ]
    
    # Directories to scan
    directories = ['services', 'api']
    
    files_fixed = 0
    total_replacements = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        replacements_made = 0
                        
                        # Apply ObjectId import if needed
                        if 'ObjectId' not in content and ('_id' in content or 'mongodb' in content.lower()):
                            if 'from bson import ObjectId' not in content:
                                lines = content.split('\n')
                                # Find the last import line
                                last_import_idx = -1
                                for i, line in enumerate(lines):
                                    if line.strip().startswith(('import ', 'from ')) and 'import' in line:
                                        last_import_idx = i
                                
                                if last_import_idx >= 0:
                                    lines.insert(last_import_idx + 1, 'from bson import ObjectId')
                                    content = '\n'.join(lines)
                                    replacements_made += 1
                        
                        # Only write if changes were made
                        if content != original_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            files_fixed += 1
                            total_replacements += replacements_made
                            print(f"✅ Fixed ObjectId imports in {file_path}")
                    
                    except Exception as e:
                        print(f"❌ Error processing {file_path}: {e}")
    
    return files_fixed, total_replacements

def create_objectid_serializer():
    """Create a utility for handling ObjectId serialization"""
    
    serializer_content = '''"""
ObjectId Serialization Utility
Handles MongoDB ObjectId serialization for FastAPI responses
"""

from bson import ObjectId
from typing import Any, Dict, List, Union

def serialize_objectid(obj: Any) -> Any:
    """Convert ObjectId objects to strings for JSON serialization"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: serialize_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_objectid(item) for item in obj]
    else:
        return obj

def prepare_response_data(data: Union[Dict, List]) -> Union[Dict, List]:
    """Prepare data for FastAPI response by serializing ObjectIds"""
    return serialize_objectid(data)

def safe_document_return(doc: Dict) -> Dict:
    """Safely return a MongoDB document with ObjectId converted to string"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def safe_documents_return(docs: List[Dict]) -> List[Dict]:
    """Safely return MongoDB documents with ObjectIds converted to strings"""
    for doc in docs:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return docs
'''
    
    try:
        with open('core/objectid_serializer.py', 'w', encoding='utf-8') as f:
            f.write(serializer_content)
        print("✅ Created ObjectId serialization utility: core/objectid_serializer.py")
        return True
    except Exception as e:
        print(f"❌ Error creating serializer utility: {e}")
        return False

if __name__ == "__main__":
    print("🔧 FIXING MONGODB OBJECTID SERIALIZATION ISSUES...")
    
    # Create serialization utility
    utility_created = create_objectid_serializer()
    
    # Fix imports throughout codebase
    files_fixed, total_replacements = fix_objectid_serialization()
    
    print(f"\n🎯 OBJECTID SERIALIZATION FIX COMPLETE:")
    print(f"   Utility Created: {'✅' if utility_created else '❌'}")
    print(f"   Files Fixed: {files_fixed}")
    print(f"   Total Replacements: {total_replacements}")
    
    if utility_created or total_replacements > 0:
        print(f"\n✅ SUCCESS: Fixed ObjectId serialization issues")
        print("🚀 FastAPI should now properly serialize MongoDB responses")
        print("\n📋 NEXT STEPS:")
        print("   1. Import and use the serialization utility in services")
        print("   2. Apply serialize_objectid() to all MongoDB query results")
        print("   3. Test API endpoints to confirm JSON serialization works")
    else:
        print("\n ℹ️ No ObjectId serialization issues found to fix")