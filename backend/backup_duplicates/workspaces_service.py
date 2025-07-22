"""
Workspaces Management Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class WorkspacesService:
    """Service for workspace management operations"""
    
    @staticmethod
    async def get_user_workspaces(user_id: str):
        """Get user's workspaces"""
        db = await get_database()
        
        workspaces = await db.workspaces.find({
    "$or": [
    {"user_id": user_id},
    {"members": user_id}
    ]
        }).sort("created_at", -1).to_list(length=None)
        
        return workspaces
    
    @staticmethod
    async def create_workspace(user_id: str, workspace_data: Dict[str, Any]):
        """Create new workspace"""
        db = await get_database()
        
        workspace = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "name": workspace_data.get("name"),
    "description": workspace_data.get("description", ""),
    "type": workspace_data.get("type", "business"),
    "industry": workspace_data.get("industry"),
    "settings": {
    "is_public": workspace_data.get("is_public", False),
    "allow_members": workspace_data.get("allow_members", True),
    "theme": workspace_data.get("theme", "default"),
    "branding": workspace_data.get("branding", {})
    },
    "members": [user_id],  # Owner is always a member
    "member_roles": {
    user_id: "owner"
    },
    "status": "active",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
    }
        
        result = await db.workspaces.insert_one(workspace)
        return workspace
    
    @staticmethod
    async def get_workspace_by_id(workspace_id: str, user_id: str = None):
        """Get workspace by ID"""
        db = await get_database()
        
        query = {"_id": workspace_id}
        
        # If user_id provided, ensure user has access
        if user_id:
            query["$or"] = [
    {"user_id": user_id},
    {"members": user_id}
    ]
        
        workspace = await db.workspaces.find_one(query)
        return workspace
    
    @staticmethod
    async def update_workspace(workspace_id: str, user_id: str, update_data: Dict[str, Any]):
        """Update workspace"""
        db = await get_database()
        
        # Verify user has permission to update
        workspace = await WorkspacesService.get_workspace_by_id(workspace_id, user_id)
        if not workspace:
            return None
        
        user_role = workspace.get("member_roles", {}).get(user_id, "member")
        if user_role not in ["owner", "admin"]:
            return None
        
        update_fields = {
    "name": update_data.get("name"),
    "description": update_data.get("description"),
    "industry": update_data.get("industry"),
    "updated_at": datetime.utcnow()
    }
        
        # Remove None values
        update_fields = {k: v for k, v in update_fields.items() if v is not None}
        
        if "settings" in update_data:
            current_settings = workspace.get("settings", {})
            new_settings = {**current_settings, **update_data["settings"]}
            update_fields["settings"] = new_settings
        
        result = await db.workspaces.update_one(
    {"_id": workspace_id},
    {"$set": update_fields}
    )
        
        return await db.workspaces.find_one({"_id": workspace_id})
    
    @staticmethod
    async def add_workspace_member(workspace_id: str, owner_id: str, member_email: str, role: str = "member"):
        """Add member to workspace"""
        db = await get_database()
        
        # Verify ownership
        workspace = await db.workspaces.find_one({
    "_id": workspace_id,
    "user_id": owner_id
    })
        if not workspace:
            return None
        
        # Find user by email
        member = await db.users.find_one({"email": member_email})
        if not member:
            return {"success": False, "error": "User not found"}
        
        member_id = member["_id"]
        
        # Check if already a member
        if member_id in workspace.get("members", []):
            return {"success": False, "error": "User is already a member"}
        
        # Add member
        result = await db.workspaces.update_one(
    {"_id": workspace_id},
    {
    "$addToSet": {"members": member_id},
    "$set": {f"member_roles.{member_id}": role}
    }
    )
        
        return {"success": True, "member_id": member_id, "role": role}
    
    @staticmethod
    async def get_workspace_analytics(workspace_id: str, user_id: str):
        """Get workspace analytics"""
        db = await get_database()
        
        # Verify access
        workspace = await WorkspacesService.get_workspace_by_id(workspace_id, user_id)
        if not workspace:
            return None
        
        # Generate analytics (simplified)
        analytics = {
    "overview": {
    "total_members": len(workspace.get("members", [])),
    "active_projects": 5,  # Would be calculated from actual data
    "total_tasks": 23,
    "completed_tasks": 18
    },
    "activity": {
    "daily_active_users": 3,
    "weekly_active_users": 7,
    "recent_activities": [
    {
    "type": "member_added",
    "message": "New member joined workspace",
    "timestamp": datetime.utcnow()
    }
    ]
    },
    "growth": {
    "member_growth": 15.5,  # percentage
    "activity_growth": 8.2
    }
    }
        
        return analytics

# Global service instance
workspaces_service = WorkspacesService()
