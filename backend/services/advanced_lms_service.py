"""
Advanced SCORM Learning Management System Service
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
from pymongo.collection import Collection
import xml.etree.ElementTree as ET

class AdvancedLMSService:
    def __init__(self, db):
        self.db = db
        self.courses_collection = db["courses"]
        self.scorm_packages = db["scorm_packages"]
        self.learning_progress = db["learning_progress"]
        self.certifications = db["certifications"]
        self.gamification = db["gamification"]
        
    async def create_scorm_package(self, package_data: Dict) -> Dict:
        """Create and process SCORM package"""
        try:
            package_id = str(uuid.uuid4())
            scorm_data = {
                "_id": package_id,
                "title": package_data.get("title"),
                "description": package_data.get("description"),
                "version": package_data.get("version", "1.2"),
                "manifest_xml": package_data.get("manifest"),
                "content_files": package_data.get("files", []),
                "tracking_enabled": True,
                "completion_threshold": 80,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            await self.scorm_packages.insert_one(scorm_data)
            self.log(f"✅ SCORM package created: {package_id}")
            return scorm_data
            
        except Exception as e:
            self.log(f"❌ SCORM package creation failed: {str(e)}")
            return {"error": str(e)}
    
    async def track_learning_progress(self, user_id: str, course_id: str, lesson_data: Dict) -> Dict:
        """Track detailed learning progress with SCORM compliance"""
        try:
            progress_id = str(uuid.uuid4())
            progress_data = {
                "_id": progress_id,
                "user_id": user_id,
                "course_id": course_id,
                "lesson_id": lesson_data.get("lesson_id"),
                "progress_percentage": lesson_data.get("progress", 0),
                "time_spent": lesson_data.get("time_spent", 0),
                "completion_status": lesson_data.get("status", "incomplete"),
                "score": lesson_data.get("score"),
                "interactions": lesson_data.get("interactions", []),
                "timestamp": datetime.utcnow()
            }
            
            await self.learning_progress.insert_one(progress_data)
            
            # Update gamification points
            await self.update_gamification_points(user_id, lesson_data.get("progress", 0))
            
            return progress_data
            
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_certificate(self, user_id: str, course_id: str) -> Dict:
        """Generate blockchain-verified certificate"""
        try:
            # Check completion status
            progress = await self.learning_progress.find(
                {"user_id": user_id, "course_id": course_id}
            ).to_list(length=None)
            
            total_progress = sum([p.get("progress_percentage", 0) for p in progress])
            avg_progress = total_progress / len(progress) if progress else 0
            
            if avg_progress >= 80:  # Completion threshold
                cert_id = str(uuid.uuid4())
                certificate = {
                    "_id": cert_id,
                    "user_id": user_id,
                    "course_id": course_id,
                    "completion_percentage": avg_progress,
                    "issued_date": datetime.utcnow(),
                    "blockchain_hash": f"bc_{uuid.uuid4().hex[:16]}",  # Mock blockchain hash
                    "verification_url": f"/verify/certificate/{cert_id}",
                    "skills_earned": ["Leadership", "Communication", "Technical Skills"],
                    "status": "verified"
                }
                
                await self.certifications.insert_one(certificate)
                return certificate
            else:
                return {"error": "Course not completed. Minimum 80% required."}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def update_gamification_points(self, user_id: str, progress_gained: float) -> Dict:
        """Update user gamification points and badges"""
        try:
            points_earned = int(progress_gained * 10)  # 10 points per percentage
            
            # Check if user exists in gamification
            user_game_data = await self.gamification.find_one({"user_id": user_id})
            
            if user_game_data:
                new_points = user_game_data.get("total_points", 0) + points_earned
                await self.gamification.update_one(
                    {"user_id": user_id},
                    {
                        "$inc": {"total_points": points_earned},
                        "$set": {"last_activity": datetime.utcnow()},
                        "$push": {"recent_achievements": f"Earned {points_earned} points"}
                    }
                )
            else:
                # Create new gamification profile
                game_data = {
                    "_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "total_points": points_earned,
                    "level": 1,
                    "badges": ["New Learner"],
                    "achievements": [f"First {points_earned} points earned"],
                    "created_at": datetime.utcnow(),
                    "last_activity": datetime.utcnow()
                }
                await self.gamification.insert_one(game_data)
                
            return {"points_earned": points_earned, "status": "updated"}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_learning_analytics(self, user_id: str) -> Dict:
        """Get comprehensive learning analytics"""
        try:
            # Get user progress across all courses
            progress_data = await self.learning_progress.find(
                {"user_id": user_id}
            ).to_list(length=None)
            
            # Get gamification data
            game_data = await self.gamification.find_one({"user_id": user_id})
            
            # Get certificates
            certificates = await self.certifications.find(
                {"user_id": user_id}
            ).to_list(length=None)
            
            analytics = {
                "total_courses_enrolled": len(set([p["course_id"] for p in progress_data])),
                "total_lessons_completed": len([p for p in progress_data if p.get("completion_status") == "complete"]),
                "total_time_spent": sum([p.get("time_spent", 0) for p in progress_data]),
                "average_score": sum([p.get("score", 0) for p in progress_data if p.get("score")]) / len(progress_data) if progress_data else 0,
                "certificates_earned": len(certificates),
                "gamification": game_data or {},
                "learning_streak": 15,  # Mock data - calculate actual streak
                "weekly_progress": [20, 35, 45, 60, 75, 80, 85]  # Mock weekly data
            }
            
            return analytics
            
        except Exception as e:
            return {"error": str(e)}
    
    def log(self, message: str):
        """Simple logging method"""
        print(f"[LMS] {message}")
