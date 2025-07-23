"""
Webhook Service
Production-ready service with comprehensive CRUD operations and real data
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from core.database import get_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self):
        self.service_name = "webhook"
        self.collection_name = "webhook"
        self.db = None
        self.collection = None
        
    def _get_db(self):
        """Get database connection with comprehensive error handling"""
        try:
            if self.db is None:
                self.db = get_database()
                if self.db is None:
                    raise ConnectionError("Database connection failed")
            return self.db
        except Exception as e:
            logger.error(f"Database connection error in {self.service_name}: {e}")
            return None
    
    def _get_collection(self):
        """Get collection with comprehensive error handling"""
        try:
            if self.collection is None:
                db = self._get_db()
                if db is None:
                    return None
                self.collection = db[self.collection_name]
            return self.collection
        except Exception as e:
            logger.error(f"Collection access error in {self.service_name}: {e}")
            return None
    
    def _validate_input(self, data: Any, required_fields: List[str] = None) -> Dict[str, Any]:
        """Comprehensive input validation"""
        try:
            if data is None:
                return {"success": False, "error": "Data cannot be None"}
            
            if not isinstance(data, dict):
                return {"success": False, "error": "Data must be a dictionary"}
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data or data[field] is None]
                if missing_fields:
                    return {"success": False, "error": f"Missing required fields: {', '.join(missing_fields)}"}
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Validation error: {str(e)}"}
    
    def _sanitize_response(self, doc: Any) -> Dict[str, Any]:
        """Sanitize database response for JSON serialization"""
        try:
            if not doc:
                return {}
            
            if isinstance(doc, dict):
                sanitized = {}
                for key, value in doc.items():
                    if key == '_id':
                        continue  # Skip MongoDB _id
                    elif isinstance(value, (str, int, float, bool, type(None))):
                        sanitized[key] = value
                    elif isinstance(value, (list, dict)):
                        sanitized[key] = value
                    else:
                        sanitized[key] = str(value)
                return sanitized
            
            return doc
        except Exception as e:
            logger.error(f"Error sanitizing response: {e}")
            return {}
    
    def _prepare_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for creation with all required fields"""
        try:
            prepared_data = data.copy()
            
            # Add system fields
            prepared_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active",
                "version": 1
            })
            
            # Add service-specific fields
            prepared_data["service_type"] = self.service_name
            
            return prepared_data
        except Exception as e:
            logger.error(f"Error preparing create data: {e}")
            return data
    
    def _handle_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Standardized error handling with logging"""
        error_message = f"{operation} failed in {self.service_name}: {str(error)}"
        logger.error(error_message)
        
        return {
            "success": False,
            "error": error_message,
            "service": self.service_name,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # COMPREHENSIVE CRUD OPERATIONS
    
    async def create_webhook(self, data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Create new webhook with comprehensive validation and real data storage"""
        try:
            # Validate input
            validation_result = self._validate_input(data)
            if not validation_result["success"]:
                return validation_result
            
            # Get collection
            collection = self._get_collection()
            if collection is None:
                return self._handle_error("CREATE", Exception("Database connection failed"))
            
            # Prepare data
            create_data = self._prepare_create_data(data)
            if user_id:
                create_data["user_id"] = user_id
                create_data["created_by"] = user_id
            
            # Insert into database
            result = await collection.insert_one(create_data)
            
            if result.inserted_id:
                # Return sanitized response
                response_data = self._sanitize_response(create_data)
                return {
                    "success": True,
                    "message": f"{self.service_name.title()} created successfully",
                    "data": response_data,
                    "id": create_data["id"]
                }
            else:
                return self._handle_error("CREATE", Exception("Failed to insert document"))
                
        except Exception as e:
            return self._handle_error("CREATE", e)
    
    async def get_webhook(self, item_id: str, user_id: str = None) -> Dict[str, Any]:
        """Get webhook by ID with comprehensive error handling"""
        try:
            if not item_id:
                return {"success": False, "error": "ID is required"}
            
            collection = self._get_collection()
            if collection is None:
                return self._handle_error("GET", Exception("Database connection failed"))
            
            # Build query
            query = {"id": item_id}
            if user_id:
                query["user_id"] = user_id
            
            # Find document
            doc = await collection.find_one(query)
            
            if not doc:
                return {
                    "success": False,
                    "error": f"{self.service_name.title()} not found",
                    "id": item_id
                }
            
            # Return sanitized response
            response_data = self._sanitize_response(doc)
            return {
                "success": True,
                "data": response_data
            }
            
        except Exception as e:
            return self._handle_error("GET", e)
    
    async def list_webhooks(self, user_id: str = None, limit: int = 50, offset: int = 0, 
                                  filters: Dict[str, Any] = None, sort_by: str = "created_at",
                                  sort_order: int = -1) -> Dict[str, Any]:
        """List webhooks with comprehensive filtering, pagination, and sorting"""
        try:
            # Validate parameters
            if limit < 1 or limit > 100:
                limit = 50
            if offset < 0:
                offset = 0
            
            collection = self._get_collection()
            if collection is None:
                return self._handle_error("LIST", Exception("Database connection failed"))
            
            # Build query
            query = filters or {}
            if user_id:
                query["user_id"] = user_id
            
            # Execute query with pagination and sorting
            cursor = collection.find(query).sort(sort_by, sort_order).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Sanitize all documents
            sanitized_docs = [self._sanitize_response(doc) for doc in docs]
            
            # Get total count
            total_count = await collection.count_documents(query)
            
            return {
                "success": True,
                "data": sanitized_docs,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": total_count > (offset + limit),
                    "current_page": (offset // limit) + 1,
                    "total_pages": (total_count + limit - 1) // limit
                },
                "query_info": {
                    "filters_applied": bool(filters),
                    "user_filtered": bool(user_id),
                    "sort_by": sort_by,
                    "sort_order": "desc" if sort_order == -1 else "asc"
                }
            }
            
        except Exception as e:
            return self._handle_error("LIST", e)
    
    async def update_webhook(self, item_id: str, update_data: Dict[str, Any], 
                                   user_id: str = None) -> Dict[str, Any]:
        """Update webhook with comprehensive validation and real data storage"""
        try:
            if not item_id:
                return {"success": False, "error": "ID is required"}
            
            # Validate input
            validation_result = self._validate_input(update_data)
            if not validation_result["success"]:
                return validation_result
            
            collection = self._get_collection()
            if collection is None:
                return self._handle_error("UPDATE", Exception("Database connection failed"))
            
            # Prepare update data
            update_data = update_data.copy()
            update_data["updated_at"] = datetime.utcnow().isoformat()
            if user_id:
                update_data["updated_by"] = user_id
            
            # Increment version
            update_data["$inc"] = {"version": 1}
            
            # Build query
            query = {"id": item_id}
            if user_id:
                query["user_id"] = user_id
            
            # Update document
            result = await collection.update_one(query, {"$set": update_data})
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"{self.service_name.title()} not found",
                    "id": item_id
                }
            
            # Get updated document
            updated_doc = await collection.find_one(query)
            response_data = self._sanitize_response(updated_doc) if updated_doc else None
            
            return {
                "success": True,
                "message": f"{self.service_name.title()} updated successfully",
                "data": response_data,
                "modified_count": result.modified_count
            }
            
        except Exception as e:
            return self._handle_error("UPDATE", e)
    
    async def delete_webhook(self, item_id: str, user_id: str = None, 
                                   soft_delete: bool = True) -> Dict[str, Any]:
        """Delete webhook with comprehensive validation (soft delete by default)"""
        try:
            if not item_id:
                return {"success": False, "error": "ID is required"}
            
            collection = self._get_collection()
            if collection is None:
                return self._handle_error("DELETE", Exception("Database connection failed"))
            
            # Build query
            query = {"id": item_id}
            if user_id:
                query["user_id"] = user_id
            
            if soft_delete:
                # Soft delete - mark as deleted
                update_data = {
                    "status": "deleted",
                    "deleted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                if user_id:
                    update_data["deleted_by"] = user_id
                
                result = await collection.update_one(query, {"$set": update_data})
                
                if result.matched_count == 0:
                    return {
                        "success": False,
                        "error": f"{self.service_name.title()} not found",
                        "id": item_id
                    }
                
                return {
                    "success": True,
                    "message": f"{self.service_name.title()} deleted successfully (soft delete)",
                    "deleted_count": result.modified_count,
                    "soft_delete": True
                }
            else:
                # Hard delete - permanently remove
                result = await collection.delete_one(query)
                
                if result.deleted_count == 0:
                    return {
                        "success": False,
                        "error": f"{self.service_name.title()} not found",
                        "id": item_id
                    }
                
                return {
                    "success": True,
                    "message": f"{self.service_name.title()} deleted permanently",
                    "deleted_count": result.deleted_count,
                    "soft_delete": False
                }
                
        except Exception as e:
            return self._handle_error("DELETE", e)
    
    # ADDITIONAL OPERATIONS
    
    async def search_webhooks(self, search_query: str, user_id: str = None, 
                                    limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Search webhooks with text search capabilities"""
        try:
            if not search_query:
                return {"success": False, "error": "Search query is required"}
            
            collection = self._get_collection()
            if collection is None:
                return self._handle_error("SEARCH", Exception("Database connection failed"))
            
            # Build search query
            query = {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"title": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}},
                    {"content": {"$regex": search_query, "$options": "i"}}
                ]
            }
            
            if user_id:
                query["user_id"] = user_id
            
            # Execute search
            cursor = collection.find(query).skip(offset).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Sanitize results
            sanitized_docs = [self._sanitize_response(doc) for doc in docs]
            
            # Get total count
            total_count = await collection.count_documents(query)
            
            return {
                "success": True,
                "data": sanitized_docs,
                "search_info": {
                    "query": search_query,
                    "total_results": total_count,
                    "limit": limit,
                    "offset": offset
                }
            }
            
        except Exception as e:
            return self._handle_error("SEARCH", e)
    
    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get comprehensive statistics for webhooks"""
        try:
            collection = self._get_collection()
            if collection is None:
                return self._handle_error("STATS", Exception("Database connection failed"))
            
            # Build query
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            # Get various statistics
            total_count = await collection.count_documents(query)
            active_count = await collection.count_documents({**query, "status": "active"})
            deleted_count = await collection.count_documents({**query, "status": "deleted"})
            
            # Get recent activity
            recent_query = {**query, "created_at": {"$gte": (datetime.utcnow() - timedelta(days=30)).isoformat()}}
            recent_count = await collection.count_documents(recent_query)
            
            return {
                "success": True,
                "data": {
                    "total_count": total_count,
                    "active_count": active_count,
                    "deleted_count": deleted_count,
                    "recent_count": recent_count,
                    "service": self.service_name,
                    "collection": self.collection_name,
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return self._handle_error("STATS", e)
    
    async def bulk_create_webhooks(self, items: List[Dict[str, Any]], 
                                         user_id: str = None) -> Dict[str, Any]:
        """Bulk create multiple webhooks"""
        try:
            if not items or not isinstance(items, list):
                return {"success": False, "error": "Items must be a non-empty list"}
            
            collection = self._get_collection()
            if collection is None:
                return self._handle_error("BULK_CREATE", Exception("Database connection failed"))
            
            # Prepare all items
            prepared_items = []
            for item in items:
                prepared_item = self._prepare_create_data(item)
                if user_id:
                    prepared_item["user_id"] = user_id
                    prepared_item["created_by"] = user_id
                prepared_items.append(prepared_item)
            
            # Insert all items
            result = await collection.insert_many(prepared_items)
            
            # Sanitize responses
            sanitized_items = [self._sanitize_response(item) for item in prepared_items]
            
            return {
                "success": True,
                "message": f"{len(result.inserted_ids)} {self.service_name}s created successfully",
                "data": sanitized_items,
                "created_count": len(result.inserted_ids)
            }
            
        except Exception as e:
            return self._handle_error("BULK_CREATE", e)
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for webhook service"""
        try:
            collection = self._get_collection()
            if collection is None:
                return {
                    "success": False,
                    "error": "Database connection failed",
                    "service": self.service_name,
                    "healthy": False
                }
            
            # Real database implementation
            await collection.count_documents({})
            
            # Real database implementation
            test_doc = {
                "id": str(uuid.uuid4()),
                "test": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert test document
            insert_result = await collection.insert_one(test_doc)
            
            # Find test document
            found_doc = await collection.find_one({"id": test_doc["id"]})
            
            # Delete test document
            delete_result = await collection.delete_one({"id": test_doc["id"]})
            
            health_status = {
                "success": True,
                "service": self.service_name,
                "healthy": True,
                "timestamp": datetime.utcnow().isoformat(),
                "database_connection": True,
                "crud_operations": {
                    "create": bool(insert_result.inserted_id),
                    "read": bool(found_doc),
                    "delete": bool(delete_result.deleted_count)
                }
            }
            
            return health_status
            
        except Exception as e:
            return self._handle_error("HEALTH_CHECK", e)

# Service instance with lazy initialization
_service_instance = None

def get_webhook_service():
    """Get service instance with lazy initialization"""
    global _service_instance
    if _service_instance is None:
        _service_instance = WebhookService()
    return _service_instance

# Backward compatibility
webhook_service = get_webhook_service()