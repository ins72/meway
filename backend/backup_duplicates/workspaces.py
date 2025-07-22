"""
Workspace API Routes
Professional Mewayz Platform
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from core.auth import get_current_active_user
from services.workspace_service import get_workspace_service

router = APIRouter()

# Initialize service instance
workspace_service = get_workspace_service()

class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class MemberAdd(BaseModel):
    email: str

@router.post("")
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new workspace with real database operations"""
    try:
        workspace = await workspace_service.create_workspace(
            name=workspace_data.name,
            owner_id=current_user["_id"],
            description=workspace_data.description
        )
        
        return {
            "success": True,
            "message": "Workspace created successfully",
            "data": workspace
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workspace"
        )

@router.get("")
async def get_user_workspaces(current_user: dict = Depends(get_current_active_user)):
    """Get all user workspaces with real database operations"""
    try:
        workspaces = await workspace_service.get_user_workspaces(current_user["_id"])
        
        return {
            "success": True,
            "data": {
                "workspaces": workspaces,
                "total_count": len(workspaces)
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch workspaces"
        )

@router.get("/{workspace_id}")
async def get_workspace_details(
    workspace_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get workspace details with real database operations"""
    try:
        workspace = await workspace_service.get_workspace_details(
            workspace_id=workspace_id,
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "data": workspace
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch workspace details"
        )

@router.put("/{workspace_id}")
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update workspace with real database operations"""
    try:
        update_data = workspace_data.dict(exclude_none=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )
        
        workspace = await workspace_service.update_workspace(
            workspace_id=workspace_id,
            user_id=current_user["_id"],
            update_data=update_data
        )
        
        return {
            "success": True,
            "message": "Workspace updated successfully",
            "data": workspace
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workspace"
        )

@router.post("/{workspace_id}/members")
async def add_workspace_member(
    workspace_id: str,
    member_data: MemberAdd,
    current_user: dict = Depends(get_current_active_user)
):
    """Add member to workspace with real database operations"""
    try:
        result = await workspace_service.add_member(
            workspace_id=workspace_id,
            owner_id=current_user["_id"],
            member_email=member_data.email
        )
        
        return {
            "success": True,
            "message": "Member added successfully",
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add member"
        )

@router.delete("/{workspace_id}/members/{member_id}")
async def remove_workspace_member(
    workspace_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Remove member from workspace with real database operations"""
    try:
        result = await workspace_service.remove_member(
            workspace_id=workspace_id,
            owner_id=current_user["_id"],
            member_id=member_id
        )
        
        return {
            "success": True,
            "message": "Member removed successfully",
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove member"
        )

@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete workspace with real database operations"""
    try:
        result = await workspace_service.delete_workspace(
            workspace_id=workspace_id,
            owner_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "message": "Workspace deleted successfully",
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workspace"
        )