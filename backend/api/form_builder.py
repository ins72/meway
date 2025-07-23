"""
Form Builder System API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
High-Value Feature Addition - Dynamic Form Creation & Management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from bson import ObjectId

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class FormField(BaseModel):
    id: Optional[str] = None  # Will be auto-generated if not provided
    type: str  # text, email, number, select, checkbox, radio, textarea, file, date
    label: str
    placeholder: Optional[str] = ""
    required: bool = False
    options: Optional[List[str]] = []  # For select, radio, checkbox
    validation: Optional[Dict[str, Any]] = {}
    order: int = 0

class FormCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    fields: List[FormField]
    settings: Dict[str, Any] = {}
    workspace_id: Optional[str] = None

class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[FormField]] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class FormSubmission(BaseModel):
    form_id: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

def get_forms_collection():
    """Get forms collection"""
    db = get_database()
    return db.forms

def get_form_submissions_collection():
    """Get form submissions collection"""
    db = get_database()
    return db.form_submissions

def get_form_analytics_collection():
    """Get form analytics collection"""
    db = get_database()
    return db.form_analytics

@router.get("/dashboard")
async def get_forms_dashboard(current_user: dict = Depends(get_current_active_user)):
    """Get forms dashboard with analytics and overview"""
    try:
        forms_collection = get_forms_collection()
        form_submissions_collection = get_form_submissions_collection()
        
        # Get user's forms
        total_forms = await forms_collection.count_documents({"created_by": current_user["_id"]})
        active_forms = await forms_collection.count_documents({
            "created_by": current_user["_id"],
            "is_active": True
        })
        
        # Get submissions stats
        total_submissions = await form_submissions_collection.count_documents({
            "user_id": current_user["_id"]
        })
        
        # Get recent submissions (last 30 days)
        thirty_days_ago = datetime.utcnow().replace(day=1) if datetime.utcnow().day > 30 else datetime.utcnow().replace(month=datetime.utcnow().month-1, day=1) if datetime.utcnow().month > 1 else datetime.utcnow().replace(year=datetime.utcnow().year-1, month=12, day=1)
        recent_submissions = await form_submissions_collection.count_documents({
            "user_id": current_user["_id"],
            "submitted_at": {"$gte": thirty_days_ago}
        })
        
        # Get top performing forms
        top_forms_pipeline = [
            {"$match": {"user_id": current_user["_id"]}},
            {"$group": {
                "_id": "$form_id",
                "submission_count": {"$sum": 1},
                "form_title": {"$first": "$form_title"}
            }},
            {"$sort": {"submission_count": -1}},
            {"$limit": 5}
        ]
        
        top_forms = await form_submissions_collection.aggregate(top_forms_pipeline).to_list(length=None)
        
        # Get recent forms
        recent_forms = await forms_collection.find({
            "created_by": current_user["_id"]
        }).sort("created_at", -1).limit(5).to_list(length=None)
        
        for form in recent_forms:
            form["id"] = str(form["_id"])
            # Get submission count for each form
            form["submission_count"] = await form_submissions_collection.count_documents({"form_id": form["id"]})
        
        dashboard_data = {
            "overview": {
                "total_forms": total_forms,
                "active_forms": active_forms,
                "total_submissions": total_submissions,
                "recent_submissions": recent_submissions,
                "conversion_rate": round((recent_submissions / max(total_forms, 1)) * 100, 1)
            },
            "top_forms": [
                {
                    "form_id": form["_id"],
                    "title": form.get("form_title", "Unknown Form"),
                    "submissions": form["submission_count"]
                } for form in top_forms
            ],
            "recent_forms": [
                {
                    "id": form["id"],
                    "title": form["title"],
                    "is_active": form.get("is_active", True),
                    "created_at": form["created_at"],
                    "submission_count": form["submission_count"],
                    "field_count": len(form.get("fields", []))
                } for form in recent_forms
            ]
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch forms dashboard: {str(e)}"
        )

@router.get("/forms")
async def get_forms(
    workspace_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get user's forms with filtering and pagination"""
    try:
        forms_collection = get_forms_collection()
        form_submissions_collection = get_form_submissions_collection()
        
        # Build query
        query = {"created_by": current_user["_id"]}
        
        if workspace_id:
            query["workspace_id"] = workspace_id
        
        if status_filter == "active":
            query["is_active"] = True
        elif status_filter == "inactive":
            query["is_active"] = False
        
        # Get total count
        total_forms = await forms_collection.count_documents(query)
        
        # Get forms with pagination
        skip = (page - 1) * limit
        forms = await forms_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        
        # Enhance forms with submission data
        for form in forms:
            form["id"] = str(form["_id"])
            
            # Get submission count
            submission_count = await form_submissions_collection.count_documents({"form_id": form["id"]})
            form["submission_count"] = submission_count
            
            # Get latest submission
            latest_submission = await form_submissions_collection.find_one(
                {"form_id": form["id"]},
                sort=[("submitted_at", -1)]
            )
            form["latest_submission"] = latest_submission.get("submitted_at") if latest_submission else None
            
            # Calculate completion rate (if tracking views)
            form["completion_rate"] = 0  # Would require view tracking
            
        return {
            "success": True,
            "data": {
                "forms": forms,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_forms + limit - 1) // limit,
                    "total_forms": total_forms,
                    "has_next": skip + limit < total_forms,
                    "has_prev": page > 1
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch forms: {str(e)}"
        )

@router.post("/create")
async def create_form(
    form_data: FormCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new form with validation"""
    try:
        # Validate fields
        if not form_data.fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form must have at least one field"
            )
        
        # Validate field types
        valid_field_types = [
            "text", "email", "number", "select", "checkbox", "radio", 
            "textarea", "file", "date", "phone", "url", "password"
        ]
        
        for field in form_data.fields:
            if field.type not in valid_field_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid field type: {field.type}"
                )
        
        # Check user's form creation limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        forms_collection = get_forms_collection()
        existing_forms = await forms_collection.count_documents({"created_by": current_user["_id"]})
        
        # Plan-based limits
        max_forms = get_form_limit(user_plan)
        if max_forms != -1 and existing_forms >= max_forms:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Form limit reached ({max_forms}). Upgrade your plan for more forms."
            )
        
        # Validate and assign field IDs
        processed_fields = []
        for i, field in enumerate(form_data.fields):
            field_dict = field.dict()
            if not field_dict.get("id"):
                field_dict["id"] = f"field_{i+1}_{str(ObjectId())[:8]}"
            processed_fields.append(field_dict)
        
        # Create form document
        form_doc = {
            "_id": str(uuid.uuid4()),
            "created_by": current_user["_id"],
            "workspace_id": form_data.workspace_id,
            "title": form_data.title,
            "description": form_data.description,
            "fields": processed_fields,
            "settings": {
                "allow_multiple_submissions": form_data.settings.get("allow_multiple_submissions", True),
                "require_authentication": form_data.settings.get("require_authentication", False),
                "send_confirmation_email": form_data.settings.get("send_confirmation_email", False),
                "redirect_url": form_data.settings.get("redirect_url", ""),
                "custom_css": form_data.settings.get("custom_css", ""),
                "submit_button_text": form_data.settings.get("submit_button_text", "Submit"),
                "success_message": form_data.settings.get("success_message", "Thank you for your submission!"),
                **form_data.settings
            },
            "is_active": True,
            "view_count": 0,
            "submission_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save form
        await forms_collection.insert_one(form_doc)
        
        # Create analytics record
        await create_form_analytics_record(form_doc["_id"], current_user["_id"])
        
        response_form = form_doc.copy()
        response_form["id"] = str(response_form["_id"])
        response_form["form_url"] = f"/forms/{response_form['id']}"
        
        return {
            "success": True,
            "message": "Form created successfully",
            "data": response_form
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create form: {str(e)}"
        )

@router.get("/forms/{form_id}")
async def get_form(
    form_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get form details with submission statistics"""
    try:
        forms_collection = get_forms_collection()
        form_submissions_collection = get_form_submissions_collection()
        
        # Find form
        form = await forms_collection.find_one({"_id": form_id})
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        # Check access permission
        if form["created_by"] != current_user["_id"]:
            # Check if user has workspace access
            workspace_id = form.get("workspace_id")
            if workspace_id:
                # Would verify workspace access here
                pass
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this form"
                )
        
        # Get submission statistics
        total_submissions = await form_submissions_collection.count_documents({"form_id": form_id})
        
        # Get recent submissions
        recent_submissions = await form_submissions_collection.find({
            "form_id": form_id
        }).sort("submitted_at", -1).limit(5).to_list(length=None)
        
        # Get field analytics
        field_analytics = {}
        for field in form.get("fields", []):
            if field["type"] in ["select", "radio", "checkbox"]:
                # Get option distribution
                field_data = await analyze_field_responses(form_id, field["id"])
                field_analytics[field["id"]] = field_data
        
        form["id"] = str(form["_id"])
        form["total_submissions"] = total_submissions
        form["recent_submissions"] = recent_submissions
        form["field_analytics"] = field_analytics
        form["form_url"] = f"/forms/{form_id}"
        
        return {
            "success": True,
            "data": form
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch form: {str(e)}"
        )

@router.put("/forms/{form_id}")
async def update_form(
    form_id: str,
    update_data: FormUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update form with validation"""
    try:
        forms_collection = get_forms_collection()
        
        # Find form
        form = await forms_collection.find_one({"_id": form_id})
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        # Check permission
        if form["created_by"] != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied to update this form"
            )
        
        # Prepare update
        update_doc = {"$set": {"updated_at": datetime.utcnow()}}
        
        if update_data.title:
            update_doc["$set"]["title"] = update_data.title
        
        if update_data.description is not None:
            update_doc["$set"]["description"] = update_data.description
        
        if update_data.fields:
            # Validate fields
            valid_field_types = [
                "text", "email", "number", "select", "checkbox", "radio",
                "textarea", "file", "date", "phone", "url", "password"
            ]
            
            for field in update_data.fields:
                if field.type not in valid_field_types:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid field type: {field.type}"
                    )
            
            update_doc["$set"]["fields"] = [field.dict() for field in update_data.fields]
        
        if update_data.settings:
            current_settings = form.get("settings", {})
            current_settings.update(update_data.settings)
            update_doc["$set"]["settings"] = current_settings
        
        if update_data.is_active is not None:
            update_doc["$set"]["is_active"] = update_data.is_active
        
        # Update form
        result = await forms_collection.update_one(
            {"_id": form_id},
            update_doc
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made"
            )
        
        return {
            "success": True,
            "message": "Form updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update form: {str(e)}"
        )

@router.post("/submit")
async def submit_form(submission_data: FormSubmission):
    """Submit form data with validation"""
    try:
        forms_collection = get_forms_collection()
        form_submissions_collection = get_form_submissions_collection()
        
        # Find form
        form = await forms_collection.find_one({"_id": submission_data.form_id})
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        # Check if form is active
        if not form.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form is not currently accepting submissions"
            )
        
        # Validate submission data against form fields
        validation_errors = validate_submission_data(form["fields"], submission_data.data)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"validation_errors": validation_errors}
            )
        
        # Create submission document
        submission_doc = {
            "_id": str(uuid.uuid4()),
            "form_id": submission_data.form_id,
            "form_title": form["title"],
            "user_id": form["created_by"],
            "data": submission_data.data,
            "metadata": {
                "ip_address": submission_data.metadata.get("ip_address"),
                "user_agent": submission_data.metadata.get("user_agent"),
                "referrer": submission_data.metadata.get("referrer"),
                **submission_data.metadata
            },
            "submitted_at": datetime.utcnow()
        }
        
        # Save submission
        await form_submissions_collection.insert_one(submission_doc)
        
        # Update form statistics
        await forms_collection.update_one(
            {"_id": submission_data.form_id},
            {"$inc": {"submission_count": 1}}
        )
        
        # Get success message
        success_message = form.get("settings", {}).get("success_message", "Thank you for your submission!")
        redirect_url = form.get("settings", {}).get("redirect_url")
        
        return {
            "success": True,
            "message": success_message,
            "submission_id": submission_doc["_id"],
            "redirect_url": redirect_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit form: {str(e)}"
        )

@router.get("/forms/{form_id}/submissions")
async def get_form_submissions(
    form_id: str,
    limit: int = 50,
    page: int = 1,
    current_user: dict = Depends(get_current_active_user)
):
    """Get form submissions with pagination"""
    try:
        forms_collection = get_forms_collection()
        form_submissions_collection = get_form_submissions_collection()
        
        # Verify form access
        form = await forms_collection.find_one({
            "_id": form_id,
            "created_by": current_user["_id"]
        })
        
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found or access denied"
            )
        
        # Get submissions with pagination
        skip = (page - 1) * limit
        total_submissions = await form_submissions_collection.count_documents({"form_id": form_id})
        
        submissions = await form_submissions_collection.find({
            "form_id": form_id
        }).sort("submitted_at", -1).skip(skip).limit(limit).to_list(length=None)
        
        # Format submissions
        for submission in submissions:
            submission["id"] = str(submission["_id"])
        
        return {
            "success": True,
            "data": {
                "form_id": form_id,
                "form_title": form["title"],
                "submissions": submissions,
                "pagination": {
                    "current_page": page,
                    "total_pages": (total_submissions + limit - 1) // limit,
                    "total_submissions": total_submissions,
                    "has_next": skip + limit < total_submissions,
                    "has_prev": page > 1
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch form submissions: {str(e)}"
        )

@router.delete("/forms/{form_id}")
async def delete_form(
    form_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete form and all its submissions"""
    try:
        forms_collection = get_forms_collection()
        form_submissions_collection = get_form_submissions_collection()
        form_analytics_collection = get_form_analytics_collection()
        
        # Find and delete form
        result = await forms_collection.delete_one({
            "_id": form_id,
            "created_by": current_user["_id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found or access denied"
            )
        
        # Delete associated submissions and analytics
        await form_submissions_collection.delete_many({"form_id": form_id})
        await form_analytics_collection.delete_many({"form_id": form_id})
        
        return {
            "success": True,
            "message": "Form deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete form: {str(e)}"
        )

# Helper functions
def get_form_limit(user_plan: str) -> int:
    """Get form creation limit based on user plan"""
    limits = {
        "free": 3,
        "pro": 50,
        "enterprise": -1  # unlimited
    }
    return limits.get(user_plan, 3)

def validate_submission_data(fields: List[dict], data: Dict[str, Any]) -> List[str]:
    """Validate form submission data"""
    errors = []
    
    for field in fields:
        field_id = field["id"]
        field_type = field["type"]
        required = field.get("required", False)
        value = data.get(field_id)
        
        # Check required fields
        if required and (value is None or value == ""):
            errors.append(f"{field['label']} is required")
            continue
        
        # Skip validation if field is empty and not required
        if value is None or value == "":
            continue
        
        # Type-specific validation
        if field_type == "email":
            if "@" not in str(value):
                errors.append(f"{field['label']} must be a valid email")
        
        elif field_type == "number":
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(f"{field['label']} must be a number")
        
        elif field_type in ["select", "radio"]:
            options = field.get("options", [])
            if value not in options:
                errors.append(f"{field['label']} must be one of: {', '.join(options)}")
        
        elif field_type == "checkbox":
            options = field.get("options", [])
            if isinstance(value, list):
                for v in value:
                    if v not in options:
                        errors.append(f"Invalid option for {field['label']}: {v}")
            else:
                errors.append(f"{field['label']} must be a list")
    
    return errors

async def analyze_field_responses(form_id: str, field_id: str) -> Dict[str, Any]:
    """Analyze responses for a specific form field"""
    try:
        form_submissions_collection = get_form_submissions_collection()
        
        # Get all responses for this field
        submissions = await form_submissions_collection.find(
            {"form_id": form_id},
            {"data": 1}
        ).to_list(length=None)
        
        responses = []
        for submission in submissions:
            field_value = submission.get("data", {}).get(field_id)
            if field_value is not None:
                responses.append(field_value)
        
        # Analyze responses
        if not responses:
            return {"total_responses": 0}
        
        # Count occurrences
        response_counts = {}
        for response in responses:
            if isinstance(response, list):
                # For checkbox fields
                for item in response:
                    response_counts[item] = response_counts.get(item, 0) + 1
            else:
                response_counts[response] = response_counts.get(response, 0) + 1
        
        return {
            "total_responses": len(responses),
            "response_distribution": response_counts
        }
        
    except Exception:
        return {"total_responses": 0}

async def create_form_analytics_record(form_id: str, user_id: str):
    """Create initial analytics record for form"""
    try:
        form_analytics_collection = get_form_analytics_collection()
        
        analytics_doc = {
            "_id": str(uuid.uuid4()),
            "form_id": form_id,
            "user_id": user_id,
            "total_views": 0,
            "total_submissions": 0,
            "conversion_rate": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await form_analytics_collection.insert_one(analytics_doc)
        
    except Exception as e:
        print(f"Failed to create form analytics record: {e}")