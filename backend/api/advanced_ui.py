"""
Advanced UI Components Backend API
Support for complex UI components like workspace wizard, goal selection, and interactive interfaces
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
from core.auth import get_current_admin
from core.database import get_database_async

router = APIRouter(tags=["advanced_ui"])

class AdvancedUIService:
    """Service for advanced UI components backend support"""
    
    def __init__(self):
        self.wizard_collection = "ui_wizard_sessions"
        self.goals_collection = "user_goals"
        self.ui_state_collection = "ui_state_management"
        self.component_configs_collection = "ui_component_configs"
    
    async def _get_collection(self, collection_name: str = None):
        """Get database collection"""
        try:
            db = await get_database_async()
            if db is None:
                return None
            return db[collection_name or self.wizard_collection]
        except Exception as e:
            return None
    
    async def create_wizard_session(self, wizard_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new wizard session"""
        try:
            collection = await self._get_collection(self.wizard_collection)
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            wizard_session = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "wizard_type": wizard_data.get("wizard_type", "workspace_setup"),
                "current_step": wizard_data.get("current_step", 1),
                "total_steps": wizard_data.get("total_steps", 5),
                "wizard_config": self._get_wizard_config(wizard_data.get("wizard_type", "workspace_setup")),
                "user_responses": wizard_data.get("user_responses", {}),
                "progress_percentage": wizard_data.get("progress_percentage", 0),
                "completion_status": "in_progress",
                "step_validation": wizard_data.get("step_validation", {}),
                "branching_logic": wizard_data.get("branching_logic", {}),
                "meta_data": {
                    "started_at": datetime.utcnow().isoformat(),
                    "last_activity": datetime.utcnow().isoformat(),
                    "device_info": wizard_data.get("device_info", {}),
                    "user_agent": wizard_data.get("user_agent", ""),
                    "session_duration": 0
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            result = await collection.insert_one(wizard_session)
            
            if result.inserted_id:
                return {
                    "success": True,
                    "message": "Wizard session created successfully",
                    "data": {k: v for k, v in wizard_session.items() if k != '_id'},
                    "session_id": wizard_session["id"]
                }
            else:
                return {"success": False, "error": "Failed to create wizard session"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_wizard_config(self, wizard_type: str) -> Dict[str, Any]:
        """Get wizard configuration based on type"""
        configs = {
            "workspace_setup": {
                "steps": [
                    {
                        "step": 1,
                        "title": "Welcome to Mewayz",
                        "description": "Let's set up your workspace",
                        "component": "welcome_screen",
                        "fields": [],
                        "validation": {"required": False}
                    },
                    {
                        "step": 2,
                        "title": "Business Information",
                        "description": "Tell us about your business",
                        "component": "business_info_form",
                        "fields": [
                            {"name": "business_name", "type": "text", "required": True, "label": "Business Name"},
                            {"name": "business_type", "type": "select", "required": True, "label": "Business Type", "options": ["Service", "Product", "E-commerce", "Content", "Other"]},
                            {"name": "industry", "type": "select", "required": True, "label": "Industry", "options": ["Technology", "Healthcare", "Finance", "Retail", "Education", "Other"]},
                            {"name": "business_size", "type": "select", "required": True, "label": "Business Size", "options": ["Solo", "2-10 employees", "11-50 employees", "51+ employees"]}
                        ],
                        "validation": {"required": True}
                    },
                    {
                        "step": 3,
                        "title": "Choose Your Goals",
                        "description": "What do you want to achieve?",
                        "component": "goals_selection",
                        "fields": [
                            {"name": "primary_goals", "type": "multi_select", "required": True, "label": "Primary Goals", 
                             "options": [
                                 {"id": "lead_generation", "label": "Lead Generation", "description": "Generate and manage leads"},
                                 {"id": "customer_management", "label": "Customer Management", "description": "Manage customer relationships"},
                                 {"id": "online_sales", "label": "Online Sales", "description": "Sell products/services online"},
                                 {"id": "content_creation", "label": "Content Creation", "description": "Create and manage content"},
                                 {"id": "social_media", "label": "Social Media Management", "description": "Manage social media presence"},
                                 {"id": "analytics", "label": "Analytics & Reporting", "description": "Track and analyze performance"}
                             ]},
                            {"name": "secondary_goals", "type": "multi_select", "required": False, "label": "Secondary Goals", 
                             "options": [
                                 {"id": "email_marketing", "label": "Email Marketing", "description": "Email campaigns and automation"},
                                 {"id": "appointment_booking", "label": "Appointment Booking", "description": "Schedule and manage appointments"},
                                 {"id": "financial_tracking", "label": "Financial Tracking", "description": "Track income and expenses"},
                                 {"id": "team_collaboration", "label": "Team Collaboration", "description": "Collaborate with team members"}
                             ]}
                        ],
                        "validation": {"required": True}
                    },
                    {
                        "step": 4,
                        "title": "Customize Your Workspace",
                        "description": "Set up your workspace preferences",
                        "component": "workspace_customization",
                        "fields": [
                            {"name": "workspace_name", "type": "text", "required": True, "label": "Workspace Name"},
                            {"name": "theme", "type": "select", "required": True, "label": "Theme", "options": ["Light", "Dark", "Auto"]},
                            {"name": "primary_color", "type": "color", "required": True, "label": "Primary Color", "default": "#007AFF"},
                            {"name": "time_zone", "type": "select", "required": True, "label": "Time Zone", "options": ["UTC", "EST", "PST", "CST", "MST"]},
                            {"name": "currency", "type": "select", "required": True, "label": "Currency", "options": ["USD", "EUR", "GBP", "CAD", "AUD"]}
                        ],
                        "validation": {"required": True}
                    },
                    {
                        "step": 5,
                        "title": "Setup Complete",
                        "description": "Your workspace is ready!",
                        "component": "completion_screen",
                        "fields": [],
                        "validation": {"required": False}
                    }
                ]
            },
            "goal_selection": {
                "steps": [
                    {
                        "step": 1,
                        "title": "Select Your Primary Goal",
                        "description": "Choose your main objective",
                        "component": "goal_selector",
                        "fields": [
                            {"name": "primary_goal", "type": "single_select", "required": True, "label": "Primary Goal",
                             "options": [
                                 {"id": "grow_business", "label": "Grow Business", "description": "Expand your customer base and revenue", "icon": "trending-up"},
                                 {"id": "manage_customers", "label": "Manage Customers", "description": "Organize and nurture customer relationships", "icon": "users"},
                                 {"id": "increase_sales", "label": "Increase Sales", "description": "Boost sales and conversions", "icon": "dollar-sign"},
                                 {"id": "improve_efficiency", "label": "Improve Efficiency", "description": "Streamline operations and processes", "icon": "zap"},
                                 {"id": "build_brand", "label": "Build Brand", "description": "Establish and strengthen brand presence", "icon": "star"},
                                 {"id": "analyze_performance", "label": "Analyze Performance", "description": "Track and optimize business metrics", "icon": "bar-chart"}
                             ]}
                        ],
                        "validation": {"required": True}
                    }
                ]
            },
            "onboarding": {
                "steps": [
                    {
                        "step": 1,
                        "title": "Welcome",
                        "description": "Welcome to the platform",
                        "component": "welcome",
                        "fields": [],
                        "validation": {"required": False}
                    },
                    {
                        "step": 2,
                        "title": "Profile Setup",
                        "description": "Set up your profile",
                        "component": "profile_form",
                        "fields": [
                            {"name": "first_name", "type": "text", "required": True, "label": "First Name"},
                            {"name": "last_name", "type": "text", "required": True, "label": "Last Name"},
                            {"name": "phone", "type": "tel", "required": False, "label": "Phone Number"},
                            {"name": "avatar", "type": "file", "required": False, "label": "Profile Picture"}
                        ],
                        "validation": {"required": True}
                    },
                    {
                        "step": 3,
                        "title": "Complete",
                        "description": "You're all set!",
                        "component": "completion",
                        "fields": [],
                        "validation": {"required": False}
                    }
                ]
            }
        }
        
        return configs.get(wizard_type, configs["workspace_setup"])
    
    async def update_wizard_session(self, session_id: str, update_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update wizard session"""
        try:
            collection = await self._get_collection(self.wizard_collection)
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Calculate progress
            current_step = update_data.get("current_step", 1)
            total_steps = update_data.get("total_steps", 5)
            progress_percentage = (current_step / total_steps) * 100
            
            update_data["progress_percentage"] = progress_percentage
            update_data["updated_at"] = datetime.utcnow().isoformat()
            update_data["meta_data.last_activity"] = datetime.utcnow().isoformat()
            
            # Check completion
            if current_step >= total_steps:
                update_data["completion_status"] = "completed"
                update_data["completed_at"] = datetime.utcnow().isoformat()
            
            result = await collection.update_one(
                {"id": session_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                updated_session = await collection.find_one({"id": session_id, "user_id": user_id})
                return {
                    "success": True,
                    "message": "Wizard session updated successfully",
                    "data": {k: v for k, v in updated_session.items() if k != '_id'} if updated_session else None
                }
            else:
                return {"success": False, "error": "Session not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def save_user_goals(self, goals_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Save user goals"""
        try:
            collection = await self._get_collection(self.goals_collection)
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            goals_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "primary_goals": goals_data.get("primary_goals", []),
                "secondary_goals": goals_data.get("secondary_goals", []),
                "goal_priorities": goals_data.get("goal_priorities", {}),
                "target_metrics": goals_data.get("target_metrics", {}),
                "timeline": goals_data.get("timeline", "3_months"),
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update existing goals or insert new ones
            result = await collection.update_one(
                {"user_id": user_id},
                {"$set": goals_record},
                upsert=True
            )
            
            return {
                "success": True,
                "message": "Goals saved successfully",
                "data": goals_record
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_ui_state(self, user_id: str, component_id: str) -> Dict[str, Any]:
        """Get UI component state"""
        try:
            collection = await self._get_collection(self.ui_state_collection)
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            state = await collection.find_one({"user_id": user_id, "component_id": component_id})
            
            if state:
                return {
                    "success": True,
                    "data": {k: v for k, v in state.items() if k != '_id'}
                }
            else:
                return {"success": False, "error": "State not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def save_ui_state(self, state_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Save UI component state"""
        try:
            collection = await self._get_collection(self.ui_state_collection)
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            component_id = state_data.get("component_id")
            if not component_id:
                return {"success": False, "error": "Component ID required"}
            
            state_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "component_id": component_id,
                "state_data": state_data.get("state_data", {}),
                "component_type": state_data.get("component_type", ""),
                "page_context": state_data.get("page_context", ""),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update existing state or insert new one
            result = await collection.update_one(
                {"user_id": user_id, "component_id": component_id},
                {"$set": state_record},
                upsert=True
            )
            
            return {
                "success": True,
                "message": "UI state saved successfully",
                "data": state_record
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_component_config(self, component_type: str) -> Dict[str, Any]:
        """Get component configuration"""
        try:
            configs = {
                "data_table": {
                    "columns": ["id", "name", "status", "created_at", "actions"],
                    "sorting": {"enabled": True, "default": "created_at"},
                    "filtering": {"enabled": True, "fields": ["name", "status"]},
                    "pagination": {"enabled": True, "page_size": 25},
                    "actions": ["view", "edit", "delete"],
                    "export": {"enabled": True, "formats": ["csv", "xlsx", "pdf"]}
                },
                "chart": {
                    "types": ["line", "bar", "pie", "doughnut", "area", "scatter"],
                    "data_sources": ["api", "static", "real_time"],
                    "customization": {"colors": True, "labels": True, "legend": True},
                    "interactivity": {"zoom": True, "hover": True, "click": True}
                },
                "form": {
                    "field_types": ["text", "email", "password", "number", "select", "multi_select", "checkbox", "radio", "textarea", "file", "date", "time", "color"],
                    "validation": {"client_side": True, "server_side": True},
                    "layout": {"columns": [1, 2, 3, 4], "responsive": True},
                    "submission": {"ajax": True, "redirect": True, "callback": True}
                },
                "calendar": {
                    "views": ["month", "week", "day", "agenda"],
                    "events": {"create": True, "edit": True, "delete": True, "drag_drop": True},
                    "integrations": ["google_calendar", "outlook", "ical"],
                    "notifications": {"email": True, "push": True, "sms": True}
                }
            }
            
            if component_type in configs:
                return {
                    "success": True,
                    "data": configs[component_type],
                    "component_type": component_type
                }
            else:
                return {"success": False, "error": "Component type not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

# Service instance
advanced_ui_service = AdvancedUIService()

@router.post("/wizard")
async def create_wizard_session(
    wizard_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin)
):
    """Create wizard session"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await advanced_ui_service.create_wizard_session(wizard_data, user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/wizard/{session_id}")
async def update_wizard_session(
    session_id: str,
    update_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin)
):
    """Update wizard session"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await advanced_ui_service.update_wizard_session(session_id, update_data, user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/goals")
async def save_user_goals(
    goals_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin)
):
    """Save user goals"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await advanced_ui_service.save_user_goals(goals_data, user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state/{component_id}")
async def get_ui_state(
    component_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Get UI component state"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await advanced_ui_service.get_ui_state(user_id, component_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/state")
async def save_ui_state(
    state_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin)
):
    """Save UI component state"""
    try:
        user_id = current_user.get("id") or current_user.get("email")
        result = await advanced_ui_service.save_ui_state(state_data, user_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/component/{component_type}/config")
async def get_component_config(
    component_type: str
):
    """Get component configuration"""
    try:
        result = await advanced_ui_service.get_component_config(component_type)
        
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
            "service": "Advanced UI Components",
            "features": {
                "wizard_sessions": True,
                "goal_selection": True,
                "ui_state_management": True,
                "component_configs": True,
                "interactive_interfaces": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "healthy": False,
            "error": str(e)
        }