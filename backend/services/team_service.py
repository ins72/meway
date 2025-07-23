"""
Team Management Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class TeamService:
    """Service for team management operations"""
    
    @staticmethod
    async def get_team_members(user_id: str, workspace_id: str = None):
        """Get team members"""
        db = await get_database()
        
        query = {"owner_id": user_id}
        if workspace_id:
            query["workspace_id"] = workspace_id
        
        members = await db.team_members.find(query).to_list(length=None)
        return members
    
    @staticmethod
    async def invite_team_member(user_id: str, invite_data: Dict[str, Any]):
        """Invite new team member"""
        db = await get_database()
        
        invitation = {
    "_id": str(uuid.uuid4()),
    "owner_id": user_id,
    "workspace_id": invite_data.get("workspace_id"),
    "email": invite_data.get("email"),
    "role": invite_data.get("role", "member"),
    "permissions": invite_data.get("permissions", []),
    "status": "pending",
    "invited_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + datetime.timedelta(days=7)
    }
        
        result = await db.team_invitations.insert_one(invitation)
        return invitation
    
    @staticmethod
    async def get_team_projects(user_id: str):
        """Get team projects"""
        db = await get_database()
        
        projects = await db.team_projects.find({
    "$or": [
    {"owner_id": user_id},
    {"team_members": user_id}
    ]
        }).sort("created_at", -1).to_list(length=None)
        
        return projects
    
    @staticmethod
    async def create_project(user_id: str, project_data: Dict[str, Any]):
        """Create new team project"""
        db = await get_database()
        
        project = {
    "_id": str(uuid.uuid4()),
    "owner_id": user_id,
    "name": project_data.get("name"),
    "description": project_data.get("description", ""),
    "status": project_data.get("status", "active"),
    "team_members": project_data.get("team_members", []),
    "tasks": [],
    "deadline": project_data.get("deadline"),
    "priority": project_data.get("priority", "medium"),
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
    }
        
        result = await db.team_projects.insert_one(project)
        return project

# Global service instance
team_service = TeamService()

    async def get_item(self, user_id: str, item_id: str):
        """Get specific item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if not item:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "data": item,
                "message": "Item retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def update_item(self, user_id: str, item_id: str, update_data: dict):
        """Update existing item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collections['items'].update_one(
                {"_id": item_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                return {"success": False, "message": "Item not found or no changes made"}
            
            # Get updated item
            updated_item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            return {
                "success": True,
                "data": updated_item,
                "message": "Item updated successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def delete_item(self, user_id: str, item_id: str):
        """Delete item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['items'].delete_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "message": "Item deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_items(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's items"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['items'].find(query).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            
            total_count = await collections['items'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "items": items,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Items retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}