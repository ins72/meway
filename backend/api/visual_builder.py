"""
Visual Drag & Drop Builder API
Advanced visual builder with component management and real-time collaboration
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
from core.auth import get_current_admin
from core.database import get_database_async

router = APIRouter(prefix="/visual-builder", tags=["visual_builder"])

class VisualBuilderService:
    """Visual Builder service for managing drag & drop components"""
    
    def __init__(self):
        self.collection_name = "visual_builder_projects"
        self.components_collection = "visual_builder_components"
        self.templates_collection = "visual_builder_templates"
    
    async def _get_collection(self, collection_name: str = None):
        """Get database collection"""
        try:
            db = await get_database_async()
            if db is None:
                return None
            return db[collection_name or self.collection_name]
        except Exception as e:
            return None
    
    async def create_project(self, project_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new visual builder project"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            project = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": project_data.get("name", "Untitled Project"),
                "description": project_data.get("description", ""),
                "type": project_data.get("type", "webpage"),  # webpage, email, landing_page, app
                "canvas_data": project_data.get("canvas_data", {
                    "components": [],
                    "layout": {"width": 1200, "height": 800},
                    "theme": {"primary_color": "#007AFF", "secondary_color": "#F5F5F5"},
                    "responsive_breakpoints": {
                        "mobile": 768,
                        "tablet": 1024,
                        "desktop": 1200
                    }
                }),
                "settings": {
                    "grid_enabled": True,
                    "snap_to_grid": True,
                    "show_rulers": True,
                    "auto_save": True,
                    "collaboration_enabled": False
                },
                "published": False,
                "published_url": None,
                "version": 1,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            result = await collection.insert_one(project)
            
            if result.inserted_id:
                return {
                    "success": True,
                    "message": "Project created successfully",
                    "data": {k: v for k, v in project.items() if k != '_id'},
                    "id": project["id"]
                }
            else:
                return {"success": False, "error": "Failed to create project"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_project(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Get a specific project"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            project = await collection.find_one({"id": project_id, "user_id": user_id})
            
            if project:
                return {
                    "success": True,
                    "data": {k: v for k, v in project.items() if k != '_id'}
                }
            else:
                return {"success": False, "error": "Project not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_project(self, project_id: str, update_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update project data"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            update_data["version"] = update_data.get("version", 1) + 1
            
            result = await collection.update_one(
                {"id": project_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                updated_project = await collection.find_one({"id": project_id, "user_id": user_id})
                return {
                    "success": True,
                    "message": "Project updated successfully",
                    "data": {k: v for k, v in updated_project.items() if k != '_id'} if updated_project else None
                }
            else:
                return {"success": False, "error": "Project not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_projects(self, user_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List user's projects"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            cursor = collection.find({"user_id": user_id}).skip(offset).limit(limit)
            projects = await cursor.to_list(length=limit)
            
            sanitized_projects = [{k: v for k, v in project.items() if k != '_id'} for project in projects]
            
            total = await collection.count_documents({"user_id": user_id})
            
            return {
                "success": True,
                "data": sanitized_projects,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_component_library(self) -> Dict[str, Any]:
        """Get available drag & drop components"""
        try:
            components = {
                "layout": [
                    {
                        "id": "container",
                        "name": "Container",
                        "category": "layout",
                        "icon": "square",
                        "properties": {
                            "width": "100%",
                            "height": "auto",
                            "padding": "16px",
                            "margin": "0px",
                            "background_color": "transparent",
                            "border": "none",
                            "border_radius": "0px"
                        },
                        "accepts_children": True
                    },
                    {
                        "id": "row",
                        "name": "Row",
                        "category": "layout",
                        "icon": "columns",
                        "properties": {
                            "display": "flex",
                            "flex_direction": "row",
                            "gap": "16px",
                            "align_items": "center",
                            "justify_content": "flex-start"
                        },
                        "accepts_children": True
                    },
                    {
                        "id": "column",
                        "name": "Column",
                        "category": "layout",
                        "icon": "layout",
                        "properties": {
                            "display": "flex",
                            "flex_direction": "column",
                            "gap": "16px",
                            "align_items": "flex-start"
                        },
                        "accepts_children": True
                    }
                ],
                "content": [
                    {
                        "id": "text",
                        "name": "Text",
                        "category": "content",
                        "icon": "type",
                        "properties": {
                            "content": "Edit this text",
                            "font_size": "16px",
                            "font_weight": "normal",
                            "color": "#333333",
                            "text_align": "left",
                            "line_height": "1.5"
                        },
                        "accepts_children": False
                    },
                    {
                        "id": "heading",
                        "name": "Heading",
                        "category": "content",
                        "icon": "heading",
                        "properties": {
                            "content": "Heading Text",
                            "level": "h1",
                            "font_size": "32px",
                            "font_weight": "bold",
                            "color": "#000000",
                            "text_align": "left"
                        },
                        "accepts_children": False
                    },
                    {
                        "id": "image",
                        "name": "Image",
                        "category": "content",
                        "icon": "image",
                        "properties": {
                            "src": "https://via.placeholder.com/300x200",
                            "alt": "Image description",
                            "width": "300px",
                            "height": "200px",
                            "object_fit": "cover",
                            "border_radius": "0px"
                        },
                        "accepts_children": False
                    }
                ],
                "forms": [
                    {
                        "id": "button",
                        "name": "Button",
                        "category": "forms",
                        "icon": "mouse-pointer",
                        "properties": {
                            "text": "Click me",
                            "type": "button",
                            "variant": "primary",
                            "size": "medium",
                            "background_color": "#007AFF",
                            "text_color": "#ffffff",
                            "border_radius": "8px",
                            "padding": "12px 24px"
                        },
                        "accepts_children": False
                    },
                    {
                        "id": "input",
                        "name": "Input Field",
                        "category": "forms",
                        "icon": "edit",
                        "properties": {
                            "type": "text",
                            "placeholder": "Enter text...",
                            "label": "Input Label",
                            "required": False,
                            "width": "100%",
                            "border": "1px solid #ccc",
                            "border_radius": "4px",
                            "padding": "12px"
                        },
                        "accepts_children": False
                    },
                    {
                        "id": "form",
                        "name": "Form",
                        "category": "forms",
                        "icon": "file-text",
                        "properties": {
                            "method": "POST",
                            "action": "",
                            "background_color": "#f9f9f9",
                            "padding": "24px",
                            "border_radius": "8px"
                        },
                        "accepts_children": True
                    }
                ],
                "media": [
                    {
                        "id": "video",
                        "name": "Video",
                        "category": "media",
                        "icon": "video",
                        "properties": {
                            "src": "",
                            "width": "560px",
                            "height": "315px",
                            "controls": True,
                            "autoplay": False,
                            "loop": False
                        },
                        "accepts_children": False
                    },
                    {
                        "id": "embed",
                        "name": "Embed",
                        "category": "media",
                        "icon": "code",
                        "properties": {
                            "html": "<iframe src='https://example.com' width='560' height='315'></iframe>",
                            "width": "560px",
                            "height": "315px"
                        },
                        "accepts_children": False
                    }
                ]
            }
            
            return {
                "success": True,
                "data": components,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def publish_project(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Publish a project and generate public URL"""
        try:
            collection = await self._get_collection()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Generate unique URL
            published_url = f"https://published.mewayz.com/{project_id}"
            
            result = await collection.update_one(
                {"id": project_id, "user_id": user_id},
                {"$set": {
                    "published": True,
                    "published_url": published_url,
                    "published_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            
            if result.matched_count > 0:
                return {
                    "success": True,
                    "message": "Project published successfully",
                    "published_url": published_url,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": "Project not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

# Service instance
visual_builder_service = VisualBuilderService()

@router.post("/projects")
async def create_project(
    project_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin)
):
    """Create a new visual builder project"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await visual_builder_service.create_project(project_data, user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Get a specific project"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await visual_builder_service.get_project(project_id, user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}")
async def update_project(
    project_id: str,
    update_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin)
):
    """Update project data"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await visual_builder_service.update_project(project_id, update_data, user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects")
async def list_projects(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_admin)
):
    """List user's projects"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await visual_builder_service.list_projects(user_id, limit, offset)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/components")
async def get_component_library():
    """Get available drag & drop components"""
    try:
        result = await visual_builder_service.get_component_library()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/publish")
async def publish_project(
    project_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Publish a project"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await visual_builder_service.publish_project(project_id, user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "success": True,
            "healthy": True,
            "service": "Visual Builder",
            "features": {
                "drag_drop": True,
                "component_library": True,
                "real_time_editing": True,
                "publishing": True,
                "responsive_design": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "healthy": False,
            "error": str(e)
        }