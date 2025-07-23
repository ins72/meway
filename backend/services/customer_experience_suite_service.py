"""
Customer Experience Suite Service
Complete CRUD operations for customer_experience_suite
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class CustomerExperienceSuiteService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["customerexperiencesuite"]

    async def create_customer_experience_suite(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer_experience_suite"""
        try:
            # Add metadata
            data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.collection.insert_one(data)
            
            return {
                "success": True,
                "message": f"Customer Experience Suite created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create customer_experience_suite: {str(e)}"
            }

    async def get_customer_experience_suite(self, item_id: str) -> Dict[str, Any]:
        """Get customer_experience_suite by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Customer Experience Suite not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get customer_experience_suite: {str(e)}"
            }

    async def list_customer_experience_suites(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List customer_experience_suites with pagination"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id field
            for doc in docs:
                doc.pop('_id', None)
            
            total_count = await self.collection.count_documents(query)
            
            return {
                "success": True,
                "data": docs,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list customer_experience_suites: {str(e)}"
            }

    async def update_customer_experience_suite(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer_experience_suite by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.collection.update_one(
                {"id": item_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Customer Experience Suite not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Customer Experience Suite updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update customer_experience_suite: {str(e)}"
            }

    async def delete_customer_experience_suite(self, item_id: str) -> Dict[str, Any]:
        """Delete customer_experience_suite by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Customer Experience Suite not found"
                }
            
            return {
                "success": True,
                "message": f"Customer Experience Suite deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete customer_experience_suite: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for customer_experience_suites"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            total_count = await self.collection.count_documents(query)
            active_count = await self.collection.count_documents({**query, "status": "active"})
            
            return {
                "success": True,
                "data": {
                    "total_count": total_count,
                    "active_count": active_count,
                    "service": "customer_experience_suite",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get customer_experience_suite stats: {str(e)}"
            }

# Service instance
_customer_experience_suite_service = None

def get_customer_experience_suite_service():
    """Get customer_experience_suite service instance"""
    global _customer_experience_suite_service
    if _customer_experience_suite_service is None:
        _customer_experience_suite_service = CustomerExperienceSuiteService()
    return _customer_experience_suite_service

# For backward compatibility
customer_experience_suite_service = get_customer_experience_suite_service()