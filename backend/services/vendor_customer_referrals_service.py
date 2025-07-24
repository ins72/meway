"""
Vendor Customer Referrals Service
Business logic for vendor customer referral programs
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from core.objectid_serializer import safe_document_return, safe_documents_return, serialize_objectid

logger = logging.getLogger(__name__)

class VendorCustomerReferralsService:
    """Service for managing vendor customer referral programs"""
    
    def __init__(self):
        self.collection_name = "vendor_customer_referrals"
        self.payouts_collection = "referral_payouts"
        self.service_name = "vendor_customer_referrals"

    def _get_collection(self):
        """Get collection for database operations"""
        try:
            from core.database import get_database
            db = get_database()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            return None

    async def _get_collection_async(self):
        """Get collection for async database operations"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.collection_name]
        except Exception as e:
            logger.error(f"Error getting async collection: {e}")
            return None

    async def _get_payouts_collection_async(self):
        """Get payouts collection for async database operations"""
        try:
            from core.database import get_database_async
            db = await get_database_async()
            if db is None:
                logger.error("Database not available")
                return None
            return db[self.payouts_collection]
        except Exception as e:
            logger.error(f"Error getting async payouts collection: {e}")
            return None

    async def health_check(self) -> dict:
        """Health check for vendor customer referrals service"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "healthy": False, "error": "Database unavailable"}
            
            await collection.count_documents({})
            
            return {
                "success": True,
                "healthy": True,
                "service": self.service_name,
                "features": ["referral_programs", "tracking", "payouts", "analytics"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check error in {self.service_name}: {e}")
            return {"success": False, "healthy": False, "error": str(e)}

    async def create_referral_program(self, data: dict) -> dict:
        """Create vendor customer referral program"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            # Generate referral code
            referral_code = f"REF_{str(uuid.uuid4())[:8].upper()}"
            
            program_data = {
                "id": str(uuid.uuid4()),
                "vendor_id": data.get("vendor_id"),
                "workspace_id": data.get("workspace_id"),
                "program_name": data.get("program_name", "Customer Referral Program"),
                "description": data.get("description", ""),
                "referral_code": referral_code,
                "referral_type": data.get("referral_type", "percentage"), # percentage or flat_fee
                "referral_percentage": data.get("referral_percentage", 10.0), # 10% default
                "flat_fee_amount": data.get("flat_fee_amount", 0.0),
                "minimum_purchase": data.get("minimum_purchase", 0.0),
                "maximum_reward": data.get("maximum_reward", 1000.0),
                "referral_duration_days": data.get("referral_duration_days", 30),
                "status": "active",
                "currency": data.get("currency", "USD"),
                "terms_conditions": data.get("terms_conditions", ""),
                "auto_approve_payouts": data.get("auto_approve_payouts", False),
                "mewayz_commission_rate": 0.10, # 10% of referral rewards go to Mewayz
                "analytics": {
                    "total_referrals": 0,
                    "successful_referrals": 0,
                    "total_referral_revenue": 0.0,
                    "total_rewards_paid": 0.0,
                    "pending_rewards": 0.0,
                    "mewayz_commission_earned": 0.0
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = await collection.insert_one(program_data)
            
            if result.inserted_id:
                program_data["_id"] = result.inserted_id
                return {
                    "success": True,
                    "data": safe_document_return(program_data),
                    "message": "Referral program created successfully"
                }
            else:
                return {"success": False, "error": "Failed to create referral program"}
                
        except Exception as e:
            logger.error(f"Create referral program error: {e}")
            return {"success": False, "error": str(e)}

    async def get_referral_program(self, program_id: str, vendor_id: str) -> dict:
        """Get referral program by ID"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            program = await collection.find_one({
                "id": program_id,
                "vendor_id": vendor_id
            })
            
            if program:
                return {
                    "success": True,
                    "data": safe_document_return(program)
                }
            else:
                return {"success": False, "error": "Referral program not found"}
                
        except Exception as e:
            logger.error(f"Get referral program error: {e}")
            return {"success": False, "error": str(e)}

    async def update_referral_program(self, program_id: str, data: dict) -> dict:
        """Update referral program"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            update_data = {}
            updatable_fields = [
                "program_name", "description", "referral_type", "referral_percentage",
                "flat_fee_amount", "minimum_purchase", "maximum_reward", 
                "referral_duration_days", "status", "terms_conditions", "auto_approve_payouts"
            ]
            
            for field in updatable_fields:
                if field in data:
                    update_data[field] = data[field]
            
            if update_data:
                update_data["updated_at"] = datetime.utcnow().isoformat()
                
                result = await collection.update_one(
                    {"id": program_id, "vendor_id": data.get("vendor_id")},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    updated_program = await collection.find_one({
                        "id": program_id,
                        "vendor_id": data.get("vendor_id")
                    })
                    return {
                        "success": True,
                        "data": safe_document_return(updated_program),
                        "message": "Referral program updated successfully"
                    }
                else:
                    return {"success": False, "error": "No changes made or program not found"}
            else:
                return {"success": False, "error": "No valid fields to update"}
                
        except Exception as e:
            logger.error(f"Update referral program error: {e}")
            return {"success": False, "error": str(e)}

    async def delete_referral_program(self, program_id: str, vendor_id: str) -> dict:
        """Delete referral program"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            result = await collection.delete_one({
                "id": program_id,
                "vendor_id": vendor_id
            })
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Referral program deleted successfully"
                }
            else:
                return {"success": False, "error": "Referral program not found"}
                
        except Exception as e:
            logger.error(f"Delete referral program error: {e}")
            return {"success": False, "error": str(e)}

    async def list_referral_programs(self, vendor_id: str, limit: int = 50, offset: int = 0) -> dict:
        """List vendor's referral programs"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            cursor = collection.find({"vendor_id": vendor_id})
            programs = await cursor.skip(offset).limit(limit).to_list(length=limit)
            
            total_count = await collection.count_documents({"vendor_id": vendor_id})
            
            return {
                "success": True,
                "data": safe_documents_return(programs),
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"List referral programs error: {e}")
            return {"success": False, "error": str(e)}

    async def generate_referral_link(self, data: dict) -> dict:
        """Generate referral link for customer"""
        try:
            referral_id = str(uuid.uuid4())
            base_url = data.get("base_url", "https://store.example.com")
            program_id = data.get("program_id")
            customer_id = data.get("customer_id")
            
            referral_link = f"{base_url}?ref={referral_id}"
            
            # Store referral link info
            referral_data = {
                "referral_id": referral_id,
                "program_id": program_id,
                "customer_id": customer_id,
                "referral_link": referral_link,
                "clicks": 0,
                "conversions": 0,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # You might want to store this in a separate referral_links collection
            
            return {
                "success": True,
                "data": {
                    "referral_id": referral_id,
                    "referral_link": referral_link,
                    "program_id": program_id
                },
                "message": "Referral link generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Generate referral link error: {e}")
            return {"success": False, "error": str(e)}

    async def process_referral_purchase(self, data: dict) -> dict:
        """Process purchase with referral tracking"""
        try:
            collection = await self._get_collection_async()
            payouts_collection = await self._get_payouts_collection_async()
            
            if collection is None or payouts_collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            referral_id = data.get("referral_id")
            order_value = float(data.get("order_value", 0))
            program_id = data.get("program_id")
            
            # Get referral program
            program = await collection.find_one({"id": program_id})
            if not program:
                return {"success": False, "error": "Referral program not found"}
            
            # Calculate referral reward
            if program["referral_type"] == "percentage":
                referral_reward = (order_value * program["referral_percentage"]) / 100
            else:
                referral_reward = program["flat_fee_amount"]
            
            # Apply maximum reward limit
            referral_reward = min(referral_reward, program["maximum_reward"])
            
            # Calculate Mewayz commission (10% of referral reward)
            mewayz_commission = referral_reward * 0.10
            net_reward = referral_reward - mewayz_commission
            
            # Create payout record
            payout_data = {
                "id": str(uuid.uuid4()),
                "referral_id": referral_id,
                "program_id": program_id,
                "vendor_id": program["vendor_id"],
                "customer_id": data.get("referrer_customer_id"),
                "order_id": data.get("order_id"),
                "order_value": order_value,
                "referral_reward": referral_reward,
                "mewayz_commission": mewayz_commission,
                "net_reward": net_reward,
                "status": "pending" if not program["auto_approve_payouts"] else "approved",
                "currency": program["currency"],
                "created_at": datetime.utcnow().isoformat(),
                "processed_at": None
            }
            
            # Store payout
            await payouts_collection.insert_one(payout_data)
            
            # Update program analytics
            await collection.update_one(
                {"id": program_id},
                {
                    "$inc": {
                        "analytics.successful_referrals": 1,
                        "analytics.total_referral_revenue": order_value,
                        "analytics.total_rewards_paid": referral_reward,
                        "analytics.pending_rewards": referral_reward if payout_data["status"] == "pending" else 0,
                        "analytics.mewayz_commission_earned": mewayz_commission
                    },
                    "$set": {"updated_at": datetime.utcnow().isoformat()}
                }
            )
            
            return {
                "success": True,
                "data": {
                    "payout_id": payout_data["id"],
                    "referral_reward": referral_reward,
                    "mewayz_commission": mewayz_commission,
                    "net_reward": net_reward,
                    "status": payout_data["status"]
                },
                "message": "Referral purchase processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Process referral purchase error: {e}")
            return {"success": False, "error": str(e)}

    async def get_referral_analytics(self, program_id: str, vendor_id: str, days: int = 30) -> dict:
        """Get referral program analytics"""
        try:
            collection = await self._get_collection_async()
            if collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            program = await collection.find_one({
                "id": program_id,
                "vendor_id": vendor_id
            })
            
            if not program:
                return {"success": False, "error": "Referral program not found"}
            
            # Get analytics from program document
            analytics = program.get("analytics", {})
            
            # Add time-based analytics if needed
            # This could be enhanced to query actual referral transactions
            
            return {
                "success": True,
                "data": {
                    "program_id": program_id,
                    "analytics": analytics,
                    "period_days": days,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Get referral analytics error: {e}")
            return {"success": False, "error": str(e)}

    async def get_referral_payouts(self, vendor_id: str, limit: int = 50, offset: int = 0, status: Optional[str] = None) -> dict:
        """Get referral payouts for vendor"""
        try:
            payouts_collection = await self._get_payouts_collection_async()
            if payouts_collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            query = {"vendor_id": vendor_id}
            if status:
                query["status"] = status
            
            cursor = payouts_collection.find(query).sort("created_at", -1)
            payouts = await cursor.skip(offset).limit(limit).to_list(length=limit)
            
            total_count = await payouts_collection.count_documents(query)
            
            return {
                "success": True,
                "data": safe_documents_return(payouts),
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Get referral payouts error: {e}")
            return {"success": False, "error": str(e)}

    async def process_referral_payout(self, payout_id: str, processed_by: str) -> dict:
        """Process referral payout (admin function)"""
        try:
            payouts_collection = await self._get_payouts_collection_async()
            if payouts_collection is None:
                return {"success": False, "error": "Database unavailable"}
            
            result = await payouts_collection.update_one(
                {"id": payout_id, "status": "pending"},
                {
                    "$set": {
                        "status": "processed",
                        "processed_at": datetime.utcnow().isoformat(),
                        "processed_by": processed_by
                    }
                }
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": "Payout processed successfully"
                }
            else:
                return {"success": False, "error": "Payout not found or already processed"}
                
        except Exception as e:
            logger.error(f"Process referral payout error: {e}")
            return {"success": False, "error": str(e)}


def get_vendor_customer_referrals_service():
    """Get vendor customer referrals service instance"""
    return VendorCustomerReferralsService()