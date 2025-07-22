"""
Workspace API Routes

Provides API endpoints for workspace management functionality including
workspace creation, member management, and workspace settings.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from services.workspace_service import workspace_service
from core.auth import get_current_user

router = APIRouter(prefix="/api/workspace", tags=["Workspace Management"])

@router.get("/list")
async def get_user_workspaces(current_user: dict = Depends(get_current_user)):
    """Get user's workspaces"""
    user_id = current_user.get("user_id")
    return await workspace_service.get_user_workspaces(user_id)

@router.post("/create")
async def create_workspace(
    workspace_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create a new workspace"""
    user_id = current_user.get("user_id")
    return await workspace_service.create_workspace(user_id, workspace_data)

@router.get("/{workspace_id}")
async def get_workspace_details(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workspace details"""
    return await workspace_service.get_workspace_details(workspace_id)

@router.put("/{workspace_id}")
async def update_workspace(
    workspace_id: str,
    update_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update workspace settings"""
    return await workspace_service.update_workspace(workspace_id, update_data)

@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete workspace"""
    return await workspace_service.delete_workspace(workspace_id)

@router.get("/{workspace_id}/members")
async def get_workspace_members(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workspace members"""
    return await workspace_service.get_workspace_members(workspace_id)

@router.post("/{workspace_id}/members/invite")
async def invite_workspace_member(
    workspace_id: str,
    invitation_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Invite member to workspace"""
    return await workspace_service.invite_workspace_member(workspace_id, invitation_data)

@router.put("/{workspace_id}/members/{member_id}/role")
async def update_member_role(
    workspace_id: str,
    member_id: str,
    role_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update workspace member role"""
    return await workspace_service.update_member_role(workspace_id, member_id, role_data)

@router.delete("/{workspace_id}/members/{member_id}")
async def remove_workspace_member(
    workspace_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove member from workspace"""
    return await workspace_service.remove_workspace_member(workspace_id, member_id)

@router.get("/{workspace_id}/analytics")
async def get_workspace_analytics(
    workspace_id: str,
    current_user: dict = Depends(get_current_user),
    period: Optional[str] = "30d"
):
    """Get workspace analytics"""
    return await workspace_service.get_workspace_analytics(workspace_id, period)

@router.post("/{workspace_id}/switch")
async def switch_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Switch to a different workspace"""
    user_id = current_user.get("user_id")
    return await workspace_service.switch_workspace(user_id, workspace_id)