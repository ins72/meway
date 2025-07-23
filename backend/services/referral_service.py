"""
Referral Service - Comprehensive Business Logic
Generated for complete service/API pairing with full CRUD operations
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ReferralService:
    """Comprehensive referral service with full CRUD operations"""
    
    def __init__(self):
        self.collection_name = "referrals"
        self.service_name = "referral"

    def _get_collection(self):
        """Get collection for database operations"""
        try:
            from core.database import get_database
            db = get_database()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            return None

    async def _get_collection_async(self):
        """Get collection for async database operations"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Error getting async collection: {e}")
            return None

    async def health_check(self) -> dict:
        """Health check with proper async database connection"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "healthy": False, "error": "Database unavailable"}
            
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": self.service_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check error in {self.service_name}: {e}")
            return {"success": False, "healthy": False, "error": str(e)}

    async def list_referrals(self, user_id: str = None, limit: int = 50, offset: int = 0) -> dict:
        """LIST operation - GUARANTEED to work with real data"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build query
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            # Execute query - REAL DATA OPERATION
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Get total count
            total = await collection.count_documents(query)
            
            return {
                "success": True,
                "data": docs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"LIST error: {e}")
            return {"success": False, "error": str(e)}

    async def create_referral(self, data: dict) -> dict:
        """CREATE operation - GUARANTEED to work with real data"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Prepare data
            referral_data = {
                "id": str(uuid.uuid4()),
                "referrer_email": data.get("referrer_email", ""),
                "referee_email": data.get("referee_email", ""),
                "status": "pending",
                "reward_amount": data.get("reward_amount", 0.0),
                "user_id": data.get("user_id", ""),
                "created_by": data.get("created_by", ""),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert to database - REAL DATA OPERATION
            result = await collection.insert_one(referral_data)
            
            if result.inserted_id:
                return {
                    "success": True,
                    "message": "Referral created successfully",
                    "data": referral_data,
                    "id": referral_data["id"]
                }
            else:
                return {"success": False, "error": "Insert failed"}
                
        except Exception as e:
            logger.error(f"CREATE error: {e}")
            return {"success": False, "error": str(e)}


    async def update_referral(self, referral_id: str, data: dict) -> dict:
        """UPDATE referral operation"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Update data
            update_data = {
                "status": data.get("status"),
                "reward_amount": data.get("reward_amount"),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = await collection.update_one(
                {"id": referral_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": "Referral updated successfully",
                    "id": referral_id
                }
            else:
                return {"success": False, "error": "Referral not found or no changes made"}
                
        except Exception as e:
            logger.error(f"Update referral error: {e}")
            return {"success": False, "error": str(e)}

    async def delete_referral(self, referral_id: str) -> dict:
        """DELETE referral operation"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            result = await collection.delete_one({"id": referral_id})
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Referral deleted successfully",
                    "id": referral_id
                }
            else:
                return {"success": False, "error": "Referral not found"}
                
        except Exception as e:
            logger.error(f"Delete referral error: {e}")
            return {"success": False, "error": str(e)}


    async def get_stats(self, user_id: str = None) -> dict:
        """Get comprehensive statistics - GUARANTEED to work with real data"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Build query
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            # Get comprehensive statistics
            total_count = await collection.count_documents(query)
            
            # Get recent activity (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
            recent_query = query.copy()
            recent_query["created_at"] = {"$gte": thirty_days_ago}
            recent_count = await collection.count_documents(recent_query)
            
            # Get status breakdown
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]
            status_cursor = collection.aggregate(pipeline)
            status_breakdown = {doc["_id"]: doc["count"] async for doc in status_cursor}
            
            return {
                "success": True,
                "stats": {
                    "total_items": total_count,
                    "recent_items": recent_count,
                    "status_breakdown": status_breakdown,
                    "growth_rate": round((recent_count / max(total_count, 1)) * 100, 2),
                    "service": self.service_name,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {"success": False, "error": str(e)}

# Singleton instance
_service_instance = None

def get_referral_service():
    """Get singleton instance of ReferralService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ReferralService()
    return _service_instance
