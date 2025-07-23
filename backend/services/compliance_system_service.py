"""
Compliance System Service
Provides business logic for Compliance System
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import get_database

class ComplianceSystemService:
    """Service class for Compliance System"""
    
    def __init__(self):
        self.db = get_database()

    async def create_compliance_system(self, compliance_system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new compliance_system"""
        try:
            # Add metadata
            compliance_system_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["compliance_system"].insert_one(compliance_system_data)
            
            return {
                "success": True,
                "message": "Compliance system created successfully",
                "data": compliance_system_data,
                "id": compliance_system_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create compliance system: {str(e)}"
            }

    async def update_compliance_system(self, compliance_system_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update compliance_system by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["compliance_system"].update_one(
                {"id": compliance_system_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": "Compliance system not found"
                }
            
            # Get updated document
            updated_doc = await self.db["compliance_system"].find_one({"id": compliance_system_id})
            if updated_doc:
                updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": "Compliance system updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update compliance system: {str(e)}"
            }

    async def delete_compliance_system(self, compliance_system_id: str) -> Dict[str, Any]:
        """Delete compliance_system by ID"""
        try:
            result = await self.db["compliance_system"].delete_one({"id": compliance_system_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": "Compliance system not found"
                }
            
            return {
                "success": True,
                "message": "Compliance system deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete compliance system: {str(e)}"
            }

    async def get_compliance_system(self, compliance_system_id: str) -> Dict[str, Any]:
        """Get compliance system by ID"""
        try:
            doc = await self.db["compliance_system"].find_one({"id": compliance_system_id})
            
            if not doc:
                return {
                    "success": False,
                    "error": "Compliance system not found"
                }
            
            doc.pop('_id', None)
            return {
                "success": True,
                "data": doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get compliance system: {str(e)}"
            }

    async def list_compliance_systems(self, user_id: str = None, limit: int = 50) -> Dict[str, Any]:
        """List compliance systems"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            cursor = self.db["compliance_system"].find(query).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id field
            for doc in docs:
                doc.pop('_id', None)
            
            return {
                "success": True,
                "data": docs,
                "count": len(docs)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list compliance systems: {str(e)}"
            }