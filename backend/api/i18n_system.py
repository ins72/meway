"""
Internationalization & Localization API
Comprehensive multi-language support system
"""

from fastapi import APIRouter, HTTPException, Depends, status, Form, Query
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime

from core.auth import get_current_user
from core.database import get_database
from services.i18n_service import I18nService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

@router.get("/languages")
async def get_supported_languages():
    """Get all supported languages for internationalization"""
    try:
        languages = await I18nService.get_supported_languages()
        return {"success": True, "data": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/translations/{language}")
async def get_translations(language: str):
    """Get all translations for a specific language"""
    try:
        translations = await I18nService.get_translations(language)
        if not translations:
            raise HTTPException(status_code=404, detail="Language not supported")
        return {"success": True, "data": translations}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-language")
async def detect_user_language(
    user_agent: str = Form(""),
    accept_language: str = Form(""),
    ip_address: str = Form(""),
    timezone: str = Form(""),
    current_user: Optional[dict] = Depends(lambda: None)  # Optional auth
):
    """Detect user's preferred language"""
    try:
        detection_result = await I18nService.detect_user_language(
            user_agent=user_agent,
            accept_language=accept_language,
            ip_address=ip_address,
            timezone=timezone,
            user_preference=current_user.get("language") if current_user else None
        )
        return {"success": True, "data": detection_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-language")
async def set_user_language(
    language: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Set user's preferred language"""
    try:
        result = await I18nService.set_user_language(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            language=language
        )
        return {"success": True, "data": result, "message": "Language preference updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-language")
async def get_user_language(
    current_user: dict = Depends(get_current_user)
):
    """Get user's language preference"""
    try:
        language = await I18nService.get_user_language(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": {"language": language}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate")
async def translate_text(
    text: str = Form(...),
    source_language: str = Form("auto"),
    target_language: str = Form(...),
    context: str = Form("general"),
    current_user: Optional[dict] = Depends(lambda: None)  # Optional auth
):
    """Translate text using advanced translation services"""
    try:
        translation = await I18nService.translate_text(
            text=text,
            source_language=source_language,
            target_language=target_language,
            context=context
        )
        return {"success": True, "data": translation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/localization/{language}")
async def get_localization_data(
    language: str,
    category: str = Query("all"),
    current_user: Optional[dict] = Depends(lambda: None)  # Optional auth
):
    """Get localization data for specific language and category"""
    try:
        localization_data = await I18nService.get_localization_data(
            language=language,
            category=category
        )
        return {"success": True, "data": localization_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/currency/{country}")
async def get_currency_info(country: str):
    """Get currency information for a country"""
    try:
        currency_info = await I18nService.get_currency_info(country)
        return {"success": True, "data": currency_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timezone/{location}")
async def get_timezone_info(location: str):
    """Get timezone information for a location"""
    try:
        timezone_info = await I18nService.get_timezone_info(location)
        return {"success": True, "data": timezone_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/format/{language}")
async def get_format_patterns(language: str):
    """Get date, time, and number formatting patterns for a language"""
    try:
        formats = await I18nService.get_format_patterns(language)
        return {"success": True, "data": formats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace-language")
async def set_workspace_language(
    language: str = Form(...),
    timezone: str = Form("UTC"),
    currency: str = Form("USD"),
    date_format: str = Form("YYYY-MM-DD"),
    current_user: dict = Depends(get_current_user)
):
    """Set workspace localization settings"""
    try:
        result = await I18nService.set_workspace_language(
            user_id=current_user.get("_id") or current_user.get("id", "default-user"),
            language=language,
            timezone=timezone,
            currency=currency,
            date_format=date_format
        )
        return {"success": True, "data": result, "message": "Workspace language settings updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workspace-language")
async def get_workspace_language(
    current_user: dict = Depends(get_current_user)
):
    """Get workspace localization settings"""
    try:
        settings = await I18nService.get_workspace_language(
            user_id=current_user.get("_id") or current_user.get("id", "default-user")
        )
        return {"success": True, "data": settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))