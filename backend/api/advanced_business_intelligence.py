"""
Advanced Business Intelligence API
Predictive analytics, ML models, cohort analysis, and data visualization
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from core.auth import get_current_user
from services.advanced_bi_service import advanced_bi_service, PredictionModel
from core.professional_logger import professional_logger, LogLevel, LogCategory

router = APIRouter(prefix="/api/business-intelligence", tags=["Advanced Business Intelligence"])

class PredictionRequest(BaseModel):
    model_type: str
    historical_days: int = 90
    parameters: Dict[str, Any] = {}

@router.post("/predictions/generate")
async def generate_predictive_insights(
    prediction_request: PredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate ML-powered predictive insights"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        # Validate model type
        try:
            model_type = PredictionModel(prediction_request.model_type)
        except ValueError:
            valid_models = [m.value for m in PredictionModel]
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model type. Valid types: {', '.join(valid_models)}"
            )
        
        predictions = await advanced_bi_service.generate_predictive_insights(
            user_id, model_type, prediction_request.historical_days
        )
        
        if "error" in predictions:
            raise HTTPException(status_code=400, detail=predictions["error"])
        
        return {
            "success": True,
            "model_type": prediction_request.model_type,
            "predictions": predictions,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ANALYTICS,
            f"Prediction generation failed: {str(e)}",
            error=e, user_id=current_user.get("_id")
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/revenue")
async def get_revenue_forecast(
    days: int = Query(90, description="Historical data period"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get revenue forecasting predictions"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        forecast = await advanced_bi_service.generate_predictive_insights(
            user_id, PredictionModel.REVENUE_FORECASTING, days
        )
        
        return {
            "success": True,
            "forecast_type": "revenue",
            "forecast": forecast,
            "period_analyzed": f"{days} days"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/churn")
async def get_churn_analysis(
    days: int = Query(90, description="Analysis period"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get customer churn predictions"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        churn_analysis = await advanced_bi_service.generate_predictive_insights(
            user_id, PredictionModel.CUSTOMER_CHURN, days
        )
        
        return {
            "success": True,
            "analysis_type": "customer_churn",
            "churn_analysis": churn_analysis,
            "period_analyzed": f"{days} days"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/customer-lifetime-value")
async def get_clv_predictions(
    days: int = Query(180, description="Analysis period"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get Customer Lifetime Value predictions"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        clv_analysis = await advanced_bi_service.generate_predictive_insights(
            user_id, PredictionModel.LIFETIME_VALUE, days
        )
        
        return {
            "success": True,
            "analysis_type": "customer_lifetime_value",
            "clv_analysis": clv_analysis,
            "period_analyzed": f"{days} days"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cohort-analysis")
async def get_cohort_analysis(
    cohort_type: str = Query("monthly", description="Cohort grouping: monthly, weekly"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get cohort analysis for customer behavior"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        if cohort_type not in ["monthly", "weekly"]:
            raise HTTPException(status_code=400, detail="Invalid cohort type. Use 'monthly' or 'weekly'")
        
        cohort_data = await advanced_bi_service.generate_cohort_analysis(user_id, cohort_type)
        
        if "error" in cohort_data:
            raise HTTPException(status_code=400, detail=cohort_data["error"])
        
        return {
            "success": True,
            "cohort_analysis": cohort_data,
            "analysis_type": cohort_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/advanced")
async def get_advanced_analytics_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get comprehensive advanced analytics dashboard"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        # Get multiple analytics in parallel
        import asyncio
        
        # Run multiple predictions concurrently
        tasks = [
            advanced_bi_service.generate_predictive_insights(user_id, PredictionModel.REVENUE_FORECASTING, 30),
            advanced_bi_service.generate_predictive_insights(user_id, PredictionModel.CUSTOMER_CHURN, 60),
            advanced_bi_service.generate_predictive_insights(user_id, PredictionModel.LIFETIME_VALUE, 90),
            advanced_bi_service.generate_cohort_analysis(user_id, "monthly")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        revenue_forecast = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        churn_analysis = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
        clv_analysis = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
        cohort_analysis = results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])}
        
        dashboard = {
            "user_id": user_id,
            "revenue_forecast": revenue_forecast,
            "churn_analysis": churn_analysis,
            "customer_lifetime_value": clv_analysis,
            "cohort_analysis": cohort_analysis,
            "dashboard_summary": {
                "predictions_available": len([r for r in results if not isinstance(r, Exception) and "error" not in r]),
                "data_quality_score": 85,  # Placeholder - would calculate based on data completeness
                "insights_generated": True,
                "last_updated": datetime.utcnow().isoformat()
            },
            "recommendations": {
                "priority_actions": [
                    "Review churn predictions for at-risk customers",
                    "Optimize marketing spend based on CLV segments",
                    "Monitor cohort performance trends"
                ],
                "next_analysis_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
        }
        
        return {
            "success": True,
            "dashboard": dashboard,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.ANALYTICS,
            f"Advanced dashboard failed: {str(e)}",
            error=e, user_id=current_user.get("_id")
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/automated")
async def get_automated_insights(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get AI-generated business insights and recommendations"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        from core.database import get_database
        db = get_database()
        
        # Gather key business metrics
        total_customers = await db.customers.count_documents({"user_id": user_id})
        total_orders = await db.orders.count_documents({"user_id": user_id})
        
        # Generate automated insights based on data patterns
        insights = []
        
        if total_customers > 0 and total_orders > 0:
            order_per_customer = total_orders / total_customers
            
            if order_per_customer < 1.5:
                insights.append({
                    "type": "opportunity",
                    "title": "Low Customer Repeat Rate",
                    "description": f"Average {order_per_customer:.1f} orders per customer",
                    "recommendation": "Implement customer retention campaigns and loyalty programs",
                    "priority": "high",
                    "impact": "revenue_growth"
                })
            elif order_per_customer > 3:
                insights.append({
                    "type": "success",
                    "title": "Strong Customer Loyalty",
                    "description": f"Excellent {order_per_customer:.1f} orders per customer",
                    "recommendation": "Scale your successful retention strategies",
                    "priority": "medium",
                    "impact": "customer_satisfaction"
                })
        
        if total_customers > 50:
            insights.append({
                "type": "growth",
                "title": "Ready for Advanced Analytics",
                "description": "Sufficient customer base for detailed analysis",
                "recommendation": "Implement customer segmentation and personalized marketing",
                "priority": "medium",
                "impact": "optimization"
            })
        
        if not insights:
            insights.append({
                "type": "getting_started",
                "title": "Building Your Data Foundation",
                "description": "Continue growing your customer base for richer insights",
                "recommendation": "Focus on customer acquisition and data collection",
                "priority": "high",
                "impact": "foundation"
            })
        
        return {
            "success": True,
            "automated_insights": insights,
            "metrics_analyzed": {
                "total_customers": total_customers,
                "total_orders": total_orders,
                "order_per_customer": total_orders / max(total_customers, 1)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
