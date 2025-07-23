"""
Integration API Routes

Provides API endpoints for third-party integrations and
integration management functionality.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from services.integration_service import integration_service
from core.auth import get_current_user
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/integration", tags=["Integrations"])

@router.get("/available")
async def get_available_integrations(current_user: dict = Depends(get_current_user)):
    """Get list of available integrations"""
    return await integration_service.get_available_integrations()

@router.get("/connected")
async def get_connected_integrations(current_user: dict = Depends(get_current_user)):
    """Get user's connected integrations"""
    user_id = current_user.get("user_id")
    return await integration_service.get_connected_integrations(user_id)

@router.post("/connect")
async def connect_integration(
    integration_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Connect a new integration"""
    user_id = current_user.get("user_id")
    return await integration_service.connect_integration(user_id, integration_data)

@router.post("/disconnect/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Disconnect an existing integration"""
    return await integration_service.disconnect_integration(integration_id)

@router.get("/{integration_id}/status")
async def get_integration_status(
    integration_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status of a specific integration"""
    return await integration_service.get_integration_status(integration_id)

@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually sync an integration"""
    return await integration_service.sync_integration(integration_id)

@router.get("/{integration_id}/logs")
async def get_integration_logs(
    integration_id: str,
    current_user: dict = Depends(get_current_user),
    limit: Optional[int] = 50
):
    """Get integration sync logs"""
    return await integration_service.get_integration_logs(integration_id, limit)

@router.put("/{integration_id}/settings")
async def update_integration_settings(
    integration_id: str,
    settings: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update integration settings"""
    return await integration_service.update_integration_settings(integration_id, settings)