"""
AI Content Generation API
Handles AI-powered content creation, conversations, and optimization
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

from core.auth import get_current_user
from services.ai_content_service import AIContentService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

# Pydantic Models
class ContentGenerationRequest(BaseModel):
    type: str  # "blog_post", "product_description", "social_post", "email", "ad_copy"
    prompt: str = Field(..., min_length=10)
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"  # "short", "medium", "long"
    keywords: List[str] = []
    target_audience: Optional[str] = None
    additional_context: Optional[str] = None

class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    model: Optional[str] = "gpt-4"
    system_prompt: Optional[str] = None

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    role: Optional[str] = "user"

class SEOOptimizationRequest(BaseModel):
    content: str = Field(..., min_length=50)
    target_keywords: List[str]
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=10)
    style: Optional[str] = "realistic"  # "realistic", "artistic", "cartoon", "professional"
    size: Optional[str] = "1024x1024"  # "512x512", "1024x1024", "1024x1792"
    quality: Optional[str] = "standard"  # "standard", "hd"

# Initialize service
ai_service = AIContentService()

@router.get("/services")
async def get_ai_services(current_user: dict = Depends(get_current_user)):
    """Get available AI services and pricing"""
    
    return {
        "success": True,
        "data": {
            "services": [
                {
                    "id": "content-generation",
                    "name": "AI Content Generation",
                    "description": "Generate high-quality content using advanced AI models",
                    "features": [
                        "Blog posts and articles",
                        "Product descriptions",
                        "Social media content",
                        "Email campaigns",
                        "Ad copy and marketing materials"
                    ],
                    "models": ["gpt-4", "gpt-3.5-turbo", "claude-3"],
                    "pricing": {
                        "free": {"tokens": 10000, "requests": 50},
                        "pro": {"tokens": 100000, "requests": 500},
                        "enterprise": {"tokens": "unlimited", "requests": "unlimited"}
                    },
                    "token_cost": 5,
                    "status": "active"
                },
                {
                    "id": "seo-optimization",
                    "name": "SEO Content Optimizer",
                    "description": "Optimize content for better search engine rankings",
                    "features": [
                        "Keyword analysis and integration",
                        "Meta descriptions generation",
                        "Content scoring and recommendations",
                        "Competitor analysis",
                        "Search intent optimization"
                    ],
                    "models": ["claude-3", "gpt-4"],
                    "pricing": {
                        "free": {"optimizations": 5},
                        "pro": {"optimizations": 50},
                        "enterprise": {"optimizations": "unlimited"}
                    },
                    "token_cost": 3,
                    "status": "active"
                },
                {
                    "id": "image-generation",
                    "name": "AI Image Generator",
                    "description": "Create stunning images and artwork using AI",
                    "features": [
                        "Custom artwork generation",
                        "Product images and mockups",
                        "Social media graphics",
                        "Brand illustrations",
                        "Marketing visuals"
                    ],
                    "models": ["dall-e-3", "midjourney", "stable-diffusion"],
                    "pricing": {
                        "free": {"images": 3},
                        "pro": {"images": 25},
                        "enterprise": {"images": "unlimited"}
                    },
                    "token_cost": 10,
                    "status": "active"
                },
                {
                    "id": "conversation-ai",
                    "name": "AI Conversation Assistant",
                    "description": "Interactive AI assistant for brainstorming and problem-solving",
                    "features": [
                        "Multi-turn conversations",
                        "Context-aware responses",
                        "Custom system prompts",
                        "Conversation history",
                        "Export and sharing"
                    ],
                    "models": ["gpt-4", "claude-3", "gemini-pro"],
                    "pricing": {
                        "free": {"messages": 100},
                        "pro": {"messages": 1000},
                        "enterprise": {"messages": "unlimited"}
                    },
                    "token_cost": 2,
                    "status": "active"
                }
            ],
            "usage_stats": {
                "current_period_usage": await service.get_metric(),
                "remaining_tokens": await service.get_metric(),
                "plan_limits": {
                    "content_generation": await service.get_metric(),
                    "seo_optimization": await service.get_metric(),
                    "image_generation": await service.get_metric()
                }
            }
        }
    }

@router.post("/generate-content")
async def generate_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI content based on request"""
    return await ai_service.generate_content(current_user.get("_id") or current_user.get("id", "default-user"), request.dict())

@router.post("/optimize-seo")
async def optimize_seo_content(
    request: SEOOptimizationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Optimize content for SEO"""
    return await ai_service.optimize_seo(current_user.get("_id") or current_user.get("id", "default-user"), request.dict())

@router.post("/generate-image")
async def generate_image(
    request: ImageGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI images"""
    return await ai_service.generate_image(current_user.get("_id") or current_user.get("id", "default-user"), request.dict())

@router.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    """Get user's AI conversations"""
    return await ai_service.get_conversations(current_user.get("_id") or current_user.get("id", "default-user"))

@router.post("/conversations")
async def create_conversation(
    conversation: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new AI conversation"""
    return await ai_service.create_conversation(current_user.get("_id") or current_user.get("id", "default-user"), conversation.dict())

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific conversation with messages"""
    return await ai_service.get_conversation(current_user.get("_id") or current_user.get("id", "default-user"), conversation_id)

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Send message in conversation"""
    return await ai_service.send_message(current_user.get("_id") or current_user.get("id", "default-user"), conversation_id, message.dict())

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete conversation"""
    return await ai_service.delete_conversation(current_user.get("_id") or current_user.get("id", "default-user"), conversation_id)

@router.get("/content-templates")
async def get_content_templates(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get AI content generation templates"""
    
    templates = [
        {
            "id": "blog-post-outline",
            "name": "Blog Post Outline",
            "category": "blog",
            "description": "Create comprehensive blog post outlines with H2/H3 structure",
            "prompt_template": "Create a detailed blog post outline for: {topic}. Include engaging H2 and H3 headings, key points to cover, and suggested word count for each section.",
            "variables": ["topic", "target_audience", "keywords"],
            "estimated_tokens": 300,
            "use_count": 1247
        },
        {
            "id": "product-description",
            "name": "Product Description",
            "category": "ecommerce",
            "description": "Generate compelling product descriptions that convert",
            "prompt_template": "Write a compelling product description for: {product_name}. Highlight key features: {features}, target audience: {audience}, and include a strong call-to-action.",
            "variables": ["product_name", "features", "audience", "price_point"],
            "estimated_tokens": 200,
            "use_count": 2156
        },
        {
            "id": "social-media-post",
            "name": "Social Media Post",
            "category": "social",
            "description": "Create engaging social media content for various platforms",
            "prompt_template": "Create an engaging {platform} post about: {topic}. Tone: {tone}, include relevant hashtags and call-to-action. Character limit: {char_limit}",
            "variables": ["platform", "topic", "tone", "char_limit"],
            "estimated_tokens": 150,
            "use_count": 3421
        },
        {
            "id": "email-campaign",
            "name": "Email Campaign",
            "category": "email",
            "description": "Write effective email campaigns that drive engagement",
            "prompt_template": "Write an email campaign for {campaign_type} with subject line and body. Goal: {goal}, audience: {audience}, tone: {tone}",
            "variables": ["campaign_type", "goal", "audience", "tone"],
            "estimated_tokens": 250,
            "use_count": 987
        },
        {
            "id": "ad-copy",
            "name": "Advertisement Copy",
            "category": "advertising",
            "description": "Generate high-converting ad copy for various platforms",
            "prompt_template": "Create compelling ad copy for {product_service} targeting {audience}. Platform: {platform}, goal: {goal}, budget considerations: {budget}",
            "variables": ["product_service", "audience", "platform", "goal", "budget"],
            "estimated_tokens": 180,
            "use_count": 1534
        },
        {
            "id": "landing-page-copy",
            "name": "Landing Page Copy",
            "category": "website",
            "description": "Write persuasive landing page copy that converts visitors",
            "prompt_template": "Write landing page copy for {product_service}. Include headline, subheadline, benefits section, features, testimonials placeholder, and strong CTA. Target: {audience}",
            "variables": ["product_service", "audience", "unique_value_prop"],
            "estimated_tokens": 400,
            "use_count": 756
        }
    ]
    
    # Filter by category if provided
    if category:
        templates = [t for t in templates if t["category"] == category]
    
    return {
        "success": True,
        "data": {
            "templates": templates,
            "categories": ["blog", "ecommerce", "social", "email", "advertising", "website"],
            "total": len(templates)
        }
    }

@router.post("/content-templates/{template_id}/generate")
async def generate_from_template(
    template_id: str,
    variables: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Generate content using template"""
    return await ai_service.generate_from_template(current_user.get("_id") or current_user.get("id", "default-user"), template_id, variables)

@router.get("/analytics")
async def get_ai_usage_analytics(
    period: str = "30d",
    current_user: dict = Depends(get_current_user)
):
    """Get AI service usage analytics"""
    
    days = 30 if period == "30d" else (7 if period == "7d" else 90)
    
    return {
        "success": True,
        "data": {
            "overview": {
                "total_requests": await service.get_metric(),
                "total_tokens_used": await service.get_metric(),
                "total_cost": round(await service.get_metric(), 2),
                "average_request_size": await service.get_metric(),
                "success_rate": round(await service.get_metric(), 1),
                "favorite_service": await service.get_status()
            },
            "usage_trends": [
                {
                    "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "requests": await service.get_metric(),
                    "tokens": await service.get_metric(),
                    "cost": round(await service.get_metric(), 2)
                } for i in range(days, 0, -1)
            ],
            "service_breakdown": {
                "content_generation": {
                    "requests": await service.get_metric(),
                    "tokens": await service.get_metric(),
                    "cost": round(await service.get_metric(), 2),
                    "avg_quality_score": round(await service.get_metric(), 1)
                },
                "seo_optimization": {
                    "requests": await service.get_metric(),
                    "tokens": await service.get_metric(),
                    "cost": round(await service.get_metric(), 2),
                    "avg_quality_score": round(await service.get_metric(), 1)
                },
                "image_generation": {
                    "requests": await service.get_metric(),
                    "tokens": await service.get_metric(),
                    "cost": round(await service.get_metric(), 2),
                    "avg_quality_score": round(await service.get_metric(), 1)
                },
                "conversations": {
                    "requests": await service.get_metric(),
                    "tokens": await service.get_metric(),
                    "cost": round(await service.get_metric(), 2),
                    "avg_quality_score": round(await service.get_metric(), 1)
                }
            },
            "content_categories": [
                {"category": "Blog Posts", "count": await service.get_metric(), "tokens": await service.get_metric()},
                {"category": "Product Descriptions", "count": await service.get_metric(), "tokens": await service.get_metric()},
                {"category": "Social Media", "count": await service.get_metric(), "tokens": await service.get_metric()},
                {"category": "Email Campaigns", "count": await service.get_metric(), "tokens": await service.get_metric()},
                {"category": "Ad Copy", "count": await service.get_metric(), "tokens": await service.get_metric()}
            ],
            "quality_metrics": {
                "user_satisfaction": round(await service.get_metric(), 1),
                "content_approval_rate": round(await service.get_metric(), 1),
                "revision_rate": round(await service.get_metric(), 1),
                "time_saved": f"{await service.get_metric()} hours"
            }
        }
    }

@router.get("/models")
async def get_available_models(current_user: dict = Depends(get_current_user)):
    """Get available AI models and their capabilities"""
    
    return {
        "success": True,
        "data": {
            "models": [
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "provider": "OpenAI",
                    "description": "Most advanced language model for complex tasks",
                    "capabilities": ["Text generation", "Code writing", "Analysis", "Creative writing"],
                    "max_tokens": 8192,
                    "cost_per_1k_tokens": 0.03,
                    "speed": "Medium",
                    "quality": "Excellent",
                    "best_for": ["Complex analysis", "Professional writing", "Code generation"],
                    "status": "active"
                },
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "provider": "OpenAI",
                    "description": "Fast and efficient for most content generation tasks",
                    "capabilities": ["Text generation", "Summarization", "Translation", "Q&A"],
                    "max_tokens": 4096,
                    "cost_per_1k_tokens": 0.002,
                    "speed": "Fast",
                    "quality": "Good",
                    "best_for": ["Quick content", "Social media", "Product descriptions"],
                    "status": "active"
                },
                {
                    "id": "claude-3",
                    "name": "Claude 3",
                    "provider": "Anthropic",
                    "description": "Advanced model with strong reasoning capabilities",
                    "capabilities": ["Analysis", "Research", "Long-form content", "Code review"],
                    "max_tokens": 100000,
                    "cost_per_1k_tokens": 0.025,
                    "speed": "Medium",
                    "quality": "Excellent",
                    "best_for": ["Research", "Long articles", "Technical analysis"],
                    "status": "active"
                },
                {
                    "id": "dall-e-3",
                    "name": "DALL-E 3",
                    "provider": "OpenAI",
                    "description": "State-of-the-art image generation model",
                    "capabilities": ["Image generation", "Artwork creation", "Product mockups"],
                    "max_resolution": "1024x1792",
                    "cost_per_image": 0.04,
                    "speed": "Medium",
                    "quality": "Excellent",
                    "best_for": ["Marketing visuals", "Product images", "Creative artwork"],
                    "status": "active"
                }
            ]
        }
    }

@router.post("/batch-generate")
async def batch_generate_content(
    requests: List[ContentGenerationRequest],
    current_user: dict = Depends(get_current_user)
):
    """Generate multiple content pieces in batch"""
    return await ai_service.batch_generate(current_user.get("_id") or current_user.get("id", "default-user"), [req.dict() for req in requests])

@router.get("/inspiration")
async def get_content_inspiration(
    category: Optional[str] = None,
    industry: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get content inspiration and ideas"""
    
    return {
        "success": True,
        "data": {
            "trending_topics": [
                {"topic": "AI in Small Business", "trend_score": 95, "difficulty": "Medium"},
                {"topic": "Sustainable Marketing", "trend_score": 88, "difficulty": "Easy"},
                {"topic": "Remote Work Tools", "trend_score": 82, "difficulty": "Easy"},
                {"topic": "Customer Experience Innovation", "trend_score": 79, "difficulty": "Hard"},
                {"topic": "Digital Transformation", "trend_score": 76, "difficulty": "Medium"}
            ],
            "content_ideas": [
                {
                    "title": "10 AI Tools Every Small Business Should Know About",
                    "type": "blog_post",
                    "estimated_length": "1500 words",
                    "target_keywords": ["AI tools", "small business", "automation"],
                    "difficulty": "Medium"
                },
                {
                    "title": "How to Create Sustainable Marketing Campaigns",
                    "type": "guide",
                    "estimated_length": "2000 words",
                    "target_keywords": ["sustainable marketing", "green business", "eco-friendly"],
                    "difficulty": "Easy"
                },
                {
                    "title": "The Future of Remote Work: Tools and Trends",
                    "type": "analysis",
                    "estimated_length": "1200 words",
                    "target_keywords": ["remote work", "digital tools", "productivity"],
                    "difficulty": "Medium"
                }
            ],
            "seasonal_content": [
                {"season": "Holiday Season", "content_types": ["gift guides", "promotions", "year-end reviews"]},
                {"season": "New Year", "content_types": ["resolutions", "planning", "goal-setting"]},
                {"season": "Spring", "content_types": ["renewal", "growth", "fresh starts"]}
            ]
        }
    }