"""
CRM Management Services Business Logic
Professional Mewayz Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.database import get_database
import uuid

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
