"""
Complete Social Media Lead Generation (TikTok & Twitter/X Focus) API
Real TikTok and Twitter API Integration (replacing )
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io
import csv

from core.auth import get_current_user
from services.complete_social_media_leads_service import complete_social_media_leads_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class TikTokSearchRequest(BaseModel):
    keywords: List[str] = Field(..., description="Search keywords", min_items=1)
    location: str = Field("", description="Location filter")
    min_followers: int = Field(1000, description="Minimum follower count", ge=0)
    max_followers: int = Field(1000000, description="Maximum follower count", ge=1000)
    content_type: str = Field("all", description="Content type filter")

class TwitterSearchRequest(BaseModel):
    keywords: List[str] = Field(..., description="Search keywords", min_items=1)
    location: str = Field("", description="Location filter")
    min_followers: int = Field(1000, description="Minimum follower count", ge=0)
    max_followers: int = Field(1000000, description="Maximum follower count", ge=1000)
    verified_only: bool = Field(False, description="Only verified accounts")

class LeadUpdateRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, description="Lead status")
    tags: Optional[List[str]] = Field(None, description="Lead tags")
    contact_attempted: Optional[bool] = Field(None, description="Contact attempted flag")
    response_received: Optional[bool] = Field(None, description="Response received flag")

class LeadFilters(BaseModel):
    platform: Optional[str] = Field(None, description="Platform filter (tiktok/twitter)")
    min_followers: Optional[int] = Field(None, ge=0)
    max_followers: Optional[int] = Field(None, ge=1)
    verified_only: Optional[bool] = Field(False, description="Only verified accounts")
    has_contact_info: Optional[bool] = Field(False, description="Has contact information")
    limit: int = Field(50, description="Results limit", ge=1, le=500)
    offset: int = Field(0, description="Results offset", ge=0)

# TikTok Lead Discovery Endpoints
@router.post("/discover/tiktok", tags=["Social Media Leads"])
async def discover_tiktok_creators(
    search_request: TikTokSearchRequest,
    user = Depends(get_current_user)
):
    """Discover TikTok creators with real API integration"""
    try:
        result = await complete_social_media_leads_service.discover_tiktok_creators(
            search_params=search_request.dict()
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400, 
                detail=result.get('error', 'Failed to discover TikTok creators')
            )
        
        return {
            "success": True,
            "message": f"Discovered {result.get('total_discovered', 0)} TikTok creators",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Discover TikTok creators error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Twitter Lead Discovery Endpoints
@router.post("/discover/twitter", tags=["Social Media Leads"])
async def discover_twitter_users(
    search_request: TwitterSearchRequest,
    user = Depends(get_current_user)
):
    """Discover Twitter users with real API integration"""
    try:
        result = await complete_social_media_leads_service.discover_twitter_users(
            search_params=search_request.dict()
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400, 
                detail=result.get('error', 'Failed to discover Twitter users')
            )
        
        return {
            "success": True,
            "message": f"Discovered {result.get('total_discovered', 0)} Twitter users",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Discover Twitter users error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Lead Management Endpoints
@router.get("/leads", tags=["Social Media Leads"])
async def get_social_media_leads(
    user = Depends(get_current_user),
    platform: Optional[str] = Query(None, description="Platform filter"),
    min_followers: Optional[int] = Query(None, description="Minimum followers", ge=0),
    max_followers: Optional[int] = Query(None, description="Maximum followers", ge=1),
    verified_only: bool = Query(False, description="Only verified accounts"),
    has_contact_info: bool = Query(False, description="Has contact information"),
    limit: int = Query(50, description="Results limit", ge=1, le=500),
    offset: int = Query(0, description="Results offset", ge=0)
):
    """Get social media leads with filtering and pagination"""
    try:
        # Validate platform
        if platform and platform not in ['tiktok', 'twitter']:
            raise HTTPException(status_code=400, detail="Platform must be 'tiktok' or 'twitter'")
        
        filters = {
            'platform': platform,
            'min_followers': min_followers,
            'max_followers': max_followers,
            'verified_only': verified_only,
            'has_contact_info': has_contact_info,
            'limit': limit,
            'offset': offset
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = await complete_social_media_leads_service.get_social_media_leads(
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            filters=filters
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to get leads'))
        
        return {
            "success": True,
            "leads": result['leads'],
            "total_count": result['total_count'],
            "filters": filters,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get social media leads error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/leads/{lead_id}", tags=["Social Media Leads"])
async def update_lead(
    lead_id: str,
    update_request: LeadUpdateRequest,
    user = Depends(get_current_user)
):
    """Update a social media lead"""
    try:
        result = await complete_social_media_leads_service.update_lead(
            lead_id=lead_id,
            update_data=update_request.dict(exclude_unset=True)
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=404, detail=result.get('error', 'Lead not found'))
        
        return {
            "success": True,
            "message": "Lead updated successfully",
            "lead": result['lead'],
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update lead error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/leads/{lead_id}", tags=["Social Media Leads"])
async def delete_lead(
    lead_id: str,
    user = Depends(get_current_user)
):
    """Delete a social media lead"""
    try:
        result = await complete_social_media_leads_service.delete_lead(lead_id=lead_id)
        
        if not result.get('success'):
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "success": True,
            "message": "Lead deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete lead error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Bulk Operations
@router.post("/leads/bulk-update", tags=["Social Media Leads"])
async def bulk_update_leads(
    update_data: Dict[str, Any] = Body(...),
    user = Depends(get_current_user)
):
    """Bulk update multiple leads"""
    try:
        lead_ids = update_data.get('lead_ids', [])
        update_fields = update_data.get('update_fields', {})
        
        if not lead_ids:
            raise HTTPException(status_code=400, detail="lead_ids required")
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="update_fields required")
        
        results = []
        success_count = 0
        
        for lead_id in lead_ids:
            result = await complete_social_media_leads_service.update_lead(
                lead_id=lead_id,
                update_data=update_fields
            )
            
            if result.get('success'):
                success_count += 1
            
            results.append({
                'lead_id': lead_id,
                'success': result.get('success', False),
                'error': result.get('error')
            })
        
        return {
            "success": True,
            "message": f"Updated {success_count}/{len(lead_ids)} leads successfully",
            "results": results,
            "success_count": success_count,
            "total_count": len(lead_ids),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk update leads error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/leads/bulk-delete", tags=["Social Media Leads"])
async def bulk_delete_leads(
    delete_data: Dict[str, List[str]] = Body(...),
    user = Depends(get_current_user)
):
    """Bulk delete multiple leads"""
    try:
        lead_ids = delete_data.get('lead_ids', [])
        
        if not lead_ids:
            raise HTTPException(status_code=400, detail="lead_ids required")
        
        results = []
        success_count = 0
        
        for lead_id in lead_ids:
            result = await complete_social_media_leads_service.delete_lead(lead_id=lead_id)
            
            if result.get('success'):
                success_count += 1
            
            results.append({
                'lead_id': lead_id,
                'success': result.get('success', False),
                'error': result.get('error')
            })
        
        return {
            "success": True,
            "message": f"Deleted {success_count}/{len(lead_ids)} leads successfully",
            "results": results,
            "success_count": success_count,
            "total_count": len(lead_ids),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk delete leads error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Export and Analytics
@router.get("/leads/export/csv", tags=["Social Media Leads"])
async def export_leads_csv(
    user = Depends(get_current_user),
    platform: Optional[str] = Query(None, description="Platform filter"),
    min_followers: Optional[int] = Query(None, description="Minimum followers"),
    max_followers: Optional[int] = Query(None, description="Maximum followers"),
    verified_only: bool = Query(False, description="Only verified accounts"),
    has_contact_info: bool = Query(False, description="Has contact information")
):
    """Export social media leads to CSV"""
    try:
        filters = {
            'platform': platform,
            'min_followers': min_followers,
            'max_followers': max_followers,
            'verified_only': verified_only,
            'has_contact_info': has_contact_info,
            'limit': 10000  # Large limit for export
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = await complete_social_media_leads_service.export_leads_csv(
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            filters=filters
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Export failed'))
        
        # Create CSV content
        csv_data = result['csv_data']
        output = io.StringIO()
        writer = csv.writer(output)
        
        for row in csv_data:
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        # Create streaming response
        response = StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=social_media_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export leads CSV error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview", tags=["Social Media Leads"])
async def get_leads_analytics(
    user = Depends(get_current_user),
    days: int = Query(30, description="Analytics period in days", ge=1, le=365)
):
    """Get social media leads analytics overview"""
    try:
        # Get leads from the specified period
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all leads for analytics
        all_leads_result = await complete_social_media_leads_service.get_social_media_leads(
            user_id=user.get('_id') or user.get('id') or user.get('user_id'),
            filters={'limit': 10000}
        )
        
        if not all_leads_result.get('success'):
            raise HTTPException(status_code=400, detail="Failed to get analytics data")
        
        leads = all_leads_result['leads']
        
        # Filter by date range
        period_leads = [
            lead for lead in leads
            if lead.get('discovered_at', start_date) >= start_date
        ]
        
        # Calculate analytics
        analytics = {
            'overview': {
                'total_leads': len(leads),
                'period_leads': len(period_leads),
                'platforms': {}
            },
            'platform_breakdown': {
                'tiktok': {'count': 0, 'avg_followers': 0, 'avg_engagement': 0},
                'twitter': {'count': 0, 'avg_followers': 0, 'avg_engagement': 0}
            },
            'engagement_metrics': {
                'high_engagement': 0,  # >5%
                'medium_engagement': 0,  # 2-5%
                'low_engagement': 0  # <2%
            },
            'contact_info_stats': {
                'with_email': 0,
                'with_phone': 0,
                'with_website': 0
            },
            'lead_scores': {
                'excellent': 0,  # 80+
                'good': 0,      # 60-79
                'fair': 0,      # 40-59
                'poor': 0       # <40
            }
        }
        
        # Process leads for analytics
        for lead in period_leads:
            platform = lead.get('platform', 'unknown')
            
            # Platform counts
            if platform in analytics['platform_breakdown']:
                platform_data = analytics['platform_breakdown'][platform]
                platform_data['count'] += 1
                platform_data['avg_followers'] += lead.get('follower_count', 0)
                platform_data['avg_engagement'] += lead.get('engagement_rate', 0)
            
            # Engagement metrics
            engagement = lead.get('engagement_rate', 0)
            if engagement > 5:
                analytics['engagement_metrics']['high_engagement'] += 1
            elif engagement > 2:
                analytics['engagement_metrics']['medium_engagement'] += 1
            else:
                analytics['engagement_metrics']['low_engagement'] += 1
            
            # Contact info stats
            contact_info = lead.get('contact_info', {})
            if contact_info.get('email'):
                analytics['contact_info_stats']['with_email'] += 1
            if contact_info.get('phone'):
                analytics['contact_info_stats']['with_phone'] += 1
            if contact_info.get('website'):
                analytics['contact_info_stats']['with_website'] += 1
            
            # Lead scores
            score = lead.get('lead_score', 0)
            if score >= 80:
                analytics['lead_scores']['excellent'] += 1
            elif score >= 60:
                analytics['lead_scores']['good'] += 1
            elif score >= 40:
                analytics['lead_scores']['fair'] += 1
            else:
                analytics['lead_scores']['poor'] += 1
        
        # Calculate averages
        for platform, data in analytics['platform_breakdown'].items():
            count = data['count']
            if count > 0:
                data['avg_followers'] = round(data['avg_followers'] / count)
                data['avg_engagement'] = round(data['avg_engagement'] / count, 2)
        
        return {
            "success": True,
            "analytics": analytics,
            "period_days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get leads analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Platform Information
@router.get("/platforms/info", tags=["Social Media Leads"])
async def get_platform_info():
    """Get information about supported platforms"""
    try:
        platform_info = {
            'supported_platforms': ['tiktok', 'twitter'],
            'platform_details': {
                'tiktok': {
                    'name': 'TikTok',
                    'description': 'Short-form video social media platform',
                    'api_features': [
                        'Creator discovery',
                        'Follower metrics',
                        'Content analytics',
                        'Engagement tracking'
                    ],
                    'search_capabilities': [
                        'Keyword search',
                        'Follower count filtering',
                        'Location targeting',
                        'Content type filtering'
                    ]
                },
                'twitter': {
                    'name': 'Twitter',
                    'description': 'Microblogging and social networking service',
                    'api_features': [
                        'User discovery',
                        'Tweet analytics',
                        'Verification status',
                        'Activity metrics'
                    ],
                    'search_capabilities': [
                        'Keyword search',
                        'Follower count filtering',
                        'Location targeting',
                        'Verification filtering'
                    ]
                }
            },
            'lead_scoring_factors': {
                'follower_count': 'Number of followers (0-40 points)',
                'engagement_rate': 'User engagement metrics (0-30 points)',
                'content_activity': 'Content creation activity (0-25 points)',
                'verification_status': 'Account verification (0-20 points)',
                'profile_completeness': 'Bio and profile completeness (0-15 points)'
            }
        }
        
        return {
            "success": True,
            "platform_info": platform_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get platform info error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["Social Media Leads"])
async def social_media_leads_health_check():
    """Health check for social media leads system"""
    return {
        "status": "healthy",
        "service": "Complete Social Media Lead Generation (TikTok & Twitter/X Focus)",
        "features": [
            "TikTok Creator Discovery",
            "Twitter User Discovery", 
            "Lead Management & CRUD",
            "Contact Information Extraction",
            "Engagement Rate Calculation",
            "Lead Scoring System",
            "CSV Export Functionality",
            "Advanced Filtering",
            "Bulk Operations",
            "Analytics & Reporting"
        ],
        "supported_platforms": ["tiktok", "twitter"],
        "api_integrations": ["TikTok Business API", "Twitter API v2"],
        "timestamp": datetime.utcnow().isoformat()
    }