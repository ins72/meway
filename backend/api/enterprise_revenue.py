"""
Enterprise Revenue Tracking API
Handles automatic calculation of 15% revenue share billing for Enterprise workspaces
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.enterprise_revenue_service import get_enterprise_revenue_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for enterprise revenue tracking"""
    try:
        service = get_enterprise_revenue_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Enterprise revenue health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.get("/revenue/{workspace_id}")
async def calculate_workspace_revenue(
    workspace_id: str = Path(..., description="Workspace ID"),
    period: str = Query("current_month", description="Period: current_month, last_month, quarter, year, custom"),
    start_date: str = Query(None, description="Start date for custom period (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date for custom period (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    """Calculate total revenue for workspace across all sources"""
    try:
        service = get_enterprise_revenue_service()
        
        # Check if user has access to this workspace
        has_access = await service.check_workspace_access(workspace_id, current_user.get("id"))
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied to workspace")
        
        result = await service.calculate_workspace_revenue(workspace_id, period, start_date, end_date)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Calculate workspace revenue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/billing/calculate")
async def calculate_enterprise_billing(
    data: Dict[str, Any] = Body(..., description="Billing calculation data"),
    current_user: dict = Depends(get_current_user)
):
    """Calculate 15% enterprise billing for workspace"""
    try:
        workspace_id = data.get("workspace_id")
        period = data.get("period", "current_month")
        
        if not workspace_id:
            raise HTTPException(status_code=400, detail="Workspace ID is required")
        
        service = get_enterprise_revenue_service()
        
        # Check if user has admin access to this workspace
        has_admin_access = await service.check_admin_access(workspace_id, current_user.get("id"))
        if not has_admin_access:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await service.calculate_enterprise_billing(workspace_id, period, current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Calculate enterprise billing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue-sources/{workspace_id}")
async def get_revenue_sources(
    workspace_id: str = Path(..., description="Workspace ID"),
    period: str = Query("current_month", description="Period for revenue breakdown"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed breakdown of revenue sources for workspace"""
    try:
        service = get_enterprise_revenue_service()
        
        # Check access
        has_access = await service.check_workspace_access(workspace_id, current_user.get("id"))
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied to workspace")
        
        result = await service.get_revenue_sources_breakdown(workspace_id, period)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get revenue sources error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/billing-history/{workspace_id}")
async def get_enterprise_billing_history(
    workspace_id: str = Path(..., description="Workspace ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get enterprise billing history for workspace"""
    try:
        service = get_enterprise_revenue_service()
        
        # Check admin access
        has_admin_access = await service.check_admin_access(workspace_id, current_user.get("id"))
        if not has_admin_access:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await service.get_enterprise_billing_history(workspace_id, limit, offset)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get enterprise billing history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/billing/generate")
async def generate_enterprise_bill(
    data: Dict[str, Any] = Body(..., description="Bill generation data"),
    current_user: dict = Depends(get_current_user)
):
    """Generate enterprise bill for workspace"""
    try:
        workspace_id = data.get("workspace_id")
        period = data.get("period", "current_month")
        
        if not workspace_id:
            raise HTTPException(status_code=400, detail="Workspace ID is required")
        
        service = get_enterprise_revenue_service()
        
        # Check admin access
        has_admin_access = await service.check_admin_access(workspace_id, current_user.get("id"))
        if not has_admin_access:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        data["generated_by"] = current_user.get("id")
        result = await service.generate_enterprise_bill(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate enterprise bill error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/{workspace_id}")
async def get_revenue_analytics(
    workspace_id: str = Path(..., description="Workspace ID"),
    period: str = Query("year", description="Period: month, quarter, year"),
    current_user: dict = Depends(get_current_user)
):
    """Get revenue analytics and trends for workspace"""
    try:
        service = get_enterprise_revenue_service()
        
        # Check access
        has_access = await service.check_workspace_access(workspace_id, current_user.get("id"))
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied to workspace")
        
        result = await service.get_revenue_analytics(workspace_id, period)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get revenue analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revenue/track")
async def track_revenue(
    data: Dict[str, Any] = Body(..., description="Revenue tracking data"),
    current_user: dict = Depends(get_current_user)
):
    """Track revenue transaction for workspace"""
    try:
        workspace_id = data.get("workspace_id")
        source = data.get("source")  # e.g., "ecommerce", "courses", "bookings", "templates"
        amount = data.get("amount")
        
        if not workspace_id or not source or not amount:
            raise HTTPException(status_code=400, detail="Workspace ID, source, and amount are required")
        
        service = get_enterprise_revenue_service()
        
        # Verify this transaction is legitimate (user has access to workspace)
        has_access = await service.check_workspace_access(workspace_id, current_user.get("id"))
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied to workspace")
        
        data["tracked_by"] = current_user.get("id")
        result = await service.track_revenue_transaction(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Track revenue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue/projections/{workspace_id}")
async def get_revenue_projections(
    workspace_id: str = Path(..., description="Workspace ID"),
    months_ahead: int = Query(12, ge=1, le=24, description="Months to project ahead"),
    current_user: dict = Depends(get_current_user)
):
    """Get revenue projections based on historical data"""
    try:
        service = get_enterprise_revenue_service()
        
        # Check access
        has_access = await service.check_workspace_access(workspace_id, current_user.get("id"))
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied to workspace")
        
        result = await service.get_revenue_projections(workspace_id, months_ahead)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get revenue projections error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/billing/dispute")
async def create_billing_dispute(
    data: Dict[str, Any] = Body(..., description="Dispute data"),
    current_user: dict = Depends(get_current_user)
):
    """Create billing dispute for enterprise charges"""
    try:
        workspace_id = data.get("workspace_id")
        billing_record_id = data.get("billing_record_id")
        dispute_reason = data.get("dispute_reason")
        
        if not workspace_id or not billing_record_id or not dispute_reason:
            raise HTTPException(status_code=400, detail="Workspace ID, billing record ID, and dispute reason are required")
        
        service = get_enterprise_revenue_service()
        
        # Check admin access
        has_admin_access = await service.check_admin_access(workspace_id, current_user.get("id"))
        if not has_admin_access:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        data["disputed_by"] = current_user.get("id")
        result = await service.create_billing_dispute(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create billing dispute error: {e}")
        raise HTTPException(status_code=500, detail=str(e))