"""
Team Management & Workspace Collaboration API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure  
High-Value Feature Addition - Complete Team & Invitation System
"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import secrets

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class TeamMemberInvite(BaseModel):
    email: EmailStr
    role: str = "member"  # owner, admin, member, viewer
    workspace_id: Optional[str] = None
    message: Optional[str] = ""

class TeamMemberUpdate(BaseModel):
    role: Optional[str] = None
    permissions: Optional[List[str]] = None

class WorkspacePermissions(BaseModel):
    can_create_content: bool = True
    can_edit_content: bool = True
    can_delete_content: bool = False
    can_manage_products: bool = True
    can_manage_bookings: bool = True
    can_view_analytics: bool = True
    can_manage_integrations: bool = False
    can_manage_team: bool = False
    can_manage_billing: bool = False

def get_team_members_collection():
    """Get team members collection"""
    db = get_database()
    return db.team_members

def get_team_invitations_collection():
    """Get team invitations collection"""
    db = get_database()
    return db.team_invitations

def get_workspaces_collection():
    """Get workspaces collection"""
    db = get_database()
    return db.workspaces

def get_workspace_activity_collection():
    """Get workspace activity collection"""
    db = get_database()
    return db.workspace_activity

@router.get("/dashboard")
async def get_team_dashboard(
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get team management dashboard with comprehensive metrics"""
    try:
        # Get user's primary workspace if not specified
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        # Verify access to workspace
        is_workspace_accessible = await verify_workspace_access(workspace_id, current_user["_id"])
        if not is_workspace_accessible:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        # Get team members and invitations
        team_members_collection = get_team_members_collection()
        team_invitations_collection = get_team_invitations_collection()
        workspace_activity_collection = get_workspace_activity_collection()
        
        # Get active team members
        team_members = await team_members_collection.find({
            "workspace_id": workspace_id,
            "status": "active"
        }).to_list(length=None)
        
        # Get pending invitations  
        pending_invitations = await team_invitations_collection.find({
            "workspace_id": workspace_id,
            "status": "pending",
            "expires_at": {"$gt": datetime.utcnow()}
        }).to_list(length=None)
        
        # Get recent activity
        recent_activity = await workspace_activity_collection.find({
            "workspace_id": workspace_id
        }).sort("created_at", -1).limit(20).to_list(length=None)
        
        # Calculate team metrics
        total_members = len(team_members)
        roles_breakdown = {}
        for member in team_members:
            role = member.get("role", "member")
            roles_breakdown[role] = roles_breakdown.get(role, 0) + 1
        
        # Get last 30 days activity
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_activity_count = await workspace_activity_collection.count_documents({
            "workspace_id": workspace_id,
            "created_at": {"$gte": thirty_days_ago}
        })
        
        # Calculate member utilization
        active_last_week = await team_members_collection.count_documents({
            "workspace_id": workspace_id,
            "status": "active",
            "last_active": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })
        
        dashboard_data = {
            "workspace_id": workspace_id,
            "overview": {
                "total_members": total_members,
                "pending_invitations": len(pending_invitations),
                "active_last_week": active_last_week,
                "roles_breakdown": roles_breakdown,
                "team_utilization": round((active_last_week / max(total_members, 1)) * 100, 1)
            },
            "team_members": [
                {
                    "id": member["_id"],
                    "name": member["name"],
                    "email": member["email"],
                    "role": member["role"],
                    "status": member["status"],
                    "last_active": member.get("last_active"),
                    "permissions": member.get("permissions", []),
                    "joined_at": member["created_at"],
                    "activity_score": calculate_activity_score(member)
                } for member in team_members
            ],
            "pending_invitations": [
                {
                    "id": inv["_id"],
                    "email": inv["email"],
                    "role": inv["role"],
                    "invited_by": inv["invited_by_name"],
                    "expires_at": inv["expires_at"],
                    "created_at": inv["created_at"]
                } for inv in pending_invitations
            ],
            "recent_activity": [
                {
                    "id": activity["_id"],
                    "action": activity["action"],
                    "user_name": activity.get("user_name", "Unknown"),
                    "description": activity["description"],
                    "created_at": activity["created_at"]
                } for activity in recent_activity
            ]
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch team dashboard: {str(e)}"
        )

@router.get("/members")
async def get_team_members(
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get team members with detailed information"""
    try:
        # Get workspace
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        # Verify access
        is_accessible = await verify_workspace_access(workspace_id, current_user["_id"])
        if not is_accessible:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        # Get team members
        team_members_collection = get_team_members_collection()
        members = await team_members_collection.find({
            "workspace_id": workspace_id
        }).sort("created_at", -1).to_list(length=None)
        
        # Enhance member data
        for member in members:
            member["id"] = str(member["_id"])
            member["activity_score"] = calculate_activity_score(member)
            member["permissions_summary"] = get_permissions_summary(member.get("permissions", []))
        
        return {
            "success": True,
            "data": {
                "workspace_id": workspace_id,
                "members": members
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch team members: {str(e)}"
        )

@router.post("/invite")
async def invite_team_member(
    invite_data: TeamMemberInvite,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_active_user)
):
    """Invite new team member with role-based permissions"""
    try:
        # Get workspace_id if not provided
        workspace_id = invite_data.workspace_id
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        # Verify user can manage team
        user_role = await get_user_role_in_workspace(workspace_id, current_user["_id"])
        if user_role not in ["owner", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to invite team members"
            )
        
        # Validate role
        valid_roles = ["owner", "admin", "member", "viewer"]
        if invite_data.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Valid options: {', '.join(valid_roles)}"
            )
        
        # Check if user is already in team
        team_members_collection = get_team_members_collection()
        existing_member = await team_members_collection.find_one({
            "workspace_id": workspace_id,
            "email": invite_data.email
        })
        
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a team member"
            )
        
        # Check for existing pending invitation
        team_invitations_collection = get_team_invitations_collection()
        existing_invitation = await team_invitations_collection.find_one({
            "workspace_id": workspace_id,
            "email": invite_data.email,
            "status": "pending",
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if existing_invitation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pending invitation already exists for this email"
            )
        
        # Create invitation
        invitation_token = secrets.token_urlsafe(32)
        invitation_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "email": invite_data.email,
            "role": invite_data.role,
            "invited_by": current_user["_id"],
            "invited_by_name": current_user["name"],
            "invitation_token": invitation_token,
            "message": invite_data.message,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=7),  # 7 days to accept
            "permissions": get_default_permissions(invite_data.role)
        }
        
        await team_invitations_collection.insert_one(invitation_doc)
        
        # Log activity
        await log_workspace_activity(
            workspace_id,
            current_user["_id"],
            current_user["name"],
            "team_invite_sent",
            f"Invited {invite_data.email} as {invite_data.role}"
        )
        
        # Send invitation email (background task)
        background_tasks.add_task(
            send_team_invitation_email,
            invite_data.email,
            current_user["name"],
            workspace_id,
            invitation_token,
            invite_data.role
        )
        
        return {
            "success": True,
            "message": "Team member invitation sent successfully",
            "data": {
                "invitation_id": invitation_doc["_id"],
                "email": invite_data.email,
                "role": invite_data.role,
                "expires_at": invitation_doc["expires_at"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send team invitation: {str(e)}"
        )

@router.post("/accept-invitation")
async def accept_team_invitation(
    invitation_token: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Accept team invitation and join workspace"""
    try:
        team_invitations_collection = get_team_invitations_collection()
        
        # Find invitation
        invitation = await team_invitations_collection.find_one({
            "invitation_token": invitation_token,
            "status": "pending",
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired invitation"
            )
        
        # Verify email matches current user
        if invitation["email"] != current_user["email"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invitation email does not match your account"
            )
        
        # Check if already a member
        team_members_collection = get_team_members_collection()
        existing_member = await team_members_collection.find_one({
            "workspace_id": invitation["workspace_id"],
            "email": current_user["email"]
        })
        
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You are already a member of this workspace"
            )
        
        # Add user to team
        member_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": invitation["workspace_id"],
            "user_id": current_user["_id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "role": invitation["role"],
            "permissions": invitation.get("permissions", []),
            "status": "active",
            "joined_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "invitation_id": invitation["_id"]
        }
        
        await team_members_collection.insert_one(member_doc)
        
        # Update invitation status
        await team_invitations_collection.update_one(
            {"_id": invitation["_id"]},
            {
                "$set": {
                    "status": "accepted",
                    "accepted_at": datetime.utcnow(),
                    "accepted_by_user_id": current_user["_id"]
                }
            }
        )
        
        # Log activity
        await log_workspace_activity(
            invitation["workspace_id"],
            current_user["_id"],
            current_user["name"],
            "team_member_joined",
            f"{current_user['name']} joined the team as {invitation['role']}"
        )
        
        return {
            "success": True,
            "message": "Successfully joined the team",
            "data": {
                "workspace_id": invitation["workspace_id"],
                "role": invitation["role"],
                "member_id": member_doc["_id"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept team invitation: {str(e)}"
        )

@router.put("/members/{member_id}")
async def update_team_member(
    member_id: str,
    update_data: TeamMemberUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update team member role and permissions"""
    try:
        team_members_collection = get_team_members_collection()
        
        # Find member
        member = await team_members_collection.find_one({"_id": member_id})
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Verify permission to update
        user_role = await get_user_role_in_workspace(member["workspace_id"], current_user["_id"])
        if user_role not in ["owner", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update team members"
            )
        
        # Prevent demoting self if owner
        if member["user_id"] == current_user["_id"] and user_role == "owner" and update_data.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace owner cannot demote themselves"
            )
        
        # Prepare update
        update_doc = {"$set": {"updated_at": datetime.utcnow()}}
        
        if update_data.role:
            valid_roles = ["owner", "admin", "member", "viewer"]
            if update_data.role not in valid_roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role. Valid options: {', '.join(valid_roles)}"
                )
            update_doc["$set"]["role"] = update_data.role
            # Update permissions based on new role
            update_doc["$set"]["permissions"] = get_default_permissions(update_data.role)
        
        if update_data.permissions:
            update_doc["$set"]["permissions"] = update_data.permissions
        
        # Update member
        result = await team_members_collection.update_one(
            {"_id": member_id},
            update_doc
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made"
            )
        
        # Log activity
        await log_workspace_activity(
            member["workspace_id"],
            current_user["_id"],
            current_user["name"],
            "team_member_updated",
            f"Updated {member['name']} role/permissions"
        )
        
        return {
            "success": True,
            "message": "Team member updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update team member: {str(e)}"
        )

@router.delete("/members/{member_id}")
async def remove_team_member(
    member_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Remove team member from workspace"""
    try:
        team_members_collection = get_team_members_collection()
        
        # Find member
        member = await team_members_collection.find_one({"_id": member_id})
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Verify permission to remove
        user_role = await get_user_role_in_workspace(member["workspace_id"], current_user["_id"])
        if user_role not in ["owner", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to remove team members"
            )
        
        # Prevent removing self if owner
        if member["user_id"] == current_user["_id"] and member["role"] == "owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace owner cannot remove themselves"
            )
        
        # Remove member
        result = await team_members_collection.delete_one({"_id": member_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Log activity
        await log_workspace_activity(
            member["workspace_id"],
            current_user["_id"],
            current_user["name"],
            "team_member_removed",
            f"Removed {member['name']} from the team"
        )
        
        return {
            "success": True,
            "message": "Team member removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove team member: {str(e)}"
        )

@router.get("/activity")
async def get_team_activity(
    workspace_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get team activity log"""
    try:
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        # Verify access
        is_accessible = await verify_workspace_access(workspace_id, current_user["_id"])
        if not is_accessible:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workspace"
            )
        
        # Get activity log
        workspace_activity_collection = get_workspace_activity_collection()
        activities = await workspace_activity_collection.find({
            "workspace_id": workspace_id
        }).sort("created_at", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "workspace_id": workspace_id,
                "activities": activities
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch team activity: {str(e)}"
        )

# Helper functions
async def verify_workspace_access(workspace_id: str, user_id: str) -> bool:
    """Verify user has access to workspace"""
    try:
        workspaces_collection = get_workspaces_collection()
        team_members_collection = get_team_members_collection()
        
        # Check if user is workspace owner
        workspace = await workspaces_collection.find_one({
            "_id": workspace_id,
            "owner_id": user_id
        })
        if workspace:
            return True
        
        # Check if user is team member
        member = await team_members_collection.find_one({
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": "active"
        })
        return bool(member)
        
    except Exception:
        return False

async def get_user_role_in_workspace(workspace_id: str, user_id: str) -> Optional[str]:
    """Get user's role in workspace"""
    try:
        # Check if owner
        workspaces_collection = get_workspaces_collection()
        workspace = await workspaces_collection.find_one({
            "_id": workspace_id,
            "owner_id": user_id
        })
        if workspace:
            return "owner"
        
        # Check team member role
        team_members_collection = get_team_members_collection()
        member = await team_members_collection.find_one({
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": "active"
        })
        return member.get("role") if member else None
        
    except Exception:
        return None

def get_default_permissions(role: str) -> List[str]:
    """Get default permissions for role"""
    permission_sets = {
        "owner": [
            "manage_workspace", "manage_team", "manage_billing",
            "create_content", "edit_content", "delete_content",
            "manage_products", "manage_bookings", "view_analytics",
            "manage_integrations", "export_data"
        ],
        "admin": [
            "manage_team", "create_content", "edit_content", "delete_content",
            "manage_products", "manage_bookings", "view_analytics",
            "manage_integrations", "export_data"
        ],
        "member": [
            "create_content", "edit_content", "manage_products",
            "manage_bookings", "view_analytics"
        ],
        "viewer": [
            "view_analytics"
        ]
    }
    
    return permission_sets.get(role, [])

def calculate_activity_score(member: dict) -> int:
    """Calculate member activity score"""
    # Simple scoring based on last activity and role
    last_active = member.get("last_active")
    if not last_active:
        return 0
    
    days_since_active = (datetime.utcnow() - last_active).days
    
    if days_since_active <= 1:
        return 100
    elif days_since_active <= 7:
        return 80
    elif days_since_active <= 30:
        return 50
    else:
        return 20

def get_permissions_summary(permissions: List[str]) -> Dict[str, bool]:
    """Get permissions summary"""
    return {
        "can_manage_team": "manage_team" in permissions,
        "can_create_content": "create_content" in permissions,
        "can_manage_products": "manage_products" in permissions,
        "can_view_analytics": "view_analytics" in permissions,
        "can_manage_integrations": "manage_integrations" in permissions
    }

async def log_workspace_activity(
    workspace_id: str,
    user_id: str,
    user_name: str,
    action: str,
    description: str
):
    """Log workspace activity"""
    try:
        workspace_activity_collection = get_workspace_activity_collection()
        
        activity_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "user_id": user_id,
            "user_name": user_name,
            "action": action,
            "description": description,
            "created_at": datetime.utcnow()
        }
        
        await workspace_activity_collection.insert_one(activity_doc)
        
    except Exception as e:
        print(f"Failed to log activity: {e}")

async def send_team_invitation_email(
    email: str,
    inviter_name: str,
    workspace_id: str,
    invitation_token: str,
    role: str
):
    """Send team invitation email (background task)"""
    try:
        # In production, integrate with email service
        print(f"📧 Sending team invitation email to {email}")
        print(f"   Inviter: {inviter_name}")
        print(f"   Role: {role}")
        print(f"   Token: {invitation_token[:10]}...")
        
        # Email would contain invitation link like:
        # https://app.mewayz.com/accept-invitation?token={invitation_token}
        
    except Exception as e:
        print(f"Failed to send invitation email: {e}")