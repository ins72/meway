"""
Advanced Team Management API
Complete team invitations, role-based access control, and collaboration endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field, EmailStr

from core.auth import get_current_user
from services.advanced_team_management_service import advanced_team_management_service, TeamRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class TeamCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    team_type: Optional[str] = Field("general", description="Type of team")
    allow_member_invites: bool = Field(False)
    require_2fa: bool = Field(False)
    default_role: str = Field(TeamRole.MEMBER.value)
    max_members: int = Field(50, ge=5, le=500)
    settings: Optional[Dict[str, Any]] = None
    permissions: Optional[Dict[str, Any]] = None

class InvitationRequest(BaseModel):
    email: EmailStr
    role: str = Field(TeamRole.MEMBER.value)
    personal_message: Optional[str] = Field(None, max_length=300)
    custom_permissions: Optional[List[str]] = None

class RoleUpdateRequest(BaseModel):
    new_role: str = Field(..., description="New role for the member")

# Team Creation & Management
@router.post("/teams", tags=["Team Management"])
async def create_team(
    request: TeamCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new team with current user as owner"""
    try:
        team = await advanced_team_management_service.create_team(
            owner_id=current_user["_id"],
            data=request.dict()
        )
        
        return {
            "success": True,
            "team": team,
            "message": "Team created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating team: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams", tags=["Team Management"])
async def get_user_teams(
    current_user: dict = Depends(get_current_user)
):
    """Get all teams user belongs to"""
    try:
        teams = await advanced_team_management_service.get_user_teams(
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "teams": teams,
            "count": len(teams)
        }
        
    except Exception as e:
        logger.error(f"Error getting teams: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Invitation System
@router.post("/teams/{team_id}/invitations", tags=["Team Invitations"])
async def create_invitation(
    team_id: str,
    request: InvitationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send invitation to join team"""
    try:
        invitation = await advanced_team_management_service.create_invitation(
            team_id=team_id,
            inviter_id=current_user["_id"],
            data=request.dict()
        )
        
        return {
            "success": True,
            "invitation": invitation,
            "message": "Invitation sent successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invitations/{invitation_token}/accept", tags=["Team Invitations"])
async def accept_invitation(
    invitation_token: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept team invitation"""
    try:
        member = await advanced_team_management_service.accept_invitation(
            invitation_token=invitation_token,
            user_id=current_user["_id"]
        )
        
        return {
            "success": True,
            "member": member,
            "message": "Invitation accepted successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error accepting invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Role & Permission Management
@router.put("/teams/{team_id}/members/{member_id}/role", tags=["Role Management"])
async def update_member_role(
    team_id: str,
    member_id: str,
    request: RoleUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update team member's role"""
    try:
        result = await advanced_team_management_service.update_member_role(
            team_id=team_id,
            updater_id=current_user["_id"],
            member_id=member_id,
            new_role=request.new_role
        )
        
        return {
            "success": True,
            **result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating member role: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/{team_id}/roles", tags=["Role Management"])
async def get_team_roles(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all available roles for team"""
    try:
        return await self._get_real_data(user_id),
            "message": "Roles retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["System"])
async def team_management_health():
    """Health check for team management system"""
    return {
        "status": "healthy",
        "service": "Advanced Team Management",
        "features": [
            "Team Creation & Management",
            "Advanced Invitation System",
            "Role-Based Access Control",
            "Custom Role Creation",
            "Member Permission Management",
            "Team Analytics & Insights",
            "Audit Logging & Compliance",
            "Multi-tier Team Support"
        ],
        "supported_roles": [role.value for role in TeamRole],
        "timestamp": datetime.utcnow().isoformat()
    }