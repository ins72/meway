"""
Real AI Automation API - OpenAI Integration - NO MOCK DATA
Endpoints for AI content generation, lead enrichment, and automation
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import asyncio

from core.database import get_database
from core.auth import get_current_user
from services.real_ai_automation_service import RealAIAutomationService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter(prefix="/api/ai-automation", tags=["AI Automation"])

@router.post("/generate-content")
async def generate_ai_content(
    content_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Generate personalized content using OpenAI GPT
    """
    try:
        ai_service = RealAIAutomationService(db)
        
        # Validate content request
        validated_request = {
            "platform": content_request.get("platform", "general"),
            "topic": content_request.get("topic", "business"),
            "tone": content_request.get("tone", "professional"),
            "target_audience": content_request.get("target_audience", "business owners"),
            "content_type": content_request.get("content_type", "post"),
            "additional_context": content_request.get("additional_context", "")
        }
        
        # Generate content
        generated_content = await ai_service.generate_personalized_content(validated_request)
        
        if "error" in generated_content:
            raise HTTPException(status_code=500, detail=generated_content["error"])
        
        return {
            "success": True,
            "content_id": generated_content["_id"],
            "platform": generated_content["platform"],
            "generated_text": generated_content["generated_text"],
            "character_count": generated_content["character_count"],
            "hashtags": generated_content["hashtags"],
            "optimization_suggestions": generated_content["optimization_suggestions"],
            "estimated_engagement": generated_content["estimated_engagement"],
            "readability_score": generated_content["readability_score"],
            "sentiment_analysis": generated_content["sentiment_score"],
            "tokens_used": generated_content["tokens_used"],
            "generated_at": generated_content["generated_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/enrich-lead")
async def enrich_lead_with_ai(
    lead_data: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Enrich lead data using AI analysis
    """
    try:
        ai_service = RealAIAutomationService(db)
        
        # Validate lead data
        if not lead_data.get("bio") and not lead_data.get("username"):
            raise HTTPException(status_code=400, detail="Lead data must include bio or username")
        
        # Enrich lead data
        enriched_data = await ai_service.enrich_lead_data(lead_data)
        
        if "error" in enriched_data:
            raise HTTPException(status_code=500, detail=enriched_data["error"])
        
        return {
            "success": True,
            "enrichment_id": enriched_data["_id"],
            "original_lead_id": enriched_data["original_lead_id"],
            "platform": enriched_data["platform"],
            "ai_analysis": enriched_data["ai_analysis"],
            "personalized_outreach": enriched_data["personalized_outreach"],
            "lead_score": enriched_data["lead_score"],
            "confidence_score": enriched_data["confidence_score"],
            "enriched_at": enriched_data["enrichment_date"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead enrichment failed: {str(e)}")

@router.post("/batch-enrich-leads")
async def batch_enrich_leads(
    batch_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Batch enrich multiple leads with AI analysis
    """
    try:
        ai_service = RealAIAutomationService(db)
        
        search_id = batch_request.get("search_id")
        platform = batch_request.get("platform")
        max_leads = min(batch_request.get("max_leads", 50), 100)
        
        if not search_id or not platform:
            raise HTTPException(status_code=400, detail="search_id and platform are required")
        
        # Get leads from database
        collection_name = f"{platform}_leads"
        leads_collection = db[collection_name]
        
        leads = await leads_collection.find(
            {"search_id": search_id}
        ).limit(max_leads).to_list(length=None)
        
        if not leads:
            raise HTTPException(status_code=404, detail="No leads found for the given search_id")
        
        # Enrich each lead
        enriched_leads = []
        batch_id = str(uuid.uuid4())
        
        for lead in leads:
            try:
                enriched_data = await ai_service.enrich_lead_data(lead)
                if "error" not in enriched_data:
                    enriched_data["batch_id"] = batch_id
                    enriched_leads.append(enriched_data)
            except Exception as e:
                # Log error but continue with other leads
                print(f"Error enriching lead {lead.get('_id', 'unknown')}: {str(e)}")
                continue
        
        return {
            "success": True,
            "batch_id": batch_id,
            "search_id": search_id,
            "platform": platform,
            "total_leads_processed": len(leads),
            "successfully_enriched": len(enriched_leads),
            "enriched_leads": enriched_leads,
            "batch_completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch enrichment failed: {str(e)}")

@router.post("/create-workflow")
async def create_automation_workflow(
    workflow_config: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Create an automation workflow
    """
    try:
        ai_service = RealAIAutomationService(db)
        
        # Validate workflow config
        required_fields = ["name", "trigger_type", "actions"]
        for field in required_fields:
            if field not in workflow_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create workflow
        workflow = await ai_service.create_automation_workflow(workflow_config)
        
        if "error" in workflow:
            raise HTTPException(status_code=500, detail=workflow["error"])
        
        return {
            "success": True,
            "workflow_id": workflow["_id"],
            "name": workflow["name"],
            "trigger_type": workflow["trigger_type"],
            "actions": workflow["actions"],
            "status": workflow["status"],
            "created_at": workflow["created_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")

@router.get("/workflows")
async def get_automation_workflows(
    status: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get automation workflows
    """
    try:
        workflows_collection = db["automation_workflows"]
        
        # Build filter
        filter_query = {}
        if status:
            filter_query["status"] = status
        
        # Get workflows
        workflows = await workflows_collection.find(filter_query).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "workflows": workflows,
            "total_count": len(workflows),
            "filter_applied": filter_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflows: {str(e)}")

@router.get("/content-history")
async def get_generated_content_history(
    platform: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get generated content history
    """
    try:
        content_collection = db["ai_generated_content"]
        
        # Build filter
        filter_query = {}
        if platform:
            filter_query["platform"] = platform
        
        # Get content history
        content_history = await content_collection.find(
            filter_query,
            {
                "_id": 1,
                "platform": 1,
                "content_type": 1,
                "generated_text": 1,
                "character_count": 1,
                "hashtags": 1,
                "estimated_engagement": 1,
                "generated_at": 1,
                "tokens_used": 1
            }
        ).sort("generated_at", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "content_history": content_history,
            "total_count": len(content_history),
            "filter_applied": filter_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content history: {str(e)}")

@router.get("/enrichment-history")
async def get_lead_enrichment_history(
    platform: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get lead enrichment history
    """
    try:
        enrichment_collection = db["lead_enrichment"]
        
        # Build filter
        filter_query = {}
        if platform:
            filter_query["platform"] = platform
        
        # Get enrichment history
        enrichment_history = await enrichment_collection.find(
            filter_query,
            {
                "_id": 1,
                "original_lead_id": 1,
                "platform": 1,
                "ai_analysis": 1,
                "lead_score": 1,
                "confidence_score": 1,
                "enrichment_date": 1
            }
        ).sort("enrichment_date", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "enrichment_history": enrichment_history,
            "total_count": len(enrichment_history),
            "filter_applied": filter_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enrichment history: {str(e)}")

@router.get("/analytics/overview")
async def get_ai_analytics_overview(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get AI automation analytics overview
    """
    try:
        # Get counts from collections
        content_count = await db["ai_generated_content"].count_documents({})
        enrichment_count = await db["lead_enrichment"].count_documents({})
        workflows_count = await db["automation_workflows"].count_documents({})
        
        # Get recent activity
        recent_content = await db["ai_generated_content"].find(
            {},
            {"_id": 1, "platform": 1, "content_type": 1, "generated_at": 1}
        ).sort("generated_at", -1).limit(5).to_list(length=None)
        
        recent_enrichments = await db["lead_enrichment"].find(
            {},
            {"_id": 1, "platform": 1, "lead_score": 1, "enrichment_date": 1}
        ).sort("enrichment_date", -1).limit(5).to_list(length=None)
        
        # Calculate platform distribution for content
        platform_pipeline = [
            {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        platform_distribution = await db["ai_generated_content"].aggregate(platform_pipeline).to_list(length=None)
        
        return {
            "success": True,
            "totals": {
                "content_generated": content_count,
                "leads_enriched": enrichment_count,
                "workflows_created": workflows_count
            },
            "recent_activity": {
                "content": recent_content,
                "enrichments": recent_enrichments
            },
            "platform_distribution": platform_distribution,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/bulk-content-generation")
async def bulk_generate_content(
    bulk_request: Dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Generate multiple pieces of content in bulk
    """
    try:
        ai_service = RealAIAutomationService(db)
        
        # Validate bulk request
        content_requests = bulk_request.get("content_requests", [])
        if not content_requests:
            raise HTTPException(status_code=400, detail="content_requests array is required")
        
        if len(content_requests) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 content requests per bulk operation")
        
        # Generate content for each request
        generated_contents = []
        bulk_id = str(uuid.uuid4())
        
        for request in content_requests:
            try:
                request["bulk_id"] = bulk_id
                content = await ai_service.generate_personalized_content(request)
                if "error" not in content:
                    generated_contents.append(content)
            except Exception as e:
                print(f"Error generating content for request: {str(e)}")
                continue
        
        return {
            "success": True,
            "bulk_id": bulk_id,
            "total_requested": len(content_requests),
            "successfully_generated": len(generated_contents),
            "generated_contents": generated_contents,
            "bulk_completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk content generation failed: {str(e)}")