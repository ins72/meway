"""
Advanced Course Platform API
Enterprise-level course management with LMS, gamification, and adaptive learning
"""
from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

from core.auth import get_current_user
from services.advanced_lms_service import advanced_lms_service
from core.professional_logger import professional_logger, LogLevel, LogCategory

router = APIRouter(prefix="/api/advanced-courses", tags=["Advanced Course Platform"])

class CourseCreate(BaseModel):
    title: str
    description: str
    difficulty_level: str = "beginner"
    duration_hours: int = 10
    objectives: List[str] = []
    prerequisites: List[str] = []
    content_types: List[str] = ["video", "text", "quiz"]
    gamification: bool = True
    adaptive_learning: bool = True
    peer_learning: bool = True
    scorm_support: bool = False
    certificates: bool = True

class ProgressUpdate(BaseModel):
    lesson_id: str
    time_spent: int = 0
    completion_data: Dict[str, Any] = {}

@router.post("/create")
async def create_advanced_course(
    course_data: CourseCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create advanced course with enterprise features"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        course_dict = course_data.dict()
        course_dict["instructor_id"] = user_id
        
        course_id = await advanced_lms_service.create_advanced_course(course_dict)
        
        return {
            "success": True,
            "course_id": course_id,
            "message": "Advanced course created successfully",
            "features_enabled": {
                "gamification": course_data.gamification,
                "adaptive_learning": course_data.adaptive_learning,
                "peer_learning": course_data.peer_learning,
                "scorm_support": course_data.scorm_support,
                "certificates": course_data.certificates
            }
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.LEARNING,
            f"Failed to create course: {str(e)}",
            error=e, user_id=current_user.get("_id")
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enroll/{course_id}")
async def enroll_in_course(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Enroll student with adaptive learning path"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        enrollment = await advanced_lms_service.enroll_student_advanced(user_id, course_id)
        
        return {
            "success": True,
            "enrollment_id": enrollment["enrollment_id"],
            "learning_path": enrollment["learning_path"],
            "message": "Successfully enrolled with personalized learning path"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/progress/{course_id}")
async def update_learning_progress(
    course_id: str,
    progress_data: ProgressUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Track learning progress with gamification"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        progress = await advanced_lms_service.track_learning_progress(
            user_id, course_id, progress_data.lesson_id, progress_data.dict()
        )
        
        return {
            "success": True,
            "progress": progress,
            "message": "Progress updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scorm/{course_id}/upload")
async def upload_scorm_package(
    course_id: str,
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload and process SCORM package"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="SCORM package must be a ZIP file")
        
        file_data = await file.read()
        scorm_info = await advanced_lms_service.scorm_processor.process_scorm_package(course_id, file_data)
        
        if "error" in scorm_info:
            raise HTTPException(status_code=400, detail=scorm_info["error"])
        
        return {
            "success": True,
            "scorm_info": scorm_info,
            "message": "SCORM package processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gamification/{user_id}")
async def get_gamification_profile(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user gamification profile"""
    try:
        auth_user_id = current_user.get("_id")
        if not auth_user_id or (auth_user_id != user_id and not current_user.get("is_admin")):
            raise HTTPException(status_code=403, detail="Access denied")
        
        from core.database import get_database
        db = get_database()
        
        profile = await db.user_gamification.find_one({"user_id": user_id})
        if not profile:
            profile = {"user_id": user_id, "total_points": 0, "badges": [], "level": 1}
        
        # Calculate level based on points
        points = profile.get("total_points", 0)
        level = min(10, max(1, points // 1000 + 1))  # Level up every 1000 points
        
        return {
            "success": True,
            "gamification": {
                "user_id": user_id,
                "total_points": points,
                "level": level,
                "badges": profile.get("badges", []),
                "next_level_points": (level * 1000) if level < 10 else "Max Level",
                "achievements": profile.get("achievements", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/study-partners/{course_id}")
async def get_study_partners(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Find compatible study partners"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        partners = await advanced_lms_service.peer_learning.match_study_partners(user_id, course_id)
        
        return {
            "success": True,
            "study_partners": partners,
            "total_matches": len(partners),
            "message": "Study partners found based on compatibility"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/course/{course_id}")
async def get_course_analytics(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get comprehensive course analytics"""
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        from core.database import get_database
        db = get_database()
        
        # Get course info
        course = await db.advanced_courses.find_one({"course_id": course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get enrollment analytics
        enrollments = await db.course_enrollments.find({"course_id": course_id}).to_list(length=None)
        
        analytics = {
            "course_id": course_id,
            "title": course.get("title"),
            "total_enrollments": len(enrollments),
            "completion_rate": 0,
            "average_progress": 0,
            "engagement_metrics": {},
            "learning_paths_generated": len(enrollments),
            "gamification_stats": {
                "total_points_awarded": 0,
                "badges_earned": 0,
                "active_learners": 0
            }
        }
        
        if enrollments:
            # Calculate averages
            total_progress = sum(e.get("progress", {}).get("percentage", 0) for e in enrollments)
            analytics["average_progress"] = total_progress / len(enrollments)
            
            completed = len([e for e in enrollments if e.get("progress", {}).get("percentage", 0) >= 100])
            analytics["completion_rate"] = (completed / len(enrollments)) * 100
        
        return {
            "success": True,
            "analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/certificates/{user_id}")
async def get_user_certificates(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user certificates"""
    try:
        auth_user_id = current_user.get("_id")
        if not auth_user_id or (auth_user_id != user_id and not current_user.get("is_admin")):
            raise HTTPException(status_code=403, detail="Access denied")
        
        from core.database import get_database
        db = get_database()
        
        certificates = await db.certificates.find({"user_id": user_id}).to_list(length=None)
        
        # Convert ObjectId and format dates
        for cert in certificates:
            cert["_id"] = str(cert["_id"])
            if "completion_date" in cert:
                cert["completion_date"] = cert["completion_date"].isoformat()
        
        return {
            "success": True,
            "certificates": certificates,
            "total_certificates": len(certificates),
            "verified_certificates": len([c for c in certificates if c.get("blockchain_verified")])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
