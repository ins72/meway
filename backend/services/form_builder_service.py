"""
Form Builder Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

class FormBuilderService:
    """Service for form builder operations"""
    
    @staticmethod
    async def get_forms(user_id: str):
        """Get user's forms"""
        db = await get_database()
        
        forms = await db.forms.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        return forms
    
    @staticmethod
    async def create_form(user_id: str, form_data: Dict[str, Any]):
        """Create new form"""
        db = await get_database()
        
        form = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": form_data.get("title"),
            "description": form_data.get("description", ""),
            "fields": form_data.get("fields", []),
            "settings": {
                "allow_multiple_submissions": form_data.get("allow_multiple", True),
                "require_login": form_data.get("require_login", False),
                "success_message": form_data.get("success_message", "Thank you for your submission!"),
                "redirect_url": form_data.get("redirect_url")
            },
            "status": "active",
            "submission_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.forms.insert_one(form)
        return form
    
    @staticmethod
    async def get_form_submissions(user_id: str, form_id: str):
        """Get form submissions"""
        db = await get_database()
        
        # Verify form ownership
        form = await db.forms.find_one({"_id": form_id, "user_id": user_id})
        if not form:
            return []
        
        submissions = await db.form_submissions.find({
            "form_id": form_id
        }).sort("submitted_at", -1).to_list(length=None)
        
        return submissions
    
    @staticmethod
    async def submit_form(form_id: str, submission_data: Dict[str, Any], submitter_ip: str = None):
        """Submit form data"""
        db = await get_database()
        
        # Verify form exists and is active
        form = await db.forms.find_one({"_id": form_id, "status": "active"})
        if not form:
            return None
        
        submission = {
            "_id": str(uuid.uuid4()),
            "form_id": form_id,
            "data": submission_data,
            "submitter_ip": submitter_ip,
            "submitted_at": datetime.utcnow()
        }
        
        result = await db.form_submissions.insert_one(submission)
        
        # Update submission count
        await db.forms.update_one(
            {"_id": form_id},
            {"$inc": {"submission_count": 1}}
        )
        
        return submission

    async def create_form_builder(self, form_builder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create form_builder with real data persistence"""
        try:
            import uuid
            from datetime import datetime
            
            form_builder_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            db = await self.get_database()
            result = await db["form_builder"].insert_one(form_builder_data)
            
            return {
                "success": True,
                "message": f"Form_Builder created successfully",
                "data": form_builder_data,
                "id": form_builder_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create form_builder: {str(e)}"
            }

    async def update_form_builder(self, form_builder_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update form_builder with real data persistence"""
        try:
            from datetime import datetime
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db = await self.get_database()
            result = await db["form_builder"].update_one(
                {"id": form_builder_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {"success": False, "error": f"Form_Builder not found"}
            
            updated = await db["form_builder"].find_one({"id": form_builder_id})
            updated.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Form_Builder updated successfully",
                "data": updated
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to update form_builder: {str(e)}"}

    async def delete_form_builder(self, form_builder_id: str) -> Dict[str, Any]:
        """Delete form_builder with real data persistence"""
        try:
            db = await self.get_database()
            result = await db["form_builder"].delete_one({"id": form_builder_id})
            
            if result.deleted_count == 0:
                return {"success": False, "error": f"Form_Builder not found"}
            
            return {
                "success": True,
                "message": f"Form_Builder deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to delete form_builder: {str(e)}"}




# Global service instance
form_builder_service = FormBuilderService()

    async def get_item(self, user_id: str, item_id: str):
        """Get specific item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if not item:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "data": item,
                "message": "Item retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def update_item(self, user_id: str, item_id: str, update_data: dict):
        """Update existing item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collections['items'].update_one(
                {"_id": item_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                return {"success": False, "message": "Item not found or no changes made"}
            
            # Get updated item
            updated_item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            return {
                "success": True,
                "data": updated_item,
                "message": "Item updated successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def delete_item(self, user_id: str, item_id: str):
        """Delete item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['items'].delete_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "message": "Item deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_items(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's items"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['items'].find(query).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            
            total_count = await collections['items'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "items": items,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Items retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}