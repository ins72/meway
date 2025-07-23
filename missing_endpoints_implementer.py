#!/usr/bin/env python3
"""
MISSING ENDPOINTS IMPLEMENTER
Adds critical missing endpoints for Template, Social Media, and Mobile PWA systems
"""

import os

class MissingEndpointsImplementer:
    def __init__(self, backend_path="/app/backend"):
        self.backend_path = backend_path
    
    def add_templates_api_endpoints(self):
        """Add missing /templates endpoints to main router"""
        print("🔧 Adding missing /templates API endpoints...")
        
        templates_api_content = '''"""
Generic Templates API - Missing endpoints fix
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.advanced_template_marketplace_service import AdvancedTemplateMarketplaceService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Service instance
template_service = AdvancedTemplateMarketplaceService()

# Request Models
class TemplateCreateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    category: str = Field(..., description="Template category")
    price: float = Field(0.0, ge=0)
    tags: List[str] = Field([], max_items=10)

@router.get("/templates", tags=["Templates"])
async def get_templates(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Get templates with pagination and filtering"""
    try:
        filters = {}
        if category:
            filters["category"] = category
        
        skip = (page - 1) * per_page
        
        result = await template_service.get_templates(
            filters=filters,
            limit=per_page,
            skip=skip
        )
        
        return {
            "success": True,
            **result,
            "message": "Templates retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates", tags=["Templates"])
async def create_template(
    request: TemplateCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new template"""
    try:
        # Normalize title/name
        data = request.dict()
        if not data.get('title') and data.get('name'):
            data['title'] = data['name']
        elif not data.get('title'):
            data['title'] = "Untitled Template"
        
        template = await template_service.create_template(
            creator_id=current_user["_id"],
            data=data
        )
        
        return {
            "success": True,
            "template": template,
            "message": "Template created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}", tags=["Templates"])
async def get_template(template_id: str):
    """Get specific template by ID"""
    try:
        template = await template_service.get_template_by_id(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "template": template,
            "message": "Template retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/templates/{template_id}", tags=["Templates"])
async def update_template(
    template_id: str,
    request: TemplateCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update template"""
    try:
        # Verify ownership
        template = await template_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if template.get("creator_id") != current_user["_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to update this template")
        
        updates = request.dict(exclude_unset=True)
        updated_template = await template_service.update_template(template_id, updates)
        
        return {
            "success": True,
            "template": updated_template,
            "message": "Template updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}", tags=["Templates"])
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete template"""
    try:
        # Verify ownership
        template = await template_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if template.get("creator_id") != current_user["_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this template")
        
        success = await template_service.delete_template(template_id)
        
        if success:
            return {
                "success": True,
                "message": "Template deleted successfully",
                "template_id": template_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to delete template")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
'''
        
        # Write the templates API file
        templates_api_path = os.path.join(self.backend_path, "api", "templates.py")
        with open(templates_api_path, 'w', encoding='utf-8') as f:
            f.write(templates_api_content)
        
        print(f"  ✅ Created {templates_api_path}")
    
    def update_main_py(self):
        """Add missing endpoints to main.py router registration"""
        print("🔧 Updating main.py to include new endpoints...")
        
        main_py_path = os.path.join(self.backend_path, "main.py")
        
        try:
            with open(main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add new router includes after the existing ones
            new_router_code = '''
# Include Templates CRUD router
try:
    from api.templates import router as templates_router
    app.include_router(templates_router, prefix="/api/templates", tags=["Templates"])
    included_count += 1
    print("  ✅ Included Templates CRUD router at /api/templates")
except Exception as e:
    print(f"  ❌ Failed to include Templates router: {str(e)}")
'''
            
            # Find a good place to insert the new router code
            insert_point = content.find('print(f"📊 Platform ready with {included_count} operational API endpoints!")')
            if insert_point != -1:
                content = content[:insert_point] + new_router_code + '\n' + content[insert_point:]
                
                with open(main_py_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  ✅ Updated {main_py_path}")
                return True
            else:
                print(f"  ⚠️  Could not find insertion point in main.py")
                return False
                
        except Exception as e:
            print(f"  ❌ Error updating main.py: {str(e)}")
            return False
    
    def run(self):
        """Execute missing endpoints implementation"""
        print("🚀 IMPLEMENTING MISSING ENDPOINTS")
        print("=" * 50)
        
        self.add_templates_api_endpoints()
        self.update_main_py()
        
        print(f"\n✅ MISSING ENDPOINTS IMPLEMENTATION COMPLETE!")
        print("=" * 50)

def main():
    implementer = MissingEndpointsImplementer()
    implementer.run()

if __name__ == "__main__":
    main()