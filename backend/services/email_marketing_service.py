"""
Email Marketing Service
Complete CRUD operations for email_marketing
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class EmailMarketingService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["emailmarketing"]

    async def create_email_marketing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new email_marketing"""
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
                "message": f"Email Marketing created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create email_marketing: {str(e)}"
            }

    async def get_email_marketing(self, item_id: str) -> Dict[str, Any]:
        """Get email_marketing by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Email Marketing not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get email_marketing: {str(e)}"
            }

    async def list_email_marketings(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List email_marketings with pagination"""
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
                "error": f"Failed to list email_marketings: {str(e)}"
            }

    async def update_email_marketing(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update email_marketing by ID"""
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
                    "error": f"Email Marketing not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Email Marketing updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update email_marketing: {str(e)}"
            }

    async def delete_email_marketing(self, item_id: str) -> Dict[str, Any]:
        """Delete email_marketing by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Email Marketing not found"
                }
            
            return {
                "success": True,
                "message": f"Email Marketing deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete email_marketing: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for email_marketings"""
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
                    "service": "email_marketing",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get email_marketing stats: {str(e)}"
            }

# Service instance
_email_marketing_service = None

def get_email_marketing_service():
    """Get email_marketing service instance"""
    global _email_marketing_service
    if _email_marketing_service is None:
        _email_marketing_service = EmailMarketingService()
    return _email_marketing_service

# For backward compatibility
email_marketing_service = get_email_marketing_service()