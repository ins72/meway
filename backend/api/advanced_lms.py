"""
Advanced Learning Management System API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional
from pydantic import BaseModel
from ..core.auth import get_current_user
from ..core.database import get_database
from ..services.advanced_lms_service import AdvancedLMSService

router = APIRouter(prefix="/api/lms", tags=["Learning Management System"])

class SCORMPackageCreate(BaseModel):
    title: str
    description: str
    version: str = "1.2"
    manifest: str
    files: List[str] = []

class LearningProgressUpdate(BaseModel):
    lesson_id: str
    progress: float
    time_spent: int
    status: str = "in_progress"
    score: Optional[float] = None
    interactions: List[Dict] = []

@router.post("/scorm/package")
async def create_scorm_package(
    package: SCORMPackageCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create new SCORM package"""
    lms_service = AdvancedLMSService(db)
    result = await lms_service.create_scorm_package(package.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "SCORM package created successfully", "data": result}

@router.post("/courses/{course_id}/progress")
async def update_learning_progress(
    course_id: str,
    progress: LearningProgressUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update learning progress for a course"""
    lms_service = AdvancedLMSService(db)
    result = await lms_service.track_learning_progress(
        current_user["user_id"], 
        course_id, 
        progress.dict()
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Progress updated successfully", "data": result}

@router.post("/certificates/{course_id}/generate")
async def generate_certificate(
    course_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Generate certificate for completed course"""
    lms_service = AdvancedLMSService(db)
    result = await lms_service.generate_certificate(
        current_user["user_id"], 
        course_id
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Certificate generated successfully", "data": result}

@router.get("/analytics")
async def get_learning_analytics(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get comprehensive learning analytics"""
    lms_service = AdvancedLMSService(db)
    result = await lms_service.get_learning_analytics(current_user["user_id"])
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Analytics retrieved successfully", "data": result}

@router.get("/gamification")
async def get_gamification_data(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user gamification data"""
    lms_service = AdvancedLMSService(db)
    
    # Get gamification data from database
    game_data = await db["gamification"].find_one({"user_id": current_user["user_id"]})
    
    if not game_data:
        # Create initial gamification profile
        initial_data = {
            "user_id": current_user["user_id"],
            "total_points": 0,
            "level": 1,
            "badges": ["New Learner"],
            "achievements": [],
            "created_at": "2024-12-01T00:00:00Z"
        }
        await db["gamification"].insert_one(initial_data)
        game_data = initial_data
    
    return {"message": "Gamification data retrieved", "data": game_data}

@router.get("/courses/scorm")
async def list_scorm_packages(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List available SCORM packages"""
    packages = await db["scorm_packages"].find({"status": "active"}).to_list(length=50)
    
    return {
        "message": "SCORM packages retrieved successfully",
        "data": packages,
        "count": len(packages)
    }
