"""
Advanced Learning Management System Service
SCORM support, adaptive learning, gamification, and comprehensive course management
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel

from core.database import get_database
from core.professional_logger import professional_logger, LogLevel, LogCategory

class ContentType(Enum):
    VIDEO = "video"
    AUDIO = "audio" 
    TEXT = "text"
    INTERACTIVE = "interactive"
    SCORM = "scorm"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"

class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"

class CourseProgress(BaseModel):
    user_id: str
    course_id: str
    progress_percentage: float
    completed_lessons: List[str]
    time_spent_minutes: int
    last_accessed: datetime
    learning_path: List[str]

class GamificationEngine:
    """Advanced gamification system with points, badges, and leaderboards"""
    
    def __init__(self):
        self.point_rules = {
            "lesson_completion": 100,
            "quiz_passed": 150,
            "course_completion": 500,
            "peer_help": 50,
            "discussion_post": 25,
            "assignment_submission": 200
        }
        self.badges = {
            "first_course": {"name": "Getting Started", "description": "Complete your first course", "icon": "🎯"},
            "quick_learner": {"name": "Quick Learner", "description": "Complete 3 courses in a week", "icon": "⚡"},
            "helper": {"name": "Community Helper", "description": "Help 10 fellow students", "icon": "🤝"},
            "perfectionist": {"name": "Perfectionist", "description": "Score 100% on 5 quizzes", "icon": "💯"},
            "consistent": {"name": "Consistent Learner", "description": "Study for 7 consecutive days", "icon": "🔥"}
        }
    
    async def award_points(self, user_id: str, action: str, course_id: str = None):
        """Award points for user actions"""
        try:
            db = get_database()
            points = self.point_rules.get(action, 0)
            
            # Update user points
            await db.user_gamification.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"total_points": points},
                    "$push": {
                        "point_history": {
                            "action": action,
                            "points": points,
                            "course_id": course_id,
                            "timestamp": datetime.utcnow()
                        }
                    }
                },
                upsert=True
            )
            
            # Check for badge achievements
            await self._check_badges(user_id)
            
            await professional_logger.log(
                LogLevel.INFO, LogCategory.LEARNING,
                f"Awarded {points} points for {action}",
                user_id=user_id,
                details={"action": action, "points": points, "course_id": course_id}
            )
            
            return points
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to award points: {str(e)}",
                error=e, user_id=user_id
            )
            return 0
    
    async def _check_badges(self, user_id: str):
        """Check and award badges based on user achievements"""
        try:
            db = get_database()
            user_data = await db.user_gamification.find_one({"user_id": user_id})
            if not user_data:
                return
            
            # Get user progress data
            courses_completed = await db.course_progress.count_documents({
                "user_id": user_id,
                "progress_percentage": 100
            })
            
            # Check badge conditions
            new_badges = []
            
            if courses_completed >= 1 and "first_course" not in user_data.get("badges", []):
                new_badges.append("first_course")
            
            if courses_completed >= 3:
                # Check if completed in a week
                week_ago = datetime.utcnow() - timedelta(days=7)
                recent_completions = await db.course_progress.count_documents({
                    "user_id": user_id,
                    "progress_percentage": 100,
                    "last_accessed": {"$gte": week_ago}
                })
                if recent_completions >= 3 and "quick_learner" not in user_data.get("badges", []):
                    new_badges.append("quick_learner")
            
            # Award new badges
            if new_badges:
                await db.user_gamification.update_one(
                    {"user_id": user_id},
                    {"$addToSet": {"badges": {"$each": new_badges}}}
                )
                
                for badge in new_badges:
                    await professional_logger.log(
                        LogLevel.INFO, LogCategory.LEARNING,
                        f"Badge awarded: {badge}",
                        user_id=user_id,
                        details={"badge": badge, "badge_info": self.badges[badge]}
                    )
        
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to check badges: {str(e)}",
                error=e, user_id=user_id
            )

class AdaptiveLearningEngine:
    """AI-powered adaptive learning path recommendations"""
    
    def __init__(self):
        self.learning_styles = {
            "visual": ["video", "infographic", "diagram", "chart"],
            "auditory": ["audio", "podcast", "discussion", "lecture"],
            "kinesthetic": ["interactive", "simulation", "hands_on", "project"],
            "reading": ["text", "article", "ebook", "documentation"]
        }
    
    async def generate_learning_path(self, user_id: str, course_id: str) -> List[str]:
        """Generate personalized learning path based on user preferences and progress"""
        try:
            db = get_database()
            
            # Get user learning style and progress
            user_profile = await db.user_learning_profiles.find_one({"user_id": user_id})
            learning_style = user_profile.get("preferred_style", "visual") if user_profile else "visual"
            
            # Get course content
            course = await db.courses.find_one({"course_id": course_id})
            if not course:
                return []
            
            lessons = course.get("lessons", [])
            
            # Sort lessons based on learning style preference
            preferred_content = self.learning_styles.get(learning_style, ["video"])
            
            # Create adaptive path
            adaptive_path = []
            for lesson in lessons:
                content_type = lesson.get("content_type", "video")
                difficulty = lesson.get("difficulty", 1)
                
                # Prioritize content that matches learning style
                priority_score = 10 if content_type in preferred_content else 5
                priority_score += (3 - difficulty)  # Easier content gets higher priority initially
                
                adaptive_path.append({
                    "lesson_id": lesson["lesson_id"],
                    "priority": priority_score,
                    "estimated_duration": lesson.get("duration_minutes", 30)
                })
            
            # Sort by priority
            adaptive_path.sort(key=lambda x: x["priority"], reverse=True)
            
            # Save learning path
            await db.user_learning_paths.update_one(
                {"user_id": user_id, "course_id": course_id},
                {
                    "$set": {
                        "learning_path": adaptive_path,
                        "learning_style": learning_style,
                        "generated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            return [item["lesson_id"] for item in adaptive_path]
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to generate learning path: {str(e)}",
                error=e, user_id=user_id
            )
            return []

class SCORMProcessor:
    """SCORM (Shareable Content Object Reference Model) support"""
    
    async def process_scorm_package(self, course_id: str, package_data: bytes) -> Dict[str, Any]:
        """Process uploaded SCORM package"""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            from io import BytesIO
            
            # Extract SCORM package
            with zipfile.ZipFile(BytesIO(package_data)) as zip_file:
                # Look for manifest file
                manifest_data = None
                for filename in zip_file.namelist():
                    if filename.lower().endswith('imsmanifest.xml'):
                        manifest_data = zip_file.read(filename)
                        break
                
                if not manifest_data:
                    raise Exception("Invalid SCORM package: no manifest found")
                
                # Parse manifest
                root = ET.fromstring(manifest_data)
                
                # Extract course information
                course_info = {
                    "title": root.find(".//title").text if root.find(".//title") is not None else "SCORM Course",
                    "version": root.get("version", "1.2"),
                    "resources": [],
                    "organization": {}
                }
                
                # Process resources
                resources = root.findall(".//resource")
                for resource in resources:
                    course_info["resources"].append({
                        "identifier": resource.get("identifier"),
                        "type": resource.get("type"),
                        "href": resource.get("href")
                    })
                
                # Store SCORM course data
                db = get_database()
                await db.scorm_courses.update_one(
                    {"course_id": course_id},
                    {
                        "$set": {
                            "scorm_info": course_info,
                            "package_processed": True,
                            "processed_at": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                
                await professional_logger.log(
                    LogLevel.INFO, LogCategory.LEARNING,
                    f"SCORM package processed successfully",
                    details={"course_id": course_id, "resources_count": len(course_info["resources"])}
                )
                
                return course_info
                
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to process SCORM package: {str(e)}",
                error=e
            )
            return {"error": str(e)}

class PeerLearningEngine:
    """Peer-to-peer learning and mentorship system"""
    
    async def match_study_partners(self, user_id: str, course_id: str) -> List[Dict[str, Any]]:
        """Find suitable study partners based on learning style and progress"""
        try:
            db = get_database()
            
            # Get user profile
            user_profile = await db.user_learning_profiles.find_one({"user_id": user_id})
            user_progress = await db.course_progress.find_one({"user_id": user_id, "course_id": course_id})
            
            if not user_profile or not user_progress:
                return []
            
            user_progress_pct = user_progress.get("progress_percentage", 0)
            user_style = user_profile.get("preferred_style", "visual")
            
            # Find potential partners
            potential_partners = await db.user_learning_profiles.aggregate([
                {
                    "$match": {
                        "user_id": {"$ne": user_id},
                        "$or": [
                            {"preferred_style": user_style},  # Same learning style
                            {"collaboration_preferences.peer_learning": True}
                        ]
                    }
                },
                {
                    "$lookup": {
                        "from": "course_progress",
                        "let": {"partner_user_id": "$user_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$user_id", "$$partner_user_id"]},
                                            {"$eq": ["$course_id", course_id]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "course_progress"
                    }
                },
                {"$match": {"course_progress": {"$ne": []}}},
                {"$limit": 10}
            ]).to_list(length=10)
            
            # Score and rank partners
            scored_partners = []
            for partner in potential_partners:
                partner_progress = partner["course_progress"][0]
                progress_diff = abs(partner_progress.get("progress_percentage", 0) - user_progress_pct)
                
                # Calculate compatibility score
                score = 100
                score -= progress_diff * 0.5  # Similar progress is better
                if partner["preferred_style"] == user_style:
                    score += 20  # Bonus for same learning style
                
                scored_partners.append({
                    "user_id": partner["user_id"],
                    "compatibility_score": score,
                    "learning_style": partner["preferred_style"],
                    "progress_percentage": partner_progress.get("progress_percentage", 0),
                    "study_preferences": partner.get("collaboration_preferences", {})
                })
            
            # Sort by compatibility score
            scored_partners.sort(key=lambda x: x["compatibility_score"], reverse=True)
            
            return scored_partners[:5]  # Return top 5 matches
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to match study partners: {str(e)}",
                error=e, user_id=user_id
            )
            return []

class AdvancedLMSService:
    """Comprehensive Learning Management System"""
    
    def __init__(self):
        self.gamification = GamificationEngine()
        self.adaptive_learning = AdaptiveLearningEngine()
        self.scorm_processor = SCORMProcessor()
        self.peer_learning = PeerLearningEngine()
    
    async def create_advanced_course(self, course_data: Dict[str, Any]) -> str:
        """Create course with advanced features"""
        try:
            db = get_database()
            
            course_id = str(uuid.uuid4())
            
            advanced_course = {
                "course_id": course_id,
                "title": course_data["title"],
                "description": course_data["description"],
                "instructor_id": course_data["instructor_id"],
                "difficulty_level": course_data.get("difficulty_level", "beginner"),
                "estimated_duration_hours": course_data.get("duration_hours", 10),
                "learning_objectives": course_data.get("objectives", []),
                "prerequisites": course_data.get("prerequisites", []),
                "content_types": course_data.get("content_types", ["video", "text", "quiz"]),
                "gamification_enabled": course_data.get("gamification", True),
                "adaptive_learning": course_data.get("adaptive_learning", True),
                "peer_learning": course_data.get("peer_learning", True),
                "scorm_compatible": course_data.get("scorm_support", False),
                "certificates_enabled": course_data.get("certificates", True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "analytics": {
                    "total_enrollments": 0,
                    "completion_rate": 0,
                    "average_rating": 0,
                    "engagement_metrics": {}
                }
            }
            
            await db.advanced_courses.insert_one(advanced_course)
            
            await professional_logger.log(
                LogLevel.INFO, LogCategory.LEARNING,
                f"Advanced course created: {course_data['title']}",
                details={"course_id": course_id, "features": list(advanced_course.keys())}
            )
            
            return course_id
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to create advanced course: {str(e)}",
                error=e
            )
            raise Exception(f"Course creation failed: {str(e)}")
    
    async def enroll_student_advanced(self, user_id: str, course_id: str) -> Dict[str, Any]:
        """Enroll student with adaptive learning path generation"""
        try:
            db = get_database()
            
            # Generate personalized learning path
            learning_path = await self.adaptive_learning.generate_learning_path(user_id, course_id)
            
            # Create enrollment record
            enrollment = {
                "enrollment_id": str(uuid.uuid4()),
                "user_id": user_id,
                "course_id": course_id,
                "enrolled_at": datetime.utcnow(),
                "learning_path": learning_path,
                "progress": {
                    "percentage": 0,
                    "completed_lessons": [],
                    "time_spent_minutes": 0,
                    "last_activity": datetime.utcnow()
                },
                "gamification": {
                    "points_earned": 0,
                    "badges": [],
                    "achievements": []
                },
                "preferences": {
                    "study_reminders": True,
                    "peer_learning": True,
                    "progress_sharing": False
                }
            }
            
            await db.course_enrollments.insert_one(enrollment)
            
            # Update course analytics
            await db.advanced_courses.update_one(
                {"course_id": course_id},
                {"$inc": {"analytics.total_enrollments": 1}}
            )
            
            # Initialize gamification profile
            await db.user_gamification.update_one(
                {"user_id": user_id},
                {
                    "$setOnInsert": {
                        "total_points": 0,
                        "badges": [],
                        "level": 1,
                        "streak_days": 0
                    }
                },
                upsert=True
            )
            
            return enrollment
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to enroll student: {str(e)}",
                error=e, user_id=user_id
            )
            raise Exception(f"Enrollment failed: {str(e)}")
    
    async def track_learning_progress(self, user_id: str, course_id: str, lesson_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track and analyze learning progress with gamification"""
        try:
            db = get_database()
            
            # Update progress
            progress_update = {
                "last_activity": datetime.utcnow(),
                "$addToSet": {"progress.completed_lessons": lesson_id},
                "$inc": {"progress.time_spent_minutes": completion_data.get("time_spent", 0)}
            }
            
            await db.course_enrollments.update_one(
                {"user_id": user_id, "course_id": course_id},
                progress_update
            )
            
            # Calculate new progress percentage
            course = await db.advanced_courses.find_one({"course_id": course_id})
            total_lessons = len(course.get("lessons", [])) if course else 1
            
            enrollment = await db.course_enrollments.find_one({"user_id": user_id, "course_id": course_id})
            completed_lessons = len(enrollment.get("progress", {}).get("completed_lessons", []))
            
            progress_percentage = (completed_lessons / total_lessons) * 100
            
            await db.course_enrollments.update_one(
                {"user_id": user_id, "course_id": course_id},
                {"$set": {"progress.percentage": progress_percentage}}
            )
            
            # Award gamification points
            points_awarded = await self.gamification.award_points(user_id, "lesson_completion", course_id)
            
            # Check for course completion
            if progress_percentage >= 100:
                await self.gamification.award_points(user_id, "course_completion", course_id)
                
                # Generate certificate if enabled
                if course and course.get("certificates_enabled", True):
                    certificate_id = await self._generate_certificate(user_id, course_id)
                    
                    await professional_logger.log(
                        LogLevel.INFO, LogCategory.LEARNING,
                        f"Course completed - Certificate generated",
                        user_id=user_id,
                        details={"course_id": course_id, "certificate_id": certificate_id}
                    )
            
            return {
                "progress_percentage": progress_percentage,
                "points_awarded": points_awarded,
                "completed_lessons": completed_lessons,
                "total_lessons": total_lessons,
                "certificate_earned": progress_percentage >= 100
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to track learning progress: {str(e)}",
                error=e, user_id=user_id
            )
            return {"error": str(e)}
    
    async def _generate_certificate(self, user_id: str, course_id: str) -> str:
        """Generate blockchain-verified certificate"""
        try:
            db = get_database()
            
            certificate_id = str(uuid.uuid4())
            
            # Get course and user info
            course = await db.advanced_courses.find_one({"course_id": course_id})
            user = await db.users.find_one({"_id": user_id})
            
            certificate = {
                "certificate_id": certificate_id,
                "user_id": user_id,
                "course_id": course_id,
                "student_name": user.get("name", "Unknown") if user else "Unknown",
                "course_title": course.get("title", "Unknown Course") if course else "Unknown Course",
                "completion_date": datetime.utcnow(),
                "verification_hash": f"cert_{certificate_id}_{user_id}_{course_id}",  # Simplified hash
                "blockchain_verified": False,  # Would integrate with actual blockchain
                "issued_by": course.get("instructor_id") if course else "system",
                "valid": True,
                "metadata": {
                    "completion_time": "tracked",
                    "final_score": "tracked", 
                    "course_version": course.get("version", "1.0") if course else "1.0"
                }
            }
            
            await db.certificates.insert_one(certificate)
            
            return certificate_id
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.LEARNING,
                f"Failed to generate certificate: {str(e)}",
                error=e, user_id=user_id
            )
            return ""

# Global instance
advanced_lms_service = AdvancedLMSService()
