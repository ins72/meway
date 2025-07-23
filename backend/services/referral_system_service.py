"""
Referral System Service
Comprehensive referral program management with rewards and tracking
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ReferralSystemService:
    """Comprehensive referral system service with rewards tracking"""
    
    def __init__(self):
        self.collection_name = "referral_system"
        self.service_name = "referral_system"

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
        """Health check for referral system"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "healthy": False, "error": "Database unavailable"}
            
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": self.service_name,
                "features": ["tracking", "rewards", "analytics"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check error in {self.service_name}: {e}")
            return {"success": False, "healthy": False, "error": str(e)}

    async def create_referral_program(self, data: dict) -> dict:
        """Create referral program"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Prepare referral program data
            program_data = {
                "id": str(uuid.uuid4()),
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "reward_type": data.get("reward_type", "percentage"),
                "reward_value": data.get("reward_value", 10.0),
                "minimum_payout": data.get("minimum_payout", 50.0),
                "user_id": data.get("user_id", ""),
                "referral_code": data.get("referral_code", f"REF_{uuid.uuid4().hex[:8].upper()}"),
                "status": "active",
                "analytics": {
                    "total_referrals": 0,
                    "successful_referrals": 0,
                    "pending_rewards": 0.0,
                    "paid_rewards": 0.0
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store in database - REAL DATA OPERATION
            result = await collection.insert_one(program_data)
            
            if result.inserted_id:
                return {
                    "success": True,
                    "message": "Referral program created successfully",
                    "data": program_data,
                    "id": program_data["id"]
                }
            else:
                return {"success": False, "error": "Database insert failed"}
                
        except Exception as e:
            logger.error(f"Create referral program error: {e}")
            return {"success": False, "error": str(e)}

    async def list_programs(self, user_id: str = None, limit: int = 50, offset: int = 0) -> dict:
        """List referral programs with real data"""
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
            logger.error(f"List programs error: {e}")
            return {"success": False, "error": str(e)}

    async def get_program(self, program_id: str) -> dict:
        """Get single referral program by ID"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            doc = await collection.find_one({"id": program_id})
            
            if doc:
                return {
                    "success": True,
                    "data": doc
                }
            else:
                return {"success": False, "error": "Program not found"}
                
        except Exception as e:
            logger.error(f"Get program error: {e}")
            return {"success": False, "error": str(e)}

    async def update_program(self, program_id: str, data: dict) -> dict:
        """Update referral program"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Update data
            update_data = {
                "name": data.get("name"),
                "description": data.get("description"),
                "reward_value": data.get("reward_value"),
                "status": data.get("status"),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = await collection.update_one(
                {"id": program_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": "Program updated successfully",
                    "id": program_id
                }
            else:
                return {"success": False, "error": "Program not found or no changes made"}
                
        except Exception as e:
            logger.error(f"Update program error: {e}")
            return {"success": False, "error": str(e)}

    async def delete_program(self, program_id: str) -> dict:
        """Delete referral program"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            result = await collection.delete_one({"id": program_id})
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Program deleted successfully",
                    "id": program_id
                }
            else:
                return {"success": False, "error": "Program not found"}
                
        except Exception as e:
            logger.error(f"Delete program error: {e}")
            return {"success": False, "error": str(e)}

# Singleton instance
_service_instance = None

def get_referral_system_service():
    """Get singleton instance of ReferralSystemService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ReferralSystemService()
    return _service_instance