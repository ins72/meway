"""
AI Token Purchase API
Handles purchasing additional AI tokens beyond bundle limits
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.ai_token_purchase_service import get_ai_token_purchase_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for AI token purchase system"""
    try:
        service = get_ai_token_purchase_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"AI token purchase health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/pricing")
async def get_token_pricing():
    """Get AI token pricing tiers"""
    try:
        service = get_ai_token_purchase_service()
        result = await service.get_token_pricing()
        
        return result
        
    except Exception as e:
        logger.error(f"Get token pricing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/balance")
async def get_token_balance(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get current AI token balance for workspace"""
    try:
        service = get_ai_token_purchase_service()
        result = await service.get_token_balance(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get token balance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/purchase")
async def purchase_tokens(
    data: Dict[str, Any] = Body(..., description="Token purchase data"),
    current_user: dict = Depends(get_current_user)
):
    """Purchase additional AI tokens"""
    try:
        workspace_id = data.get("workspace_id")
        package_id = data.get("package_id")
        payment_method = data.get("payment_method", "stripe")
        
        if not workspace_id or not package_id:
            raise HTTPException(status_code=400, detail="Workspace ID and package ID are required")
        
        service = get_ai_token_purchase_service()
        data["purchased_by"] = current_user.get("id")
        
        result = await service.purchase_tokens(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Purchase tokens error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/usage-history")
async def get_token_usage_history(
    workspace_id: str = Path(..., description="Workspace ID"),
    period: str = Query("month", description="Period: week, month, quarter"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get AI token usage history for workspace"""
    try:
        service = get_ai_token_purchase_service()
        result = await service.get_token_usage_history(workspace_id, period, limit, offset, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get token usage history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/purchase-history")
async def get_purchase_history(
    workspace_id: str = Path(..., description="Workspace ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get token purchase history for workspace"""
    try:
        service = get_ai_token_purchase_service()
        result = await service.get_purchase_history(workspace_id, limit, offset, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get purchase history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gift")
async def gift_tokens(
    data: Dict[str, Any] = Body(..., description="Token gift data"),
    current_user: dict = Depends(get_current_user)
):
    """Gift AI tokens to another workspace (premium feature)"""
    try:
        from_workspace_id = data.get("from_workspace_id")
        to_workspace_id = data.get("to_workspace_id")
        token_amount = data.get("token_amount")
        message = data.get("message", "")
        
        if not from_workspace_id or not to_workspace_id or not token_amount:
            raise HTTPException(status_code=400, detail="From workspace, to workspace, and token amount are required")
        
        service = get_ai_token_purchase_service()
        data["gifted_by"] = current_user.get("id")
        
        result = await service.gift_tokens(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gift tokens error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/{workspace_id}/auto-refill")
async def setup_auto_refill(
    workspace_id: str = Path(..., description="Workspace ID"),
    data: Dict[str, Any] = Body(..., description="Auto-refill configuration"),
    current_user: dict = Depends(get_current_user)
):
    """Setup automatic token refill when balance gets low"""
    try:
        service = get_ai_token_purchase_service()
        
        # Check if user has admin access to workspace
        has_admin_access = await service.check_admin_access(workspace_id, current_user.get("id"))
        if not has_admin_access:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        data["workspace_id"] = workspace_id
        data["configured_by"] = current_user.get("id")
        
        result = await service.setup_auto_refill(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Setup auto-refill error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/recommendations")
async def get_token_recommendations(
    workspace_id: str = Path(..., description="Workspace ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get personalized token purchase recommendations based on usage patterns"""
    try:
        service = get_ai_token_purchase_service()
        result = await service.get_token_recommendations(workspace_id, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get token recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/redeem-promo")
async def redeem_promo_code(
    data: Dict[str, Any] = Body(..., description="Promo code redemption data"),
    current_user: dict = Depends(get_current_user)
):
    """Redeem promotional code for free tokens"""
    try:
        workspace_id = data.get("workspace_id")
        promo_code = data.get("promo_code")
        
        if not workspace_id or not promo_code:
            raise HTTPException(status_code=400, detail="Workspace ID and promo code are required")
        
        service = get_ai_token_purchase_service()
        data["redeemed_by"] = current_user.get("id")
        
        result = await service.redeem_promo_code(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redeem promo code error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace/{workspace_id}/analytics")
async def get_token_analytics(
    workspace_id: str = Path(..., description="Workspace ID"),
    period: str = Query("month", description="Period: week, month, quarter, year"),
    current_user: dict = Depends(get_current_user)
):
    """Get AI token usage analytics and insights"""
    try:
        service = get_ai_token_purchase_service()
        result = await service.get_token_analytics(workspace_id, period, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get token analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))