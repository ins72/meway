"""
Advanced Social Media Management Suite API Endpoints
Multi-platform management, AI content generation, and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
from core.auth import get_current_user
from core.database import get_database
from services.advanced_social_media_suite_service import AdvancedSocialMediaSuiteService

router = APIRouter(prefix="/api/social-media-suite", tags=["Social Media Suite"])

class SocialAccountConnect(BaseModel):
    platform: str
    account_name: str
    account_handle: str
    access_token: str
    refresh_token: Optional[str] = None
    follower_count: int = 0
    bio: Optional[str] = None

class AIContentRequest(BaseModel):
    platform: str
    content_type: str = "post"
    brand_voice: str = "professional"
    target_audience: str = "general"
    topic: str

class SocialListeningSetup(BaseModel):
    brand_name: str
    keywords: List[str] = []
    hashtags: List[str] = []
    competitors: List[str] = []
    platforms: List[str] = []
    email_alerts: bool = False
    real_time_alerts: bool = False

class InfluencerDiscoveryRequest(BaseModel):
    platform: str = "instagram"
    niche: str
    min_followers: int = 1000
    max_followers: int = 1000000
    location: Optional[str] = None
    engagement_rate_min: float = 2.0
    max_budget: Optional[float] = None

@router.post("/accounts/connect")
async def connect_social_account(
    account_data: SocialAccountConnect,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Connect social media account to the platform"""
    service = AdvancedSocialMediaSuiteService(db)
    
    account_dict = account_data.dict()
    account_dict["user_id"] = current_user["user_id"]
    
    result = await service.connect_social_account(account_dict)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Social account connected successfully", "data": result}

@router.get("/accounts")
async def list_social_accounts(
    platform: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List connected social media accounts"""
    filter_query = {"user_id": current_user["user_id"]}
    if platform:
        filter_query["platform"] = platform
    
    accounts = await db["social_accounts"].find(filter_query).to_list(length=50)
    
    return {
        "message": "Social accounts retrieved successfully",
        "data": accounts,
        "count": len(accounts)
    }

@router.post("/content/ai-generate")
async def generate_ai_content(
    content_request: AIContentRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Generate AI-powered social media content"""
    service = AdvancedSocialMediaSuiteService(db)
    result = await service.generate_ai_content(content_request.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "AI content generated successfully", "data": result}

@router.post("/listening/setup")
async def setup_social_listening(
    listening_data: SocialListeningSetup,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Set up social listening for brand monitoring"""
    service = AdvancedSocialMediaSuiteService(db)
    
    listening_dict = listening_data.dict()
    listening_dict["user_id"] = current_user["user_id"]
    
    result = await service.setup_social_listening(listening_dict)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Social listening setup successfully", "data": result}

@router.get("/listening/mentions")
async def get_brand_mentions(
    sentiment: Optional[str] = None,
    platform: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get brand mentions from social listening"""
    # Mock mentions data
    mentions = [
        {
            "id": "mention_1",
            "platform": "twitter",
            "content": "Really impressed with @YourBrand's new features!",
            "author": "@satisfied_customer",
            "sentiment": "positive",
            "engagement": {"likes": 15, "retweets": 3},
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "id": "mention_2",
            "platform": "instagram",
            "content": "Using @YourBrand for my business - game changer!",
            "author": "@business_owner",
            "sentiment": "positive",
            "engagement": {"likes": 42, "comments": 8},
            "timestamp": datetime.utcnow().isoformat()
        }
    ]
    
    if sentiment:
        mentions = [m for m in mentions if m["sentiment"] == sentiment]
    if platform:
        mentions = [m for m in mentions if m["platform"] == platform]
    
    return {
        "message": "Brand mentions retrieved successfully",
        "data": mentions,
        "count": len(mentions)
    }

@router.post("/influencers/discover")
async def discover_influencers(
    criteria: InfluencerDiscoveryRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Discover and analyze influencers based on criteria"""
    service = AdvancedSocialMediaSuiteService(db)
    result = await service.discover_influencers(criteria.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Influencers discovered successfully", "data": result}

@router.get("/analytics")
async def get_social_analytics(
    time_period: str = "30d",
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get comprehensive social media analytics"""
    service = AdvancedSocialMediaSuiteService(db)
    result = await service.get_social_analytics(current_user["user_id"], time_period)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Social analytics retrieved successfully", "data": result}

@router.get("/content/templates")
async def get_content_templates(
    platform: Optional[str] = None,
    content_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get AI-generated content templates"""
    filter_query = {}
    if platform:
        filter_query["platform"] = platform
    if content_type:
        filter_query["content_type"] = content_type
    
    templates = await db["content_templates"].find(filter_query).sort("generated_at", -1).to_list(length=20)
    
    return {
        "message": "Content templates retrieved successfully",
        "data": templates,
        "count": len(templates)
    }

@router.get("/dashboard")
async def get_social_dashboard(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get social media management dashboard"""
    dashboard_data = {
        "connected_accounts": 5,
        "scheduled_posts": 12,
        "active_campaigns": 3,
        "total_reach": 125000,
        "engagement_rate": 4.6,
        "recent_posts": [
            {"platform": "instagram", "content": "New feature announcement!", "engagement": 542},
            {"platform": "twitter", "content": "Thanks for your feedback!", "engagement": 89},
            {"platform": "linkedin", "content": "Industry insights...", "engagement": 156}
        ],
        "trending_hashtags": ["#business", "#innovation", "#AI", "#automation"],
        "optimal_posting_times": {
            "instagram": ["2PM-4PM", "7PM-9PM"],
            "twitter": ["9AM-11AM", "1PM-3PM"],
            "linkedin": ["8AM-10AM", "5PM-6PM"]
        }
    }
    
    return {"message": "Social dashboard retrieved successfully", "data": dashboard_data}