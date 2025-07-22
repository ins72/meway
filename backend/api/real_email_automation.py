"""
Real Email Automation API - ElasticMail Integration - NO MOCK DATA
Endpoints for email campaigns, automation, and subscriber management
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import asyncio

from core.database import get_database
from core.auth import get_current_user
from services.real_email_automation_service import RealEmailAutomationService

router = APIRouter(prefix="/api/email-automation", tags=["Email Automation"])

@router.post("/send-email")
async def send_real_email(
    email_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Send real email using ElasticMail API
    """
    try:
        email_service = RealEmailAutomationService(db)
        
        # Validate email request
        required_fields = ["to_email", "subject"]
        for field in required_fields:
            if field not in email_request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Prepare email data
        email_data = {
            "to_email": email_request["to_email"],
            "subject": email_request["subject"],
            "text_content": email_request.get("text_content", ""),
            "html_content": email_request.get("html_content", ""),
            "from_email": email_request.get("from_email", "hello@mewayz.com"),
            "from_name": email_request.get("from_name", "Mewayz Team"),
            "cc": email_request.get("cc"),
            "bcc": email_request.get("bcc"),
            "is_transactional": email_request.get("is_transactional", True),
            "campaign_id": email_request.get("campaign_id"),
            "template_id": email_request.get("template_id")
        }
        
        # Send email
        result = await email_service.send_real_email(email_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "send_id": result["send_id"],
            "status": result["status"],
            "message_id": result["message_id"],
            "sent_at": result["sent_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

@router.post("/campaigns")
async def create_email_campaign(
    campaign_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Create email campaign
    """
    try:
        email_service = RealEmailAutomationService(db)
        
        # Validate campaign request
        required_fields = ["name", "subject"]
        for field in required_fields:
            if field not in campaign_request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create campaign
        campaign = await email_service.create_email_campaign(campaign_request)
        
        if "error" in campaign:
            raise HTTPException(status_code=500, detail=campaign["error"])
        
        return {
            "success": True,
            "campaign_id": campaign["_id"],
            "name": campaign["name"],
            "subject": campaign["subject"],
            "status": campaign["status"],
            "created_at": campaign["created_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign creation failed: {str(e)}")

@router.get("/campaigns")
async def get_email_campaigns(
    status: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get email campaigns
    """
    try:
        campaigns_collection = db["email_campaigns"]
        
        # Build filter
        filter_query = {}
        if status:
            filter_query["status"] = status
        
        # Get campaigns
        campaigns = await campaigns_collection.find(filter_query).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "campaigns": campaigns,
            "total_count": len(campaigns),
            "filter_applied": filter_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaigns: {str(e)}")

@router.get("/campaigns/{campaign_id}/statistics")
async def get_campaign_statistics(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get real campaign statistics from ElasticMail
    """
    try:
        email_service = RealEmailAutomationService(db)
        
        # Get statistics
        statistics = await email_service.get_real_email_statistics(campaign_id)
        
        if "error" in statistics:
            raise HTTPException(status_code=500, detail=statistics["error"])
        
        return {
            "success": True,
            "statistics": statistics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.post("/automation-sequence")
async def create_automation_sequence(
    sequence_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Create automated email sequence
    """
    try:
        email_service = RealEmailAutomationService(db)
        
        # Validate sequence request
        required_fields = ["name", "trigger_type", "emails"]
        for field in required_fields:
            if field not in sequence_request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create sequence
        sequence = await email_service.create_automation_sequence(sequence_request)
        
        if "error" in sequence:
            raise HTTPException(status_code=500, detail=sequence["error"])
        
        return {
            "success": True,
            "sequence_id": sequence["_id"],
            "name": sequence["name"],
            "trigger_type": sequence["trigger_type"],
            "emails_count": len(sequence["emails"]),
            "status": sequence["status"],
            "created_at": sequence["created_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sequence creation failed: {str(e)}")

@router.post("/subscribers")
async def manage_subscribers(
    subscriber_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Manage email subscribers (add/remove)
    """
    try:
        email_service = RealEmailAutomationService(db)
        
        # Validate request
        action = subscriber_request.get("action")
        if action not in ["add", "remove"]:
            raise HTTPException(status_code=400, detail="Action must be 'add' or 'remove'")
        
        if not subscriber_request.get("email"):
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Manage subscriber
        result = await email_service.manage_subscribers(action, subscriber_request)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "action": result["action"],
            "email": result["email"],
            "status": result["status"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subscriber management failed: {str(e)}")

@router.get("/subscribers")
async def get_subscribers(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get email subscribers list
    """
    try:
        subscribers_collection = db["email_subscribers"]
        
        # Build filter
        filter_query = {}
        if status:
            filter_query["status"] = status
        
        # Get subscribers
        subscribers = await subscribers_collection.find(filter_query).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "subscribers": subscribers,
            "total_count": len(subscribers),
            "filter_applied": filter_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscribers: {str(e)}")

@router.get("/email-logs")
async def get_email_logs(
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get email sending logs
    """
    try:
        logs_collection = db["email_logs"]
        
        # Build filter
        filter_query = {}
        if campaign_id:
            filter_query["campaign_id"] = campaign_id
        if status:
            filter_query["status"] = status
        
        # Get logs
        logs = await logs_collection.find(filter_query).sort("sent_at", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "logs": logs,
            "total_count": len(logs),
            "filter_applied": filter_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email logs: {str(e)}")

@router.post("/bulk-email")
async def send_bulk_emails(
    bulk_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Send bulk emails to multiple recipients
    """
    try:
        email_service = RealEmailAutomationService(db)
        
        # Validate bulk request
        recipients = bulk_request.get("recipients", [])
        if not recipients:
            raise HTTPException(status_code=400, detail="Recipients list is required")
        
        if len(recipients) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 recipients per bulk operation")
        
        # Required fields
        required_fields = ["subject", "text_content"]
        for field in required_fields:
            if field not in bulk_request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Send emails to all recipients
        bulk_id = str(uuid.uuid4())
        sent_emails = []
        failed_emails = []
        
        for recipient in recipients:
            email_data = {
                "to_email": recipient,
                "subject": bulk_request["subject"],
                "text_content": bulk_request["text_content"],
                "html_content": bulk_request.get("html_content", ""),
                "from_email": bulk_request.get("from_email", "hello@mewayz.com"),
                "from_name": bulk_request.get("from_name", "Mewayz Team"),
                "campaign_id": bulk_request.get("campaign_id"),
                "bulk_id": bulk_id
            }
            
            try:
                result = await email_service.send_real_email(email_data)
                if "error" not in result:
                    sent_emails.append({
                        "recipient": recipient,
                        "send_id": result["send_id"],
                        "status": result["status"]
                    })
                else:
                    failed_emails.append({
                        "recipient": recipient,
                        "error": result["error"]
                    })
            except Exception as e:
                failed_emails.append({
                    "recipient": recipient,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "bulk_id": bulk_id,
            "total_recipients": len(recipients),
            "sent_count": len(sent_emails),
            "failed_count": len(failed_emails),
            "sent_emails": sent_emails,
            "failed_emails": failed_emails,
            "bulk_completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk email sending failed: {str(e)}")

@router.get("/analytics/overview")
async def get_email_analytics_overview(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get email automation analytics overview
    """
    try:
        # Get counts from collections
        campaigns_count = await db["email_campaigns"].count_documents({})
        subscribers_count = await db["email_subscribers"].count_documents({"status": "active"})
        total_emails_sent = await db["email_logs"].count_documents({"status": "sent"})
        failed_emails = await db["email_logs"].count_documents({"status": "failed"})
        
        # Calculate success rate
        total_attempts = total_emails_sent + failed_emails
        success_rate = round((total_emails_sent / max(total_attempts, 1)) * 100, 2)
        
        # Get recent activity
        recent_campaigns = await db["email_campaigns"].find(
            {},
            {"_id": 1, "name": 1, "subject": 1, "status": 1, "created_at": 1}
        ).sort("created_at", -1).limit(5).to_list(length=None)
        
        recent_logs = await db["email_logs"].find(
            {},
            {"_id": 1, "to_email": 1, "subject": 1, "status": 1, "sent_at": 1}
        ).sort("sent_at", -1).limit(10).to_list(length=None)
        
        return {
            "success": True,
            "totals": {
                "campaigns": campaigns_count,
                "active_subscribers": subscribers_count,
                "emails_sent": total_emails_sent,
                "failed_emails": failed_emails,
                "success_rate": success_rate
            },
            "recent_activity": {
                "campaigns": recent_campaigns,
                "email_logs": recent_logs
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/templates")
async def create_email_template(
    template_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Create email template
    """
    try:
        # Validate template request
        required_fields = ["name", "subject", "html_content"]
        for field in required_fields:
            if field not in template_request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create template
        template = {
            "_id": str(uuid.uuid4()),
            "name": template_request["name"],
            "subject": template_request["subject"],
            "html_content": template_request["html_content"],
            "text_content": template_request.get("text_content", ""),
            "description": template_request.get("description", ""),
            "category": template_request.get("category", "general"),
            "tags": template_request.get("tags", []),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "usage_count": 0
        }
        
        await db["email_templates"].insert_one(template)
        
        return {
            "success": True,
            "template_id": template["_id"],
            "name": template["name"],
            "subject": template["subject"],
            "category": template["category"],
            "created_at": template["created_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template creation failed: {str(e)}")

@router.get("/templates")
async def get_email_templates(
    category: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get email templates
    """
    try:
        templates_collection = db["email_templates"]
        
        # Build filter
        filter_query = {}
        if category:
            filter_query["category"] = category
        
        # Get templates
        templates = await templates_collection.find(filter_query).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "templates": templates,
            "total_count": len(templates),
            "filter_applied": filter_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")