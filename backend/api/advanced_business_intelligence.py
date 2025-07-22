"""
Advanced Business Intelligence API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..core.auth import get_current_user
from ..core.database import get_database
from ..services.advanced_business_intelligence_service import AdvancedBusinessIntelligenceService

router = APIRouter(prefix="/api/business-intelligence", tags=["Business Intelligence"])

class PredictionRequest(BaseModel):
    business_id: str
    prediction_type: str  # "revenue_forecast", "customer_churn", etc.
    
class CohortAnalysisRequest(BaseModel):
    business_id: str
    date_range: Dict
    
class FunnelTrackingRequest(BaseModel):
    business_id: str
    name: str
    stages: List[str]
    
class CompetitiveAnalysisRequest(BaseModel):
    business_id: str
    competitors: List[str]
    
class CustomReportRequest(BaseModel):
    business_id: str
    name: str
    type: str = "dashboard"
    metrics: List[str] = []
    chart_types: List[str] = ["line", "bar"]
    schedule: str = "manual"
    recipients: List[str] = []

@router.post("/predictive-analytics")
async def generate_predictive_analytics(
    request: PredictionRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Generate ML-powered predictive analytics"""
    bi_service = AdvancedBusinessIntelligenceService(db)
    result = await bi_service.generate_predictive_analytics(
        request.business_id, 
        request.prediction_type
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Predictive analytics generated", "data": result}

@router.post("/cohort-analysis")
async def generate_cohort_analysis(
    request: CohortAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Generate comprehensive cohort analysis"""
    bi_service = AdvancedBusinessIntelligenceService(db)
    result = await bi_service.generate_cohort_analysis(
        request.business_id, 
        request.date_range
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Cohort analysis generated", "data": result}

@router.post("/funnel-tracking")
async def track_conversion_funnel(
    request: FunnelTrackingRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Track and analyze conversion funnels"""
    bi_service = AdvancedBusinessIntelligenceService(db)
    
    funnel_config = {
        "name": request.name,
        "stages": request.stages
    }
    
    result = await bi_service.track_conversion_funnel(
        request.business_id, 
        funnel_config
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Funnel analysis completed", "data": result}

@router.post("/competitive-analysis")
async def generate_competitive_analysis(
    request: CompetitiveAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Generate competitive intelligence report"""
    bi_service = AdvancedBusinessIntelligenceService(db)
    result = await bi_service.generate_competitive_analysis(
        request.business_id, 
        request.competitors
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Competitive analysis generated", "data": result}

@router.post("/custom-reports")
async def create_custom_report(
    request: CustomReportRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create custom business intelligence report"""
    bi_service = AdvancedBusinessIntelligenceService(db)
    
    report_config = request.dict()
    result = await bi_service.create_custom_report(
        request.business_id, 
        report_config
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Custom report created", "data": result}

@router.get("/visualizations")
async def get_advanced_visualizations(
    business_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get advanced data visualization options"""
    bi_service = AdvancedBusinessIntelligenceService(db)
    result = await bi_service.get_advanced_visualizations(business_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Visualization options retrieved", "data": result}

@router.get("/reports")
async def list_custom_reports(
    business_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List all custom reports"""
    filter_query = {}
    if business_id:
        filter_query["business_id"] = business_id
    
    reports = await db["custom_reports"].find(filter_query).to_list(length=50)
    
    return {
        "message": "Custom reports retrieved",
        "data": reports,
        "count": len(reports)
    }

@router.get("/predictive-models")
async def list_predictive_models(
    business_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List all predictive models"""
    filter_query = {}
    if business_id:
        filter_query["business_id"] = business_id
    
    models = await db["predictive_models"].find(filter_query).sort("generated_at", -1).to_list(length=20)
    
    return {
        "message": "Predictive models retrieved",
        "data": models,
        "count": len(models)
    }
