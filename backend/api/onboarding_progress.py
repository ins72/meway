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
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        user_service = get_user_service()
        result = await user_service.update_onboarding_progress(user_id, step, data)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Onboarding progress saved",
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to save progress"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save onboarding progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress")
async def get_onboarding_progress(
    current_user: dict = Depends(get_current_user)
):
    """Get user's onboarding progress"""
    try:
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
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
            raise HTTPException(status_code=404, detail="User not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get onboarding progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))