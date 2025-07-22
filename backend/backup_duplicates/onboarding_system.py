"""
Onboarding System API
Handles user onboarding, guided setup, and workspace creation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
import uuid

from core.auth import get_current_user
from services.onboarding_service import OnboardingService

router = APIRouter()

# Pydantic Models
class OnboardingProgress(BaseModel):
    current_step: int = 0
    completed_steps: List[int] = []
    data: Dict[str, Any] = {}

class WorkspaceSetup(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    timezone: Optional[str] = "America/New_York"
    selected_goals: List[str] = []
    primary_goal: Optional[str] = None
    selected_plan: Optional[str] = "free"

class TeamMemberInvite(BaseModel):
    email: EmailStr
    role: str = "editor"
    name: Optional[str] = None

class BrandingSetup(BaseModel):
    brand_name: Optional[str] = None
    primary_color: str = "#3B82F6"
    secondary_color: str = "#10B981"
    accent_color: str = "#F59E0B"
    logo_url: Optional[str] = None
    font_family: str = "Inter"

class OnboardingCompletion(BaseModel):
    workspace: WorkspaceSetup
    team_members: List[TeamMemberInvite] = []
    branding: BrandingSetup = BrandingSetup()
    features_to_enable: List[str] = []
    integrations: List[str] = []

# Initialize service
onboarding_service = OnboardingService()

@router.get("/progress")
async def get_onboarding_progress(current_user: dict = Depends(get_current_user)):
    """Get user's onboarding progress"""
    user_id = current_user.get("_id") or current_user.get("id") or str(current_user.get("email", "default-user"))
    return await onboarding_service.get_progress(user_id)

@router.post("/progress")
async def save_onboarding_progress(
    progress: OnboardingProgress,
    current_user: dict = Depends(get_current_user)
):
    """Save user's onboarding progress"""
    user_id = current_user.get("_id") or current_user.get("id") or str(current_user.get("email", "default-user"))
    return await onboarding_service.save_progress(user_id, progress.dict())

@router.get("/steps")
async def get_onboarding_steps(current_user: dict = Depends(get_current_user)):
    """Get available onboarding steps and configuration"""
    
    return {
        "success": True,
        "data": {
            "steps": [
                {
                    "id": 0,
                    "title": "Welcome to Mewayz",
                    "description": "Let's get you set up with your new workspace",
                    "type": "welcome",
                    "required": True,
                    "estimated_time": "1 minute"
                },
                {
                    "id": 1,
                    "title": "Tell Us About Your Business",
                    "description": "Help us personalize your experience",
                    "type": "business_info",
                    "required": True,
                    "estimated_time": "3 minutes",
                    "fields": [
                        {"name": "workspaceName", "type": "text", "required": True},
                        {"name": "industry", "type": "select", "required": True},
                        {"name": "companySize", "type": "select", "required": True},
                        {"name": "description", "type": "textarea", "required": False}
                    ]
                },
                {
                    "id": 2,
                    "title": "What Are Your Goals?",
                    "description": "Select your primary business objectives",
                    "type": "goals_selection",
                    "required": True,
                    "estimated_time": "2 minutes",
                    "options": [
                        {"id": "social_media", "title": "Social Media Management", "description": "Manage and grow your social presence"},
                        {"id": "link_in_bio", "title": "Link in Bio", "description": "Create a professional bio page"},
                        {"id": "ecommerce", "title": "E-commerce", "description": "Sell products online"},
                        {"id": "courses", "title": "Online Courses", "description": "Create and sell educational content"},
                        {"id": "crm", "title": "Customer Management", "description": "Manage customer relationships"},
                        {"id": "email_marketing", "title": "Email Marketing", "description": "Build and engage your audience"},
                        {"id": "analytics", "title": "Business Analytics", "description": "Track and analyze performance"},
                        {"id": "bookings", "title": "Appointment Booking", "description": "Schedule and manage appointments"}
                    ]
                },
                {
                    "id": 3,
                    "title": "Choose Your Plan",
                    "description": "Select the plan that fits your needs",
                    "type": "plan_selection",
                    "required": True,
                    "estimated_time": "2 minutes",
                    "plans": [
                        {
                            "id": "free",
                            "name": "Free",
                            "price": 0,
                            "features": ["Basic features", "1 workspace", "Community support"],
                            "limits": {"users": 1, "projects": 3, "storage": "1GB"}
                        },
                        {
                            "id": "pro",
                            "name": "Professional",
                            "price": 29,
                            "features": ["All features", "5 workspaces", "Priority support", "Advanced analytics"],
                            "limits": {"users": 10, "projects": 50, "storage": "100GB"}
                        },
                        {
                            "id": "enterprise",
                            "name": "Enterprise",
                            "price": 99,
                            "features": ["Unlimited everything", "Custom integrations", "Dedicated support"],
                            "limits": {"users": "unlimited", "projects": "unlimited", "storage": "unlimited"}
                        }
                    ]
                },
                {
                    "id": 4,
                    "title": "Customize Your Brand",
                    "description": "Set up your brand colors and style",
                    "type": "branding",
                    "required": False,
                    "estimated_time": "3 minutes",
                    "fields": [
                        {"name": "brandName", "type": "text", "required": False},
                        {"name": "primaryColor", "type": "color", "required": False},
                        {"name": "secondaryColor", "type": "color", "required": False},
                        {"name": "logo", "type": "file", "required": False}
                    ]
                },
                {
                    "id": 5,
                    "title": "Invite Your Team",
                    "description": "Add team members to collaborate",
                    "type": "team_setup",
                    "required": False,
                    "estimated_time": "2 minutes",
                    "fields": [
                        {"name": "teamMembers", "type": "array", "required": False}
                    ]
                },
                {
                    "id": 6,
                    "title": "Connect Integrations",
                    "description": "Connect your favorite tools and services",
                    "type": "integrations",
                    "required": False,
                    "estimated_time": "5 minutes",
                    "integrations": [
                        {"id": "google_analytics", "name": "Google Analytics", "category": "analytics"},
                        {"id": "mailchimp", "name": "Mailchimp", "category": "email"},
                        {"id": "stripe", "name": "Stripe", "category": "payments"},
                        {"id": "shopify", "name": "Shopify", "category": "ecommerce"},
                        {"id": "slack", "name": "Slack", "category": "communication"},
                        {"id": "zapier", "name": "Zapier", "category": "automation"}
                    ]
                },
                {
                    "id": 7,
                    "title": "All Set!",
                    "description": "Your workspace is ready to use",
                    "type": "completion",
                    "required": True,
                    "estimated_time": "1 minute"
                }
            ],
            "total_steps": 8,
            "estimated_total_time": "15-20 minutes"
        }
    }

@router.get("/recommendations")
async def get_recommendations(current_user: dict = Depends(get_current_user)):
    """Get personalized recommendations based on user data"""
    
    return {
        "success": True,
        "data": {
            "feature_recommendations": [
                {
                    "feature": "social_media",
                    "title": "Social Media Management",
                    "description": "Based on your industry, social media presence is crucial",
                    "priority": "high",
                    "setup_time": "10 minutes",
                    "benefits": ["Increase brand awareness", "Engage with customers", "Drive traffic"]
                },
                {
                    "feature": "email_marketing",
                    "title": "Email Marketing",
                    "description": "Build and nurture your customer relationships",
                    "priority": "medium",
                    "setup_time": "5 minutes",
                    "benefits": ["Higher ROI", "Direct communication", "Customer retention"]
                },
                {
                    "feature": "analytics",
                    "title": "Business Analytics",
                    "description": "Track your performance and make data-driven decisions",
                    "priority": "medium",
                    "setup_time": "3 minutes",
                    "benefits": ["Better insights", "Performance tracking", "ROI measurement"]
                }
            ],
            "integration_recommendations": [
                {
                    "service": "Google Analytics",
                    "description": "Essential for tracking website performance",
                    "category": "analytics",
                    "difficulty": "easy"
                },
                {
                    "service": "Mailchimp",
                    "description": "Popular email marketing platform",
                    "category": "email_marketing",
                    "difficulty": "easy"
                },
                {
                    "service": "Stripe",
                    "description": "Secure payment processing",
                    "category": "payments",
                    "difficulty": "medium"
                }
            ],
            "template_recommendations": [
                {
                    "name": "Professional Services Website",
                    "description": "Perfect for service-based businesses",
                    "category": "website",
                    "popularity": 95
                },
                {
                    "name": "E-commerce Store",
                    "description": "Start selling products online",
                    "category": "ecommerce",
                    "popularity": 88
                },
                {
                    "name": "Course Platform",
                    "description": "Create and sell online courses",
                    "category": "education",
                    "popularity": 76
                }
            ]
        }
    }

@router.post("/complete")
async def complete_onboarding(
    completion_data: OnboardingCompletion,
    current_user: dict = Depends(get_current_user)
):
    """Complete the onboarding process and create workspace"""
    user_id = current_user.get("_id") or current_user.get("id") or str(current_user.get("email", "default-user"))
    return await onboarding_service.complete_onboarding(user_id, completion_data.dict())

@router.get("/checklist")
async def get_setup_checklist(current_user: dict = Depends(get_current_user)):
    """Get post-onboarding setup checklist"""
    
    return {
        "success": True,
        "data": {
            "checklist": [
                {
                    "id": "profile_complete",
                    "title": "Complete Your Profile",
                    "description": "Add profile picture and bio",
                    "completed": await service.get_status(),
                    "priority": "high",
                    "estimated_time": "2 minutes",
                    "action_url": "/profile/edit"
                },
                {
                    "id": "first_content",
                    "title": "Create Your First Content",
                    "description": "Publish your first post or page",
                    "completed": await service.get_status(),
                    "priority": "high",
                    "estimated_time": "10 minutes",
                    "action_url": "/content/create"
                },
                {
                    "id": "customize_theme",
                    "title": "Customize Your Theme",
                    "description": "Personalize colors and layout",
                    "completed": await service.get_status(),
                    "priority": "medium",
                    "estimated_time": "5 minutes",
                    "action_url": "/settings/theme"
                },
                {
                    "id": "setup_analytics",
                    "title": "Set Up Analytics",
                    "description": "Connect Google Analytics or similar",
                    "completed": await service.get_status(),
                    "priority": "medium",
                    "estimated_time": "5 minutes",
                    "action_url": "/integrations/analytics"
                },
                {
                    "id": "invite_team",
                    "title": "Invite Team Members",
                    "description": "Add collaborators to your workspace",
                    "completed": await service.get_status(),
                    "priority": "low",
                    "estimated_time": "3 minutes",
                    "action_url": "/team/invite"
                },
                {
                    "id": "explore_features",
                    "title": "Explore Advanced Features",
                    "description": "Take a tour of premium features",
                    "completed": await service.get_status(),
                    "priority": "low",
                    "estimated_time": "15 minutes",
                    "action_url": "/features/tour"
                }
            ],
            "completion_stats": {
                "completed": await service.get_metric(),
                "total": 6,
                "progress_percentage": await service.get_metric()
            },
            "next_recommended_action": {
                "title": "Complete Your Profile",
                "description": "Adding a profile picture and bio helps build trust with your audience",
                "action_url": "/profile/edit"
            }
        }
    }

@router.get("/tour")
async def get_guided_tour(current_user: dict = Depends(get_current_user)):
    """Get guided tour steps for the platform"""
    
    return {
        "success": True,
        "data": {
            "tour_steps": [
                {
                    "id": "dashboard",
                    "title": "Welcome to Your Dashboard",
                    "description": "This is your command center. Here you can see all your important metrics and recent activity.",
                    "target": "#dashboard-overview",
                    "position": "bottom",
                    "action": "highlight"
                },
                {
                    "id": "navigation",
                    "title": "Navigation Menu",
                    "description": "Use this menu to access all platform features. Your most-used features will appear at the top.",
                    "target": "#main-navigation",
                    "position": "right",
                    "action": "highlight"
                },
                {
                    "id": "workspace_switcher",
                    "title": "Workspace Switcher",
                    "description": "If you have multiple workspaces, you can switch between them here.",
                    "target": "#workspace-switcher",
                    "position": "bottom",
                    "action": "click"
                },
                {
                    "id": "create_content",
                    "title": "Create Your First Content",
                    "description": "Click here to create your first post, page, or other content.",
                    "target": "#create-button",
                    "position": "left",
                    "action": "pulse"
                },
                {
                    "id": "analytics",
                    "title": "Analytics & Insights",
                    "description": "Track your performance and growth with detailed analytics and reports.",
                    "target": "#analytics-section",
                    "position": "top",
                    "action": "highlight"
                },
                {
                    "id": "settings",
                    "title": "Settings & Configuration",
                    "description": "Customize your workspace, manage team members, and configure integrations here.",
                    "target": "#settings-menu",
                    "position": "left",
                    "action": "highlight"
                },
                {
                    "id": "help",
                    "title": "Need Help?",
                    "description": "Access documentation, tutorials, and support whenever you need assistance.",
                    "target": "#help-center",
                    "position": "top",
                    "action": "bounce"
                }
            ],
            "tour_settings": {
                "show_progress": True,
                "allow_skip": True,
                "auto_advance": False,
                "highlight_color": "#3B82F6",
                "overlay_opacity": 0.5
            }
        }
    }

@router.post("/skip")
async def skip_onboarding(current_user: dict = Depends(get_current_user)):
    """Skip onboarding and create basic workspace"""
    return await onboarding_service.skip_onboarding(current_user["id"])

@router.get("/templates")
async def get_onboarding_templates(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get available workspace templates for onboarding"""
    
    templates = [
        {
            "id": "professional_services",
            "name": "Professional Services",
            "description": "Perfect for consultants, agencies, and service providers",
            "category": "business",
            "preview_image": "/templates/professional-services.jpg",
            "features": ["Contact forms", "Service pages", "Testimonials", "Portfolio"],
            "popularity": 95,
            "setup_time": "15 minutes"
        },
        {
            "id": "ecommerce_store",
            "name": "E-commerce Store",
            "description": "Start selling products online immediately",
            "category": "ecommerce",
            "preview_image": "/templates/ecommerce-store.jpg",
            "features": ["Product catalog", "Shopping cart", "Payment processing", "Inventory management"],
            "popularity": 88,
            "setup_time": "25 minutes"
        },
        {
            "id": "creator_portfolio",
            "name": "Creator Portfolio",
            "description": "Showcase your work and build your personal brand",
            "category": "portfolio",
            "preview_image": "/templates/creator-portfolio.jpg",
            "features": ["Image galleries", "Video embeds", "Social links", "Contact forms"],
            "popularity": 82,
            "setup_time": "10 minutes"
        },
        {
            "id": "course_platform",
            "name": "Online Course Platform",
            "description": "Create and sell educational content",
            "category": "education",
            "preview_image": "/templates/course-platform.jpg",
            "features": ["Course builder", "Student dashboard", "Progress tracking", "Certificates"],
            "popularity": 76,
            "setup_time": "30 minutes"
        },
        {
            "id": "restaurant_menu",
            "name": "Restaurant & Menu",
            "description": "Digital menu and online ordering system",
            "category": "restaurant",
            "preview_image": "/templates/restaurant-menu.jpg",
            "features": ["Digital menu", "Online ordering", "Table reservations", "Reviews"],
            "popularity": 71,
            "setup_time": "20 minutes"
        },
        {
            "id": "nonprofit_organization",
            "name": "Nonprofit Organization",
            "description": "Raise awareness and collect donations",
            "category": "nonprofit",
            "preview_image": "/templates/nonprofit-org.jpg",
            "features": ["Donation forms", "Event calendar", "Volunteer signup", "Impact stories"],
            "popularity": 64,
            "setup_time": "20 minutes"
        }
    ]
    
    # Filter by category if specified
    if category:
        templates = [t for t in templates if t["category"] == category]
    
    return {
        "success": True,
        "data": {
            "templates": templates,
            "categories": ["business", "ecommerce", "portfolio", "education", "restaurant", "nonprofit"],
            "popular_templates": sorted(templates, key=lambda x: x["popularity"], reverse=True)[:3]
        }
    }

@router.post("/feedback")
async def submit_onboarding_feedback(
    feedback_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit feedback about onboarding experience"""
    return await onboarding_service.submit_feedback(current_user["id"], feedback_data)