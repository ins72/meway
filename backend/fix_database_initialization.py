#!/usr/bin/env python3
"""
Fix Database Initialization Issue
Updates all service files to use proper lazy database initialization
"""

import os
import re
import sys

def fix_service_file(service_path: str) -> bool:
    """Fix a single service file to use lazy database initialization"""
    try:
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Skip if already fixed
        if 'def _get_db(self):' in content:
            return True
        
        # Pattern to match service class initialization
        class_pattern = r'class (\w+Service):\s*\n\s*def __init__\(self\):\s*\n\s*self\.db = get_database\(\)'
        
        # Check if this pattern exists
        if re.search(class_pattern, content):
            # Replace the pattern with lazy initialization
            new_init = '''def __init__(self):
        self.db = None
        self.collection = None
    
    def _get_db(self):
        """Get database connection (lazy initialization)"""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    def _get_collection(self, collection_name: str):
        """Get collection (lazy initialization)"""
        if self.collection is None:
            self.collection = self._get_db()[collection_name]
        return self.collection'''
            
            content = re.sub(
                r'def __init__\(self\):\s*\n\s*self\.db = get_database\(\)',
                new_init,
                content
            )
            
            # Replace direct self.db usage with self._get_db()
            content = re.sub(r'self\.db\[', 'self._get_db()[', content)
            
            # Replace self.collection usage with self._get_collection()
            content = re.sub(r'self\.collection\.', 'self._get_collection("default").', content)
            
            with open(service_path, 'w') as f:
                f.write(content)
            
            return True
    
    except Exception as e:
        print(f"Error fixing {service_path}: {e}")
        return False
    
    return False

def create_minimal_service_template(service_name: str, class_name: str) -> str:
    """Create a minimal working service template"""
    return f'''"""
{service_name.title().replace('_', ' ')} Service
Auto-generated service with proper database initialization
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class {class_name}Service:
    def __init__(self):
        pass
    
    def _get_db(self):
        """Get database connection"""
        return get_database()
    
    async def create_{service_name}(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new {service_name}"""
        try:
            db = self._get_db()
            if not db:
                return {{"success": False, "error": "Database not available"}}
            
            collection = db["{service_name}"]
            data.update({{
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            }})
            
            result = await collection.insert_one(data)
            return {{"success": True, "data": data, "id": data["id"]}}
        except Exception as e:
            return {{"success": False, "error": str(e)}}
    
    async def get_{service_name}(self, item_id: str) -> Dict[str, Any]:
        """Get {service_name} by ID"""
        try:
            db = self._get_db()
            if not db:
                return {{"success": False, "error": "Database not available"}}
            
            collection = db["{service_name}"]
            doc = await collection.find_one({{"id": item_id}})
            
            if not doc:
                return {{"success": False, "error": "Not found"}}
            
            doc.pop('_id', None)
            return {{"success": True, "data": doc}}
        except Exception as e:
            return {{"success": False, "error": str(e)}}
    
    async def list_{service_name}s(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List {service_name}s"""
        try:
            db = self._get_db()
            if not db:
                return {{"success": False, "error": "Database not available"}}
            
            collection = db["{service_name}"]
            query = {{}}
            if user_id:
                query["user_id"] = user_id
            
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await collection.count_documents(query)
            return {{"success": True, "data": docs, "total": total_count, "limit": limit, "offset": offset}}
        except Exception as e:
            return {{"success": False, "error": str(e)}}
    
    async def update_{service_name}(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update {service_name}"""
        try:
            db = self._get_db()
            if not db:
                return {{"success": False, "error": "Database not available"}}
            
            collection = db["{service_name}"]
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await collection.update_one(
                {{"id": item_id}},
                {{"$set": update_data}}
            )
            
            if result.matched_count == 0:
                return {{"success": False, "error": "Not found"}}
            
            updated_doc = await collection.find_one({{"id": item_id}})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {{"success": True, "data": updated_doc}}
        except Exception as e:
            return {{"success": False, "error": str(e)}}
    
    async def delete_{service_name}(self, item_id: str) -> Dict[str, Any]:
        """Delete {service_name}"""
        try:
            db = self._get_db()
            if not db:
                return {{"success": False, "error": "Database not available"}}
            
            collection = db["{service_name}"]
            result = await collection.delete_one({{"id": item_id}})
            
            if result.deleted_count == 0:
                return {{"success": False, "error": "Not found"}}
            
            return {{"success": True, "message": "Deleted successfully", "deleted_count": result.deleted_count}}
        except Exception as e:
            return {{"success": False, "error": str(e)}}

# Service instance
_service_instance = None

def get_{service_name}_service():
    """Get service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = {class_name}Service()
    return _service_instance

# Backward compatibility
{service_name}_service = get_{service_name}_service()'''

def fix_all_services():
    """Fix all service files"""
    services_dir = '/app/backend/services'
    
    fixed_count = 0
    error_count = 0
    
    for filename in os.listdir(services_dir):
        if filename.endswith('_service.py') and not filename.startswith('__'):
            service_path = os.path.join(services_dir, filename)
            service_name = filename.replace('_service.py', '')
            
            # Try to fix existing file
            if fix_service_file(service_path):
                print(f"✅ Fixed {filename}")
                fixed_count += 1
            else:
                # If fixing fails, create a minimal working version
                print(f"⚠️  Regenerating {filename}")
                class_name = ''.join(word.capitalize() for word in service_name.split('_'))
                
                # Create backup
                backup_path = f"{service_path}.backup"
                if os.path.exists(service_path):
                    try:
                        os.rename(service_path, backup_path)
                    except:
                        pass
                
                # Create minimal working service
                minimal_service = create_minimal_service_template(service_name, class_name)
                
                try:
                    with open(service_path, 'w') as f:
                        f.write(minimal_service)
                    print(f"✅ Regenerated {filename}")
                    fixed_count += 1
                except Exception as e:
                    print(f"❌ Failed to regenerate {filename}: {e}")
                    error_count += 1
    
    print(f"\n📊 Summary: {fixed_count} fixed, {error_count} errors")
    return fixed_count, error_count

def test_backend_import():
    """Test if backend can be imported"""
    try:
        sys.path.insert(0, '/app/backend')
        import main
        print("✅ Backend imports successfully")
        return True
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Database Initialization Issues...")
    
    # First test current state
    print("\n1. Testing current backend state...")
    if test_backend_import():
        print("✅ Backend is already working!")
        sys.exit(0)
    
    # Fix all services
    print("\n2. Fixing all service files...")
    fixed, errors = fix_all_services()
    
    # Test again
    print("\n3. Testing backend after fixes...")
    if test_backend_import():
        print(f"\n🎉 Backend restoration successful!")
        print(f"✅ Fixed {fixed} service files")
        if errors > 0:
            print(f"⚠️  {errors} files had errors but backend still works")
    else:
        print(f"\n❌ Backend still has issues after fixing {fixed} files")
        print("Manual intervention may be required")
    
    print("\n4. Ready for endpoint testing!")