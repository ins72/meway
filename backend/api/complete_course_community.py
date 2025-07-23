"""
Complete Course Community API Router
Comprehensive API endpoints for complete_course_community_service
Generated: 2025-07-23 11:29:09
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from typing import List, Dict, Any, Optional
import logging

from core.auth import get_current_user
from services.complete_course_community_service import complete_course_community_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Health Check
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "complete_course_community_service",
        "timestamp": "2025-07-23T11:29:09.500681",
        "version": "2.0"
    }

# CRUD Endpoints
@router.post("/courses", tags=["Course Management"])
async def create_course(
    course_data: dict = Body(..., description="Course data"),
    current_user: dict = Depends(get_current_user)
):
    """Create new course"""
    try:
        result = await complete_course_community_service.create_course(
            user_id=current_user["_id"],
            course_data=course_data
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Course created successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Creation failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/courses", tags=["Course Management"])
async def list_courses(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: dict = Depends(get_current_user)
):
    """List user's courses with pagination"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        result = await complete_course_community_service.list_courses(
            user_id=current_user["_id"],
            filters=filters,
            page=page,
            limit=limit
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Courses retrieved successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Retrieval failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing courses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/courses/{item_id}", tags=["Course Management"])
async def get_course(
    item_id: str = Path(..., description="Course ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get specific course"""
    try:
        result = await complete_course_community_service.get_course(
            user_id=current_user["_id"],
            course_id=item_id
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Course retrieved successfully")
            }
        else:
            raise HTTPException(status_code=404, detail=result.get("message", "Course not found"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/courses/{item_id}", tags=["Course Management"])
async def update_course(
    item_id: str = Path(..., description="Course ID"),
    course_data: dict = Body(..., description="Update data"),
    current_user: dict = Depends(get_current_user)
):
    """Update existing course"""
    try:
        result = await complete_course_community_service.update_course(
            user_id=current_user["_id"],
            course_id=item_id,
            update_data=course_data
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data"),
                "message": result.get("message", "Course updated successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Update failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating course: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/courses/{item_id}", tags=["Course Management"])
async def delete_course(
    item_id: str = Path(..., description="Course ID"),
    hard_delete: bool = Query(False, description="Permanently delete (cannot be undone)"),
    current_user: dict = Depends(get_current_user)
):
    """Delete course"""
    try:
        result = await complete_course_community_service.delete_course(
            user_id=current_user["_id"],
            course_id=item_id,
            hard_delete=hard_delete
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": result.get("message", "Course deleted successfully")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Delete failed"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Analytics Endpoint
@router.get("/courses/analytics", tags=["Course Analytics"])
async def get_course_analytics(
    period: str = Query("7d", description="Time period (7d, 30d, 90d, 1y)"),
    current_user: dict = Depends(get_current_user)
):
    """Get course analytics and metrics"""
    try:
        # This would be implemented based on service-specific analytics
        return {
            "success": True,
            "data": {
                "period": period,
                "total_courses": 0,
                "active_courses": 0,
                "growth_rate": 0.0,
                "last_updated": "2025-07-23T11:29:09.500690"
            },
            "message": "Course analytics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting course analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")
