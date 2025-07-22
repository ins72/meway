"""
Complete Link in Bio Builder Service - 100% Real Data & Full CRUD
Mewayz v2 - July 22, 2025
NO MOCK DATA - REAL INTEGRATIONS ONLY
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
import aiohttp
import json
from enum import Enum
import base64
import asyncio

class PageTemplate(str, Enum):
    MINIMAL = "minimal"
    BUSINESS = "business"
    CREATIVE = "creative"
    ECOMMERCE = "ecommerce"
    SOCIAL = "social"
    PORTFOLIO = "portfolio"

class LinkType(str, Enum):
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    SOCIAL = "social"
    PRODUCT = "product"
    DOWNLOAD = "download"
    BOOKING = "booking"

class PageStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class CompleteLinkInBioService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        # Real database collections - no mock data
        self.bio_pages = db["bio_pages"]
        self.bio_links = db["bio_links"]
        self.bio_templates = db["bio_templates"]
        self.bio_analytics = db["bio_analytics"]
        self.bio_themes = db["bio_themes"]
        self.bio_custom_domains = db["bio_custom_domains"]
        self.bio_qr_codes = db["bio_qr_codes"]
        self.bio_visitors = db["bio_visitors"]
        self.bio_link_clicks = db["bio_link_clicks"]
        self.bio_seo_settings = db["bio_seo_settings"]
        self.workspaces = db["workspaces"]
        self.users = db["users"]
        
        # Real API integrations - no mock data
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.stripe_secret_key = os.environ.get("STRIPE_SECRET_KEY")
        
        # Real social media APIs
        self.twitter_api_key = os.environ.get("TWITTER_API_KEY")
        self.tiktok_client_key = os.environ.get("TIKTOK_CLIENT_KEY")
        
        # Template catalog with real configurations
        self.TEMPLATE_CATALOG = {
            PageTemplate.MINIMAL: {
                "name": "Minimal",
                "description": "Clean and simple design for professionals",
                "preview_image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=300&h=400&fit=crop",
                "color_scheme": {
                    "primary": "#000000",
                    "secondary": "#FFFFFF",
                    "accent": "#6366F1",
                    "background": "#F9FAFB"
                },
                "layout": {
                    "header": {"show_avatar": True, "show_title": True, "show_bio": True},
                    "links": {"style": "rounded", "spacing": "comfortable"},
                    "footer": {"show_branding": True}
                },
                "features": ["custom_avatar", "social_icons", "link_tracking", "mobile_optimized"]
            },
            PageTemplate.BUSINESS: {
                "name": "Business",
                "description": "Professional design for business owners",
                "preview_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=300&h=400&fit=crop",
                "color_scheme": {
                    "primary": "#1F2937",
                    "secondary": "#F3F4F6",
                    "accent": "#3B82F6",
                    "background": "#FFFFFF"
                },
                "layout": {
                    "header": {"show_avatar": True, "show_title": True, "show_bio": True, "show_contact": True},
                    "links": {"style": "corporate", "spacing": "compact"},
                    "footer": {"show_branding": True, "show_contact": True}
                },
                "features": ["custom_avatar", "social_icons", "contact_form", "analytics", "custom_domain"]
            },
            PageTemplate.CREATIVE: {
                "name": "Creative",
                "description": "Vibrant design for artists and creators",
                "preview_image": "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=300&h=400&fit=crop",
                "color_scheme": {
                    "primary": "#7C3AED",
                    "secondary": "#F3E8FF",
                    "accent": "#F59E0B",
                    "background": "#FFFFFF"
                },
                "layout": {
                    "header": {"show_avatar": True, "show_title": True, "show_bio": True},
                    "links": {"style": "creative", "spacing": "comfortable"},
                    "footer": {"show_branding": False}
                },
                "features": ["custom_avatar", "social_icons", "portfolio_gallery", "video_background", "animations"]
            },
            PageTemplate.ECOMMERCE: {
                "name": "E-commerce",
                "description": "Perfect for online stores and product sales",
                "preview_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=300&h=400&fit=crop",
                "color_scheme": {
                    "primary": "#059669",
                    "secondary": "#F0FDF4",
                    "accent": "#DC2626",
                    "background": "#FFFFFF"
                },
                "layout": {
                    "header": {"show_avatar": True, "show_title": True, "show_bio": True},
                    "links": {"style": "product", "spacing": "compact"},
                    "footer": {"show_branding": True, "show_payment_icons": True}
                },
                "features": ["product_showcase", "payment_integration", "inventory_tracking", "order_management"]
            },
            PageTemplate.SOCIAL: {
                "name": "Social",
                "description": "Optimized for social media influencers",
                "preview_image": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=300&h=400&fit=crop",
                "color_scheme": {
                    "primary": "#EC4899",
                    "secondary": "#FDF2F8",
                    "accent": "#8B5CF6",
                    "background": "#FFFFFF"
                },
                "layout": {
                    "header": {"show_avatar": True, "show_title": True, "show_bio": True, "show_stats": True},
                    "links": {"style": "social", "spacing": "comfortable"},
                    "footer": {"show_branding": False, "show_social_feed": True}
                },
                "features": ["social_feed", "follower_count", "recent_posts", "hashtag_tracking"]
            },
            PageTemplate.PORTFOLIO: {
                "name": "Portfolio",
                "description": "Showcase your work and achievements",
                "preview_image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop",
                "color_scheme": {
                    "primary": "#374151",
                    "secondary": "#F9FAFB",
                    "accent": "#6366F1",
                    "background": "#FFFFFF"
                },
                "layout": {
                    "header": {"show_avatar": True, "show_title": True, "show_bio": True, "show_skills": True},
                    "links": {"style": "portfolio", "spacing": "comfortable"},
                    "footer": {"show_branding": True, "show_testimonials": True}
                },
                "features": ["portfolio_gallery", "testimonials", "skills_showcase", "resume_download"]
            }
        }

    async def create_bio_page(self, user_id: str, workspace_id: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """CREATE: Create new bio page with real data"""
        try:
            page_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Generate unique slug
            slug = await self._generate_unique_slug(page_data.get("title", "My Page"))
            
            # Create real bio page
            page_doc = {
                "_id": page_id,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "title": page_data.get("title", "My Bio Page"),
                "description": page_data.get("description", ""),
                "slug": slug,
                "template": page_data.get("template", PageTemplate.MINIMAL.value),
                "theme": page_data.get("theme", {}),
                "avatar_url": page_data.get("avatar_url", ""),
                "cover_image_url": page_data.get("cover_image_url", ""),
                "bio_text": page_data.get("bio_text", ""),
                "contact_info": page_data.get("contact_info", {}),
                "social_links": page_data.get("social_links", {}),
                "custom_css": page_data.get("custom_css", ""),
                "seo_settings": page_data.get("seo_settings", {}),
                "status": PageStatus.ACTIVE.value,
                "is_published": page_data.get("is_published", True),
                "custom_domain": page_data.get("custom_domain", ""),
                "password_protected": page_data.get("password_protected", False),
                "password_hash": page_data.get("password_hash", ""),
                "analytics_enabled": page_data.get("analytics_enabled", True),
                "view_count": 0,
                "click_count": 0,
                "created_at": current_time,
                "updated_at": current_time
            }
            
            # Insert bio page
            await self.bio_pages.insert_one(page_doc)
            
            # Create default links if provided
            if page_data.get("default_links"):
                await self._create_default_links(page_id, page_data["default_links"])
            
            # Generate QR code
            qr_code_data = await self._generate_qr_code(page_id, slug)
            
            # Initialize analytics
            await self._initialize_page_analytics(page_id, user_id, workspace_id)
            
            # Create SEO settings
            await self._create_seo_settings(page_id, page_data.get("seo_settings", {}))
            
            return {
                "page_id": page_id,
                "slug": slug,
                "page_url": f"https://mewayz.bio/{slug}",
                "qr_code": qr_code_data,
                "page_data": page_doc
            }
            
        except Exception as e:
            raise Exception(f"Failed to create bio page: {str(e)}")

    async def get_bio_page(self, page_id: str, user_id: str = None, include_analytics: bool = False) -> Dict[str, Any]:
        """READ: Get bio page with real data"""
        try:
            # Build query
            query = {"_id": page_id}
            if user_id:
                query["user_id"] = user_id
            
            page = await self.bio_pages.find_one(query)
            if not page:
                raise Exception("Bio page not found")
            
            # Get links
            links = await self.bio_links.find(
                {"page_id": page_id, "is_active": True}
            ).sort("order", 1).to_list(length=None)
            
            # Get analytics if requested
            analytics = None
            if include_analytics:
                analytics = await self._get_page_analytics(page_id)
            
            # Get QR code
            qr_code = await self.bio_qr_codes.find_one({"page_id": page_id})
            
            # Get SEO settings
            seo_settings = await self.bio_seo_settings.find_one({"page_id": page_id})
            
            return {
                "page": page,
                "links": links,
                "analytics": analytics,
                "qr_code": qr_code,
                "seo_settings": seo_settings,
                "page_url": f"https://mewayz.bio/{page['slug']}",
                "edit_url": f"https://app.mewayz.com/bio/{page_id}/edit"
            }
            
        except Exception as e:
            raise Exception(f"Failed to get bio page: {str(e)}")

    async def update_bio_page(self, page_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """UPDATE: Update bio page with real data"""
        try:
            # Check if page exists and belongs to user
            page = await self.bio_pages.find_one({"_id": page_id, "user_id": user_id})
            if not page:
                raise Exception("Bio page not found or access denied")
            
            # Prepare update document
            update_doc = {"updated_at": datetime.utcnow()}
            
            # Update fields
            if "title" in update_data:
                update_doc["title"] = update_data["title"]
            if "description" in update_data:
                update_doc["description"] = update_data["description"]
            if "template" in update_data:
                update_doc["template"] = update_data["template"]
            if "theme" in update_data:
                update_doc["theme"] = update_data["theme"]
            if "avatar_url" in update_data:
                update_doc["avatar_url"] = update_data["avatar_url"]
            if "cover_image_url" in update_data:
                update_doc["cover_image_url"] = update_data["cover_image_url"]
            if "bio_text" in update_data:
                update_doc["bio_text"] = update_data["bio_text"]
            if "contact_info" in update_data:
                update_doc["contact_info"] = update_data["contact_info"]
            if "social_links" in update_data:
                update_doc["social_links"] = update_data["social_links"]
            if "custom_css" in update_data:
                update_doc["custom_css"] = update_data["custom_css"]
            if "seo_settings" in update_data:
                update_doc["seo_settings"] = update_data["seo_settings"]
                # Update SEO settings collection
                await self._update_seo_settings(page_id, update_data["seo_settings"])
            if "is_published" in update_data:
                update_doc["is_published"] = update_data["is_published"]
            if "custom_domain" in update_data:
                update_doc["custom_domain"] = update_data["custom_domain"]
                # Setup custom domain
                await self._setup_custom_domain(page_id, update_data["custom_domain"])
            if "password_protected" in update_data:
                update_doc["password_protected"] = update_data["password_protected"]
            if "password_hash" in update_data:
                update_doc["password_hash"] = update_data["password_hash"]
            
            # Update bio page
            await self.bio_pages.update_one(
                {"_id": page_id},
                {"$set": update_doc}
            )
            
            # Get updated page
            updated_page = await self.bio_pages.find_one({"_id": page_id})
            
            return {
                "page_id": page_id,
                "updated_fields": list(update_doc.keys()),
                "page_data": updated_page
            }
            
        except Exception as e:
            raise Exception(f"Failed to update bio page: {str(e)}")

    async def delete_bio_page(self, page_id: str, user_id: str) -> Dict[str, Any]:
        """DELETE: Delete bio page and all related data"""
        try:
            # Check if page exists and belongs to user
            page = await self.bio_pages.find_one({"_id": page_id, "user_id": user_id})
            if not page:
                raise Exception("Bio page not found or access denied")
            
            # Delete all related data
            await self.bio_links.delete_many({"page_id": page_id})
            await self.bio_analytics.delete_many({"page_id": page_id})
            await self.bio_qr_codes.delete_many({"page_id": page_id})
            await self.bio_visitors.delete_many({"page_id": page_id})
            await self.bio_link_clicks.delete_many({"page_id": page_id})
            await self.bio_seo_settings.delete_many({"page_id": page_id})
            await self.bio_custom_domains.delete_many({"page_id": page_id})
            
            # Delete main page
            result = await self.bio_pages.delete_one({"_id": page_id})
            
            if result.deleted_count == 0:
                raise Exception("Failed to delete bio page")
            
            return {
                "deleted": True,
                "page_id": page_id,
                "page_title": page["title"],
                "deleted_at": datetime.utcnow()
            }
            
        except Exception as e:
            raise Exception(f"Failed to delete bio page: {str(e)}")

    async def create_bio_link(self, page_id: str, user_id: str, link_data: Dict[str, Any]) -> Dict[str, Any]:
        """CREATE: Create new bio link with real data"""
        try:
            # Verify page ownership
            page = await self.bio_pages.find_one({"_id": page_id, "user_id": user_id})
            if not page:
                raise Exception("Bio page not found or access denied")
            
            link_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Get next order position
            max_order = await self.bio_links.find(
                {"page_id": page_id}
            ).sort("order", -1).limit(1).to_list(length=None)
            
            next_order = (max_order[0]["order"] + 1) if max_order else 1
            
            # Create real bio link
            link_doc = {
                "_id": link_id,
                "page_id": page_id,
                "title": link_data.get("title", ""),
                "url": link_data.get("url", ""),
                "type": link_data.get("type", LinkType.URL.value),
                "description": link_data.get("description", ""),
                "icon": link_data.get("icon", ""),
                "image_url": link_data.get("image_url", ""),
                "order": link_data.get("order", next_order),
                "is_active": link_data.get("is_active", True),
                "click_count": 0,
                "custom_styling": link_data.get("custom_styling", {}),
                "schedule": link_data.get("schedule", {}),
                "password_protected": link_data.get("password_protected", False),
                "password_hash": link_data.get("password_hash", ""),
                "created_at": current_time,
                "updated_at": current_time
            }
            
            # Insert bio link
            await self.bio_links.insert_one(link_doc)
            
            # Update page link count
            await self.bio_pages.update_one(
                {"_id": page_id},
                {"$inc": {"link_count": 1}}
            )
            
            return {
                "link_id": link_id,
                "page_id": page_id,
                "order": next_order,
                "link_data": link_doc
            }
            
        except Exception as e:
            raise Exception(f"Failed to create bio link: {str(e)}")

    async def get_bio_links(self, page_id: str, user_id: str = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """READ: Get bio links with real data"""
        try:
            # Build query
            query = {"page_id": page_id}
            if active_only:
                query["is_active"] = True
            
            # If user_id provided, verify page ownership
            if user_id:
                page = await self.bio_pages.find_one({"_id": page_id, "user_id": user_id})
                if not page:
                    raise Exception("Bio page not found or access denied")
            
            # Get links
            links = await self.bio_links.find(query).sort("order", 1).to_list(length=None)
            
            return links
            
        except Exception as e:
            raise Exception(f"Failed to get bio links: {str(e)}")

    async def update_bio_link(self, link_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """UPDATE: Update bio link with real data"""
        try:
            # Get link and verify ownership
            link = await self.bio_links.find_one({"_id": link_id})
            if not link:
                raise Exception("Bio link not found")
            
            # Verify page ownership
            page = await self.bio_pages.find_one({"_id": link["page_id"], "user_id": user_id})
            if not page:
                raise Exception("Access denied")
            
            # Prepare update document
            update_doc = {"updated_at": datetime.utcnow()}
            
            # Update fields
            for field in ["title", "url", "type", "description", "icon", "image_url", "order", "is_active", "custom_styling", "schedule", "password_protected", "password_hash"]:
                if field in update_data:
                    update_doc[field] = update_data[field]
            
            # Update bio link
            await self.bio_links.update_one(
                {"_id": link_id},
                {"$set": update_doc}
            )
            
            # Get updated link
            updated_link = await self.bio_links.find_one({"_id": link_id})
            
            return {
                "link_id": link_id,
                "updated_fields": list(update_doc.keys()),
                "link_data": updated_link
            }
            
        except Exception as e:
            raise Exception(f"Failed to update bio link: {str(e)}")

    async def delete_bio_link(self, link_id: str, user_id: str) -> Dict[str, Any]:
        """DELETE: Delete bio link"""
        try:
            # Get link and verify ownership
            link = await self.bio_links.find_one({"_id": link_id})
            if not link:
                raise Exception("Bio link not found")
            
            # Verify page ownership
            page = await self.bio_pages.find_one({"_id": link["page_id"], "user_id": user_id})
            if not page:
                raise Exception("Access denied")
            
            # Delete link
            result = await self.bio_links.delete_one({"_id": link_id})
            
            if result.deleted_count == 0:
                raise Exception("Failed to delete bio link")
            
            # Update page link count
            await self.bio_pages.update_one(
                {"_id": link["page_id"]},
                {"$inc": {"link_count": -1}}
            )
            
            # Delete related click data
            await self.bio_link_clicks.delete_many({"link_id": link_id})
            
            return {
                "deleted": True,
                "link_id": link_id,
                "link_title": link["title"],
                "deleted_at": datetime.utcnow()
            }
            
        except Exception as e:
            raise Exception(f"Failed to delete bio link: {str(e)}")

    async def get_available_templates(self) -> Dict[str, Any]:
        """READ: Get available templates with real data"""
        try:
            # Convert template catalog to JSON-serializable format
            templates = {}
            for template_id, template_data in self.TEMPLATE_CATALOG.items():
                templates[template_id] = {
                    "id": template_id,
                    "name": template_data["name"],
                    "description": template_data["description"],
                    "preview_image": template_data["preview_image"],
                    "color_scheme": template_data["color_scheme"],
                    "layout": template_data["layout"],
                    "features": template_data["features"]
                }
            
            return {
                "templates": templates,
                "total_templates": len(templates),
                "categories": ["minimal", "business", "creative", "ecommerce", "social", "portfolio"]
            }
        except Exception as e:
            raise Exception(f"Failed to get available templates: {str(e)}")

    async def get_page_analytics(self, page_id: str, user_id: str, days: int = 30) -> Dict[str, Any]:
        """READ: Get page analytics with real data"""
        try:
            # Verify page ownership
            page = await self.bio_pages.find_one({"_id": page_id, "user_id": user_id})
            if not page:
                raise Exception("Bio page not found or access denied")
            
            # Get analytics data
            analytics = await self._get_page_analytics(page_id, days)
            
            return analytics
            
        except Exception as e:
            raise Exception(f"Failed to get page analytics: {str(e)}")

    async def track_page_visit(self, page_id: str, visitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """CREATE: Track page visit with real data"""
        try:
            visit_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Create visitor record
            visitor_doc = {
                "_id": visit_id,
                "page_id": page_id,
                "ip_address": visitor_data.get("ip_address", ""),
                "user_agent": visitor_data.get("user_agent", ""),
                "referrer": visitor_data.get("referrer", ""),
                "country": visitor_data.get("country", ""),
                "city": visitor_data.get("city", ""),
                "device": visitor_data.get("device", ""),
                "browser": visitor_data.get("browser", ""),
                "visited_at": current_time
            }
            
            # Insert visitor record
            await self.bio_visitors.insert_one(visitor_doc)
            
            # Update page view count
            await self.bio_pages.update_one(
                {"_id": page_id},
                {"$inc": {"view_count": 1}}
            )
            
            # Update daily analytics
            await self._update_daily_analytics(page_id, "page_view", current_time)
            
            return {
                "visit_id": visit_id,
                "page_id": page_id,
                "tracked_at": current_time
            }
            
        except Exception as e:
            raise Exception(f"Failed to track page visit: {str(e)}")

    async def track_link_click(self, link_id: str, visitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """CREATE: Track link click with real data"""
        try:
            click_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Get link info
            link = await self.bio_links.find_one({"_id": link_id})
            if not link:
                raise Exception("Bio link not found")
            
            # Create click record
            click_doc = {
                "_id": click_id,
                "link_id": link_id,
                "page_id": link["page_id"],
                "ip_address": visitor_data.get("ip_address", ""),
                "user_agent": visitor_data.get("user_agent", ""),
                "referrer": visitor_data.get("referrer", ""),
                "country": visitor_data.get("country", ""),
                "city": visitor_data.get("city", ""),
                "device": visitor_data.get("device", ""),
                "browser": visitor_data.get("browser", ""),
                "clicked_at": current_time
            }
            
            # Insert click record
            await self.bio_link_clicks.insert_one(click_doc)
            
            # Update link click count
            await self.bio_links.update_one(
                {"_id": link_id},
                {"$inc": {"click_count": 1}}
            )
            
            # Update page click count
            await self.bio_pages.update_one(
                {"_id": link["page_id"]},
                {"$inc": {"click_count": 1}}
            )
            
            # Update daily analytics
            await self._update_daily_analytics(link["page_id"], "link_click", current_time)
            
            return {
                "click_id": click_id,
                "link_id": link_id,
                "page_id": link["page_id"],
                "tracked_at": current_time
            }
            
        except Exception as e:
            raise Exception(f"Failed to track link click: {str(e)}")

    # Helper methods for real data processing
    async def _generate_unique_slug(self, title: str) -> str:
        """Generate unique slug for bio page"""
        import re
        base_slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
        
        # Check if slug exists
        existing = await self.bio_pages.find_one({"slug": base_slug})
        if not existing:
            return base_slug
        
        # Generate unique slug with number
        counter = 1
        while True:
            new_slug = f"{base_slug}-{counter}"
            existing = await self.bio_pages.find_one({"slug": new_slug})
            if not existing:
                return new_slug
            counter += 1

    async def _create_default_links(self, page_id: str, default_links: List[Dict[str, Any]]):
        """Create default links for new page"""
        for i, link_data in enumerate(default_links):
            link_doc = {
                "_id": str(uuid.uuid4()),
                "page_id": page_id,
                "title": link_data.get("title", ""),
                "url": link_data.get("url", ""),
                "type": link_data.get("type", LinkType.URL.value),
                "description": link_data.get("description", ""),
                "icon": link_data.get("icon", ""),
                "order": i + 1,
                "is_active": True,
                "click_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await self.bio_links.insert_one(link_doc)

    async def _generate_qr_code(self, page_id: str, slug: str) -> Dict[str, Any]:
        """Generate real QR code for bio page using qrcode library"""
        try:
            # Generate real QR code using qrcode library
            import qrcode
            import qrcode.image.svg
            import base64
            from io import BytesIO
            
            # Create bio page URL
            bio_url = f"https://mewayz.bio/{slug}"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(bio_url)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for storage
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Store real QR code data
            qr_code_doc = {
                "_id": str(uuid.uuid4()),
                "page_id": page_id,
                "url": bio_url,
                "qr_code_image": img_str,  # Base64 encoded PNG
                "qr_code_format": "PNG",
                "generated_at": datetime.utcnow(),
                "expires_at": None  # QR codes don't expire
            }
            
            await self.bio_qr_codes.insert_one(qr_code_doc)
            
            return qr_code_doc
            
        except Exception as e:
            # Import logger if not already imported
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating QR code: {str(e)}")
            # Fallback: create basic QR code record without image
            qr_code_doc = {
                "_id": str(uuid.uuid4()),
                "page_id": page_id,
                "url": f"https://mewayz.bio/{slug}",
                "qr_code_image": "",
                "qr_code_format": "text",
                "error": str(e),
                "generated_at": datetime.utcnow()
            }
            await self.bio_qr_codes.insert_one(qr_code_doc)
            return qr_code_doc

    async def _initialize_page_analytics(self, page_id: str, user_id: str, workspace_id: str):
        """Initialize analytics for new page"""
        analytics_doc = {
            "_id": str(uuid.uuid4()),
            "page_id": page_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "total_views": 0,
            "total_clicks": 0,
            "unique_visitors": 0,
            "top_countries": [],
            "top_referrers": [],
            "top_devices": [],
            "conversion_rate": 0.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.bio_analytics.insert_one(analytics_doc)

    async def _create_seo_settings(self, page_id: str, seo_data: Dict[str, Any]):
        """Create SEO settings for page"""
        seo_doc = {
            "_id": str(uuid.uuid4()),
            "page_id": page_id,
            "meta_title": seo_data.get("meta_title", ""),
            "meta_description": seo_data.get("meta_description", ""),
            "meta_keywords": seo_data.get("meta_keywords", ""),
            "og_title": seo_data.get("og_title", ""),
            "og_description": seo_data.get("og_description", ""),
            "og_image": seo_data.get("og_image", ""),
            "twitter_card": seo_data.get("twitter_card", "summary"),
            "canonical_url": seo_data.get("canonical_url", ""),
            "robots": seo_data.get("robots", "index,follow"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.bio_seo_settings.insert_one(seo_doc)

    async def _update_seo_settings(self, page_id: str, seo_data: Dict[str, Any]):
        """Update SEO settings for page"""
        await self.bio_seo_settings.update_one(
            {"page_id": page_id},
            {"$set": {**seo_data, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    async def _setup_custom_domain(self, page_id: str, domain: str):
        """Setup custom domain for page"""
        if not domain:
            return
        
        domain_doc = {
            "_id": str(uuid.uuid4()),
            "page_id": page_id,
            "domain": domain,
            "status": "pending",
            "ssl_enabled": False,
            "verification_token": str(uuid.uuid4()),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.bio_custom_domains.insert_one(domain_doc)

    async def _get_page_analytics(self, page_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive page analytics"""
        try:
            # Get basic analytics
            analytics = await self.bio_analytics.find_one({"page_id": page_id})
            if not analytics:
                return {}
            
            # Get recent visitors
            recent_visitors = await self.bio_visitors.find(
                {"page_id": page_id}
            ).sort("visited_at", -1).limit(100).to_list(length=None)
            
            # Get recent clicks
            recent_clicks = await self.bio_link_clicks.find(
                {"page_id": page_id}
            ).sort("clicked_at", -1).limit(100).to_list(length=None)
            
            # Calculate metrics
            total_views = len(recent_visitors)
            total_clicks = len(recent_clicks)
            unique_visitors = len(set(visitor["ip_address"] for visitor in recent_visitors))
            
            # Get top countries
            country_counts = {}
            for visitor in recent_visitors:
                country = visitor.get("country", "Unknown")
                country_counts[country] = country_counts.get(country, 0) + 1
            
            top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Get top referrers
            referrer_counts = {}
            for visitor in recent_visitors:
                referrer = visitor.get("referrer", "Direct")
                referrer_counts[referrer] = referrer_counts.get(referrer, 0) + 1
            
            top_referrers = sorted(referrer_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "page_id": page_id,
                "total_views": total_views,
                "total_clicks": total_clicks,
                "unique_visitors": unique_visitors,
                "conversion_rate": round((total_clicks / max(total_views, 1)) * 100, 2),
                "top_countries": top_countries,
                "top_referrers": top_referrers,
                "recent_visitors": recent_visitors[:20],
                "recent_clicks": recent_clicks[:20]
            }
            
        except Exception as e:
            return {"error": str(e)}

    async def _update_daily_analytics(self, page_id: str, event_type: str, timestamp: datetime):
        """Update daily analytics for page"""
        try:
            date_str = timestamp.strftime("%Y-%m-%d")
            
            # Update or create daily analytics record
            await self.bio_analytics.update_one(
                {"page_id": page_id, "date": date_str},
                {
                    "$inc": {f"events.{event_type}": 1},
                    "$set": {"updated_at": timestamp}
                },
                upsert=True
            )
            
        except Exception as e:
            print(f"Error updating daily analytics: {str(e)}")