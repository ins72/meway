"""
Workspace Service - Real Database Operations
Professional Mewayz Platform
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from core.database import get_workspaces_collection, get_users_collection

class WorkspaceService:
    def __init__(self):
        self.workspaces_collection = None
        self.users_collection = None
    
    def _ensure_collections(self):
        """Ensure collections are initialized"""
        if self.workspaces_collection is None:
            self.workspaces_collection = get_workspaces_collection()
        if self.users_collection is None:
            self.users_collection = get_users_collection()

    async def create_workspace(self, name: str, owner_id: str, description: str = "") -> Dict[str, Any]:
        """Create a new workspace with real database operations"""
        self._ensure_collections()
        
        # Check if user exists
        user = await self.users_collection.find_one({"_id": owner_id})
        if not user:
            raise ValueError("User not found")
        
        # Check user's subscription limits
        plan_limits = self._get_plan_limits(user.get("subscription_plan", "free"))
        
        # Count existing workspaces
        existing_count = await self.workspaces_collection.count_documents({"owner_id": owner_id})
        
        if plan_limits["workspaces"] != -1 and existing_count >= plan_limits["workspaces"]:
            raise ValueError(f"Workspace limit reached. Upgrade your plan to create more workspaces.")
        
        # Create workspace document
        workspace_doc = {
            "_id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "members": [owner_id],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "settings": {
                "theme": "dark",
                "language": "en",
                "timezone": "UTC",
                "visibility": "private"
            },
            "subscription_plan": user.get("subscription_plan", "free"),
            "features_enabled": self._get_plan_features(user.get("subscription_plan", "free")),
            "statistics": {
                "total_projects": 0,
                "total_members": 1,
                "storage_used_mb": 0,
                "last_activity": datetime.utcnow()
            }
        }
        
        # Insert workspace
        await self.workspaces_collection.insert_one(workspace_doc)
        
        # Update user workspace count
        await self.users_collection.update_one(
            {"_id": owner_id},
            {"$inc": {"usage_stats.workspaces_created": 1}}
        )
        
        return workspace_doc

    async def get_user_workspaces(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all workspaces for a user with real database operations"""
        self._ensure_collections()
        
        # Find workspaces where user is owner or member
        workspaces = await self.workspaces_collection.find({
            "$or": [
                {"owner_id": user_id},
                {"members": user_id}
            ]
        }).sort("created_at", -1).to_list(length=None)
        
        # Enrich with additional data
        for workspace in workspaces:
            # Get member count
            workspace["member_count"] = len(workspace.get("members", []))
            
            # Add user role
            if workspace["owner_id"] == user_id:
                workspace["user_role"] = "owner"
            else:
                workspace["user_role"] = "member"
            
            # Calculate activity score (real calculation based on last activity)
            days_since_activity = (datetime.utcnow() - workspace.get("statistics", {}).get("last_activity", datetime.utcnow())).days
            workspace["activity_score"] = max(0, 100 - (days_since_activity * 2))
        
        return workspaces

    async def get_workspace_details(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get detailed workspace information with real database operations"""
        # Find workspace
        workspace = await self.workspaces_collection.find_one({"_id": workspace_id})
        if not workspace:
            raise ValueError("Workspace not found")
        
        # Check if user has access
        if user_id not in workspace.get("members", []) and workspace["owner_id"] != user_id:
            raise ValueError("Access denied")
        
        # Get member details
        member_ids = workspace.get("members", [])
        members = await self.users_collection.find(
            {"_id": {"$in": member_ids}},
            {"password": 0}  # Exclude password
        ).to_list(length=None)
        
        # Add member info to workspace
        workspace["member_details"] = members
        workspace["member_count"] = len(members)
        
        # Add user role
        if workspace["owner_id"] == user_id:
            workspace["user_role"] = "owner"
            workspace["permissions"] = ["read", "write", "admin", "delete"]
        else:
            workspace["user_role"] = "member"
            workspace["permissions"] = ["read", "write"]
        
        return workspace

    async def update_workspace(self, workspace_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update workspace with real database operations"""
        # Find workspace
        workspace = await self.workspaces_collection.find_one({"_id": workspace_id})
        if not workspace:
            raise ValueError("Workspace not found")
        
        # Check permissions (only owner can update most settings)
        if workspace["owner_id"] != user_id:
            raise ValueError("Only workspace owner can update settings")
        
        # Prepare update document
        update_doc = {
            "$set": {
                "updated_at": datetime.utcnow()
            }
        }
        
        # Update allowed fields
        allowed_fields = ["name", "description", "settings"]
        for field in allowed_fields:
            if field in update_data:
                if field == "settings":
                    # Merge settings
                    for key, value in update_data[field].items():
                        update_doc["$set"][f"settings.{key}"] = value
                else:
                    update_doc["$set"][field] = update_data[field]
        
        # Update workspace
        result = await self.workspaces_collection.update_one(
            {"_id": workspace_id},
            update_doc
        )
        
        if result.modified_count == 0:
            raise ValueError("No changes made")
        
        # Return updated workspace
        return await self.get_workspace_details(workspace_id, user_id)

    async def add_member(self, workspace_id: str, owner_id: str, member_email: str) -> Dict[str, Any]:
        """Add member to workspace with real database operations"""
        # Find workspace
        workspace = await self.workspaces_collection.find_one({"_id": workspace_id})
        if not workspace:
            raise ValueError("Workspace not found")
        
        # Check permissions
        if workspace["owner_id"] != owner_id:
            raise ValueError("Only workspace owner can add members")
        
        # Find user by email
        user = await self.users_collection.find_one({"email": member_email})
        if not user:
            raise ValueError("User not found")
        
        # Check if user is already a member
        if user["_id"] in workspace.get("members", []):
            raise ValueError("User is already a member")
        
        # Check member limits
        plan_limits = self._get_plan_limits(workspace.get("subscription_plan", "free"))
        current_member_count = len(workspace.get("members", []))
        
        if plan_limits["team_members"] != -1 and current_member_count >= plan_limits["team_members"]:
            raise ValueError("Member limit reached. Upgrade your plan to add more members.")
        
        # Add member
        await self.workspaces_collection.update_one(
            {"_id": workspace_id},
            {
                "$push": {"members": user["_id"]},
                "$set": {"updated_at": datetime.utcnow()},
                "$inc": {"statistics.total_members": 1}
            }
        )
        
        return {
            "workspace_id": workspace_id,
            "member_added": {
                "id": user["_id"],
                "name": user["name"],
                "email": user["email"]
            },
            "total_members": current_member_count + 1
        }

    async def remove_member(self, workspace_id: str, owner_id: str, member_id: str) -> Dict[str, Any]:
        """Remove member from workspace with real database operations"""
        # Find workspace
        workspace = await self.workspaces_collection.find_one({"_id": workspace_id})
        if not workspace:
            raise ValueError("Workspace not found")
        
        # Check permissions
        if workspace["owner_id"] != owner_id:
            raise ValueError("Only workspace owner can remove members")
        
        # Can't remove owner
        if member_id == owner_id:
            raise ValueError("Cannot remove workspace owner")
        
        # Check if user is a member
        if member_id not in workspace.get("members", []):
            raise ValueError("User is not a member")
        
        # Remove member
        await self.workspaces_collection.update_one(
            {"_id": workspace_id},
            {
                "$pull": {"members": member_id},
                "$set": {"updated_at": datetime.utcnow()},
                "$inc": {"statistics.total_members": -1}
            }
        )
        
        return {
            "workspace_id": workspace_id,
            "member_removed": member_id,
            "total_members": len(workspace.get("members", [])) - 1
        }

    async def delete_workspace(self, workspace_id: str, owner_id: str) -> Dict[str, Any]:
        """Delete workspace with real database operations"""
        # Find workspace
        workspace = await self.workspaces_collection.find_one({"_id": workspace_id})
        if not workspace:
            raise ValueError("Workspace not found")
        
        # Check permissions
        if workspace["owner_id"] != owner_id:
            raise ValueError("Only workspace owner can delete workspace")
        
        # Delete workspace
        result = await self.workspaces_collection.delete_one({"_id": workspace_id})
        
        if result.deleted_count == 0:
            raise ValueError("Failed to delete workspace")
        
        return {
            "workspace_id": workspace_id,
            "deleted": True,
            "message": "Workspace deleted successfully"
        }

    def _get_plan_limits(self, plan: str) -> Dict[str, int]:
        """Get limits for subscription plan"""
        limits = {
            "free": {
                "workspaces": 1,
                "team_members": 1,
                "storage_gb": 1
            },
            "pro": {
                "workspaces": 5,
                "team_members": 10,
                "storage_gb": 10
            },
            "enterprise": {
                "workspaces": -1,  # Unlimited
                "team_members": -1,  # Unlimited
                "storage_gb": 100
            }
        }
        
        return limits.get(plan, limits["free"])

    def _get_plan_features(self, plan: str) -> List[str]:
        """Get features available for subscription plan"""
        features = {
            "free": [
                "basic_workspace",
                "basic_analytics"
            ],
            "pro": [
                "basic_workspace",
                "basic_analytics",
                "advanced_analytics",
                "team_collaboration",
                "integrations",
                "priority_support"
            ],
            "enterprise": [
                "basic_workspace",
                "basic_analytics", 
                "advanced_analytics",
                "team_collaboration",
                "integrations",
                "priority_support",
                "custom_branding",
                "sso_integration",
                "advanced_security",
                "dedicated_support"
            ]
        }
        
        return features.get(plan, features["free"])

# Create service instance function (dependency injection)
def get_workspace_service() -> WorkspaceService:
    return WorkspaceService()
# Global service instance
workspace_service = WorkspaceService()
