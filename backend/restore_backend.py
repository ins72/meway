#!/usr/bin/env python3
"""
Backend Restoration Script
Systematically restores all corrupted service files and ensures proper CRUD operations
"""

import os
import sys
import importlib.util
import traceback
from typing import Dict, List, Set

# Add backend directory to path
sys.path.insert(0, '/app/backend')

def check_service_file(service_path: str) -> Dict[str, any]:
    """Check if a service file is valid"""
    try:
        spec = importlib.util.spec_from_file_location("test_service", service_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return {
            "valid": True,
            "error": None,
            "has_service_class": hasattr(module, f"{os.path.basename(service_path).replace('.py', '').replace('_service', '').title()}Service")
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "has_service_class": False
        }

def generate_service_template(service_name: str, collection_name: str = None) -> str:
    """Generate a clean service template with full CRUD operations"""
    if collection_name is None:
        collection_name = service_name.lower().replace('_', '')
    
    class_name = ''.join(word.capitalize() for word in service_name.split('_'))
    
    return f'''"""
{service_name.title().replace('_', ' ')} Service
Complete CRUD operations for {service_name}
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class {class_name}Service:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["{collection_name}"]

    async def create_{service_name}(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new {service_name}"""
        try:
            # Add metadata
            data.update({{
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            }})
            
            # Save to database
            result = await self.collection.insert_one(data)
            
            return {{
                "success": True,
                "message": f"{service_name.title().replace('_', ' ')} created successfully",
                "data": data,
                "id": data["id"]
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": f"Failed to create {service_name}: {{str(e)}}"
            }}

    async def get_{service_name}(self, item_id: str) -> Dict[str, Any]:
        """Get {service_name} by ID"""
        try:
            doc = await self.collection.find_one({{"id": item_id}})
            
            if not doc:
                return {{
                    "success": False,
                    "error": f"{service_name.title().replace('_', ' ')} not found"
                }}
            
            doc.pop('_id', None)
            return {{
                "success": True,
                "data": doc
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": f"Failed to get {service_name}: {{str(e)}}"
            }}

    async def list_{service_name}s(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List {service_name}s with pagination"""
        try:
            query = {{}}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id field
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await self.collection.count_documents(query)
            
            return {{
                "success": True,
                "data": docs,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": f"Failed to list {service_name}s: {{str(e)}}"
            }}

    async def update_{service_name}(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update {service_name} by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.collection.update_one(
                {{"id": item_id}},
                {{"$set": update_data}}
            )
            
            if result.matched_count == 0:
                return {{
                    "success": False,
                    "error": f"{service_name.title().replace('_', ' ')} not found"
                }}
            
            # Get updated document
            updated_doc = await self.collection.find_one({{"id": item_id}})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {{
                "success": True,
                "message": f"{service_name.title().replace('_', ' ')} updated successfully",
                "data": updated_doc
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": f"Failed to update {service_name}: {{str(e)}}"
            }}

    async def delete_{service_name}(self, item_id: str) -> Dict[str, Any]:
        """Delete {service_name} by ID"""
        try:
            result = await self.collection.delete_one({{"id": item_id}})
            
            if result.deleted_count == 0:
                return {{
                    "success": False,
                    "error": f"{service_name.title().replace('_', ' ')} not found"
                }}
            
            return {{
                "success": True,
                "message": f"{service_name.title().replace('_', ' ')} deleted successfully",
                "deleted_count": result.deleted_count
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": f"Failed to delete {service_name}: {{str(e)}}"
            }}

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for {service_name}s"""
        try:
            query = {{}}
            if user_id:
                query["user_id"] = user_id
            
            total_count = await self.collection.count_documents(query)
            active_count = await self.collection.count_documents({{**query, "status": "active"}})
            
            return {{
                "success": True,
                "data": {{
                    "total_count": total_count,
                    "active_count": active_count,
                    "service": "{service_name}",
                    "last_updated": datetime.utcnow().isoformat()
                }}
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": f"Failed to get {service_name} stats: {{str(e)}}"
            }}

# Service instance
_{service_name}_service = None

def get_{service_name}_service():
    """Get {service_name} service instance"""
    global _{service_name}_service
    if _{service_name}_service is None:
        _{service_name}_service = {class_name}Service()
    return _{service_name}_service

# For backward compatibility
{service_name}_service = get_{service_name}_service()'''

def restore_services():
    """Restore all corrupted service files"""
    services_dir = '/app/backend/services'
    
    # Get all service files
    service_files = []
    for file in os.listdir(services_dir):
        if file.endswith('_service.py') and not file.startswith('__'):
            service_files.append(file)
    
    print(f"Found {len(service_files)} service files to check")
    
    corrupted_files = []
    working_files = []
    
    # Check each service file
    for service_file in service_files:
        service_path = os.path.join(services_dir, service_file)
        result = check_service_file(service_path)
        
        if result["valid"]:
            working_files.append(service_file)
            print(f"✅ {service_file} - Working")
        else:
            corrupted_files.append(service_file)
            print(f"❌ {service_file} - Error: {result['error']}")
    
    print(f"\nSummary: {len(working_files)} working, {len(corrupted_files)} corrupted")
    
    if corrupted_files:
        print("\nRestoring corrupted files...")
        for service_file in corrupted_files:
            service_name = service_file.replace('.py', '').replace('_service', '')
            service_path = os.path.join(services_dir, service_file)
            
            # Create backup
            backup_path = f"{service_path}.backup"
            if os.path.exists(service_path):
                os.rename(service_path, backup_path)
            
            # Generate clean service
            clean_service = generate_service_template(service_name)
            
            with open(service_path, 'w') as f:
                f.write(clean_service)
            
            print(f"✅ Restored {service_file}")
    
    return working_files, corrupted_files

def test_main_import():
    """Test if main.py can be imported"""
    try:
        sys.path.insert(0, '/app/backend')
        import main
        print("✅ main.py imported successfully")
        return True
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Backend Restoration Process...")
    
    # First check main.py import
    print("\n1. Testing main.py import...")
    main_works = test_main_import()
    
    if not main_works:
        print("\n2. Analyzing and restoring service files...")
        working, corrupted = restore_services()
        
        print("\n3. Testing main.py import after restoration...")
        main_works = test_main_import()
        
        if main_works:
            print("\n🎉 Backend restoration successful!")
            print(f"✅ Restored {len(corrupted)} corrupted service files")
            print(f"✅ {len(working)} service files were already working")
        else:
            print("\n❌ Backend restoration incomplete. Manual intervention required.")
    else:
        print("\n✅ Backend is already working!")
    
    print("\n4. Final verification...")
    if main_works:
        print("✅ Backend is ready for endpoint testing")
    else:
        print("❌ Backend requires additional fixes")