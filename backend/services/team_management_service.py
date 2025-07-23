"""
Team_Management Service - Comprehensive Business Logic
Generated for complete service/API pairing with full CRUD operations
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class Team_ManagementService:
    """Comprehensive team_management service with full CRUD operations"""
    
    def __init__(self):
        self.db = None
    
    async def get_database(self):
        """Get database connection with lazy initialization"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def create_team_management(self, team_management_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create team_management with real data persistence"""
        try:
            # Add metadata
            team_management_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": team_management_data.get("status", "active")
            })
            
            # Save to database
            db = await self.get_database()
            result = await db["team_management"].insert_one(team_management_data)
            
            return {
                "success": True,
                "message": f"Team_Management created successfully",
                "data": team_management_data,
                "id": team_management_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create team_management: {str(e)}"
            }
    
    async def get_team_management(self, team_management_id: str) -> Dict[str, Any]:
        """Get team_management by ID with real data"""
        try:
            db = await self.get_database()
            result = await db["team_management"].find_one({"id": team_management_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Team_Management not found"
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
                "error": f"Failed to get team_management: {str(e)}"
            }
    
    async def list_team_management(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all team_management with real data"""
        try:
            db = await self.get_database()
            cursor = db["team_management"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await db["team_management"].count_documents({})
            
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
                "error": f"Failed to list team_management: {str(e)}"
            }
    
    async def update_team_management(self, team_management_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update team_management with real data persistence"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["team_management"].update_one(
                {"id": team_management_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Team_Management not found"
                }
            
            # Get updated document
            updated_doc = await db["team_management"].find_one({"id": team_management_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Team_Management updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update team_management: {str(e)}"
            }
    
    async def delete_team_management(self, team_management_id: str) -> Dict[str, Any]:
        """Delete team_management with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["team_management"].delete_one({"id": team_management_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Team_Management not found"
                }
            
            return {
                "success": True,
                "message": f"Team_Management deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete team_management: {str(e)}"
            }
    
    async def search_team_management(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search team_management with real data"""
        try:
            db = await self.get_database()
            
            # Simple text search (can be enhanced with MongoDB text search)
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = db["team_management"].find(search_filter).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            return {
                "success": True,
                "data": results,
                "query": query,
                "count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search team_management: {str(e)}"
            }
