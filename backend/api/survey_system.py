"""
Survey & Feedback System API
Comprehensive survey creation and management system
"""

from fastapi import APIRouter, HTTPException, Depends, status, Form
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime

from core.auth import get_current_user
from core.database import get_database
from services.survey_service import SurveyService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

@router.get("")
async def get_surveys(current_user: dict = Depends(get_current_user)):
    """Get all surveys for the workspace"""
    try:
        user_id = current_user.get("_id") or current_user.get("id", "default-user")
        surveys = await SurveyService.get_workspace_surveys(user_id)
        return {"success": True, "data": surveys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_survey(
    title: str = Form(...),
    description: str = Form(""),
    questions: str = Form(...),  # JSON string
    settings: str = Form("{}"),  # JSON string for survey settings
    current_user: dict = Depends(get_current_user)
):
    """Create a new survey"""
    try:
        user_id = current_user.get("_id") or current_user.get("id", "default-user")
        questions_data = json.loads(questions)
        settings_data = json.loads(settings)
        
        survey = await SurveyService.create_survey(
            user_id=user_id,
            title=title,
            description=description,
            questions=questions_data,
            settings=settings_data
        )
        return {"success": True, "data": survey}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in questions or settings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{survey_id}")
async def get_survey(
    survey_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific survey"""
    try:
        user_id = current_user.get("_id") or current_user.get("id", "default-user")
        survey = await SurveyService.get_survey(survey_id, user_id)
        if not survey:
            raise HTTPException(status_code=404, detail="Survey not found")
        return {"success": True, "data": survey}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{survey_id}")
async def update_survey(
    survey_id: str,
    title: str = Form(None),
    description: str = Form(None),
    questions: str = Form(None),
    settings: str = Form(None),
    status: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Update a survey"""
    try:
        user_id = current_user.get("_id") or current_user.get("id", "default-user")
        updates = {}
        if title:
            updates["title"] = title
        if description:
            updates["description"] = description
        if questions:
            updates["questions"] = json.loads(questions)
        if settings:
            updates["settings"] = json.loads(settings)
        if status:
            updates["status"] = status
            
        survey = await SurveyService.update_survey(survey_id, user_id, updates)
        return {"success": True, "data": survey}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in questions or settings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{survey_id}")
async def delete_survey(
    survey_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a survey"""
    try:
        user_id = current_user.get("_id") or current_user.get("id", "default-user")
        result = await SurveyService.delete_survey(survey_id, user_id)
        return {"success": True, "message": "Survey deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{survey_id}/responses")
async def submit_survey_response(
    survey_id: str,
    responses: str = Form(...),  # JSON string
    respondent_email: str = Form(None),
    respondent_name: str = Form(None)
):
    """Submit a response to a survey (public endpoint)"""
    try:
        responses_data = json.loads(responses)
        
        response = await SurveyService.submit_response(
            survey_id=survey_id,
            responses=responses_data,
            respondent_email=respondent_email,
            respondent_name=respondent_name
        )
        return {"success": True, "data": response, "message": "Response submitted successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in responses")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{survey_id}/responses")
async def get_survey_responses(
    survey_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all responses for a survey"""
    try:
        user_id = current_user.get("_id") or current_user.get("id", "default-user")
        responses = await SurveyService.get_survey_responses(survey_id, user_id)
        return {"success": True, "data": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{survey_id}/analytics")
async def get_survey_analytics(
    survey_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a survey"""
    try:
        user_id = current_user.get("_id") or current_user.get("id", "default-user")
        analytics = await SurveyService.get_survey_analytics(survey_id, user_id)
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{survey_id}/export")
async def export_survey_responses(
    survey_id: str,
    format: str = "csv",
    current_user: dict = Depends(get_current_user)
):
    """Export survey responses"""
    try:
        user_id = current_user.get("_id") or current_user.get("id", "default-user")
        export_data = await SurveyService.export_responses(survey_id, user_id, format)
        return {"success": True, "data": export_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_survey_templates():
    """Get survey templates"""
    try:
        templates = await SurveyService.get_survey_templates()
        return {"success": True, "data": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))