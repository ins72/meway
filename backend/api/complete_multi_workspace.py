"""
Complete Multi-Workspace System API
Comprehensive workspace management with RBAC, invitations, and real data
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field, EmailStr

from core.auth import get_current_user
from services.complete_multi_workspace_service import complete_multi_workspace_service, WorkspaceRole
from typing import Dict, Any, List, Optional
from core.auth import get_current_active_user
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., description="Workspace name", min_length=3, max_length=100)
    description: str = Field("", description="Workspace description", max_length=500)
    workspace_type: str = Field("business", description="Workspace type")
    settings: Optional[Dict[str, Any]] = Field(None, description="Workspace settings")

class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    settings: Optional[Dict[str, Any]] = None
    features_enabled: Optional[List[str]] = None

class InvitationCreateRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to invite")
    role: str = Field(WorkspaceRole.MEMBER.value, description="Role to assign")
    custom_message: str = Field("", description="Custom invitation message", max_length=500)

class MemberRoleUpdateRequest(BaseModel):
    new_role: str = Field(..., description="New role for the member")

class InvitationAcceptRequest(BaseModel):
    invitation_token: str = Field(..., description="Invitation token from email")

# Workspace Management Endpoints
@router.post("/workspaces", tags=["Multi-Workspace"])
async def create_workspace(
    workspace_data: WorkspaceCreateRequest,
    user = Depends(get_current_user)
):
    """Create a new workspace with real data persistence"""
    try:
        result = await complete_multi_workspace_service.create_workspace(
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            name=workspace_data.name,
            description=workspace_data.description,
            workspace_type=workspace_data.workspace_type,
            settings=workspace_data.settings
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create workspace")
        
        return {
            "success": True,
            "message": "Workspace created successfully",
            "workspace": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Create workspace error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspaces", tags=["Multi-Workspace"])
async def get_user_workspaces(
    user = Depends(get_current_user),
    include_archived: bool = Query(False, description="Include archived workspaces")
):
    """Get all workspaces for the current user"""
    try:
        workspaces = await complete_multi_workspace_service.get_user_workspaces(
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            include_archived=include_archived
        )
        
        return {
            "success": True,
            "workspaces": workspaces,
            "total_count": len(workspaces),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get user workspaces error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspaces/{workspace_id}", tags=["Multi-Workspace"])
async def get_workspace_details(
    workspace_id: str,
    user = Depends(get_current_user)
):
    """Get detailed workspace information"""
    try:
        workspace = await complete_multi_workspace_service.get_workspace_details(
            workspace_id=workspace_id,
            user_id=user.get('_id') or user.get('id') or user.get('user_id')
        )
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found or access denied")
        
        return {
            "success": True,
            "workspace": workspace,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace details error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/workspaces/{workspace_id}", tags=["Multi-Workspace"])
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdateRequest,
    user = Depends(get_current_user)
):
    """Update workspace with RBAC checks"""
    try:
        result = await complete_multi_workspace_service.update_workspace(
            workspace_id=workspace_id,
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            update_data=workspace_data.dict(exclude_unset=True)
        )
        
        if not result:
            raise HTTPException(
                status_code=403, 
                detail="Permission denied or workspace not found"
            )
        
        return {
            "success": True,
            "message": "Workspace updated successfully",
            "workspace": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update workspace error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Member Management Endpoints
@router.post("/workspaces/{workspace_id}/invitations", tags=["Multi-Workspace"])
async def invite_member(
    workspace_id: str,
    invitation_data: InvitationCreateRequest,
    user = Depends(get_current_user)
):
    """Send workspace invitation to new member"""
    try:
        # Validate role
        if invitation_data.role not in [role.value for role in WorkspaceRole]:
            raise HTTPException(status_code=400, detail="Invalid role specified")
        
        result = await complete_multi_workspace_service.invite_member(
            workspace_id=workspace_id,
            inviter_id=user.get('_id') or user.get('id') or user.get('user_id'),
            email=invitation_data.email,
            role=invitation_data.role,
            custom_message=invitation_data.custom_message
        )
        
        if not result:
            raise HTTPException(
                status_code=403, 
                detail="Permission denied, invalid role, or user already invited"
            )
        
        return {
            "success": True,
            "message": "Invitation sent successfully",
            "invitation": {
                "invitation_id": result['invitation_id'],
                "email": result['email'],
                "role": result['role'],
                "expires_at": result['expires_at'].isoformat(),
                "status": result['status']
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Invite member error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invitations/accept", tags=["Multi-Workspace"])
async def accept_invitation(
    accept_data: InvitationAcceptRequest,
    user = Depends(get_current_user)
):
    """Accept workspace invitation"""
    try:
        result = await complete_multi_workspace_service.accept_invitation(
            invitation_token=accept_data.invitation_token,
            user_id=user.get('_id') or user.get('id') or user.get('user_id')
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="Invalid or expired invitation token"
            )
        
        return {
            "success": True,
            "message": "Invitation accepted successfully",
            "membership": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Accept invitation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspaces/{workspace_id}/members", tags=["Multi-Workspace"])
async def get_workspace_members(
    workspace_id: str,
    user = Depends(get_current_user),
    role_filter: Optional[str] = Query(None, description="Filter members by role")
):
    """Get workspace members with role information"""
    try:
        if role_filter and role_filter not in [role.value for role in WorkspaceRole]:
            raise HTTPException(status_code=400, detail="Invalid role filter")
        
        members = await complete_multi_workspace_service.get_workspace_members(
            workspace_id=workspace_id,
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            role_filter=role_filter
        )
        
        return {
            "success": True,
            "members": members,
            "total_count": len(members),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace members error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/workspaces/{workspace_id}/members/{member_id}/role", tags=["Multi-Workspace"])
async def change_member_role(
    workspace_id: str,
    member_id: str,
    role_data: MemberRoleUpdateRequest,
    user = Depends(get_current_user)
):
    """Change member role with proper RBAC checks"""
    try:
        # Validate new role
        if role_data.new_role not in [role.value for role in WorkspaceRole]:
            raise HTTPException(status_code=400, detail="Invalid role specified")
        
        success = await complete_multi_workspace_service.change_member_role(
            workspace_id=workspace_id,
            admin_id=user.get('_id') or user.get('id') or user.get('user_id'),
            member_id=member_id,
            new_role=role_data.new_role
        )
        
        if not success:
            raise HTTPException(
                status_code=403, 
                detail="Permission denied or invalid operation"
            )
        
        return {
            "success": True,
            "message": "Member role updated successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change member role error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/workspaces/{workspace_id}/members/{member_id}", tags=["Multi-Workspace"])
async def remove_member(
    workspace_id: str,
    member_id: str,
    user = Depends(get_current_user)
):
    """Remove member from workspace"""
    try:
        success = await complete_multi_workspace_service.remove_member(
            workspace_id=workspace_id,
            admin_id=user.get('_id') or user.get('id') or user.get('user_id'),
            member_id=member_id
        )
        
        if not success:
            raise HTTPException(
                status_code=403, 
                detail="Permission denied or invalid operation"
            )
        
        return {
            "success": True,
            "message": "Member removed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove member error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Permission and RBAC Endpoints
@router.get("/workspaces/{workspace_id}/permissions", tags=["Multi-Workspace"])
async def get_user_permissions(
    workspace_id: str,
    user = Depends(get_current_user)
):
    """Get user permissions for workspace"""
    try:
        permissions = await complete_multi_workspace_service.get_user_permissions(
            workspace_id=workspace_id,
            user_id=user.get('_id') or user.get('id') or user.get('user_id')
        )
        
        return {
            "success": True,
            "permissions": permissions,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get user permissions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspaces/{workspace_id}/permissions/check", tags=["Multi-Workspace"])
async def check_user_permission(
    workspace_id: str,
    permission_data: Dict[str, str] = Body(..., description="Permission to check"),
    user = Depends(get_current_user)
):
    """Check if user has specific permission"""
    try:
        permission = permission_data.get('permission')
        if not permission:
            raise HTTPException(status_code=400, detail="Permission name required")
        
        has_permission = await complete_multi_workspace_service.check_user_permission(
            workspace_id=workspace_id,
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            permission=permission
        )
        
        return {
            "success": True,
            "has_permission": has_permission,
            "permission": permission,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Check user permission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and Activity Endpoints
@router.get("/workspaces/{workspace_id}/analytics", tags=["Multi-Workspace"])
async def get_workspace_analytics(
    workspace_id: str,
    user = Depends(get_current_user),
    days: int = Query(30, description="Number of days for analytics", ge=1, le=365)
):
    """Get workspace analytics with proper access control"""
    try:
        analytics = await complete_multi_workspace_service.get_workspace_analytics(
            workspace_id=workspace_id,
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            days=days
        )
        
        if analytics is None:
            raise HTTPException(
                status_code=403, 
                detail="Permission denied to view analytics"
            )
        
        return {
            "success": True,
            "analytics": analytics,
            "period_days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Role and Permission Information Endpoints
@router.get("/roles", tags=["Multi-Workspace"])
async def get_available_roles():
    """Get all available workspace roles and their permissions"""
    try:
        roles_info = []
        for role in WorkspaceRole:
            permissions = complete_multi_workspace_service.ROLE_PERMISSIONS.get(role, [])
            roles_info.append({
                "role": role.value,
                "permissions": permissions,
                "description": f"{role.value.title()} level access"
            })
        
        return {
            "success": True,
            "roles": roles_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get available roles error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/permissions", tags=["Multi-Workspace"])
async def get_all_permissions():
    """Get all available permissions in the system"""
    try:
        all_permissions = set()
        for role_permissions in complete_multi_workspace_service.ROLE_PERMISSIONS.values():
            all_permissions.update(role_permissions)
        
        permission_categories = {
            'workspace_management': [
                'manage_workspace', 'delete_workspace', 'manage_settings'
            ],
            'member_management': [
                'invite_members', 'remove_members', 'change_roles', 'change_member_roles'
            ],
            'content_management': [
                'manage_own_content', 'use_features', 'manage_projects'
            ],
            'analytics_reporting': [
                'view_analytics', 'view_reports', 'export_data'
            ],
            'administration': [
                'manage_billing', 'manage_integrations', 'view_audit_logs', 'all_features'
            ]
        }
        
        return {
            "success": True,
            "all_permissions": sorted(list(all_permissions)),
            "permission_categories": permission_categories,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get all permissions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["Multi-Workspace"])
async def workspace_health_check():
    """Health check for multi-workspace system"""
    return {
        "status": "healthy",
        "service": "Complete Multi-Workspace System",
        "features": [
            "Workspace Creation & Management",
            "Role-Based Access Control (RBAC)",
            "Member Invitations",
            "Permission Management",
            "Activity Tracking",
            "Analytics & Reporting",
            "Team Collaboration"
        ],
        "supported_roles": [role.value for role in WorkspaceRole],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/{workspace_id}/invite", tags=["Workspace Invitations"])
async def invite_user_to_workspace(
    workspace_id: str,
    invitation_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Send invitation to user for workspace collaboration"""
    try:
        result = await multi_workspace_service.invite_user_to_workspace(
            workspace_id=workspace_id,
            inviter_id=current_user["_id"],
            invitation_data=invitation_data
        )
        
        return {
            "success": True,
            "data": result,
            "message": "User invitation processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error inviting user to workspace: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invitations/{invitation_token}/accept", tags=["Workspace Invitations"])
async def accept_workspace_invitation(
    invitation_token: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept workspace invitation"""
    try:
        result = await multi_workspace_service.accept_workspace_invitation(
            invitation_token=invitation_token,
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Workspace invitation accepted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error accepting workspace invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workspace_id}/invitations", tags=["Workspace Invitations"])
async def get_workspace_invitations(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all invitations for a workspace"""
    try:
        result = await multi_workspace_service.get_workspace_invitations(
            workspace_id=workspace_id,
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Workspace invitations retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting workspace invitations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
