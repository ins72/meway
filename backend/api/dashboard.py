"""
Dashboard API Routes
Professional Mewayz Platform
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional

from core.auth import get_current_active_user
from services.user_service import get_user_service
from services.analytics_service import get_analytics_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
import uuid
from datetime import datetime

router = APIRouter()

# Initialize service instances
user_service = get_user_service()
analytics_service = get_analytics_service()

@router.get("/overview")
async def get_dashboard_overview(current_user: dict = Depends(get_current_active_user)):
    """Get dashboard overview with real data from database"""
    try:
        # Get user stats
        user_stats = await user_service.get_user_stats(current_user["_id"])
        
        # Get user analytics for last 7 days
        recent_analytics = await analytics_service.get_user_analytics(
            user_id=current_user["_id"],
            days=7
        )
        
        # Get feature usage
        feature_usage = await analytics_service.get_feature_usage_analytics(
            user_id=current_user["_id"]
        )
        
        # Combine data for dashboard
        dashboard_data = {
            "user_overview": {
                "name": user_stats["user_info"]["name"],
                "subscription_plan": user_stats["user_info"]["subscription_plan"],
                "account_status": "active" if user_stats["user_info"]["is_active"] else "inactive",
                "member_since": user_stats["user_info"]["account_created"],
                "last_activity": user_stats["user_info"]["last_login"]
            },
            "quick_stats": {
                "workspaces": user_stats["usage_statistics"]["workspaces_owned"],
                "total_logins": user_stats["usage_statistics"]["login_count"],
                "ai_requests_used": user_stats["usage_statistics"]["ai_requests_used"],
                "storage_used_mb": user_stats["usage_statistics"]["storage_used_mb"],
                "activity_last_7_days": recent_analytics["summary"]["total_events"]
            },
            "recent_activity": {
                "total_events_7d": recent_analytics["summary"]["total_events"],
                "avg_daily_events": recent_analytics["summary"]["avg_events_per_day"],
                "top_activities": recent_analytics["top_activities"][:5],
                "daily_breakdown": recent_analytics["daily_activity"]
            },
            "feature_insights": {
                "total_features_used": len(feature_usage["feature_usage"]),
                "most_used_features": feature_usage["most_popular_features"][:5]
            },
            "subscription_info": user_stats["subscription_info"]
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard data: {str(e)}"
        )

@router.get("/activity-summary")
async def get_activity_summary(
    days: int = 30,
    current_user: dict = Depends(get_current_active_user)
):
    """Get detailed activity summary with real database data"""
    try:
        analytics = await analytics_service.get_user_analytics(
            user_id=current_user["_id"],
            days=days
        )
        
        return {
            "success": True,
            "data": {
                "time_period": f"Last {days} days",
                "summary": analytics["summary"],
                "activity_breakdown": analytics["events_by_type"],
                "daily_activity": analytics["daily_activity"],
                "insights": {
                    "most_active_day": max(analytics["daily_activity"].items(), key=lambda x: x[1])[0] if analytics["daily_activity"] else None,
                    "activity_trend": "increasing" if analytics["summary"]["total_events"] > 0 else "low",
                    "engagement_level": "high" if analytics["summary"]["avg_events_per_day"] > 5 else "moderate" if analytics["summary"]["avg_events_per_day"] > 1 else "low"
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch activity summary"
        )