"""
Templates Service
Auto-generated to complete service/API pairing
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database

class TemplatesService:
    def __init__(self):
        self.db = get_database()

    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new template"""
        try:
            # Add metadata
            template_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["templates"].insert_one(template_data)
            
            return {
                "success": True,
                "message": f"Template created successfully",
                "data": template_data,
                "id": template_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create template: {str(e)}"
            }

    async def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get template by ID"""
        try:
            result = await self.db["templates"].find_one({"id": template_id})
            
            if not result:
                return {
                    "success": False,
                    "error": f"Template not found"
                }
            
            # Remove MongoDB _id
            result.pop('_id', None)
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get template: {str(e)}"
            }

    async def list_templates(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List all templates"""
        try:
            cursor = self.db["templates"].find({}).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Remove MongoDB _id from all results
            for result in results:
                result.pop('_id', None)
            
            total_count = await self.db["templates"].count_documents({})
            
            return {
                "success": True,
                "data": results,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list templates: {str(e)}"
            }

    async def update_template(self, template_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update template by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["templates"].update_one(
                {"id": template_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Template not found"
                }
            
            # Get updated document
            updated_doc = await self.db["templates"].find_one({"id": template_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Template updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update template: {str(e)}"
            }

    async def delete_template(self, template_id: str) -> Dict[str, Any]:
        """Delete template by ID"""
        try:
            result = await self.db["templates"].delete_one({"id": template_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Template not found"
                }
            
            return {
                "success": True,
                "message": f"Template deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete template: {str(e)}"
            }
