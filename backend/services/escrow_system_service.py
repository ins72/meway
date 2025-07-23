"""
Escrow_System Service
Auto-generated to complete service/API pairing
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class Escrow_SystemService:
    def __init__(self):
        self.db = get_database()

    async def create_escrow_system(self, escrow_system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new escrow_system"""
        try:
            # Add metadata
            escrow_system_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["escrow_system"].insert_one(escrow_system_data)
            
            return {
                "success": True,
                "message": f"Escrow_System created successfully",
                "data": escrow_system_data,
                "id": escrow_system_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create escrow_system: {str(e)}"
            }

    async def get_escrow_system(self, escrow_system_id: str) -> Dict[str, Any]:
        """Get escrow_system by ID"""
        try:
            result = await self.db["escrow_system"].find_one({"id": escrow_system_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Escrow_System not found"
                }
            
            # Remove MongoDB _id
            result.pop('_id', None)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get escrow_system: {str(e)}"
            }

    async def list_escrow_system(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all escrow_system"""
        try:
            cursor = self.db["escrow_system"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await self.db["escrow_system"].count_documents({})
            
            return {
                "success": True,
                "data": results,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list escrow_system: {str(e)}"
            }

    async def update_escrow_system(self, escrow_system_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update escrow_system by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["escrow_system"].update_one(
                {"id": escrow_system_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Escrow_System not found"
                }
            
            # Get updated document
            updated_doc = await self.db["escrow_system"].find_one({"id": escrow_system_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Escrow_System updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update escrow_system: {str(e)}"
            }

    async def delete_escrow_system(self, escrow_system_id: str) -> Dict[str, Any]:
        """Delete escrow_system by ID"""
        try:
            result = await self.db["escrow_system"].delete_one({"id": escrow_system_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Escrow_System not found"
                }
            
            return {
                "success": True,
                "message": f"Escrow_System deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete escrow_system: {str(e)}"
            }
