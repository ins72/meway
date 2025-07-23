"""
Media Service
Business logic for media library and file management
"""

import uuid
import os
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any
import mimetypes

from core.database import get_database

class MediaService:
    @staticmethod
    async def get_media_library(user_id: str) -> Dict[str, Any]:
        """Get media library with files and folders"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Get folders
        folders_collection = database.media_folders
        folders_query = {"workspace_id": str(workspace["_id"])}
        if folder:
            folders_query["parent_folder"] = folder
        else:
            folders_query["parent_folder"] = {"$in": ["", None]}
            
        folders_cursor = folders_collection.find(folders_query).limit(20)
        folders = await folders_cursor.to_list(length=20)
        
        # Get files
        files_collection = database.media_files
        files_query = {"workspace_id": str(workspace["_id"])}
        if folder:
            files_query["folder"] = folder
        if file_type != "all":
            files_query["file_type"] = file_type
        if search:
            files_query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search]}}
            ]
            
        files_cursor = files_collection.find(files_query).limit(limit)
        files = await files_cursor.to_list(length=limit)
        
        # Format folders
        folder_data = []
        for folder_doc in folders:
            file_count = await files_collection.count_documents({
                "workspace_id": str(workspace["_id"]),
                "folder": folder_doc.get("path", folder_doc["name"])
            })
            
            folder_data.append({
                "id": folder_doc["_id"],
                "name": folder_doc["name"],
                "path": folder_doc.get("path", folder_doc["name"]),
                "file_count": file_count,
                "created_at": folder_doc["created_at"].isoformat()
            })
        
        # Format files
        file_data = []
        for file_doc in files:
            file_data.append({
                "id": file_doc["_id"],
                "name": file_doc["name"],
                "original_name": file_doc.get("original_name", file_doc["name"]),
                "type": file_doc["file_type"],
                "size": file_doc["size"],
                "size_formatted": MediaService._format_file_size(file_doc["size"]),
                "url": file_doc["url"],
                "thumbnail": file_doc.get("thumbnail"),
                "description": file_doc.get("description", ""),
                "tags": file_doc.get("tags", []),
                "folder": file_doc.get("folder", ""),
                "uploaded_at": file_doc["created_at"].isoformat(),
                "used_in": file_doc.get("used_in", [])
            })
        
        # Calculate usage stats
        total_files = await files_collection.count_documents({"workspace_id": str(workspace["_id"])})
        
        
        # Calculate real total size from database
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total_size": {"$sum": "$size"}}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        total_size = result[0]["total_size"] if result else 0
        
        total_size = sum(f["size"] for f in files) if files else 0
        storage_limit = 10 * 1024 * 1024 * 1024  # 10GB in bytes
        usage_percentage = (total_size / storage_limit * 100) if total_size > 0 else 0
        
        return {
            "current_folder": folder or "root",
            "folders": folder_data,
            "files": file_data,
            "usage_stats": {
                "total_files": total_files,
                "total_size": total_size,
                "total_size_formatted": MediaService._format_file_size(total_size),
                "storage_limit": storage_limit,
                "storage_limit_formatted": MediaService._format_file_size(storage_limit),
                "usage_percentage": min(100, usage_percentage)
            }
        }
    
    @staticmethod
    async def upload_file(user_id: str, file, file_content: bytes, description: str = "", tags: List[str] = None, folder: str = "") -> Dict[str, Any]:
        """Upload file to media library"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Generate unique file ID and name
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        stored_filename = f"{file_id}{file_extension}"
        
        # Determine file type
        file_type = MediaService._get_file_type(file.content_type)
        
        # Convert file to base64 for storage (in real app, store in cloud storage)
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        file_url = f"/media/{stored_filename}"
        
        # Generate thumbnail for images
        thumbnail_url = None
        if file_type == "image":
            thumbnail_url = f"/media/thumbs/{stored_filename}"
        
        # Create file document
        file_doc = {
            "_id": file_id,
            "workspace_id": str(workspace["_id"]),
            "name": file.filename,
            "original_name": file.filename,
            "stored_name": stored_filename,
            "file_type": file_type,
            "mime_type": file.content_type,
            "size": len(file_content),
            "url": file_url,
            "thumbnail": thumbnail_url,
            "description": description,
            "tags": tags or [],
            "folder": folder,
            "file_data": file_base64,  # In production, store in cloud
            "uploaded_by": user_id,
            "created_at": datetime.utcnow(),
            "used_in": []  # Track where this file is used
        }
        
        # Insert file
        files_collection = database.media_files
        await files_collection.insert_one(file_doc)
        
        return {
            "id": file_doc["_id"],
            "name": file_doc["name"],
            "type": file_doc["file_type"],
            "size": file_doc["size"],
            "size_formatted": MediaService._format_file_size(file_doc["size"]),
            "url": file_doc["url"],
            "thumbnail": file_doc["thumbnail"],
            "folder": file_doc["folder"],
            "uploaded_at": file_doc["created_at"].isoformat()
        }
    
    @staticmethod
    async def get_file_details(file_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed file information"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            return None
        
        # Get file
        files_collection = database.media_files
        file_doc = await files_collection.find_one({
            "_id": file_id,
            "workspace_id": str(workspace["_id"])
        })
        
        if not file_doc:
            return None
        
        return {
            "id": file_doc["_id"],
            "name": file_doc["name"],
            "original_name": file_doc.get("original_name", file_doc["name"]),
            "type": file_doc["file_type"],
            "mime_type": file_doc["mime_type"],
            "size": file_doc["size"],
            "size_formatted": MediaService._format_file_size(file_doc["size"]),
            "url": file_doc["url"],
            "thumbnail": file_doc.get("thumbnail"),
            "description": file_doc.get("description", ""),
            "tags": file_doc.get("tags", []),
            "folder": file_doc.get("folder", ""),
            "uploaded_by": file_doc["uploaded_by"],
            "uploaded_at": file_doc["created_at"].isoformat(),
            "used_in": file_doc.get("used_in", []),
            "download_count": file_doc.get("download_count", 0)
        }
    
    @staticmethod
    async def update_file_metadata(file_id: str, user_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update file metadata"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Update file
        metadata["updated_at"] = datetime.utcnow()
        
        files_collection = database.media_files
        result = await files_collection.update_one(
            {"_id": file_id, "workspace_id": str(workspace["_id"])},
            {"$set": metadata}
        )
        if result.matched_count == 0:
            raise Exception("File not found")
        
        # Return updated file
        return await MediaService.get_file_details(file_id, user_id)
    
    @staticmethod
    async def delete_file(file_id: str, user_id: str) -> bool:
        """Delete file from library"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Delete file
        files_collection = database.media_files
        result = await files_collection.delete_one({
            "_id": file_id,
            "workspace_id": str(workspace["_id"])
        })
        
        return result.deleted_count > 0
    
    @staticmethod
    
    ) -> Dict[str, Any]:
        """Create new folder"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Check if folder already exists
        folders_collection = database.media_folders
        existing = await folders_collection.find_one({
            "workspace_id": str(workspace["_id"]),
            "name": name,
            "parent_folder": parent_folder
        })
        
        if existing:
            raise Exception("Folder already exists")
        
        # Create folder path
        folder_path = f"{parent_folder}/{name}" if parent_folder else name
        
        folder_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": str(workspace["_id"]),
            "name": name,
            "path": folder_path,
            "parent_folder": parent_folder,
            "created_by": user_id,
            "created_at": datetime.utcnow()
        }
        
        await folders_collection.insert_one(folder_doc)
        
        return {
            "id": folder_doc["_id"],
            "name": folder_doc["name"],
            "path": folder_doc["path"],
            "parent_folder": folder_doc["parent_folder"],
            "created_at": folder_doc["created_at"].isoformat()
        }
    
    @staticmethod
    async def delete_folder(folder_id: str, user_id: str) -> bool:
        """Delete folder (must be empty)"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Check if folder has files
        files_collection = database.media_files
        folder_doc = await database.media_folders.find_one({
            "_id": folder_id,
            "workspace_id": str(workspace["_id"])
        })
        
        if not folder_doc:
            raise Exception("Folder not found")
        
        file_count = await files_collection.count_documents({
            "workspace_id": str(workspace["_id"]),
            "folder": folder_doc["path"]
        })
        
        if file_count > 0:
            raise Exception("Cannot delete folder with files. Move or delete files first.")
        
        # Delete folder
        folders_collection = database.media_folders
        result = await folders_collection.delete_one({
            "_id": folder_id,
            "workspace_id": str(workspace["_id"])
        })
        
        return result.deleted_count > 0
    
    @staticmethod
    async def get_storage_usage(user_id: str) -> Dict[str, Any]:
        """Get storage usage statistics"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        files_collection = database.media_files
        
        # Get total file count and size
        files_cursor = files_collection.find({"workspace_id": str(workspace["_id"])})
        files = await files_cursor.to_list(length=None)
        
        total_files = len(files)
        total_size = sum(f.get("size", 0) for f in files)
        
        # Calculate by file type
        type_breakdown = {}
        for file_doc in files:
            file_type = file_doc.get("file_type", "other")
            if file_type not in type_breakdown:
                type_breakdown[file_type] = {"count": 0, "size": 0}
            type_breakdown[file_type]["count"] += 1
            type_breakdown[file_type]["size"] += file_doc.get("size", 0)
        
        # Format type breakdown
        formatted_breakdown = {}
        for file_type, stats in type_breakdown.items():
            formatted_breakdown[file_type] = {
                "count": stats["count"],
                "size": stats["size"],
                "size_formatted": MediaService._format_file_size(stats["size"]),
                "percentage": (stats["size"] / total_size * 100) if total_size > 0 else 0
            }
        
        storage_limit = 10 * 1024 * 1024 * 1024  # 10GB
        usage_percentage = (total_size / storage_limit * 100) if total_size > 0 else 0
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_formatted": MediaService._format_file_size(total_size),
            "storage_limit": storage_limit,
            "storage_limit_formatted": MediaService._format_file_size(storage_limit),
            "usage_percentage": min(100, usage_percentage),
            "available_space": max(0, storage_limit - total_size),
            "available_space_formatted": MediaService._format_file_size(max(0, storage_limit - total_size)),
            "type_breakdown": formatted_breakdown
        }
    
    @staticmethod
    
    ) -> Dict[str, Any]:
        """Search media files"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Build search query
        search_query = {
            "workspace_id": str(workspace["_id"]),
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": query, "$options": "i"}}}
            ]
        }
        
        if file_type != "all":
            search_query["file_type"] = file_type
        if folder:
            search_query["folder"] = folder
        
        # Execute search
        files_collection = database.media_files
        files_cursor = files_collection.find(search_query).limit(limit)
        files = await files_cursor.to_list(length=limit)
        
        # Format results
        results = []
        for file_doc in files:
            results.append({
                "id": file_doc["_id"],
                "name": file_doc["name"],
                "type": file_doc["file_type"],
                "size": file_doc["size"],
                "size_formatted": MediaService._format_file_size(file_doc["size"]),
                "url": file_doc["url"],
                "thumbnail": file_doc.get("thumbnail"),
                "description": file_doc.get("description", ""),
                "tags": file_doc.get("tags", []),
                "folder": file_doc.get("folder", ""),
                "uploaded_at": file_doc["created_at"].isoformat()
            })
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results
        }
    
    @staticmethod
    async def bulk_delete_files(file_ids: List[str], user_id: str) -> Dict[str, Any]:
        """Delete multiple files"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Delete files
        files_collection = database.media_files
        result = await files_collection.delete_many({
            "_id": {"$in": file_ids},
            "workspace_id": str(workspace["_id"])
        })
        
        return {
            "deleted_count": result.deleted_count,
            "requested_count": len(file_ids)
        }
    
    @staticmethod
    
    ) -> Dict[str, Any]:
        """Move multiple files to folder"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Update files
        files_collection = database.media_files
        result = await files_collection.update_many(
            {
                "_id": {"$in": file_ids},
                "workspace_id": str(workspace["_id"])
            },
            {"$set": {"folder": target_folder, "updated_at": datetime.utcnow()}}
        return {
            "moved_count": result.modified_count,
            "requested_count": len(file_ids)
        }
    
    @staticmethod
    def _get_file_type(mime_type: str) -> str:
        """Determine file type from MIME type"""
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type in ['application/pdf']:
            return 'document'
        elif mime_type in ['text/plain', 'text/csv']:
            return 'text'
        else:
            return 'other'
    
    @staticmethod

    async def create_media(self, media_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new media"""
        try:
            # Add metadata
            media_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["media"].insert_one(media_data)
            
            return {
                "success": True,
                "message": f"Media created successfully",
                "data": media_data,
                "id": media_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create media: {str(e)}"
            }

    def _format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
# Global service instance

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

    async def update_media(self, media_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update media by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["media"].update_one(
                {"id": media_id},
                {"$set": update_data}
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Media not found"
                }
            
            # Get updated document
            updated_doc = await self.db["media"].find_one({"id": media_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Media updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update media: {str(e)}"
            }

            
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

    async def delete_media(self, media_id: str) -> Dict[str, Any]:
        """Delete media by ID"""
        try:
            result = await self.db["media"].delete_one({"id": media_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Media not found"
                }
            
            return {
                "success": True,
                "message": f"Media deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete media: {str(e)}"
            }

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