"""
Advanced Team Management Service
Complete team invitations, role-based access control, and collaboration features
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import secrets
import hashlib

from core.database import get_database

class TeamRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"
    GUEST = "guest"

class InvitationStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

class PermissionType(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    INVITE = "invite"
    BILLING = "billing"

class AdvancedTeamManagementService:
    """Advanced team management with full RBAC and invitation system"""
    
    def __init__(self):
        self.db = get_database()
        self.teams_collection = self.db["teams"]
        self.team_members_collection = self.db["team_members"]
        self.invitations_collection = self.db["team_invitations"]
        self.roles_collection = self.db["team_roles"]
        self.permissions_collection = self.db["team_permissions"]
        self.audit_log_collection = self.db["team_audit_log"]
        
    # Team Creation & Management
    async def create_team(self, owner_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new team with owner"""
        team = {
            "id": str(uuid.uuid4()),
            "name": data["name"],
            "description": data.get("description", ""),
            "owner_id": owner_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "member_count": 1,
            "settings": {
                "allow_member_invites": data.get("allow_member_invites", False),
                "require_2fa": data.get("require_2fa", False),
                "default_role": data.get("default_role", TeamRole.MEMBER.value),
                "invitation_expiry_hours": data.get("invitation_expiry_hours", 168),  # 1 week
                "max_members": data.get("max_members", 50)
            },
            "integrations": {
                "slack_webhook": data.get("slack_webhook"),
                "discord_webhook": data.get("discord_webhook")
            },
            "billing_info": {
                "subscription_tier": "basic",
                "member_limit": 10
            }
        }
        
        await self.teams_collection.insert_one(team)
        
        # Add owner as team member
        owner_member = {
            "id": str(uuid.uuid4()),
            "team_id": team["id"],
            "user_id": owner_id,
            "role": TeamRole.OWNER.value,
            "joined_at": datetime.utcnow(),
            "invited_by": owner_id,
            "status": "active",
            "last_active": datetime.utcnow()
        }
        
        await self.team_members_collection.insert_one(owner_member)
        
        # Log team creation
        await self._log_team_action(team["id"], owner_id, "team_created", {
            "team_name": team["name"]
        })
        
        return team
    
    # Invitation System
    async def create_invitation(self, team_id: str, inviter_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create invitation for new team member"""
        # Verify inviter has permission
        if not await self._has_permission(team_id, inviter_id, PermissionType.INVITE):
            raise ValueError("No permission to invite members")
        
        team = await self.teams_collection.find_one({"id": team_id})
        if not team:
            raise ValueError("Team not found")
        
        # Check member limits
        current_members = await self.team_members_collection.count_documents({"team_id": team_id})
        if current_members >= team["billing_info"]["member_limit"]:
            raise ValueError("Team member limit reached")
        
        # Generate secure invitation token
        invitation_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(invitation_token.encode()).hexdigest()
        
        invitation = {
            "id": str(uuid.uuid4()),
            "team_id": team_id,
            "inviter_id": inviter_id,
            "email": data["email"],
            "role": data.get("role", team["settings"]["default_role"]),
            "personal_message": data.get("personal_message", ""),
            "token_hash": token_hash,
            "status": InvitationStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=team["settings"]["invitation_expiry_hours"]),
            "permissions": data.get("custom_permissions", [])
        }
        
        await self.invitations_collection.insert_one(invitation)
        
        # Log invitation
        await self._log_team_action(team_id, inviter_id, "member_invited", {
            "invited_email": data["email"],
            "role": invitation["role"]
        })
        
        return {
            **invitation,
            "invitation_url": f"/invitations/accept/{invitation_token}"
        }
    
    async def accept_invitation(self, invitation_token: str, user_id: str) -> Dict[str, Any]:
        """Accept team invitation"""
        token_hash = hashlib.sha256(invitation_token.encode()).hexdigest()
        
        invitation = await self.invitations_collection.find_one({
            "token_hash": token_hash,
            "status": InvitationStatus.PENDING.value
        })
        
        if not invitation:
            raise ValueError("Invalid or expired invitation")
        
        if invitation["expires_at"] < datetime.utcnow():
            await self.invitations_collection.update_one(
                {"id": invitation["id"]},
                {"$set": {"status": InvitationStatus.EXPIRED.value}}
            )
            raise ValueError("Invitation has expired")
        
        # Add user to team
        member = {
            "id": str(uuid.uuid4()),
            "team_id": invitation["team_id"],
            "user_id": user_id,
            "role": invitation["role"],
            "custom_permissions": invitation["permissions"],
            "joined_at": datetime.utcnow(),
            "invited_by": invitation["inviter_id"],
            "status": "active",
            "last_active": datetime.utcnow()
        }
        
        await self.team_members_collection.insert_one(member)
        
        # Update invitation status
        await self.invitations_collection.update_one(
            {"id": invitation["id"]},
            {
                "$set": {
                    "status": InvitationStatus.ACCEPTED.value,
                    "accepted_at": datetime.utcnow(),
                    "accepted_by": user_id
                }
            }
        )
        
        # Update team member count
        await self.teams_collection.update_one(
            {"id": invitation["team_id"]},
            {"$inc": {"member_count": 1}}
        )
        
        return member
    
    # Role & Permission Management
    async def update_member_role(self, team_id: str, updater_id: str, member_id: str, new_role: str) -> Dict[str, Any]:
        """Update team member's role"""
        # Verify updater has admin permission
        if not await self._has_permission(team_id, updater_id, PermissionType.ADMIN):
            raise ValueError("No permission to update member roles")
        
        member = await self.team_members_collection.find_one({
            "team_id": team_id,
            "user_id": member_id
        })
        
        if not member:
            raise ValueError("Member not found")
        
        old_role = member["role"]
        
        await self.team_members_collection.update_one(
            {"team_id": team_id, "user_id": member_id},
            {
                "$set": {
                    "role": new_role,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log role change
        await self._log_team_action(team_id, updater_id, "role_updated", {
            "member_id": member_id,
            "old_role": old_role,
            "new_role": new_role
        })
        
        return {"message": "Role updated successfully"}
    
    # Helper Methods
    async def _has_permission(self, team_id: str, user_id: str, permission: PermissionType) -> bool:
        """Check if user has specific permission in team"""
        member = await self.team_members_collection.find_one({
            "team_id": team_id,
            "user_id": user_id,
            "status": "active"
        })
        
        if not member:
            return False
        
        # Admin and owner have all permissions
        if member["role"] in [TeamRole.ADMIN.value, TeamRole.OWNER.value]:
            return True
            
        # Manager can invite and has read/write
        if member["role"] == TeamRole.MANAGER.value:
            return permission in [PermissionType.READ, PermissionType.WRITE, PermissionType.INVITE]
        
        # Member has read/write
        if member["role"] == TeamRole.MEMBER.value:
            return permission in [PermissionType.READ, PermissionType.WRITE]
        
        # Viewer has only read
        if member["role"] == TeamRole.VIEWER.value:
            return permission == PermissionType.READ
        
        return False
    
    async def _log_team_action(self, team_id: str, user_id: str, action: str, metadata: Dict = None):
        """Log team action for audit trail"""
        log_entry = {
            "id": str(uuid.uuid4()),
            "team_id": team_id,
            "user_id": user_id,
            "action": action,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow(),
            "ip_address": None,
            "user_agent": None
        }
        
        await self.audit_log_collection.insert_one(log_entry)
    
    async def get_user_teams(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all teams user belongs to"""
        member_records = await self.team_members_collection.find({
            "user_id": user_id,
            "status": "active"
        }).to_list(None)
        
        team_ids = [member["team_id"] for member in member_records]
        if not team_ids:
            return []
        
        teams = await self.teams_collection.find({
            "id": {"$in": team_ids}
        }).to_list(None)
        
        # Enrich with member role info
        for team in teams:
            member_info = next((m for m in member_records if m["team_id"] == team["id"]), None)
            if member_info:
                team["user_role"] = member_info["role"]
                team["joined_at"] = member_info["joined_at"]
        
        return teams

# Service instance
advanced_team_management_service = AdvancedTeamManagementService()