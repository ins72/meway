"""
Real Social Media Lead Generation API - NO MOCK DATA
Endpoints for Twitter/X and TikTok lead generation with real API integrations
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import asyncio

from core.database import get_database
from core.auth import get_current_user
from services.real_twitter_lead_generation_service import RealTwitterLeadGenerationService
from services.real_tiktok_lead_generation_service import RealTikTokLeadGenerationService

router = APIRouter(prefix="/api/social-media-leads", tags=["Social Media Lead Generation"])

@router.post("/twitter/search")
async def search_twitter_leads(
    search_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Search for Twitter/X leads using real Twitter API
    """
    try:
        twitter_service = RealTwitterLeadGenerationService(db)
        
        # Validate search criteria
        search_criteria = {
            "keywords": search_request.get("keywords", []),
            "hashtags": search_request.get("hashtags", []),
            "location": search_request.get("location"),
            "max_results": min(search_request.get("max_results", 50), 100),
            "verified_only": search_request.get("verified_only", False),
            "min_followers": search_request.get("min_followers", 0)
        }
        
        # Execute Twitter search
        results = await twitter_service.search_twitter_leads(search_criteria)
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        
        return {
            "success": True,
            "platform": "twitter",
            "search_id": results["search_id"],
            "leads_found": results["leads_found"],
            "leads_preview": results["leads"][:5],  # Show first 5 leads
            "total_available": results["total_available"],
            "search_criteria": search_criteria,
            "search_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Twitter search failed: {str(e)}")

@router.post("/tiktok/search")
async def search_tiktok_creators(
    search_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Search for TikTok creators using real TikTok Business API
    """
    try:
        tiktok_service = RealTikTokLeadGenerationService(db)
        
        # Validate search criteria
        search_criteria = {
            "keywords": search_request.get("keywords", []),
            "region": search_request.get("region"),
            "max_results": min(search_request.get("max_results", 50), 50),
            "min_followers": search_request.get("min_followers", 0),
            "niche": search_request.get("niche"),
            "cursor": search_request.get("cursor", 0)
        }
        
        # Execute TikTok search
        results = await tiktok_service.search_tiktok_creators(search_criteria)
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        
        return {
            "success": True,
            "platform": "tiktok",
            "search_id": results["search_id"],
            "leads_found": results["leads_found"],
            "leads_preview": results["leads"][:5],  # Show first 5 leads
            "has_more": results.get("has_more", False),
            "next_cursor": results.get("cursor", 0),
            "search_criteria": search_criteria,
            "search_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok search failed: {str(e)}")

@router.get("/twitter/leads/{search_id}")
async def get_twitter_leads(
    search_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get full Twitter leads list from a search
    """
    try:
        twitter_leads = db["twitter_leads"]
        
        # Get leads from database
        leads = await twitter_leads.find(
            {"search_id": search_id}
        ).skip(skip).limit(limit).to_list(length=None)
        
        # Get total count
        total_count = await twitter_leads.count_documents({"search_id": search_id})
        
        return {
            "success": True,
            "search_id": search_id,
            "leads": leads,
            "total_count": total_count,
            "returned_count": len(leads),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Twitter leads: {str(e)}")

@router.get("/tiktok/leads/{search_id}")
async def get_tiktok_leads(
    search_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get full TikTok leads list from a search
    """
    try:
        tiktok_leads = db["tiktok_leads"]
        
        # Get leads from database
        leads = await tiktok_leads.find(
            {"search_id": search_id}
        ).skip(skip).limit(limit).to_list(length=None)
        
        # Get total count
        total_count = await tiktok_leads.count_documents({"search_id": search_id})
        
        return {
            "success": True,
            "search_id": search_id,
            "leads": leads,
            "total_count": total_count,
            "returned_count": len(leads),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TikTok leads: {str(e)}")

@router.post("/twitter/export/{search_id}")
async def export_twitter_leads(
    search_id: str,
    export_format: str = "csv",
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Export Twitter leads to CSV
    """
    try:
        twitter_service = RealTwitterLeadGenerationService(db)
        
        # Export leads
        export_result = await twitter_service.export_leads_to_csv(search_id, export_format)
        
        if "error" in export_result:
            raise HTTPException(status_code=500, detail=export_result["error"])
        
        return {
            "success": True,
            "export_id": export_result["export_id"],
            "format": export_result["format"],
            "leads_count": export_result["leads_count"],
            "csv_content": export_result["csv_content"],
            "generated_at": export_result["generated_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/tiktok/export/{search_id}")
async def export_tiktok_leads(
    search_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Export TikTok leads to CSV
    """
    try:
        tiktok_service = RealTikTokLeadGenerationService(db)
        
        # Export leads
        export_result = await tiktok_service.export_tiktok_leads(search_id)
        
        if "error" in export_result:
            raise HTTPException(status_code=500, detail=export_result["error"])
        
        return {
            "success": True,
            "export_id": export_result["export_id"],
            "format": export_result["format"],
            "leads_count": export_result["leads_count"],
            "csv_content": export_result["csv_content"],
            "generated_at": export_result["generated_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/search-history")
async def get_search_history(
    platform: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get search history for lead generation
    """
    try:
        collections = []
        
        if platform == "twitter" or platform is None:
            collections.append(("twitter", db["lead_searches"]))
        
        if platform == "tiktok" or platform is None:
            collections.append(("tiktok", db["tiktok_searches"]))
        
        search_history = []
        
        for platform_name, collection in collections:
            searches = await collection.find(
                {},
                {"_id": 1, "search_criteria": 1, "results_count": 1, "executed_at": 1, "status": 1}
            ).sort("executed_at", -1).limit(limit).to_list(length=None)
            
            for search in searches:
                search["platform"] = platform_name
                search_history.append(search)
        
        # Sort by date
        search_history.sort(key=lambda x: x["executed_at"], reverse=True)
        
        return {
            "success": True,
            "search_history": search_history[:limit],
            "total_count": len(search_history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get search history: {str(e)}")

@router.get("/analytics/overview")
async def get_lead_analytics(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get lead generation analytics overview
    """
    try:
        # Get counts from all collections
        twitter_leads_count = await db["twitter_leads"].count_documents({})
        tiktok_leads_count = await db["tiktok_leads"].count_documents({})
        twitter_searches_count = await db["lead_searches"].count_documents({})
        tiktok_searches_count = await db["tiktok_searches"].count_documents({})
        
        # Get recent activity
        recent_twitter = await db["lead_searches"].find({}).sort("executed_at", -1).limit(5).to_list(length=None)
        recent_tiktok = await db["tiktok_searches"].find({}).sort("executed_at", -1).limit(5).to_list(length=None)
        
        # Calculate platform distribution
        total_leads = twitter_leads_count + tiktok_leads_count
        
        return {
            "success": True,
            "total_leads": total_leads,
            "platform_breakdown": {
                "twitter": {
                    "leads_count": twitter_leads_count,
                    "searches_count": twitter_searches_count,
                    "percentage": round((twitter_leads_count / max(total_leads, 1)) * 100, 2)
                },
                "tiktok": {
                    "leads_count": tiktok_leads_count,
                    "searches_count": tiktok_searches_count,
                    "percentage": round((tiktok_leads_count / max(total_leads, 1)) * 100, 2)
                }
            },
            "recent_activity": {
                "twitter_searches": recent_twitter,
                "tiktok_searches": recent_tiktok
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")