"""
Workspace API - Complete CRUD Operations
Production-ready workspace management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from services.workspace_service import get_workspace_service
from models.workspace_models import (
    WorkspaceCreate, 
    WorkspaceUpdate, 
    WorkspaceResponse,
    WorkspaceMemberInvite,
    WorkspaceMemberUpdate,
    WorkspaceMemberResponse
)
import logging
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test")
async def test_workspace_router():
    """Test endpoint to verify router is working"""
    return {
        "message": "Workspace router is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "active"
    }

@router.get("/health")
async def health_check():
    """Health check for workspace service"""
    try:
        service = get_workspace_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Workspace health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

# ==================== WORKSPACE CRUD OPERATIONS ====================

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new workspace"""
    try:
        service = get_workspace_service()
        workspace = await service.create_workspace(
            user_id=str(current_user["_id"]),
            workspace_data=workspace_data.dict()
        )
        return workspace
    except Exception as e:
        logger.error(f"Create workspace error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List all workspaces for the current user"""
    try:
        service = get_workspace_service()
        workspaces = await service.list_workspaces(
            user_id=str(current_user["_id"]),
            limit=limit,
            offset=offset
        )
        return workspaces
    except Exception as e:
        logger.error(f"List workspaces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific workspace by ID"""
    try:
        service = get_workspace_service()
        workspace = await service.get_workspace(
            workspace_id=workspace_id,
            user_id=str(current_user["_id"])
        )
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workspace error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str = Path(..., description="Workspace ID"),
    workspace_data: WorkspaceUpdate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update a workspace"""
    try:
        service = get_workspace_service()
        workspace = await service.update_workspace(
            workspace_id=workspace_id,
            user_id=str(current_user["_id"]),
            update_data=workspace_data.dict(exclude_unset=True)
        )
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update workspace error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Delete a workspace"""
    try:
        service = get_workspace_service()
        success = await service.delete_workspace(
            workspace_id=workspace_id,
            user_id=str(current_user["_id"])
        )
        if not success:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"success": True, "message": "Workspace deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete workspace error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WORKSPACE MEMBERS CRUD ====================

@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
async def invite_member(
    workspace_id: str = Path(..., description="Workspace ID"),
    member_data: WorkspaceMemberInvite = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Invite a member to the workspace"""
    try:
        service = get_workspace_service()
        member = await service.invite_member(
            workspace_id=workspace_id,
            user_id=str(current_user["_id"]),
            member_data=member_data.dict()
        )
        return member
    except Exception as e:
        logger.error(f"Invite member error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
async def list_members(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """List all members of a workspace"""
    try:
        service = get_workspace_service()
        members = await service.list_members(
            workspace_id=workspace_id,
            user_id=str(current_user["_id"])
        )
        return members
    except Exception as e:
        logger.error(f"List members error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{workspace_id}/members/{member_id}", response_model=WorkspaceMemberResponse)
async def update_member(
    workspace_id: str = Path(..., description="Workspace ID"),
    member_id: str = Path(..., description="Member ID"),
    member_data: WorkspaceMemberUpdate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update a workspace member"""
    try:
        service = get_workspace_service()
        member = await service.update_member(
            workspace_id=workspace_id,
            member_id=member_id,
            user_id=str(current_user["_id"]),
            update_data=member_data.dict(exclude_unset=True)
        )
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        return member
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update member error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{workspace_id}/members/{member_id}")
async def remove_member(
    workspace_id: str = Path(..., description="Workspace ID"),
    member_id: str = Path(..., description="Member ID"),
    current_user: dict = Depends(get_current_user)
):
    """Remove a member from the workspace"""
    try:
        service = get_workspace_service()
        success = await service.remove_member(
            workspace_id=workspace_id,
            member_id=member_id,
            user_id=str(current_user["_id"])
        )
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"success": True, "message": "Member removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove member error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WORKSPACE ANALYTICS ====================

@router.get("/{workspace_id}/analytics")
async def get_workspace_analytics(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get workspace analytics"""
    try:
        service = get_workspace_service()
        analytics = await service.get_analytics(
            workspace_id=workspace_id,
            user_id=str(current_user["_id"])
        )
        return analytics
    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN OPERATIONS ====================

@router.get("/admin/all", response_model=List[WorkspaceResponse])
async def admin_list_all_workspaces(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """Admin: List all workspaces in the system"""
    try:
        service = get_workspace_service()
        workspaces = await service.admin_list_all_workspaces(
            limit=limit,
            offset=offset
        )
        return workspaces
    except Exception as e:
        logger.error(f"Admin list workspaces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/{workspace_id}")
async def admin_delete_workspace(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_admin)
):
    """Admin: Force delete a workspace"""
    try:
        service = get_workspace_service()
        success = await service.admin_delete_workspace(workspace_id=workspace_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"success": True, "message": "Workspace force deleted by admin"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin delete workspace error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_workspace_stats(
    current_user: dict = Depends(get_current_admin)
):
    """Get workspace statistics (admin only)"""
    try:
        service = get_workspace_service()
        stats = await service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))