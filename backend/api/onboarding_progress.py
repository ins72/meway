"""
Onboarding Progress API
BULLETPROOF API for tracking user onboarding progress
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any
from core.auth import get_current_user
from services.user_service import get_user_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/progress")
async def save_onboarding_progress(
    progress_data: Dict[str, Any] = Body(..., description="Onboarding progress data"),
    current_user: dict = Depends(get_current_user)
):
    """Save user's onboarding progress"""
    try:
        user_id = current_user.get("id")
        step = progress_data.get("step", 1)
        data = progress_data.get("data", {})
        
        if not user_id:
            # Don't fail if user not authenticated, just return success
            return {
                "success": True,
                "message": "Progress not saved - user not authenticated",
                "data": {"step": step, "completed": False}
            }
        
        user_service = get_user_service()
        result = await user_service.update_onboarding_progress(user_id, step, data)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Onboarding progress saved",
                "data": result["data"]
            }
        else:
            # Don't fail on save error, just log it
            logger.warning(f"Failed to save progress for user {user_id}: {result.get('error')}")
            return {
                "success": True,
                "message": "Progress save failed but continuing",
                "data": {"step": step, "completed": False}
            }
            
    except Exception as e:
        logger.error(f"Save onboarding progress error: {e}")
        # Don't fail on save error, just return success to not block user
        return {
            "success": True,
            "message": "Progress save failed but continuing",
            "data": {"step": progress_data.get("step", 1), "completed": False}
        }

@router.get("/progress")
async def get_onboarding_progress(
    current_user: dict = Depends(get_current_user)
):
    """Get user's onboarding progress"""
    try:
        user_id = current_user.get("id")
        
        if not user_id:
            # Return default progress if user not authenticated
            return {
                "success": True,
                "data": {
                    "step": 1,
                    "completed": False,
                    "data": {},
                    "has_workspace": False
                }
            }
        
        user_service = get_user_service()
        result = await user_service.get_user(user_id)
        
        if result.get("success"):
            user_data = result["data"]
            return {
                "success": True,
                "data": {
                    "step": user_data.get("onboarding_step", 1),
                    "completed": user_data.get("onboarding_completed", False),
                    "data": user_data.get("onboarding_data", {}),
                    "has_workspace": user_data.get("has_workspace", False)
                }
            }
        else:
            # Return default progress if user not found
            return {
                "success": True,
                "data": {
                    "step": 1,
                    "completed": False,
                    "data": {},
                    "has_workspace": False
                }
            }
            
    except Exception as e:
        logger.error(f"Get onboarding progress error: {e}")
        # Return default progress on error instead of failing
        return {
            "success": True,
            "data": {
                "step": 1,
                "completed": False,
                "data": {},
                "has_workspace": False
            }
        }