"""
Support System API
Comprehensive customer support, help desk, and customer service features
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

from core.auth import get_current_user
from services.support_service import SupportService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

# Pydantic Models
class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=5)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=1)
    priority: str = "medium"
    urgency: str = "normal"

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    internal_notes: Optional[str] = None

class KnowledgeArticle(BaseModel):
    title: str = Field(..., min_length=5)
    content: str = Field(..., min_length=20)
    category: str
    tags: List[str] = []
    difficulty_level: str = "beginner"

# Initialize service
support_service = SupportService()

@router.get("/tickets")
async def get_support_tickets(
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get user's support tickets with filtering"""
    return await support_service.get_user_tickets(
        current_user.get("_id") or current_user.get("id", "default-user"), status, category, priority, limit
    )

@router.post("/tickets/create")
async def create_support_ticket(
    ticket_data: TicketCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new support ticket"""
    return await support_service.create_ticket(current_user.get("_id") or current_user.get("id", "default-user"), ticket_data.dict())

@router.get("/tickets/{ticket_id}")
async def get_ticket_details(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed ticket information"""
    return await support_service.get_ticket_details(current_user.get("_id") or current_user.get("id", "default-user"), ticket_id)

@router.put("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    update_data: TicketUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update ticket information"""
    return await support_service.update_ticket(current_user.get("_id") or current_user.get("id", "default-user"), ticket_id, update_data.dict())

@router.post("/tickets/{ticket_id}/messages")
async def add_ticket_message(
    ticket_id: str,
    message: str = Form(...),
    attachment: Optional[UploadFile] = File(None),
    is_internal: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):
    """Add message to support ticket"""
    return await support_service.add_ticket_message(
        current_user["id"], ticket_id, message, attachment, is_internal
    )

@router.get("/dashboard")
async def get_support_dashboard(current_user: dict = Depends(get_current_user)):
    """Get support system dashboard"""
    return await support_service.get_support_dashboard(current_user["id"])

@router.get("/categories")
async def get_support_categories(current_user: dict = Depends(get_current_user)):
    """Get available support categories"""
    
    return {
        "success": True,
        "data": {
            "categories": [
                {
                    "id": "technical",
                    "name": "Technical Support",
                    "description": "Issues with platform functionality, bugs, and technical problems",
                    "average_resolution_time": "4-8 hours",
                    "escalation_level": 2,
                    "common_issues": ["Login problems", "Feature not working", "Performance issues"]
                },
                {
                    "id": "billing",
                    "name": "Billing & Payments",
                    "description": "Subscription, payment, refund, and billing related inquiries",
                    "average_resolution_time": "2-4 hours",
                    "escalation_level": 1,
                    "common_issues": ["Payment failed", "Subscription changes", "Invoice questions"]
                },
                {
                    "id": "account",
                    "name": "Account Management",
                    "description": "Account settings, profile, security, and access issues",
                    "average_resolution_time": "1-2 hours",
                    "escalation_level": 1,
                    "common_issues": ["Password reset", "Account verification", "Profile updates"]
                },
                {
                    "id": "feature_request",
                    "name": "Feature Requests",
                    "description": "Suggestions for new features or improvements",
                    "average_resolution_time": "1-2 weeks",
                    "escalation_level": 3,
                    "common_issues": ["New feature idea", "Enhancement request", "Integration needs"]
                },
                {
                    "id": "integration",
                    "name": "Integrations",
                    "description": "Third-party integrations and API related questions",
                    "average_resolution_time": "6-12 hours",
                    "escalation_level": 2,
                    "common_issues": ["API setup", "Integration troubleshooting", "Webhook issues"]
                },
                {
                    "id": "training",
                    "name": "Training & Onboarding",
                    "description": "Help with learning the platform and best practices",
                    "average_resolution_time": "30 minutes - 2 hours",
                    "escalation_level": 1,
                    "common_issues": ["How-to questions", "Best practices", "Training materials"]
                }
            ],
            "priority_levels": [
                {"level": "low", "name": "Low Priority", "sla": "48 hours", "description": "General questions, non-urgent issues"},
                {"level": "medium", "name": "Medium Priority", "sla": "24 hours", "description": "Standard issues affecting workflow"},
                {"level": "high", "name": "High Priority", "sla": "8 hours", "description": "Urgent issues affecting business operations"},
                {"level": "critical", "name": "Critical", "sla": "2 hours", "description": "System down, security issues, data loss"}
            ]
        }
    }

@router.get("/knowledge-base")
async def get_knowledge_base(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get knowledge base articles"""
    return await support_service.get_knowledge_base(current_user["id"], category, search, limit)

@router.get("/knowledge-base/{article_id}")
async def get_knowledge_article(
    article_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific knowledge base article"""
    return await support_service.get_knowledge_article(current_user["id"], article_id)

@router.get("/faq")
async def get_frequently_asked_questions(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get frequently asked questions"""
    
    faqs = [
        {
            "id": "faq_001",
            "question": "How do I reset my password?",
            "answer": "You can reset your password by clicking 'Forgot Password' on the login page and following the email instructions.",
            "category": "account",
            "views": await service.get_metric(),
            "helpful_votes": await service.get_metric(),
            "last_updated": (datetime.now() - timedelta(days=await service.get_metric())).isoformat()
        },
        {
            "id": "faq_002", 
            "question": "How do I upgrade my subscription?",
            "answer": "Go to Settings > Billing and click 'Upgrade Plan' to select a higher tier subscription.",
            "category": "billing",
            "views": await service.get_metric(),
            "helpful_votes": await service.get_metric(),
            "last_updated": (datetime.now() - timedelta(days=await service.get_metric())).isoformat()
        },
        {
            "id": "faq_003",
            "question": "How do I integrate with third-party services?",
            "answer": "Visit the Integrations page in your dashboard and follow the setup guide for your desired service.",
            "category": "integration",
            "views": await service.get_metric(),
            "helpful_votes": await service.get_metric(),
            "last_updated": (datetime.now() - timedelta(days=await service.get_metric())).isoformat()
        },
        {
            "id": "faq_004",
            "question": "What AI features are available?",
            "answer": "Our platform offers content generation, image creation, voice synthesis, and automated workflows powered by AI.",
            "category": "technical",
            "views": await service.get_metric(),
            "helpful_votes": await service.get_metric(),
            "last_updated": (datetime.now() - timedelta(days=await service.get_metric())).isoformat()
        },
        {
            "id": "faq_005",
            "question": "How do I export my data?",
            "answer": "Data export is available in Settings > Data Management. You can export in various formats including CSV and JSON.",
            "category": "technical",
            "views": await service.get_metric(),
            "helpful_votes": await service.get_metric(),
            "last_updated": (datetime.now() - timedelta(days=await service.get_metric())).isoformat()
        }
    ]
    
    if category:
        faqs = [f for f in faqs if f["category"] == category]
    
    return {
        "success": True,
        "data": {
            "faqs": faqs,
            "total_count": len(faqs),
            "categories": ["account", "billing", "technical", "integration", "general"],
            "most_viewed": sorted(faqs, key=lambda x: x["views"], reverse=True)[:3]
        }
    }

@router.get("/live-chat/status")
async def get_live_chat_status(current_user: dict = Depends(get_current_user)):
    """Get live chat availability status"""
    
    return {
        "success": True,
        "data": {
            "live_chat": {
                "available": True,
                "status": await service.get_status(),
                "average_wait_time": f"{await service.get_metric()} minutes",
                "agents_online": await service.get_metric(),
                "queue_position": await service.get_metric() if await service.get_status() else 0,
                "estimated_response_time": f"{await service.get_metric()} seconds"
            },
            "office_hours": {
                "timezone": "UTC",
                "monday_friday": "9:00 AM - 6:00 PM",
                "saturday": "10:00 AM - 4:00 PM",
                "sunday": "Closed",
                "current_status": "Open" if await service.get_status() else "Closed"
            },
            "alternative_support": {
                "email_support": "24/7 available",
                "community_forum": "Community-driven support",
                "knowledge_base": "Self-service articles",
                "video_tutorials": "Step-by-step guides"
            }
        }
    }

@router.post("/live-chat/initiate")
async def initiate_live_chat(
    message: str = Form(...),
    department: str = Form("general"),
    current_user: dict = Depends(get_current_user)
):
    """Initiate a live chat session"""
    return await support_service.initiate_live_chat(current_user["id"], message, department)

@router.get("/feedback/surveys")
async def get_feedback_surveys(current_user: dict = Depends(get_current_user)):
    """Get available feedback surveys"""
    return await support_service.get_feedback_surveys(current_user["id"])

@router.post("/feedback/submit")
async def submit_feedback(
    survey_id: str = Form(...),
    responses: str = Form(...),  # JSON string of responses
    rating: int = Form(...),
    additional_comments: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Submit feedback survey"""
    return await support_service.submit_feedback(
        current_user["id"], survey_id, responses, rating, additional_comments
    )

@router.get("/analytics/dashboard")
async def get_support_analytics(
    period: str = "monthly",
    current_user: dict = Depends(get_current_user)
):
    """Get support analytics dashboard"""
    return await support_service.get_support_analytics(current_user["id"], period)

@router.get("/escalation/rules")
async def get_escalation_rules(current_user: dict = Depends(get_current_user)):
    """Get support escalation rules and procedures"""
    
    return {
        "success": True,
        "data": {
            "escalation_matrix": [
                {
                    "level": 1,
                    "name": "First Line Support",
                    "description": "General inquiries and common issues",
                    "response_time": "1-4 hours",
                    "capabilities": ["Account help", "Basic technical", "Billing questions"],
                    "escalation_triggers": ["Complex technical issue", "Billing dispute", "Manager request"]
                },
                {
                    "level": 2,
                    "name": "Technical Support",
                    "description": "Advanced technical issues and integrations",
                    "response_time": "2-8 hours",
                    "capabilities": ["API issues", "Integration problems", "Advanced features"],
                    "escalation_triggers": ["System bug", "Data corruption", "Security concern"]
                },
                {
                    "level": 3,
                    "name": "Engineering Team",
                    "description": "System-level issues and development",
                    "response_time": "8-24 hours",
                    "capabilities": ["Bug fixes", "System issues", "Custom development"],
                    "escalation_triggers": ["Critical system failure", "Security breach", "Data loss"]
                },
                {
                    "level": 4,
                    "name": "Management",
                    "description": "Executive-level issues and disputes",
                    "response_time": "24-48 hours",
                    "capabilities": ["Contract disputes", "Refund authorization", "Partnership issues"],
                    "escalation_triggers": ["Legal threat", "Major client complaint", "PR concern"]
                }
            ],
            "automatic_escalation": {
                "enabled": True,
                "rules": [
                    {"condition": "No response in 24 hours", "action": "Escalate to level 2"},
                    {"condition": "Customer reply to unresolved ticket", "action": "Increase priority"},
                    {"condition": "Critical priority ticket", "action": "Immediate escalation"},
                    {"condition": "Multiple tickets from same customer", "action": "Manager notification"}
                ]
            },
            "sla_guidelines": {
                "response_times": {
                    "critical": "2 hours",
                    "high": "8 hours", 
                    "medium": "24 hours",
                    "low": "48 hours"
                },
                "resolution_targets": {
                    "critical": "4 hours",
                    "high": "24 hours",
                    "medium": "72 hours", 
                    "low": "1 week"
                }
            }
        }
    }

@router.get("/system/health")
async def get_support_system_health(current_user: dict = Depends(get_current_user)):
    """Get support system health and status"""
    
    return {
        "success": True,
        "data": {
            "system_status": {
                "overall_health": "Excellent",
                "uptime": "99.98%",
                "last_incident": "2024-11-15T10:30:00Z",
                "response_time": f"{round(await service.get_metric(), 1)} seconds",
                "ticket_processing": "Normal",
                "live_chat": "Available"
            },
            "performance_metrics": {
                "average_first_response": f"{await service.get_metric()} minutes",
                "average_resolution_time": f"{round(await service.get_metric(), 1)} hours",
                "customer_satisfaction": round(await service.get_metric(), 1),
                "first_contact_resolution": f"{round(await service.get_metric(), 1)}%",
                "ticket_backlog": await service.get_metric()
            },
            "team_availability": {
                "agents_online": await service.get_metric(),
                "total_agents": await service.get_metric(),
                "availability_rate": f"{round(await service.get_metric(), 1)}%",
                "current_load": await service.get_status(),
                "peak_hours": "2:00 PM - 5:00 PM UTC"
            },
            "recent_improvements": [
                {
                    "date": "2024-12-01",
                    "improvement": "Added AI-powered ticket routing",
                    "impact": "35% faster initial response time"
                },
                {
                    "date": "2024-11-15", 
                    "improvement": "Enhanced knowledge base search",
                    "impact": "25% reduction in duplicate tickets"
                },
                {
                    "date": "2024-11-01",
                    "improvement": "Implemented proactive monitoring",
                    "impact": "45% reduction in system-related tickets"
                }
            ]
        }
    }

@router.get("/training/materials")
async def get_training_materials(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get training materials and tutorials"""
    return await support_service.get_training_materials(current_user["id"], category, difficulty)

@router.get("/community/forum")
async def get_community_forum_info(current_user: dict = Depends(get_current_user)):
    """Get community forum information and recent topics"""
    return await support_service.get_community_forum_info(current_user["id"])