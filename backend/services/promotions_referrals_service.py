"""
Promotions Referrals Service
Complete CRUD operations for promotions_referrals
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class PromotionsReferralsService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["promotionsreferrals"]

    async def create_promotions_referrals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new promotions_referrals"""
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
                "message": f"Promotions Referrals created successfully",
                "data": data,
                "id": data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create promotions_referrals: {str(e)}"
            }

    async def get_promotions_referrals(self, item_id: str) -> Dict[str, Any]:
        """Get promotions_referrals by ID"""
        try:
            doc = await self.collection.find_one({"id": item_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Promotions Referrals not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get promotions_referrals: {str(e)}"
            }

    async def list_promotions_referralss(self, user_id: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List promotions_referralss with pagination"""
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
                "error": f"Failed to list promotions_referralss: {str(e)}"
            }

    async def update_promotions_referrals(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update promotions_referrals by ID"""
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
                    "error": f"Promotions Referrals not found"
                }
            
            # Get updated document
            updated_doc = await self.collection.find_one({"id": item_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Promotions Referrals updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update promotions_referrals: {str(e)}"
            }

    async def delete_promotions_referrals(self, item_id: str) -> Dict[str, Any]:
        """Delete promotions_referrals by ID"""
        try:
            result = await self.collection.delete_one({"id": item_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Promotions Referrals not found"
                }
            
            return {
                "success": True,
                "message": f"Promotions Referrals deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete promotions_referrals: {str(e)}"
            }

    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics for promotions_referralss"""
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
                    "service": "promotions_referrals",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get promotions_referrals stats: {str(e)}"
            }

# Service instance
_promotions_referrals_service = None

def get_promotions_referrals_service():
    """Get promotions_referrals service instance"""
    global _promotions_referrals_service
    if _promotions_referrals_service is None:
        _promotions_referrals_service = PromotionsReferralsService()
    return _promotions_referrals_service

# For backward compatibility
promotions_referrals_service = get_promotions_referrals_service()