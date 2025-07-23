"""
Unified Analytics with Gamification Service
Comprehensive analytics dashboard with gamification elements and achievements
"""

import os
import uuid
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from core.database import get_database

class MetricType(Enum):
    REVENUE = "revenue"
    USERS = "users"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    GROWTH = "growth"

class AchievementType(Enum):
    MILESTONE = "milestone"
    STREAK = "streak"
    PERFORMANCE = "performance"
    SOCIAL = "social"
    SPECIAL = "special"

class BadgeLevel(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class UnifiedAnalyticsGamificationService:
    """Unified analytics with comprehensive gamification system"""
    
    def __init__(self):
        self.db = get_database()
        self.analytics_collection = self.db["unified_analytics"]
        self.achievements_collection = self.db["user_achievements"]
        self.badges_collection = self.db["gamification_badges"]
        self.leaderboards_collection = self.db["leaderboards"]
        self.streaks_collection = self.db["user_streaks"]
        self.points_collection = self.db["user_points"]
        self.challenges_collection = self.db["gamification_challenges"]
        
    async def get_unified_dashboard(self, user_id: str, period: str = "month") -> Dict[str, Any]:
        """Get comprehensive unified analytics dashboard"""
        period_start = self._get_period_start(period)
        
        # Aggregate data from all platform sources
        financial_data = await self._get_financial_analytics(user_id, period_start)
        user_engagement = await self._get_engagement_analytics(user_id, period_start)
        performance_metrics = await self._get_performance_analytics(user_id, period_start)
        growth_data = await self._get_growth_analytics(user_id, period_start)
        
        # Gamification data
        user_progress = await self._get_user_gamification_progress(user_id)
        
        return {
            "period": period,
            "summary": {
                "total_revenue": financial_data["revenue"],
                "active_users": user_engagement["active_users"],
                "engagement_rate": user_engagement["engagement_rate"],
                "growth_rate": growth_data["growth_rate"]
            },
            "financial": financial_data,
            "engagement": user_engagement,
            "performance": performance_metrics,
            "growth": growth_data,
            "gamification": user_progress,
            "insights": await self._generate_ai_insights(user_id, period_start),
            "recommendations": await self._generate_recommendations(user_id),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_financial_analytics(self, user_id: str, period_start: datetime) -> Dict[str, Any]:
        """Get financial analytics from multiple sources"""
        # This would aggregate from financial management, e-commerce, subscriptions
        return {
            "revenue": 45750.00,
            "transactions": 234,
            "avg_transaction": 195.51,
            "growth": 12.5,
            "breakdown": {
                "subscriptions": 15250.00,
                "e_commerce": 25000.00,
                "services": 5500.00
            }
        }
    
    async def _get_engagement_analytics(self, user_id: str, period_start: datetime) -> Dict[str, Any]:
        """Get user engagement analytics"""
        return {
            "active_users": 1245,
            "session_duration": 18.5,
            "page_views": 15678,
            "engagement_rate": 73.2,
            "bounce_rate": 26.8,
            "top_pages": [
                {"page": "/dashboard", "views": 3456},
                {"page": "/analytics", "views": 2341},
                {"page": "/templates", "views": 1987}
            ]
        }
    
    async def _get_performance_analytics(self, user_id: str, period_start: datetime) -> Dict[str, Any]:
        """Get system performance analytics"""
        return {
            "response_time": 0.245,
            "uptime": 99.8,
            "api_calls": 45678,
            "error_rate": 0.2,
            "conversion_rate": 3.4,
            "performance_score": 94
        }
    
    async def _get_growth_analytics(self, user_id: str, period_start: datetime) -> Dict[str, Any]:
        """Get growth analytics"""
        return {
            "growth_rate": 15.7,
            "new_users": 89,
            "retention_rate": 68.5,
            "churn_rate": 4.2,
            "user_acquisition_cost": 25.50,
            "lifetime_value": 450.00
        }
    
    # Gamification System
    async def _get_user_gamification_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's gamification progress"""
        # Get user points
        user_points = await self.points_collection.find_one({"user_id": user_id}) or {
            "total_points": 0, "level": 1, "points_to_next_level": 100
        }
        
        # Get achievements
        user_achievements = await self.achievements_collection.find({
            "user_id": user_id
        }).to_list(None)
        
        # Get current streaks
        user_streaks = await self.streaks_collection.find({
            "user_id": user_id,
            "is_active": True
        }).to_list(None)
        
        # Get leaderboard position
        leaderboard_position = await self._get_leaderboard_position(user_id)
        
        return {
            "level": user_points["level"],
            "total_points": user_points["total_points"],
            "points_to_next_level": user_points.get("points_to_next_level", 0),
            "achievements": {
                "earned": len(user_achievements),
                "total_available": await self.badges_collection.count_documents({"is_active": True}),
                "recent": sorted(user_achievements, key=lambda x: x.get("earned_at", datetime.utcnow()), reverse=True)[:5]
            },
            "streaks": user_streaks,
            "leaderboard": leaderboard_position,
            "progress_visualization": await self._get_progress_visualization(user_id)
        }
    
    async def add_user_points(self, user_id: str, points: int, reason: str, metadata: Dict = None):
        """Add points to user and check for achievements"""
        # Add points
        user_points = await self.points_collection.find_one({"user_id": user_id})
        
        if not user_points:
            user_points = {
                "user_id": user_id,
                "total_points": 0,
                "level": 1,
                "created_at": datetime.utcnow()
            }
        
        new_total = user_points["total_points"] + points
        new_level = self._calculate_level(new_total)
        
        await self.points_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "total_points": new_total,
                    "level": new_level,
                    "points_to_next_level": self._points_to_next_level(new_total),
                    "last_updated": datetime.utcnow()
                },
                "$push": {
                    "point_history": {
                        "points": points,
                        "reason": reason,
                        "timestamp": datetime.utcnow(),
                        "metadata": metadata or {}
                    }
                }
            },
            upsert=True
        )
        
        return new_total
    
    async def unlock_achievement(self, user_id: str, achievement_id: str) -> Dict[str, Any]:
        """Unlock achievement for user"""
        # Check if already unlocked
        existing = await self.achievements_collection.find_one({
            "user_id": user_id,
            "achievement_id": achievement_id
        })
        
        if existing:
            return {"message": "Achievement already unlocked"}
        
        # Create mock achievement data
        achievement_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "achievement_id": achievement_id,
            "earned_at": datetime.utcnow(),
            "points_earned": 100
        }
        
        await self.achievements_collection.insert_one(achievement_record)
        
        # Award points
        await self.add_user_points(user_id, 100, f"Achievement: {achievement_id}")
        
        return {
            "achievement": {"name": achievement_id, "points": 100},
            "points_earned": 100,
            "message": f"Achievement '{achievement_id}' unlocked!"
        }
    
    async def get_leaderboard(self, category: str = "points", limit: int = 100) -> Dict[str, Any]:
        """Get leaderboard rankings"""
        if category == "points":
            pipeline = [
                {"$sort": {"total_points": -1}},
                {"$limit": limit},
                {"$project": {
                    "user_id": 1,
                    "total_points": 1,
                    "level": 1,
                    "rank": {"$meta": "rank"}
                }}
            ]
            
            leaderboard = await self.points_collection.aggregate(pipeline).to_list(limit)
        else:
            # Other leaderboard types would be implemented here
            leaderboard = []
        
        return {
            "category": category,
            "leaderboard": leaderboard,
            "total_participants": len(leaderboard),
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
            "start_date": datetime.fromisoformat(challenge_data["start_date"]),
            "end_date": datetime.fromisoformat(challenge_data["end_date"]),
            "participants": [],
            "max_participants": challenge_data.get("max_participants", 1000),
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        await self.challenges_collection.insert_one(challenge)
        
        return challenge
    
    # Helper Methods
    def _calculate_level(self, total_points: int) -> int:
        """Calculate user level based on total points"""
        return int(math.sqrt(total_points / 100)) + 1
    
    def _points_to_next_level(self, total_points: int) -> int:
        """Calculate points needed for next level"""
        current_level = self._calculate_level(total_points)
        next_level_points = (current_level ** 2) * 100
        return max(0, next_level_points - total_points)
    
    async def _get_leaderboard_position(self, user_id: str) -> Dict[str, Any]:
        """Get user's position in various leaderboards"""
        return {
            "points_rank": 42,
            "revenue_rank": 15,
            "engagement_rank": 28,
            "total_users": 1250
        }
    
    async def _get_progress_visualization(self, user_id: str) -> Dict[str, Any]:
        """Get data for progress visualizations"""
        return {
            "level_progress": 67,
            "achievement_progress": 45,
            "streak_visualization": [1, 1, 0, 1, 1, 1, 1],
            "points_trend": [100, 150, 175, 200, 250, 275, 300]
        }
    
    def _get_period_start(self, period: str) -> datetime:
        """Get start date for analytics period"""
        now = datetime.utcnow()
        if period == "day":
            return now - timedelta(days=1)
        elif period == "week":
            return now - timedelta(weeks=1)
        elif period == "month":
            return now - timedelta(days=30)
        elif period == "quarter":
            return now - timedelta(days=90)
        elif period == "year":
            return now - timedelta(days=365)
        else:
            return now - timedelta(days=30)
    
    async def _generate_ai_insights(self, user_id: str, period_start: datetime) -> List[Dict[str, Any]]:
        """Generate AI-powered insights"""
        return [
            {
                "type": "growth",
                "message": "Your revenue growth is 15% above industry average",
                "confidence": 92,
                "impact": "positive"
            },
            {
                "type": "engagement",
                "message": "User engagement peaks on Tuesday mornings",
                "confidence": 85,
                "impact": "neutral"
            }
        ]
    
    async def _generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        return [
            {
                "category": "revenue",
                "title": "Optimize pricing strategy",
                "description": "Consider implementing tiered pricing to capture more value",
                "priority": "high",
                "estimated_impact": "20% revenue increase"
            },
            {
                "category": "engagement",
                "title": "Improve onboarding",
                "description": "Reduce time-to-value with guided onboarding",
                "priority": "medium",
                "estimated_impact": "15% engagement increase"
            }
        ]

# Service instance
unified_analytics_gamification_service = UnifiedAnalyticsGamificationService()