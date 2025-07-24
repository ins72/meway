"""
Plan Change Impact Analysis API
Analyzes impact of plan changes on existing subscriptions BEFORE applying changes
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.plan_change_impact_service import get_plan_change_impact_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check for plan change impact analysis"""
    try:
        service = get_plan_change_impact_service()
        return await service.health_check()
    except Exception as e:
        logger.error(f"Plan change impact analysis health check error: {e}")
        return {"success": False, "healthy": False, "error": str(e)}

@router.post("/analyze-pricing-change")
async def analyze_pricing_change_impact(
    data: Dict[str, Any] = Body(..., description="Pricing change analysis data"),
    current_user: dict = Depends(get_current_user)
):
    """Analyze impact of pricing changes on existing subscriptions"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        data["analyzed_by"] = current_user.get("id")
        
        result = await service.analyze_pricing_change_impact(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze pricing change impact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-feature-change")
async def analyze_feature_change_impact(
    data: Dict[str, Any] = Body(..., description="Feature change analysis data"),
    current_user: dict = Depends(get_current_user)
):
    """Analyze impact of feature changes on existing subscriptions"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        data["analyzed_by"] = current_user.get("id")
        
        result = await service.analyze_feature_change_impact(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze feature change impact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-limit-change")
async def analyze_limit_change_impact(
    data: Dict[str, Any] = Body(..., description="Limit change analysis data"),
    current_user: dict = Depends(get_current_user)
):
    """Analyze impact of usage limit changes on existing subscriptions"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        data["analyzed_by"] = current_user.get("id")
        
        result = await service.analyze_limit_change_impact(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze limit change impact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-plan-disable")
async def analyze_plan_disable_impact(
    data: Dict[str, Any] = Body(..., description="Plan disable analysis data"),
    current_user: dict = Depends(get_current_user)
):
    """Analyze impact of disabling a plan on existing subscriptions"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        data["analyzed_by"] = current_user.get("id")
        
        result = await service.analyze_plan_disable_impact(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze plan disable impact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-change")
async def simulate_plan_change(
    data: Dict[str, Any] = Body(..., description="Plan change simulation data"),
    current_user: dict = Depends(get_current_user)
):
    """Simulate complete plan change with full impact analysis"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        data["simulated_by"] = current_user.get("id")
        
        result = await service.simulate_plan_change(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Simulate plan change error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/affected-subscriptions/{plan_name}")
async def get_affected_subscriptions(
    plan_name: str = Path(..., description="Plan name"),
    change_type: str = Query(..., description="Type of change: pricing, features, limits, disable"),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """Get list of subscriptions that would be affected by plan changes"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        result = await service.get_affected_subscriptions(plan_name, change_type, limit)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get affected subscriptions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-migration-plan")
async def create_migration_plan(
    data: Dict[str, Any] = Body(..., description="Migration plan data"),
    current_user: dict = Depends(get_current_user)
):
    """Create a migration plan for moving subscriptions between plan versions"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        data["created_by"] = current_user.get("id")
        
        result = await service.create_migration_plan(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create migration plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-migration-plan/{migration_id}")
async def execute_migration_plan(
    migration_id: str = Path(..., description="Migration plan ID"),
    data: Dict[str, Any] = Body(..., description="Execution parameters"),
    current_user: dict = Depends(get_current_user)
):
    """Execute a migration plan to safely apply plan changes"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        data["executed_by"] = current_user.get("id")
        
        result = await service.execute_migration_plan(migration_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Execute migration plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migration-plan/{migration_id}")
async def get_migration_plan_status(
    migration_id: str = Path(..., description="Migration plan ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get status and progress of a migration plan"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        result = await service.get_migration_plan_status(migration_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get migration plan status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback-plan-change")
async def rollback_plan_change(
    data: Dict[str, Any] = Body(..., description="Rollback data"),
    current_user: dict = Depends(get_current_user)
):
    """Rollback a plan change to previous state"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        data["rolled_back_by"] = current_user.get("id")
        
        result = await service.rollback_plan_change(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rollback plan change error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/impact-history")
async def get_impact_analysis_history(
    plan_name: str = Query(None, description="Filter by plan name"),
    days_back: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get history of impact analyses performed"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        result = await service.get_impact_analysis_history(plan_name, days_back, limit)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get impact analysis history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-assessment/{plan_name}")
async def get_plan_change_risk_assessment(
    plan_name: str = Path(..., description="Plan name"),
    change_type: str = Query(..., description="Type of change"),
    current_user: dict = Depends(get_current_user)
):
    """Get risk assessment for potential plan changes"""
    try:
        # Check admin access
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        service = get_plan_change_impact_service()
        result = await service.get_plan_change_risk_assessment(plan_name, change_type)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get plan change risk assessment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))