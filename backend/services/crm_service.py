"""
CRM Management Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid


    async def update_crm(self, crm_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update crm by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["crm"].update_one(
                {"id": crm_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Crm not found"
                }
            
            # Get updated document
            updated_doc = await self.db["crm"].find_one({"id": crm_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Crm updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update crm: {str(e)}"
            }

class CRMService:
    """Service for CRM operations"""
    
    @staticmethod
    async def get_contacts(user_id: str):
        """Get user's CRM contacts"""
        db = await get_database()
        
        contacts = await db.crm_contacts.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        return contacts
    
    @staticmethod
    async def create_contact(user_id: str, contact_data: Dict[str, Any]):
        """Create new CRM contact"""
        db = await get_database()
        
        contact = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "name": contact_data.get("name"),
    "email": contact_data.get("email"),
    "phone": contact_data.get("phone"),
    "company": contact_data.get("company"),
    "position": contact_data.get("position"),
    "status": contact_data.get("status", "lead"),
    "tags": contact_data.get("tags", []),
    "notes": contact_data.get("notes", ""),
    "last_contact": contact_data.get("last_contact"),
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
    }
        

    async def delete_crm(self, crm_id: str) -> Dict[str, Any]:
        """Delete crm by ID"""
        try:
            result = await self.db["crm"].delete_one({"id": crm_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Crm not found"
                }
            
            return {
                "success": True,
                "message": f"Crm deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete crm: {str(e)}"
            }

        result = await db.crm_contacts.insert_one(contact)
        return contact
    
    @staticmethod
    async def get_deals(user_id: str):
        """Get user's CRM deals"""
        db = await get_database()
        
        deals = await db.crm_deals.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        return deals
    
    @staticmethod
    async def create_deal(user_id: str, deal_data: Dict[str, Any]):
        """Create new CRM deal"""
        db = await get_database()
        
        deal = {
    "_id": str(uuid.uuid4()),
    "user_id": user_id,
    "contact_id": deal_data.get("contact_id"),
    "title": deal_data.get("title"),
    "value": deal_data.get("value", 0),
    "stage": deal_data.get("stage", "prospect"),
    "probability": deal_data.get("probability", 0),
    "expected_close": deal_data.get("expected_close"),
    "notes": deal_data.get("notes", ""),
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
    }
        
        result = await db.crm_deals.insert_one(deal)
        return deal

# Global service instance
crm_service = CRMService()
    async def update_contact(self, contact_id: str, user_id: str, updates: dict) -> dict:
        """Update contact"""
        try:
            db = get_database()
            if not db:
                return {"success": False, "message": "Database unavailable"}
            
            # Add update metadata
            updates["updated_at"] = datetime.utcnow()
            updates["updated_by"] = user_id
            
            result = await db.contacts.update_one(
                {"_id": contact_id, "user_id": user_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                updated_contact = await db.contacts.find_one({"_id": contact_id})
                return {"success": True, "contact": updated_contact, "message": "Contact updated successfully"}
            else:
                return {"success": False, "message": "Contact not found or unauthorized"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    async def delete_contact(self, contact_id: str, user_id: str) -> dict:
        """Delete contact (soft delete)"""
        try:
            db = get_database()
            if not db:
                return {"success": False, "message": "Database unavailable"}
            
            result = await db.contacts.update_one(
                {"_id": contact_id, "user_id": user_id},
                {
                    "$set": {
                        "deleted": True,
                        "deleted_at": datetime.utcnow(),
                        "deleted_by": user_id
                    }
                }
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Contact deleted successfully"}
            else:
                return {"success": False, "message": "Contact not found or unauthorized"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}

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