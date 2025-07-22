"""
i18n_system Service
Provides business logic for I18N System
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import get_database

class I18nSystemService:
    """Service class for I18N System"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["i18n_system"]
    
    async def get_all(self, user_id: str, limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all records for user"""
        cursor = self.collection.find(
            {"user_id": user_id},
            limit=limit,
            skip=skip,
            sort=[("created_at", -1)]
        )
        return await cursor.to_list(length=limit)
    
    async def get_by_id(self, user_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        return await self.collection.find_one({
            "id": record_id,
            "user_id": user_id
        })
    
    async def create(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new record"""
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **data
        }
        
        await self.collection.insert_one(record)
        return record
    
    async def update(self, user_id: str, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing record"""
        update_data = {
            **data,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.find_one_and_update(
            {"id": record_id, "user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
        
        return result
    
    async def delete(self, user_id: str, record_id: str) -> bool:
        """Delete record"""
        result = await self.collection.delete_one({
            "id": record_id,
            "user_id": user_id
        })
        
        return result.deleted_count > 0
    
    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics"""
        total = await self.collection.count_documents({"user_id": user_id})
        
        return {
            "total_records": total,
            "service": "i18n_system",
            "last_updated": datetime.utcnow().isoformat()
        }

# Service instance
i18n_system_service = I18nSystemService()
