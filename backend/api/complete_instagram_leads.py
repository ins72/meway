"""
Complete Instagram Lead Generation API
Real Instagram Graph API Integration for Lead Discovery and Contact Extraction
Version: 1.0.0 - Production Ready
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from core.auth import get_current_user
from services.complete_instagram_service import instagram_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class InstagramSearchRequest(BaseModel):
    hashtags: Optional[List[str]] = Field(default=[], description="Hashtags to search for")
    location: Optional[str] = Field(default=None, description="Location to search in")
    industry: Optional[str] = Field(default=None, description="Industry category")
    follower_range: Optional[Dict[str, int]] = Field(
        default={'min': 1000, 'max': 100000},
        description="Follower count range"
    )
    engagement_rate_min: Optional[float] = Field(default=0.02, description="Minimum engagement rate")
    account_type: Optional[str] = Field(default='business', description="Account type to search")
    content_language: Optional[str] = Field(default='en', description="Content language")
    posting_frequency: Optional[str] = Field(default='active', description="Posting frequency filter")
    similar_to_username: Optional[str] = Field(default=None, description="Find accounts similar to this username")

class InstagramLeadFilters(BaseModel):
    min_followers: Optional[int] = Field(default=None, description="Minimum follower count")
    max_followers: Optional[int] = Field(default=None, description="Maximum follower count")
    min_engagement_rate: Optional[float] = Field(default=None, description="Minimum engagement rate")
    category: Optional[str] = Field(default=None, description="Account category")
    has_contact_info: Optional[bool] = Field(default=None, description="Must have contact information")

@router.post("/instagram/search", tags=["Instagram Lead Generation"])
async def discover_instagram_accounts(
    search_request: InstagramSearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Discover Instagram business accounts based on search criteria
    Real Instagram Graph API integration for comprehensive lead discovery
    """
    try:
        search_params = search_request.dict()
        search_params['user_id'] = current_user['user_id']
        
        result = await instagram_service.discover_instagram_accounts(search_params)
        
        if result['success']:
            return {
                "success": True,
                "message": "Instagram account discovery completed successfully",
                "data": {
                    "search_id": result['search_id'],
                    "total_accounts_found": result['total_accounts_found'],
                    "preview_accounts": result['accounts'],
                    "search_criteria": result['search_criteria'],
                    "completion_time": result['completion_time']
                }
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Instagram discovery failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Instagram search endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Instagram account discovery failed: {str(e)}"
        )

@router.get("/instagram/leads/{search_id}", tags=["Instagram Lead Generation"])
async def get_instagram_leads(
    search_id: str,
    min_followers: Optional[int] = None,
    max_followers: Optional[int] = None,
    min_engagement_rate: Optional[float] = None,
    category: Optional[str] = None,
    has_contact_info: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get discovered Instagram leads with optional filtering
    """
    try:
        filters = {}
        if min_followers is not None:
            filters['min_followers'] = min_followers
        if max_followers is not None:
            filters['max_followers'] = max_followers
        if min_engagement_rate is not None:
            filters['min_engagement_rate'] = min_engagement_rate
        if category:
            filters['category'] = category
        if has_contact_info is not None:
            filters['has_contact_info'] = has_contact_info
        
        result = await instagram_service.get_instagram_leads(search_id, filters)
        
        if result['success']:
            return {
                "success": True,
                "message": "Instagram leads retrieved successfully",
                "data": {
                    "search_id": result['search_id'],
                    "total_leads": result['total_leads'],
                    "leads": result['leads'],
                    "filters_applied": result['filters_applied']
                }
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Instagram leads not found: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Get Instagram leads error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve Instagram leads: {str(e)}"
        )

@router.post("/instagram/export/{search_id}", tags=["Instagram Lead Generation"])
async def export_instagram_leads_csv(
    search_id: str,
    filters: Optional[InstagramLeadFilters] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Export Instagram leads to CSV format with comprehensive lead data
    """
    try:
        filter_dict = filters.dict(exclude_none=True) if filters else None
        
        result = await instagram_service.export_instagram_leads_csv(search_id, filter_dict)
        
        if result['success']:
            return {
                "success": True,
                "message": "Instagram leads exported successfully",
                "data": {
                    "export_id": result['export_id'],
                    "csv_headers": result['csv_headers'],
                    "csv_data": result['csv_data'],
                    "total_records": result['total_records'],
                    "exported_at": result['exported_at']
                }
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Instagram leads export failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Export Instagram leads error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export Instagram leads: {str(e)}"
        )

@router.get("/instagram/search-history", tags=["Instagram Lead Generation"])
async def get_instagram_search_history(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's Instagram search history
    """
    try:
        user_id = current_user['user_id']
        result = await instagram_service.get_instagram_search_history(user_id)
        
        if result['success']:
            return {
                "success": True,
                "message": "Instagram search history retrieved successfully",
                "data": {
                    "searches": result['searches'],
                    "total_searches": result['total_searches']
                }
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Search history not found: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Get search history error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve search history: {str(e)}"
        )

@router.get("/instagram/analytics/overview", tags=["Instagram Lead Generation"])
async def get_instagram_analytics_overview(
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive Instagram lead generation analytics
    """
    try:
        user_id = current_user['user_id']
        result = await instagram_service.get_instagram_analytics_overview(user_id)
        
        if result['success']:
            return {
                "success": True,
                "message": "Instagram analytics retrieved successfully",
                "data": result['analytics']
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Analytics retrieval failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Get analytics overview error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )

@router.get("/instagram/account/{username}", tags=["Instagram Lead Generation"])
async def get_instagram_account_details(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific Instagram account
    """
    try:
        # Create a mock account info for discovery and then enrich it
        mock_account = {
            'username': username,
            'discovery_method': 'direct_lookup',
            'discovery_context': 'manual_search'
        }
        
        # Use the existing enrichment method
        enriched_account = await instagram_service._enrich_instagram_account(mock_account)
        
        if enriched_account and enriched_account.get('profile_data'):
            return {
                "success": True,
                "message": "Instagram account details retrieved successfully",
                "data": {
                    "account": enriched_account,
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Instagram account not found or not accessible: {username}"
            )
            
    except Exception as e:
        logger.error(f"Get account details error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve account details: {str(e)}"
        )

@router.get("/instagram/categories", tags=["Instagram Lead Generation"])
async def get_instagram_account_categories(
    current_user: dict = Depends(get_current_user)
):
    """
    Get available Instagram account categories for filtering
    """
    try:
        categories = [
            {
                'category': 'fitness',
                'display_name': 'Fitness & Health',
                'description': 'Fitness trainers, gyms, health coaches',
                'keywords': ['fitness', 'gym', 'workout', 'trainer', 'yoga', 'health']
            },
            {
                'category': 'food',
                'display_name': 'Food & Culinary',
                'description': 'Restaurants, chefs, food bloggers',
                'keywords': ['food', 'chef', 'restaurant', 'recipe', 'cooking', 'kitchen']
            },
            {
                'category': 'fashion',
                'display_name': 'Fashion & Style',
                'description': 'Fashion brands, boutiques, stylists',
                'keywords': ['fashion', 'style', 'boutique', 'clothing', 'brand', 'designer']
            },
            {
                'category': 'beauty',
                'display_name': 'Beauty & Cosmetics',
                'description': 'Beauty brands, makeup artists, salons',
                'keywords': ['beauty', 'makeup', 'skincare', 'cosmetics', 'salon', 'nail']
            },
            {
                'category': 'business',
                'display_name': 'Business & Entrepreneurship',
                'description': 'Entrepreneurs, business coaches, companies',
                'keywords': ['business', 'entrepreneur', 'ceo', 'founder', 'company', 'startup']
            },
            {
                'category': 'lifestyle',
                'display_name': 'Lifestyle & Travel',
                'description': 'Lifestyle influencers, travel bloggers',
                'keywords': ['lifestyle', 'blogger', 'influencer', 'travel', 'photography']
            },
            {
                'category': 'education',
                'display_name': 'Education & Training',
                'description': 'Teachers, coaches, online courses',
                'keywords': ['education', 'teacher', 'coach', 'course', 'training', 'learning']
            },
            {
                'category': 'technology',
                'display_name': 'Technology & Digital',
                'description': 'Tech companies, developers, digital agencies',
                'keywords': ['tech', 'developer', 'software', 'digital', 'coding', 'ai']
            },
            {
                'category': 'creative',
                'display_name': 'Creative & Arts',
                'description': 'Artists, designers, photographers, musicians',
                'keywords': ['artist', 'designer', 'creative', 'art', 'music', 'photography']
            }
        ]
        
        return {
            "success": True,
            "message": "Instagram account categories retrieved successfully",
            "data": {
                "categories": categories,
                "total_categories": len(categories)
            }
        }
        
    except Exception as e:
        logger.error(f"Get categories error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve categories: {str(e)}"
        )

@router.get("/instagram/search-templates", tags=["Instagram Lead Generation"])
async def get_instagram_search_templates(
    current_user: dict = Depends(get_current_user)
):
    """
    Get pre-configured search templates for different industries
    """
    try:
        templates = [
            {
                'template_id': 'fitness_influencers',
                'name': 'Fitness Influencers',
                'description': 'Find fitness trainers and health influencers',
                'criteria': {
                    'hashtags': ['fitness', 'gym', 'workout', 'health', 'motivation'],
                    'follower_range': {'min': 5000, 'max': 500000},
                    'engagement_rate_min': 0.03,
                    'account_type': 'business'
                }
            },
            {
                'template_id': 'local_businesses',
                'name': 'Local Businesses',
                'description': 'Find local business accounts in your area',
                'criteria': {
                    'location': 'user_location',
                    'follower_range': {'min': 500, 'max': 50000},
                    'engagement_rate_min': 0.02,
                    'account_type': 'business'
                }
            },
            {
                'template_id': 'fashion_brands',
                'name': 'Fashion Brands',
                'description': 'Find fashion and clothing brands',
                'criteria': {
                    'hashtags': ['fashion', 'style', 'clothing', 'brand', 'outfit'],
                    'follower_range': {'min': 10000, 'max': 1000000},
                    'engagement_rate_min': 0.025,
                    'account_type': 'business'
                }
            },
            {
                'template_id': 'food_bloggers',
                'name': 'Food Bloggers',
                'description': 'Find food bloggers and restaurants',
                'criteria': {
                    'hashtags': ['food', 'foodie', 'restaurant', 'cooking', 'recipe'],
                    'follower_range': {'min': 2000, 'max': 200000},
                    'engagement_rate_min': 0.04,
                    'account_type': 'business'
                }
            },
            {
                'template_id': 'beauty_brands',
                'name': 'Beauty & Cosmetics',
                'description': 'Find beauty brands and makeup artists',
                'criteria': {
                    'hashtags': ['beauty', 'makeup', 'skincare', 'cosmetics', 'beautyblogger'],
                    'follower_range': {'min': 3000, 'max': 300000},
                    'engagement_rate_min': 0.035,
                    'account_type': 'business'
                }
            },
            {
                'template_id': 'micro_influencers',
                'name': 'Micro Influencers',
                'description': 'Find micro influencers with high engagement',
                'criteria': {
                    'hashtags': ['influencer', 'content', 'creator', 'lifestyle'],
                    'follower_range': {'min': 1000, 'max': 100000},
                    'engagement_rate_min': 0.05,
                    'account_type': 'business'
                }
            }
        ]
        
        return {
            "success": True,
            "message": "Instagram search templates retrieved successfully",
            "data": {
                "templates": templates,
                "total_templates": len(templates)
            }
        }
        
    except Exception as e:
        logger.error(f"Get search templates error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve search templates: {str(e)}"
        )

@router.get("/instagram/health", tags=["Instagram Lead Generation"])
async def instagram_service_health_check():
    """
    Health check for Instagram lead generation service
    """
    try:
        return {
            "success": True,
            "message": "Instagram lead generation service is operational",
            "data": {
                "service_name": "Complete Instagram Lead Generation",
                "version": "1.0.0",
                "features": [
                    "Instagram Graph API Integration",
                    "Business Account Discovery",
                    "Lead Scoring and Categorization",
                    "Contact Information Extraction",
                    "Engagement Metrics Analysis",
                    "CSV Export Functionality",
                    "Advanced Filtering",
                    "Search History Tracking",
                    "Analytics and Reporting"
                ],
                "api_endpoints": 9,
                "status": "operational",
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Instagram health check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Instagram service health check failed: {str(e)}"
        )