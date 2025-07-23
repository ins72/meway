"""
Link Shortener System API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition - Complete URL Shortening Service
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import secrets
import re
from urllib.parse import urlparse

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from services.analytics_service import get_analytics_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()
analytics_service = get_analytics_service()

class ShortLinkCreate(BaseModel):
    original_url: HttpUrl
    custom_slug: Optional[str] = None
    title: Optional[str] = ""
    description: Optional[str] = ""
    expires_at: Optional[datetime] = None
    password: Optional[str] = None
    utm_parameters: Optional[Dict[str, str]] = {}

class ShortLinkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class BulkLinkCreate(BaseModel):
    links: List[Dict[str, str]]  # [{"url": "...", "title": "..."}]
    default_domain: str = "mwz.to"

def get_short_links_collection():
    """Get short links collection"""
    db = get_database()
    return db.short_links

def get_link_analytics_collection():
    """Get link analytics collection"""
    db = get_database()
    return db.link_analytics

def get_link_clicks_collection():
    """Get link clicks collection"""
    db = get_database()
    return db.link_clicks

def generate_short_code(length: int = 8) -> str:
    """Generate a random short code"""
    # Use URL-safe characters
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(secrets.choice(chars) for _ in range(length))

def validate_custom_slug(slug: str) -> bool:
    """Validate custom slug format"""
    if not slug:
        return False
    
    # Check length (3-50 characters)
    if len(slug) < 3 or len(slug) > 50:
        return False
    
    # Check characters (alphanumeric, hyphens, underscores only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        return False
    
    # Reserved keywords
    reserved = ['api', 'www', 'admin', 'app', 'dashboard', 'analytics', 'stats']
    if slug.lower() in reserved:
        return False
    
    return True

@router.get("/dashboard")
async def get_link_shortener_dashboard(current_user: dict = Depends(get_current_active_user)):
    """Get link shortener dashboard with comprehensive analytics"""
    try:
        short_links_collection = get_short_links_collection()
        link_clicks_collection = get_link_clicks_collection()
        
        # Get user's links overview
        total_links = await short_links_collection.count_documents({"user_id": current_user["_id"]})
        active_links = await short_links_collection.count_documents({
            "user_id": current_user["_id"],
            "is_active": True
        })
        
        # Calculate total clicks
        clicks_pipeline = [
            {"$match": {"user_id": current_user["_id"]}},
            {"$group": {
                "_id": None,
                "total_clicks": {"$sum": "$total_clicks"}
            }}
        ]
        
        clicks_result = await short_links_collection.aggregate(clicks_pipeline).to_list(length=1)
        total_clicks = await self._calculate_real_metric("clicks")
        if clicks_result and len(clicks_result) > 0 and clicks_result[0]:
            total_clicks = clicks_result[0].get("total_clicks", 0) or 0
        
        # Get top performing links
        top_links = await short_links_collection.find(
            {"user_id": current_user["_id"]}
        ).sort("total_clicks", -1).limit(10).to_list(length=None)
        
        # Get recent clicks (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_clicks = await link_clicks_collection.count_documents({
            "user_id": current_user["_id"],
            "clicked_at": {"$gte": thirty_days_ago}
        })
        
        # Get clicks by day (last 7 days) for chart
        daily_clicks = []
        for i in range(7):
            day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_clicks = await link_clicks_collection.count_documents({
                "user_id": current_user["_id"],
                "clicked_at": {"$gte": day_start, "$lt": day_end}
            })
            
            daily_clicks.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "clicks": day_clicks
            })
        
        # Get device and location breakdown
        device_pipeline = [
            {"$match": {
                "user_id": current_user["_id"],
                "clicked_at": {"$gte": thirty_days_ago}
            }},
            {"$group": {
                "_id": "$device_type",
                "count": {"$sum": 1}
            }}
        ]
        
        device_breakdown = await link_clicks_collection.aggregate(device_pipeline).to_list(length=None)
        
        # Get country breakdown
        country_pipeline = [
            {"$match": {
                "user_id": current_user["_id"],
                "clicked_at": {"$gte": thirty_days_ago}
            }},
            {"$group": {
                "_id": "$country",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        country_breakdown = await link_clicks_collection.aggregate(country_pipeline).to_list(length=None)
        
        dashboard_data = {
            "overview": {
                "total_links": total_links,
                "active_links": active_links,
                "total_clicks": total_clicks,
                "clicks_last_30_days": recent_clicks,
                "avg_clicks_per_link": round(total_clicks / max(total_links, 1), 1)
            },
            "top_links": [
                {
                    "id": link["_id"],
                    "title": link.get("title", "Untitled"),
                    "short_code": link["short_code"],
                    "short_url": f"https://mwz.to/{link['short_code']}",
                    "original_url": link["original_url"],
                    "clicks": link.get("total_clicks", 0),
                    "created_at": link["created_at"]
                } for link in top_links
            ],
            "analytics": {
                "daily_clicks": list(reversed(daily_clicks)),
                "device_breakdown": device_breakdown,
                "country_breakdown": country_breakdown
            },
            "limits": {
                "max_links": await get_user_link_limit(current_user),
                "custom_domains": await has_custom_domain_access(current_user),
                "password_protection": await has_password_protection_access(current_user)
            }
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch link shortener dashboard: {str(e)}"
        )

@router.get("/links")
async def get_short_links(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get user's short links with filtering and pagination"""
    try:
        short_links_collection = get_short_links_collection()
        
        # Build query
        query = {"user_id": current_user["_id"]}
        
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"original_url": {"$regex": search, "$options": "i"}},
                {"short_code": {"$regex": search, "$options": "i"}}
            ]
        
        if status_filter == "active":
            query["is_active"] = True
        elif status_filter == "expired":
            query["expires_at"] = {"$lt": datetime.utcnow()}
        elif status_filter == "password_protected":
            query["password"] = {"$ne": None}
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get links
        links = await short_links_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        total_links = await short_links_collection.count_documents(query)
        
        # Enhance links with additional data
        for link in links:
            link["short_url"] = f"https://mwz.to/{link['short_code']}"
            expires_at = link.get("expires_at")
            link["is_expired"] = expires_at is not None and expires_at < datetime.utcnow()
            link["has_password"] = bool(link.get("password"))
            # Remove password from response for security
            link.pop("password", None)
        
        return {
            "success": True,
            "data": {
                "links": links,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_links + limit - 1) // limit,
                    "total_links": total_links,
                    "has_next": skip + limit < total_links,
                    "has_prev": page > 1
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch short links: {str(e)}"
        )

@router.post("/create")
async def create_short_link(
    link_data: ShortLinkCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new short link with comprehensive validation"""
    try:
        short_links_collection = get_short_links_collection()
        
        # Check user's link creation limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        # Count existing links
        existing_links = await short_links_collection.count_documents({"user_id": current_user["_id"]})
        max_links = await get_user_link_limit(current_user)
        
        if max_links != -1 and existing_links >= max_links:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Link limit reached ({max_links}). Upgrade your plan for more links."
            )
        
        # Validate and generate short code
        if link_data.custom_slug:
            if not validate_custom_slug(link_data.custom_slug):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid custom slug. Use 3-50 alphanumeric characters, hyphens, or underscores."
                )
            
            # Check if custom slug already exists
            existing_link = await short_links_collection.find_one({"short_code": link_data.custom_slug})
            if existing_link:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Custom slug already exists"
                )
            
            short_code = link_data.custom_slug
        else:
            # Generate unique short code
            attempts = 0
            while attempts < 10:  # Prevent infinite loop
                short_code = generate_short_code()
                existing = await short_links_collection.find_one({"short_code": short_code})
                if not existing:
                    break
                attempts += 1
            
            if attempts >= 10:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate unique short code"
                )
        
        # Validate original URL
        original_url = str(link_data.original_url)
        parsed_url = urlparse(original_url)
        if not parsed_url.netloc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format"
            )
        
        # Create short link document
        link_doc = {
            "_id": await self._generate_unique_id(),
            "user_id": current_user["_id"],
            "short_code": short_code,
            "original_url": original_url,
            "title": link_data.title or f"Link to {parsed_url.netloc}",
            "description": link_data.description,
            "total_clicks": 0,
            "unique_clicks": 0,
            "expires_at": link_data.expires_at,
            "password": link_data.password,  # In production, hash this
            "utm_parameters": link_data.utm_parameters,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_clicked_at": None,
            "domain": "mwz.to"  # Default domain
        }
        
        # Save to database
        await short_links_collection.insert_one(link_doc)
        
        # Create analytics record
        await create_link_analytics_record(link_doc["_id"], current_user["_id"])
        
        # Remove password from response
        response_link = link_doc.copy()
        response_link.pop("password", None)
        response_link["short_url"] = f"https://mwz.to/{short_code}"
        response_link["has_password"] = bool(link_data.password)
        
        return {
            "success": True,
            "message": "Short link created successfully",
            "data": response_link
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create short link: {str(e)}"
        )

@router.get("/{short_code}")
async def redirect_short_link(short_code: str, request: Request):
    """Redirect short link and track analytics"""
    try:
        short_links_collection = get_short_links_collection()
        link_clicks_collection = get_link_clicks_collection()
        
        # Find short link
        link = await short_links_collection.find_one({"short_code": short_code})
        
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short link not found"
            )
        
        # Check if link is active
        if not link.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This link has been disabled"
            )
        
        # Check if link is expired
        if link.get("expires_at") and link["expires_at"] < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This link has expired"
            )
        
        # Handle password protection
        if link.get("password"):
            # In a real implementation, this would redirect to a password entry page
            # For now, we'll just track the click and redirect
            pass
        
        # Extract click information
        user_agent = request.headers.get("user-agent", "")
        client_ip = request.client.host
        referer = request.headers.get("referer", "")
        
        # Determine device type (simple detection)
        device_type = "desktop"
        if any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone']):
            device_type = "mobile"
        elif 'tablet' in user_agent.lower() or 'ipad' in user_agent.lower():
            device_type = "tablet"
        
        # Record click
        click_doc = {
            "_id": await self._generate_unique_id(),
            "user_id": link["user_id"],
            "link_id": link["_id"],
            "short_code": short_code,
            "clicked_at": datetime.utcnow(),
            "ip_address": client_ip,
            "user_agent": user_agent,
            "referer": referer,
            "device_type": device_type,
            "country": "Unknown",  # Would integrate with GeoIP service
            "city": "Unknown"
        }
        
        await link_clicks_collection.insert_one(click_doc)
        
        # Update link statistics
        await short_links_collection.update_one(
            {"_id": link["_id"]},
            {
                "$inc": {"total_clicks": 1},
                "$set": {"last_clicked_at": datetime.utcnow()}
            }
        )
        
        # Build final URL with UTM parameters
        final_url = link["original_url"]
        if link.get("utm_parameters"):
            utm_params = []
            for key, value in link["utm_parameters"].items():
                utm_params.append(f"{key}={value}")
            
            separator = "&" if "?" in final_url else "?"
            final_url = f"{final_url}{separator}{'&'.join(utm_params)}"
        
        # Redirect to original URL
        return RedirectResponse(url=final_url, status_code=302)
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error but still try to redirect if we have the URL
        print(f"Error tracking click: {e}")
        if 'link' in locals() and link:
            return RedirectResponse(url=link["original_url"], status_code=302)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/analytics/{link_id}")
async def get_link_analytics(
    link_id: str,
    days: int = 30,
    current_user: dict = Depends(get_current_active_user)
):
    """Get detailed analytics for a specific link"""
    try:
        short_links_collection = get_short_links_collection()
        link_clicks_collection = get_link_clicks_collection()
        
        # Verify link ownership
        link = await short_links_collection.find_one({
            "_id": link_id,
            "user_id": current_user["_id"]
        })
        
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get click data for the period
        clicks = await link_clicks_collection.find({
            "link_id": link_id,
            "clicked_at": {"$gte": start_date, "$lte": end_date}
        }).sort("clicked_at", -1).to_list(length=None)
        
        # Analyze clicks by day
        daily_clicks = {}
        for click in clicks:
            day = click["clicked_at"].strftime("%Y-%m-%d")
            daily_clicks[day] = daily_clicks.get(day, 0) + 1
        
        # Fill missing days with 0
        current_date = start_date
        complete_daily_data = []
        while current_date <= end_date:
            day_str = current_date.strftime("%Y-%m-%d")
            complete_daily_data.append({
                "date": day_str,
                "clicks": daily_clicks.get(day_str, 0)
            })
            current_date += timedelta(days=1)
        
        # Analyze by device type
        device_breakdown = {}
        for click in clicks:
            device = click.get("device_type", "unknown")
            device_breakdown[device] = device_breakdown.get(device, 0) + 1
        
        # Analyze by referer
        referer_breakdown = {}
        for click in clicks:
            referer = click.get("referer", "direct")
            if referer == "":
                referer = "direct"
            elif referer:
                # Extract domain from referer
                try:
                    domain = urlparse(referer).netloc
                    referer = domain if domain else "direct"
                except:
                    referer = "other"
            
            referer_breakdown[referer] = referer_breakdown.get(referer, 0) + 1
        
        # Get top referers (limit to top 10)
        top_referers = sorted(referer_breakdown.items(), key=lambda x: x[1], reverse=True)[:10]
        
        analytics_data = {
            "link_info": {
                "id": link["_id"],
                "short_code": link["short_code"],
                "short_url": f"https://mwz.to/{link['short_code']}",
                "original_url": link["original_url"],
                "title": link.get("title", "Untitled"),
                "created_at": link["created_at"],
                "total_clicks": link["total_clicks"]
            },
            "period_stats": {
                "period_clicks": len(clicks),
                "period_days": days,
                "avg_daily_clicks": round(len(clicks) / days, 1)
            },
            "daily_breakdown": complete_daily_data,
            "device_breakdown": [
                {"device": device, "clicks": count}
                for device, count in device_breakdown.items()
            ],
            "referer_breakdown": [
                {"referer": referer, "clicks": count}
                for referer, count in top_referers
            ],
            "recent_clicks": [
                {
                    "clicked_at": click["clicked_at"],
                    "device_type": click.get("device_type", "unknown"),
                    "referer": click.get("referer", "direct"),
                    "country": click.get("country", "unknown")
                }
                for click in clicks[:20]  # Last 20 clicks
            ]
        }
        
        return {
            "success": True,
            "data": analytics_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch link analytics: {str(e)}"
        )

@router.put("/links/{link_id}")
async def update_short_link(
    link_id: str,
    update_data: ShortLinkUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update short link with validation"""
    try:
        short_links_collection = get_short_links_collection()
        
        # Find link
        link = await short_links_collection.find_one({
            "_id": link_id,
            "user_id": current_user["_id"]
        })
        
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        
        # Prepare update document
        update_doc = {"$set": {"updated_at": datetime.utcnow()}}
        
        # Update allowed fields
        update_fields = update_data.dict(exclude_none=True)
        for field, value in update_fields.items():
            update_doc["$set"][field] = value
        
        # Update link
        result = await short_links_collection.update_one(
            {"_id": link_id},
            update_doc
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made"
            )
        
        return {
            "success": True,
            "message": "Link updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update link: {str(e)}"
        )

@router.delete("/links/{link_id}")
async def delete_short_link(
    link_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete short link and all associated analytics"""
    try:
        short_links_collection = get_short_links_collection()
        link_clicks_collection = get_link_clicks_collection()
        link_analytics_collection = get_link_analytics_collection()
        
        # Find and delete link
        result = await short_links_collection.delete_one({
            "_id": link_id,
            "user_id": current_user["_id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        
        # Delete associated analytics data
        await link_clicks_collection.delete_many({"link_id": link_id})
        await link_analytics_collection.delete_many({"link_id": link_id})
        
        return {
            "success": True,
            "message": "Link deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete link: {str(e)}"
        )

# Helper functions
async def get_user_link_limit(current_user: dict) -> int:
    """Get user's link creation limit based on plan"""
    user_stats = await user_service.get_user_stats(current_user["_id"])
    user_plan = user_stats["subscription_info"]["plan"]
    
    limits = {
        "free": 10,
        "pro": 1000,
        "enterprise": -1  # unlimited
    }
    
    return limits.get(user_plan, 10)

async def has_custom_domain_access(current_user: dict) -> bool:
    """Check if user has custom domain access"""
    user_stats = await user_service.get_user_stats(current_user["_id"])
    user_plan = user_stats["subscription_info"]["plan"]
    return user_plan in ["pro", "enterprise"]

async def has_password_protection_access(current_user: dict) -> bool:
    """Check if user has password protection access"""
    user_stats = await user_service.get_user_stats(current_user["_id"])
    user_plan = user_stats["subscription_info"]["plan"]
    return user_plan in ["pro", "enterprise"]

async def create_link_analytics_record(link_id: str, user_id: str):
    """Create initial analytics record for a new link"""
    try:
        link_analytics_collection = get_link_analytics_collection()
        
        analytics_doc = {
            "_id": await self._generate_unique_id(),
            "link_id": link_id,
            "user_id": user_id,
            "total_clicks": 0,
            "unique_clicks": 0,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        
        await link_analytics_collection.insert_one(analytics_doc)
        
    except Exception as e:
        print(f"Failed to create analytics record: {e}")
        # Don't fail link creation if analytics fails