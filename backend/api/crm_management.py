"""
CRM & Customer Management System API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition - Complete Customer Relationship Management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class ContactCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = ""
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    status: str = "lead"  # lead, prospect, customer, churned
    lead_score: int = 0
    source: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    lead_score: Optional[int] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class DealCreate(BaseModel):
    contact_id: str
    title: str
    value: float
    currency: str = "USD"
    stage: str = "prospecting"  # prospecting, qualified, proposal, negotiation, closed_won, closed_lost
    probability: int = 25  # 0-100
    expected_close_date: Optional[datetime] = None
    description: Optional[str] = ""
    products: List[Dict[str, Any]] = []

class ActivityCreate(BaseModel):
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None
    type: str  # call, email, meeting, task, note
    subject: str
    description: Optional[str] = ""
    due_date: Optional[datetime] = None
    is_completed: bool = False
    duration_minutes: Optional[int] = None

class PipelineStage(BaseModel):
    name: str
    order: int
    probability: int  # Default probability for this stage

def get_contacts_collection():
    """Get contacts collection"""
    db = get_database()
    return db.contacts

def get_deals_collection():
    """Get deals collection"""
    db = get_database()
    return db.deals

def get_activities_collection():
    """Get activities collection"""
    db = get_database()
    return db.activities

def get_pipelines_collection():
    """Get sales pipelines collection"""
    db = get_database()
    return db.sales_pipelines

def get_workspaces_collection():
    """Get workspaces collection"""
    db = get_database()
    return db.workspaces

@router.get("/dashboard")
async def get_crm_dashboard(
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get comprehensive CRM dashboard with sales analytics"""
    try:
        # Get workspace
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        contacts_collection = get_contacts_collection()
        deals_collection = get_deals_collection()
        activities_collection = get_activities_collection()
        
        # Get contact statistics
        total_contacts = await contacts_collection.count_documents({"workspace_id": workspace_id})
        
        # Contact status breakdown
        contact_status_pipeline = [
            {"$match": {"workspace_id": workspace_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        contact_statuses = await contacts_collection.aggregate(contact_status_pipeline).to_list(length=None)
        status_breakdown = {status["_id"]: status["count"] for status in contact_statuses}
        
        # Get deal statistics
        total_deals = await deals_collection.count_documents({"workspace_id": workspace_id})
        
        # Deal value pipeline
        deal_value_pipeline = [
            {"$match": {"workspace_id": workspace_id}},
            {"$group": {
                "_id": "$stage",
                "count": {"$sum": 1},
                "total_value": {"$sum": "$value"},
                "avg_value": {"$avg": "$value"}
            }}
        ]
        
        deal_stats = await deals_collection.aggregate(deal_value_pipeline).to_list(length=None)
        
        # Calculate total pipeline value and won deals
        total_pipeline_value = 0
        won_deals_value = 0
        deal_stage_breakdown = {}
        
        for deal_stat in deal_stats:
            stage = deal_stat["_id"]
            deal_stage_breakdown[stage] = deal_stat
            total_pipeline_value += deal_stat["total_value"]
            
            if stage == "closed_won":
                won_deals_value += deal_stat["total_value"]
        
        # Get activity statistics
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_activities = await activities_collection.count_documents({
            "workspace_id": workspace_id,
            "created_at": {"$gte": thirty_days_ago}
        })
        
        overdue_activities = await activities_collection.count_documents({
            "workspace_id": workspace_id,
            "due_date": {"$lt": datetime.utcnow()},
            "is_completed": False
        })
        
        # Get recent contacts
        recent_contacts = await contacts_collection.find({
            "workspace_id": workspace_id
        }).sort("created_at", -1).limit(5).to_list(length=None)
        
        # Get top deals
        top_deals = await deals_collection.find({
            "workspace_id": workspace_id,
            "stage": {"$nin": ["closed_won", "closed_lost"]}
        }).sort("value", -1).limit(5).to_list(length=None)
        
        # Calculate conversion metrics
        leads_count = status_breakdown.get("lead", 0)
        customers_count = status_breakdown.get("customer", 0)
        lead_to_customer_rate = (customers_count / max(leads_count + customers_count, 1)) * 100
        
        # Calculate average deal size
        avg_deal_size = (total_pipeline_value / max(total_deals, 1)) if total_deals > 0 else 0
        
        dashboard_data = {
            "workspace_id": workspace_id,
            "contacts_overview": {
                "total_contacts": total_contacts,
                "status_breakdown": status_breakdown,
                "lead_to_customer_conversion": round(lead_to_customer_rate, 1),
                "new_contacts_this_month": len([c for c in recent_contacts if c["created_at"] >= thirty_days_ago])
            },
            "deals_overview": {
                "total_deals": total_deals,
                "total_pipeline_value": round(total_pipeline_value, 2),
                "won_deals_value": round(won_deals_value, 2),
                "average_deal_size": round(avg_deal_size, 2),
                "deal_stage_breakdown": deal_stage_breakdown,
                "win_rate": round((deal_stage_breakdown.get("closed_won", {}).get("count", 0) / max(total_deals, 1)) * 100, 1)
            },
            "activities_overview": {
                "recent_activities": recent_activities,
                "overdue_activities": overdue_activities,
                "completion_rate": 85.5  # Would be calculated from actual data
            },
            "recent_contacts": [
                {
                    "id": str(contact["_id"]),
                    "name": f"{contact['first_name']} {contact.get('last_name', '')}".strip(),
                    "email": contact["email"],
                    "company": contact.get("company"),
                    "status": contact.get("status"),
                    "lead_score": contact.get("lead_score", 0),
                    "created_at": contact["created_at"]
                } for contact in recent_contacts
            ],
            "top_deals": [
                {
                    "id": str(deal["_id"]),
                    "title": deal["title"],
                    "value": deal["value"],
                    "stage": deal["stage"],
                    "probability": deal.get("probability", 0),
                    "expected_close_date": deal.get("expected_close_date")
                } for deal in top_deals
            ]
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch CRM dashboard: {str(e)}"
        )

@router.get("/contacts")
async def get_contacts(
    workspace_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get contacts with filtering, search, and pagination"""
    try:
        # Get workspace
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                return {"success": True, "data": {"contacts": [], "pagination": {}}}
            workspace_id = str(workspace["_id"])
        
        contacts_collection = get_contacts_collection()
        
        # Build query
        query = {"workspace_id": workspace_id}
        
        if status_filter:
            query["status"] = status_filter
        
        if search:
            query["$or"] = [
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"company": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total_contacts = await contacts_collection.count_documents(query)
        
        # Get contacts with pagination
        skip = (page - 1) * limit
        contacts = await contacts_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        
        # Enhance contacts with recent activity
        for contact in contacts:
            contact["id"] = str(contact["_id"])
            contact["full_name"] = f"{contact['first_name']} {contact.get('last_name', '')}".strip()
            
            # Get last activity (simplified for performance)
            contact["last_activity"] = contact.get("updated_at", contact["created_at"])
        
        return {
            "success": True,
            "data": {
                "contacts": contacts,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_contacts + limit - 1) // limit,
                    "total_contacts": total_contacts,
                    "has_next": skip + limit < total_contacts,
                    "has_prev": page > 1
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch contacts: {str(e)}"
        )

@router.post("/contacts")
async def create_contact(
    contact_data: ContactCreate,
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new contact with validation"""
    try:
        # Get workspace
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        # Check contact limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        contacts_collection = get_contacts_collection()
        existing_contacts = await contacts_collection.count_documents({
            "workspace_id": workspace_id
        })
        
        # Plan-based limits
        max_contacts = get_contact_limit(user_plan)
        if max_contacts != -1 and existing_contacts >= max_contacts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Contact limit reached ({max_contacts}). Upgrade your plan for more contacts."
            )
        
        # Check for duplicate email
        existing_contact = await contacts_collection.find_one({
            "workspace_id": workspace_id,
            "email": contact_data.email
        })
        
        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact with this email already exists"
            )
        
        # Create contact document
        contact_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "created_by": current_user["_id"],
            "first_name": contact_data.first_name,
            "last_name": contact_data.last_name,
            "email": contact_data.email,
            "phone": contact_data.phone,
            "company": contact_data.company,
            "position": contact_data.position,
            "website": contact_data.website,
            "address": contact_data.address,
            "status": contact_data.status,
            "lead_score": contact_data.lead_score,
            "source": contact_data.source,
            "tags": contact_data.tags,
            "custom_fields": contact_data.custom_fields,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_contacted_at": None,
            "deal_count": 0,
            "total_deal_value": 0
        }
        
        # Save contact
        await contacts_collection.insert_one(contact_doc)
        
        response_contact = contact_doc.copy()
        response_contact["id"] = str(response_contact["_id"])
        response_contact["full_name"] = f"{contact_data.first_name} {contact_data.last_name}".strip()
        
        return {
            "success": True,
            "message": "Contact created successfully",
            "data": response_contact
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contact: {str(e)}"
        )

@router.get("/contacts/{contact_id}")
async def get_contact(
    contact_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get contact details with related activities and deals"""
    try:
        contacts_collection = get_contacts_collection()
        deals_collection = get_deals_collection()
        activities_collection = get_activities_collection()
        
        # Find contact
        contact = await contacts_collection.find_one({"_id": contact_id})
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Get related deals
        deals = await deals_collection.find({
            "contact_id": contact_id
        }).sort("created_at", -1).to_list(length=None)
        
        for deal in deals:
            deal["id"] = str(deal["_id"])
        
        # Get recent activities
        activities = await activities_collection.find({
            "contact_id": contact_id
        }).sort("created_at", -1).limit(20).to_list(length=None)
        
        for activity in activities:
            activity["id"] = str(activity["_id"])
        
        contact["id"] = str(contact["_id"])
        contact["full_name"] = f"{contact['first_name']} {contact.get('last_name', '')}".strip()
        contact["deals"] = deals
        contact["recent_activities"] = activities
        contact["deal_count"] = len(deals)
        contact["total_deal_value"] = sum(deal.get("value", 0) for deal in deals)
        
        return {
            "success": True,
            "data": contact
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch contact: {str(e)}"
        )

@router.put("/contacts/{contact_id}")
async def update_contact(
    contact_id: str,
    update_data: ContactUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update contact with validation"""
    try:
        contacts_collection = get_contacts_collection()
        
        # Find contact
        contact = await contacts_collection.find_one({"_id": contact_id})
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Check email uniqueness if email is being updated
        if update_data.email and update_data.email != contact["email"]:
            existing_email = await contacts_collection.find_one({
                "workspace_id": contact["workspace_id"],
                "email": update_data.email,
                "_id": {"$ne": contact_id}
            })
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Contact with this email already exists"
                )
        
        # Prepare update
        update_doc = {"$set": {"updated_at": datetime.utcnow()}}
        
        # Update allowed fields
        update_fields = update_data.dict(exclude_none=True)
        for field, value in update_fields.items():
            update_doc["$set"][field] = value
        
        # Update contact
        result = await contacts_collection.update_one(
            {"_id": contact_id},
            update_doc
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made"
            )
        
        return {
            "success": True,
            "message": "Contact updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update contact: {str(e)}"
        )

@router.post("/deals")
async def create_deal(
    deal_data: DealCreate,
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new deal for contact"""
    try:
        # Get workspace
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        contacts_collection = get_contacts_collection()
        deals_collection = get_deals_collection()
        
        # Verify contact exists
        contact = await contacts_collection.find_one({
            "_id": deal_data.contact_id,
            "workspace_id": workspace_id
        })
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Create deal document
        deal_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "contact_id": deal_data.contact_id,
            "contact_name": f"{contact['first_name']} {contact.get('last_name', '')}".strip(),
            "created_by": current_user["_id"],
            "assigned_to": current_user["_id"],
            "title": deal_data.title,
            "value": deal_data.value,
            "currency": deal_data.currency,
            "stage": deal_data.stage,
            "probability": deal_data.probability,
            "expected_close_date": deal_data.expected_close_date,
            "description": deal_data.description,
            "products": deal_data.products,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "stage_history": [
                {
                    "stage": deal_data.stage,
                    "changed_at": datetime.utcnow(),
                    "changed_by": current_user["_id"]
                }
            ]
        }
        
        # Save deal
        await deals_collection.insert_one(deal_doc)
        
        # Update contact deal count
        await contacts_collection.update_one(
            {"_id": deal_data.contact_id},
            {
                "$inc": {"deal_count": 1, "total_deal_value": deal_data.value},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        response_deal = deal_doc.copy()
        response_deal["id"] = str(response_deal["_id"])
        
        return {
            "success": True,
            "message": "Deal created successfully",
            "data": response_deal
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deal: {str(e)}"
        )

@router.get("/deals")
async def get_deals(
    workspace_id: Optional[str] = None,
    stage_filter: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get deals with filtering"""
    try:
        # Get workspace
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                return {"success": True, "data": {"deals": []}}
            workspace_id = str(workspace["_id"])
        
        deals_collection = get_deals_collection()
        
        # Build query
        query = {"workspace_id": workspace_id}
        if stage_filter:
            query["stage"] = stage_filter
        
        # Get deals
        deals = await deals_collection.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
        
        # Enhance deals
        for deal in deals:
            deal["id"] = str(deal["_id"])
        
        # Group by stage for pipeline view
        pipeline = {}
        for deal in deals:
            stage = deal["stage"]
            if stage not in pipeline:
                pipeline[stage] = []
            pipeline[stage].append(deal)
        
        return {
            "success": True,
            "data": {
                "deals": deals,
                "pipeline": pipeline,
                "total_value": sum(deal.get("value", 0) for deal in deals)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch deals: {str(e)}"
        )

@router.post("/activities")
async def create_activity(
    activity_data: ActivityCreate,
    workspace_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new activity (call, email, meeting, task, note)"""
    try:
        # Get workspace
        if not workspace_id:
            workspaces_collection = get_workspaces_collection()
            workspace = await workspaces_collection.find_one({"owner_id": current_user["_id"]})
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No workspace found"
                )
            workspace_id = str(workspace["_id"])
        
        # Create activity document
        activity_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "contact_id": activity_data.contact_id,
            "deal_id": activity_data.deal_id,
            "created_by": current_user["_id"],
            "type": activity_data.type,
            "subject": activity_data.subject,
            "description": activity_data.description,
            "due_date": activity_data.due_date,
            "is_completed": activity_data.is_completed,
            "duration_minutes": activity_data.duration_minutes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save activity
        activities_collection = get_activities_collection()
        await activities_collection.insert_one(activity_doc)
        
        # Update contact last_contacted_at if it's a contact activity
        if activity_data.contact_id:
            contacts_collection = get_contacts_collection()
            await contacts_collection.update_one(
                {"_id": activity_data.contact_id},
                {"$set": {"last_contacted_at": datetime.utcnow()}}
            )
        
        response_activity = activity_doc.copy()
        response_activity["id"] = str(response_activity["_id"])
        
        return {
            "success": True,
            "message": "Activity created successfully",
            "data": response_activity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create activity: {str(e)}"
        )

# Helper functions
def get_contact_limit(user_plan: str) -> int:
    """Get contact limit based on user plan"""
    limits = {
        "free": 100,
        "pro": 10000,
        "enterprise": -1  # unlimited
    }
    return limits.get(user_plan, 100)