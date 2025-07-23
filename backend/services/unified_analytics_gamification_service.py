"""
Unified Analytics with Gamification Service - Simplified
Comprehensive analytics dashboard with gamification elements
"""

import uuid
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from core.database import get_database

class UnifiedAnalyticsGamificationService:
    """Unified analytics with gamification system"""
    
    def __init__(self):
        pass
    
    def _get_collections(self):
        """Get database collections"""
        db = get_database()
        if not db:
            raise RuntimeError("Database connection not available")
        
        return {
            'analytics': db["unified_analytics"],
            'achievements': db["user_achievements"],
            'points': db["user_points"],
            'leaderboards': db["leaderboards"]
        }
    
    async def get_unified_dashboard(self, user_id: str, period: str = "month") -> Dict[str, Any]:
        """Get comprehensive unified analytics dashboard"""
        # Simplified dashboard with mock data
        return {
            "period": period,
            "summary": {
                "total_revenue": 45750.00,
                "active_users": 1245,
                "engagement_rate": 73.2,
                "growth_rate": 15.7
            },
            "financial": {
                "revenue": 45750.00,
                "transactions": 234,
                "growth": 12.5
            },
            "engagement": {
                "active_users": 1245,
                "session_duration": 18.5,
                "engagement_rate": 73.2
            },
            "gamification": {
                "level": 5,
                "total_points": 2500,
                "points_to_next_level": 150,
                "achievements": {"earned": 12, "total_available": 25}
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def add_user_points(self, user_id: str, points: int, reason: str, metadata: Dict = None):
        """Add points to user account"""
        collections = self._get_collections()
        
        user_points = await collections['points'].find_one({"user_id": user_id})
        
        if not user_points:
            user_points = {
                "user_id": user_id,
                "total_points": 0,
                "level": 1,
                "created_at": datetime.utcnow()
            }
        
        new_total = user_points["total_points"] + points
        new_level = int(math.sqrt(new_total / 100)) + 1
        
        await collections['points'].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "total_points": new_total,
                    "level": new_level,
                    "last_updated": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return new_total
    
    async def unlock_achievement(self, user_id: str, achievement_id: str) -> Dict[str, Any]:
        """Unlock achievement for user"""
        collections = self._get_collections()
        
        achievement_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "achievement_id": achievement_id,
            "earned_at": datetime.utcnow(),
            "points_earned": 100
        }
        
        await collections['achievements'].insert_one(achievement_record)
        
        return {
            "achievement": {"name": achievement_id, "points": 100},
            "points_earned": 100,
            "message": f"Achievement '{achievement_id}' unlocked!"
        }
    
    async def get_leaderboard(self, category: str = "points", limit: int = 100) -> Dict[str, Any]:
        """Get leaderboard rankings"""
        return {
            "category": category,
            "leaderboard": [],
            "total_participants": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def create_challenge(self, creator_id: str, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create gamified challenge"""
        challenge = {
            "id": str(uuid.uuid4()),
            "creator_id": creator_id,
            "name": challenge_data["name"],
            "description": challenge_data["description"],
            "requirements": challenge_data["requirements"],
            "reward_points": challenge_data["reward_points"],
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        return challenge

def get_unified_analytics_gamification_service():
    """Factory function to get service instance"""
    return UnifiedAnalyticsGamificationService()

# Service instance
unified_analytics_gamification_service = get_unified_analytics_gamification_service()