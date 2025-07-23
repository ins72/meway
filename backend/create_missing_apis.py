#!/usr/bin/env python3
"""
Create Missing API Modules
Generates missing API modules with proper router structure
"""

import os
import sys

def generate_api_template(module_name: str) -> str:
    """Generate a clean API template with proper router structure"""
    service_name = f"{module_name}_service"
    class_name = ''.join(word.capitalize() for word in module_name.split('_'))
    
    return f'''"""
{module_name.title().replace('_', ' ')} API
RESTful endpoints for {module_name}
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, Any, List, Optional
from core.auth import get_current_user
from services.{service_name} import get_{module_name}_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{
        "status": "healthy",
        "service": "{module_name}",
        "message": "{module_name.title().replace('_', ' ')} API is operational"
    }}

@router.post("/")
async def create_{module_name}(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create new {module_name}"""
    try:
        service = get_{module_name}_service()
        result = await service.create_{module_name}(data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Creation failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_{module_name}s(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """List {module_name}s with pagination"""
    try:
        service = get_{module_name}_service()
        result = await service.list_{module_name}s(
            user_id=current_user.get("id"),
            limit=limit,
            offset=offset
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "List failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{{item_id}}")
async def get_{module_name}(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get {module_name} by ID"""
    try:
        service = get_{module_name}_service()
        result = await service.get_{module_name}(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{{item_id}}")
async def update_{module_name}(
    item_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update {module_name} by ID"""
    try:
        service = get_{module_name}_service()
        result = await service.update_{module_name}(item_id, data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{{item_id}}")
async def delete_{module_name}(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete {module_name} by ID"""
    try:
        service = get_{module_name}_service()
        result = await service.delete_{module_name}(item_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_{module_name}_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get {module_name} statistics"""
    try:
        service = get_{module_name}_service()
        result = await service.get_stats(user_id=current_user.get("id"))
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Stats failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''

def create_missing_apis():
    """Create all missing API modules"""
    api_dir = '/app/backend/api'
    
    # Expected API modules from main.py
    all_modules = [
        'admin', 'advanced_ai', 'advanced_ai_analytics', 'advanced_ai_suite', 'advanced_analytics', 
        'advanced_financial', 'advanced_financial_analytics', 'ai', 'ai_content', 'ai_content_generation', 
        'ai_token_management', 'analytics', 'analytics_system', 'auth', 'automation_system',
        'backup_system', 'bio_sites', 'blog', 'business_intelligence',
        'compliance_system', 'content', 'content_creation', 'content_creation_suite',
        'course_management', 'crm_management', 'customer_experience', 'customer_experience_suite',
        'dashboard', 'email_marketing', 'escrow_system',
        'form_builder', 'google_oauth', 'i18n_system', 'integration',
        'integrations', 'link_shortener', 'marketing', 'media', 'media_library',
        'monitoring_system', 'notification_system', 'promotions_referrals',
        'rate_limiting_system', 'realtime_notifications', 'social_email', 'social_email_integration', 
        'social_media', 'social_media_suite', 'support_system', 'survey_system',
        'team_management', 'template_marketplace', 'user',
        'webhook_system', 'workflow_automation'
    ]
    
    # Get existing API files
    existing_files = set()
    for file in os.listdir(api_dir):
        if file.endswith('.py') and not file.startswith('__'):
            existing_files.add(file.replace('.py', ''))
    
    # Find missing modules
    missing_modules = []
    for module in all_modules:
        if module not in existing_files:
            missing_modules.append(module)
    
    print(f"Found {len(missing_modules)} missing API modules")
    
    # Create missing modules
    for module in missing_modules:
        api_file = os.path.join(api_dir, f"{module}.py")
        api_content = generate_api_template(module)
        
        with open(api_file, 'w') as f:
            f.write(api_content)
        
        print(f"✅ Created {module}.py")
    
    print(f"\n✅ Created {len(missing_modules)} missing API modules")
    return missing_modules

if __name__ == "__main__":
    print("🚀 Creating Missing API Modules...")
    created_modules = create_missing_apis()
    
    if created_modules:
        print("\n📋 Created modules:")
        for module in created_modules:
            print(f"  - {module}")
    
    print("\n✅ All API modules are now available!")