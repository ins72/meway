"""
Advanced Automation System API
Business process automation, workflows, and intelligent automation features
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
import json

from core.auth import get_current_user
from services.automation_service import AutomationService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

# Pydantic Models
class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=3)
    description: Optional[str] = None
    trigger_type: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool = True

class AutomationRule(BaseModel):
    name: str = Field(..., min_length=3)
    trigger: Dict[str, Any]
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    schedule: Optional[Dict[str, Any]] = None

# Initialize service
automation_service = AutomationService()

@router.get("/workflows/advanced")
async def get_advanced_workflows(current_user: dict = Depends(get_current_user)):
    """Advanced workflow automation system"""
    return await automation_service.get_advanced_workflows(current_user.get("_id") or current_user.get("id", "default-user"))

@router.post("/workflows/create")
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new automation workflow"""
    return await automation_service.create_workflow(current_user.get("_id") or current_user.get("id", "default-user"), workflow_data.dict())

@router.get("/workflows")
async def get_user_workflows(
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's automation workflows with filtering"""
    return await automation_service.get_user_workflows(current_user.get("_id") or current_user.get("id", "default-user"), category, status)

@router.get("/workflows/{workflow_id}")
async def get_workflow_details(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed workflow information"""
    return await automation_service.get_workflow_details(current_user.get("_id") or current_user.get("id", "default-user"), workflow_id)

@router.put("/workflows/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update existing workflow"""
    return await automation_service.update_workflow(current_user.get("_id") or current_user.get("id", "default-user"), workflow_id, workflow_data.dict())

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    execution_data: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Execute workflow manually"""
    return await automation_service.execute_workflow(current_user.get("_id") or current_user.get("id", "default-user"), workflow_id, execution_data)

@router.get("/triggers/available")
async def get_available_triggers(current_user: dict = Depends(get_current_user)):
    """Get available automation triggers"""
    
    return {
        "success": True,
        "data": {
            "trigger_categories": {
                "behavioral_triggers": [
                    {"type": "page_visit", "name": "Page Visit", "description": "Triggered when user visits specific page"},
                    {"type": "form_submission", "name": "Form Submission", "description": "Triggered when user submits form"},
                    {"type": "download_action", "name": "File Download", "description": "Triggered when user downloads file"},
                    {"type": "time_on_site", "name": "Time on Site", "description": "Triggered based on time spent on site"},
                    {"type": "scroll_depth", "name": "Scroll Depth", "description": "Triggered when user scrolls to specific depth"}
                ],
                "temporal_triggers": [
                    {"type": "time_delay", "name": "Time Delay", "description": "Triggered after specified time period"},
                    {"type": "specific_date", "name": "Specific Date", "description": "Triggered on specific date/time"},
                    {"type": "recurring_schedule", "name": "Recurring Schedule", "description": "Triggered on recurring schedule"},
                    {"type": "anniversary", "name": "Anniversary", "description": "Triggered on anniversary dates"},
                    {"type": "seasonal", "name": "Seasonal Trigger", "description": "Triggered during specific seasons/holidays"}
                ],
                "conditional_triggers": [
                    {"type": "if_then_logic", "name": "If/Then Logic", "description": "Complex conditional triggers"},
                    {"type": "custom_field_match", "name": "Custom Field Match", "description": "Triggered when custom field matches criteria"},
                    {"type": "segment_entry", "name": "Segment Entry", "description": "Triggered when user enters specific segment"},
                    {"type": "score_threshold", "name": "Score Threshold", "description": "Triggered when score reaches threshold"},
                    {"type": "multi_condition", "name": "Multi-Condition", "description": "Multiple conditions must be met"}
                ],
                "external_triggers": [
                    {"type": "api_webhook", "name": "API Webhook", "description": "Triggered by external API webhook"},
                    {"type": "third_party_event", "name": "Third-Party Event", "description": "Triggered by external service events"},
                    {"type": "system_integration", "name": "System Integration", "description": "Triggered by system integrations"},
                    {"type": "payment_event", "name": "Payment Event", "description": "Triggered by payment processing events"},
                    {"type": "email_event", "name": "Email Event", "description": "Triggered by email events (open, click, etc.)"}
                ]
            },
            "popular_combinations": [
                {"name": "Lead Nurturing", "triggers": ["form_submission", "time_delay"], "success_rate": 78.5},
                {"name": "Cart Recovery", "triggers": ["cart_abandonment", "time_delay"], "success_rate": 23.4},
                {"name": "Onboarding Flow", "triggers": ["account_creation", "behavioral"], "success_rate": 65.8}
            ]
        }
    }

@router.get("/actions/available")
async def get_available_actions(current_user: dict = Depends(get_current_user)):
    """Get available automation actions"""
    
    return {
        "success": True,
        "data": {
            "action_categories": {
                "communication_actions": [
                    {"type": "send_email", "name": "Send Email", "description": "Send personalized email"},
                    {"type": "send_sms", "name": "Send SMS", "description": "Send SMS message"},
                    {"type": "push_notification", "name": "Push Notification", "description": "Send push notification"},
                    {"type": "in_app_message", "name": "In-App Message", "description": "Display in-app message"},
                    {"type": "slack_notification", "name": "Slack Notification", "description": "Send Slack notification"}
                ],
                "data_actions": [
                    {"type": "update_profile", "name": "Update Profile", "description": "Update user profile data"},
                    {"type": "add_tag", "name": "Add Tag", "description": "Add tag to user"},
                    {"type": "remove_tag", "name": "Remove Tag", "description": "Remove tag from user"},
                    {"type": "update_score", "name": "Update Score", "description": "Update user score"},
                    {"type": "create_task", "name": "Create Task", "description": "Create task in system"}
                ],
                "system_actions": [
                    {"type": "api_call", "name": "API Call", "description": "Make external API call"},
                    {"type": "webhook_trigger", "name": "Webhook Trigger", "description": "Trigger webhook"},
                    {"type": "database_update", "name": "Database Update", "description": "Update database record"},
                    {"type": "file_creation", "name": "File Creation", "description": "Create or update file"},
                    {"type": "system_log", "name": "System Log", "description": "Create system log entry"}
                ],
                "business_actions": [
                    {"type": "create_lead", "name": "Create Lead", "description": "Create new lead in CRM"},
                    {"type": "assign_sales_rep", "name": "Assign Sales Rep", "description": "Assign lead to sales representative"},
                    {"type": "schedule_meeting", "name": "Schedule Meeting", "description": "Schedule meeting or call"},
                    {"type": "generate_quote", "name": "Generate Quote", "description": "Generate price quote"},
                    {"type": "create_invoice", "name": "Create Invoice", "description": "Generate invoice"}
                ]
            }
        }
    }

@router.get("/analytics/dashboard")
async def get_automation_analytics(current_user: dict = Depends(get_current_user)):
    """Get automation analytics dashboard"""
    return await automation_service.get_automation_analytics(current_user.get("_id") or current_user.get("id", "default-user"))

@router.get("/templates")
async def get_workflow_templates(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get pre-built workflow templates"""
    
    templates = [
        {
            "id": "lead_nurturing_template",
            "name": "Lead Nurturing Sequence",
            "category": "sales",
            "description": "Automated lead nurturing with email sequence",
            "triggers": ["form_submission"],
            "actions": ["send_email", "add_tag", "update_score"],
            "estimated_setup": "10 minutes",
            "success_rate": 78.5,
            "usage_count": 1250
        },
        {
            "id": "cart_recovery_template",
            "name": "Abandoned Cart Recovery",
            "category": "ecommerce",
            "description": "Recover abandoned carts with targeted messaging",
            "triggers": ["cart_abandonment"],
            "actions": ["send_email", "push_notification", "discount_offer"],
            "estimated_setup": "15 minutes",
            "success_rate": 23.4,
            "usage_count": 890
        },
        {
            "id": "onboarding_template",
            "name": "Customer Onboarding Flow",
            "category": "customer_success",
            "description": "Complete customer onboarding automation",
            "triggers": ["account_creation"],
            "actions": ["send_welcome_email", "create_tasks", "schedule_check_in"],
            "estimated_setup": "20 minutes",
            "success_rate": 65.8,
            "usage_count": 2100
        },
        {
            "id": "reengagement_template",
            "name": "User Re-engagement Campaign",
            "category": "retention",
            "description": "Re-engage inactive users with personalized content",
            "triggers": ["inactivity_detected"],
            "actions": ["send_personalized_email", "special_offer", "survey"],
            "estimated_setup": "12 minutes",
            "success_rate": 42.7,
            "usage_count": 750
        }
    ]
    
    if category:
        templates = [t for t in templates if t["category"] == category]
    
    return {
        "success": True,
        "data": {
            "templates": templates,
            "categories": ["sales", "ecommerce", "customer_success", "retention", "marketing"],
            "total_templates": len(templates)
        }
    }

@router.post("/templates/{template_id}/install")
async def install_workflow_template(
    template_id: str,
    customization: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Install and customize workflow template"""
    return await automation_service.install_template(current_user.get("_id") or current_user.get("id", "default-user"), template_id, customization)

@router.get("/executions/history")
async def get_execution_history(
    workflow_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get workflow execution history"""
    return await automation_service.get_execution_history(current_user.get("_id") or current_user.get("id", "default-user"), workflow_id, limit)

@router.get("/performance/metrics")
async def get_performance_metrics(
    period: str = "monthly",
    current_user: dict = Depends(get_current_user)
):
    """Get automation performance metrics"""
    return await automation_service.get_performance_metrics(current_user.get("_id") or current_user.get("id", "default-user"), period)

@router.post("/rules/create")
async def create_automation_rule(
    rule_data: AutomationRule,
    current_user: dict = Depends(get_current_user)
):
    """Create custom automation rule"""
    return await automation_service.create_automation_rule(current_user.get("_id") or current_user.get("id", "default-user"), rule_data.dict())

@router.get("/integrations/available")
async def get_available_integrations(current_user: dict = Depends(get_current_user)):
    """Get available third-party integrations for automation"""
    
    return {
        "success": True,
        "data": {
            "integrations": [
                {
                    "name": "Zapier",
                    "category": "automation_platform",
                    "description": "Connect with 3000+ apps via Zapier",
                    "features": ["Bi-directional sync", "Real-time triggers", "Custom webhooks"],
                    "setup_complexity": "Easy",
                    "pricing": "Free tier available"
                },
                {
                    "name": "Salesforce",
                    "category": "crm",
                    "description": "Sync with Salesforce CRM",
                    "features": ["Lead sync", "Opportunity tracking", "Custom fields"],
                    "setup_complexity": "Medium",
                    "pricing": "Enterprise only"
                },
                {
                    "name": "HubSpot",
                    "category": "marketing_crm",
                    "description": "HubSpot marketing automation integration",
                    "features": ["Contact sync", "Email automation", "Lead scoring"],
                    "setup_complexity": "Easy",
                    "pricing": "Free tier available"
                },
                {
                    "name": "Mailchimp",
                    "category": "email_marketing",
                    "description": "Mailchimp email automation integration",
                    "features": ["List sync", "Campaign triggers", "Audience segmentation"],
                    "setup_complexity": "Easy",
                    "pricing": "Usage-based"
                }
            ]
        }
    }