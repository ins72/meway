"""
Rate Limiting Service
Business logic for API rate limiting and throttling system
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

from core.database import get_database

class RateLimitingService:
    
    # Default rate limits by subscription tier
    SUBSCRIPTION_LIMITS = {
        "free": {
            "api_calls_per_minute": 60,
            "api_calls_per_hour": 1000,
            "api_calls_per_day": 10000,
            "file_uploads_per_day": 50,
            "ai_requests_per_hour": 10,
            "storage_gb": 1,
            "team_members": 1,
            "monthly_email_sends": 1000
        },
        "basic": {
            "api_calls_per_minute": 120,
            "api_calls_per_hour": 2500,
            "api_calls_per_day": 25000,
            "file_uploads_per_day": 200,
            "ai_requests_per_hour": 50,
            "storage_gb": 10,
            "team_members": 5,
            "monthly_email_sends": 5000
        },
        "professional": {
            "api_calls_per_minute": 300,
            "api_calls_per_hour": 10000,
            "api_calls_per_day": 100000,
            "file_uploads_per_day": 500,
            "ai_requests_per_hour": 200,
            "storage_gb": 100,
            "team_members": 25,
            "monthly_email_sends": 25000
        },
        "enterprise": {
            "api_calls_per_minute": 1000,
            "api_calls_per_hour": 50000,
            "api_calls_per_day": 500000,
            "file_uploads_per_day": 2000,
            "ai_requests_per_hour": 1000,
            "storage_gb": 1000,
            "team_members": 100,
            "monthly_email_sends": 100000
        }
    }
    
    @staticmethod
    async def get_rate_limit_status(user_id: str) -> Dict[str, Any]:
        """Get current rate limit status for user"""
        database = get_database()
        
        # Get user's subscription tier
        users_collection = database.users
        user = await users_collection.find_one({"_id": user_id})
        subscription_tier = user.get("subscription_tier", "free") if user else "free"
        
        # Get user's current usage
        rate_limit_collection = database.rate_limits
        current_time = datetime.utcnow()
        
        # Calculate time windows
        minute_start = current_time.replace(second=0, microsecond=0)
        hour_start = current_time.replace(minute=0, second=0, microsecond=0)
        day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get current usage counts (mock for now)
        limits = RateLimitingService.SUBSCRIPTION_LIMITS[subscription_tier]
        
        # Mock current usage (in real implementation, query actual usage)
        usage_data = {
            "api_calls_per_minute": {
                "limit": limits["api_calls_per_minute"],
                "used": 23,  # Mock data
                "remaining": limits["api_calls_per_minute"] - 23,
                "resets_at": (minute_start + timedelta(minutes=1)).isoformat(),
                "reset_in_seconds": 60 - current_time.second
            },
            "api_calls_per_hour": {
                "limit": limits["api_calls_per_hour"],
                "used": 1347,  # Mock data
                "remaining": limits["api_calls_per_hour"] - 1347,
                "resets_at": (hour_start + timedelta(hours=1)).isoformat(),
                "reset_in_seconds": 3600 - (current_time.minute * 60 + current_time.second)
            },
            "api_calls_per_day": {
                "limit": limits["api_calls_per_day"],
                "used": 8934,  # Mock data
                "remaining": limits["api_calls_per_day"] - 8934,
                "resets_at": (day_start + timedelta(days=1)).isoformat(),
                "reset_in_seconds": 86400 - (current_time.hour * 3600 + current_time.minute * 60 + current_time.second)
            },
            "file_uploads_per_day": {
                "limit": limits["file_uploads_per_day"],
                "used": 12,
                "remaining": limits["file_uploads_per_day"] - 12,
                "resets_at": (day_start + timedelta(days=1)).isoformat()
            },
            "ai_requests_per_hour": {
                "limit": limits["ai_requests_per_hour"],
                "used": 34,
                "remaining": limits["ai_requests_per_hour"] - 34,
                "resets_at": (hour_start + timedelta(hours=1)).isoformat()
            }
        }
        
        # Workspace limits
        workspace_limits = {
            "team_members": {
                "limit": limits["team_members"],
                "used": 3,  # Mock data
                "remaining": limits["team_members"] - 3
            },
            "storage_gb": {
                "limit": limits["storage_gb"],
                "used": 2.34,  # Mock data in GB
                "remaining": limits["storage_gb"] - 2.34,
                "usage_percentage": (2.34 / limits["storage_gb"]) * 100
            },
            "monthly_email_sends": {
                "limit": limits["monthly_email_sends"],
                "used": 234,
                "remaining": limits["monthly_email_sends"] - 234,
                "resets_at": (current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1).isoformat()
            }
        }
        
        return {
            "user_id": user_id,
            "subscription_tier": subscription_tier,
            "user_limits": usage_data,
            "workspace_limits": workspace_limits,
            "next_tier_info": RateLimitingService._get_next_tier_info(subscription_tier),
            "warnings": RateLimitingService._get_usage_warnings(usage_data, workspace_limits)
        }
    
    @staticmethod
    async def get_rate_limit_metrics(user_id: str, timeframe: str = "24h") -> Dict[str, Any]:
        """Get rate limiting metrics and analytics"""
        database = get_database()
        
        # Calculate time range
        if timeframe == "1h":
            start_time = datetime.utcnow() - timedelta(hours=1)
            interval = "minute"
        elif timeframe == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
            interval = "hour"
        elif timeframe == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
            interval = "day"
        else:
            start_time = datetime.utcnow() - timedelta(hours=24)
            interval = "hour"
        
        # Mock metrics data (in real implementation, aggregate from rate_limit_usage collection)
        usage_patterns = []
        current = start_time
        
        while current <= datetime.utcnow():
            if interval == "minute":
                timestamp = current.strftime("%H:%M")
                requests = max(0, int(50 + (hash(current.isoformat()) % 100) - 50))
                throttled = max(0, int(requests * 0.02))  # 2% throttled
                current += timedelta(minutes=1)
            elif interval == "hour":
                timestamp = current.strftime("%H:00")
                requests = max(0, int(500 + (hash(current.isoformat()) % 1000) - 500))
                throttled = max(0, int(requests * 0.03))  # 3% throttled
                current += timedelta(hours=1)
            else:  # day
                timestamp = current.strftime("%Y-%m-%d")
                requests = max(0, int(5000 + (hash(current.isoformat()) % 5000) - 2500))
                throttled = max(0, int(requests * 0.01))  # 1% throttled
                current += timedelta(days=1)
            
            success_rate = ((requests - throttled) / max(requests, 1)) * 100
            
            usage_patterns.append({
                "timestamp": timestamp,
                "requests": requests,
                "throttled": throttled,
                "success_rate": round(success_rate, 1)
            })
        
        # Top endpoints (mock data)
        top_endpoints = [
            {
                "endpoint": "/api/dashboard/overview",
                "requests": 1234,
                "avg_response_time": "67ms",
                "throttled": 12,
                "success_rate": 99.0
            },
            {
                "endpoint": "/api/analytics/data",
                "requests": 897,
                "avg_response_time": "145ms",
                "throttled": 23,
                "success_rate": 97.4
            },
            {
                "endpoint": "/api/users/profile",
                "requests": 654,
                "avg_response_time": "89ms",
                "throttled": 3,
                "success_rate": 99.5
            },
            {
                "endpoint": "/api/workspaces",
                "requests": 432,
                "avg_response_time": "234ms",
                "throttled": 8,
                "success_rate": 98.1
            }
        ]
        
        # Calculate totals
        total_requests = sum(pattern["requests"] for pattern in usage_patterns)
        total_throttled = sum(pattern["throttled"] for pattern in usage_patterns)
        overall_success_rate = ((total_requests - total_throttled) / max(total_requests, 1)) * 100
        
        return {
            "timeframe": timeframe,
            "interval": interval,
            "usage_patterns": usage_patterns,
            "top_endpoints": top_endpoints,
            "summary": {
                "total_requests": total_requests,
                "total_throttled": total_throttled,
                "overall_success_rate": round(overall_success_rate, 1),
                "avg_requests_per_interval": round(total_requests / len(usage_patterns), 1)
            },
            "recommendations": RateLimitingService._get_optimization_recommendations(overall_success_rate, total_throttled)
        }
    
    @staticmethod
    async def get_api_usage(user_id: str, timeframe: str = "24h", endpoint: str = "all") -> Dict[str, Any]:
        """Get detailed API usage statistics"""
        database = get_database()
        
        # Mock detailed usage data
        if endpoint == "all":
            endpoints_data = [
                {
                    "endpoint": "/api/dashboard/overview",
                    "method": "GET",
                    "requests": 1234,
                    "avg_response_time": 67,
                    "min_response_time": 45,
                    "max_response_time": 234,
                    "error_rate": 0.5,
                    "throttle_rate": 1.2,
                    "data_transferred_mb": 15.6,
                    "cache_hit_rate": 78.5
                },
                {
                    "endpoint": "/api/analytics/data",
                    "method": "POST",
                    "requests": 897,
                    "avg_response_time": 145,
                    "min_response_time": 89,
                    "max_response_time": 456,
                    "error_rate": 2.3,
                    "throttle_rate": 2.8,
                    "data_transferred_mb": 45.2,
                    "cache_hit_rate": 45.6
                },
                {
                    "endpoint": "/api/users/profile",
                    "method": "GET",
                    "requests": 654,
                    "avg_response_time": 89,
                    "min_response_time": 34,
                    "max_response_time": 178,
                    "error_rate": 0.8,
                    "throttle_rate": 0.5,
                    "data_transferred_mb": 8.9,
                    "cache_hit_rate": 89.2
                }
            ]
        else:
            # Single endpoint data
            endpoints_data = [
                {
                    "endpoint": endpoint,
                    "method": "GET",
                    "requests": 1234,
                    "avg_response_time": 67,
                    "min_response_time": 45,
                    "max_response_time": 234,
                    "error_rate": 0.5,
                    "throttle_rate": 1.2,
                    "data_transferred_mb": 15.6,
                    "cache_hit_rate": 78.5,
                    "hourly_breakdown": [
                        {"hour": "00:00", "requests": 45, "avg_response_time": 56},
                        {"hour": "01:00", "requests": 23, "avg_response_time": 78},
                        {"hour": "09:00", "requests": 156, "avg_response_time": 67},
                        {"hour": "14:00", "requests": 234, "avg_response_time": 89}
                    ]
                }
            ]
        
        return {
            "timeframe": timeframe,
            "endpoint_filter": endpoint,
            "endpoints": endpoints_data,
            "summary": {
                "total_requests": sum(ep["requests"] for ep in endpoints_data),
                "avg_response_time": sum(ep["avg_response_time"] * ep["requests"] for ep in endpoints_data) / sum(ep["requests"] for ep in endpoints_data),
                "total_data_transferred_mb": sum(ep["data_transferred_mb"] for ep in endpoints_data),
                "overall_error_rate": sum(ep["error_rate"] * ep["requests"] for ep in endpoints_data) / sum(ep["requests"] for ep in endpoints_data),
                "overall_cache_hit_rate": sum(ep["cache_hit_rate"] * ep["requests"] for ep in endpoints_data) / sum(ep["requests"] for ep in endpoints_data)
            }
        }
    
    @staticmethod
    async def check_rate_limit(
        user_id: str,
        endpoint: str,
        action: str = "api_call",
        ip_address: str = "unknown"
    ) -> Dict[str, Any]:
        """Check if request is within rate limits"""
        database = get_database()
        
        # Get user's subscription tier
        users_collection = database.users
        user = await users_collection.find_one({"_id": user_id})
        subscription_tier = user.get("subscription_tier", "free") if user else "free"
        
        limits = RateLimitingService.SUBSCRIPTION_LIMITS[subscription_tier]
        
        # Mock rate limit check
        current_usage = {
            "minute": 23,  # Mock current minute usage
            "hour": 1347,  # Mock current hour usage
            "day": 8934   # Mock current day usage
        }
        
        # Check limits
        checks = {
            "minute_limit": {
                "passed": current_usage["minute"] < limits["api_calls_per_minute"],
                "current": current_usage["minute"],
                "limit": limits["api_calls_per_minute"],
                "remaining": limits["api_calls_per_minute"] - current_usage["minute"],
                "resets_in": 60 - datetime.utcnow().second
            },
            "hour_limit": {
                "passed": current_usage["hour"] < limits["api_calls_per_hour"],
                "current": current_usage["hour"],
                "limit": limits["api_calls_per_hour"],
                "remaining": limits["api_calls_per_hour"] - current_usage["hour"],
                "resets_in": 3600 - (datetime.utcnow().minute * 60 + datetime.utcnow().second)
            },
            "day_limit": {
                "passed": current_usage["day"] < limits["api_calls_per_day"],
                "current": current_usage["day"],
                "limit": limits["api_calls_per_day"],
                "remaining": limits["api_calls_per_day"] - current_usage["day"],
                "resets_in": 86400 - (datetime.utcnow().hour * 3600 + datetime.utcnow().minute * 60 + datetime.utcnow().second)
            }
        }
        
        # Determine if request should be allowed
        allowed = all(check["passed"] for check in checks.values())
        
        # Get the most restrictive limit that's being approached
        most_restrictive = min(checks.values(), key=lambda x: x["remaining"] / x["limit"])
        
        return {
            "allowed": allowed,
            "endpoint": endpoint,
            "action": action,
            "subscription_tier": subscription_tier,
            "checks": checks,
            "most_restrictive": most_restrictive,
            "retry_after": most_restrictive["resets_in"] if not allowed else None,
            "headers": {
                "X-RateLimit-Limit": str(most_restrictive["limit"]),
                "X-RateLimit-Remaining": str(most_restrictive["remaining"]),
                "X-RateLimit-Reset": str(int(datetime.utcnow().timestamp()) + most_restrictive["resets_in"])
            }
        }
    
    @staticmethod
    async def record_api_usage(
        user_id: str,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        ip_address: str = "unknown"
    ) -> Dict[str, Any]:
        """Record API usage for analytics"""
        database = get_database()
        
        usage_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "endpoint": endpoint,
            "method": method,
            "response_time": response_time,
            "status_code": status_code,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow(),
            "success": status_code < 400,
            "throttled": status_code == 429
        }
        
        # In real implementation, store this data
        # rate_limit_usage_collection = database.rate_limit_usage
        # await rate_limit_usage_collection.insert_one(usage_doc)
        
        return {
            "recorded": True,
            "usage_id": usage_doc["_id"],
            "timestamp": usage_doc["timestamp"].isoformat()
        }
    
    @staticmethod
    async def get_user_quotas(user_id: str) -> Dict[str, Any]:
        """Get user's rate limit quotas and subscription limits"""
        database = get_database()
        
        # Get user's subscription tier
        users_collection = database.users
        user = await users_collection.find_one({"_id": user_id})
        subscription_tier = user.get("subscription_tier", "free") if user else "free"
        
        limits = RateLimitingService.SUBSCRIPTION_LIMITS[subscription_tier]
        
        return {
            "user_id": user_id,
            "subscription_tier": subscription_tier,
            "quotas": limits,
            "features": {
                "api_access": True,
                "webhook_support": subscription_tier != "free",
                "advanced_analytics": subscription_tier in ["professional", "enterprise"],
                "priority_support": subscription_tier == "enterprise",
                "custom_rate_limits": subscription_tier == "enterprise"
            },
            "upgrade_benefits": RateLimitingService._get_upgrade_benefits(subscription_tier)
        }
    
    @staticmethod
    async def get_rate_limit_alerts(user_id: str) -> Dict[str, Any]:
        """Get rate limit alerts and warnings"""
        # Mock alerts based on usage patterns
        alerts = []
        
        # Mock high usage alert
        alerts.append({
            "id": str(uuid.uuid4()),
            "type": "warning",
            "severity": "medium",
            "title": "High API Usage Detected",
            "message": "You've used 85% of your hourly API limit. Consider optimizing your requests or upgrading your plan.",
            "category": "usage_warning",
            "triggered_at": datetime.utcnow().isoformat(),
            "action_required": False,
            "suggestions": [
                "Implement request caching",
                "Batch multiple requests together",
                "Upgrade to Professional plan"
            ]
        })
        
        # Mock approaching limit alert
        alerts.append({
            "id": str(uuid.uuid4()),
            "type": "info",
            "severity": "low",
            "title": "Storage Limit Approaching",
            "message": "You've used 70% of your storage quota. Clean up unused files or upgrade for more space.",
            "category": "storage_warning",
            "triggered_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "action_required": False,
            "suggestions": [
                "Delete old uploads",
                "Compress large files",
                "Archive unused content"
            ]
        })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "severity_breakdown": {
                "high": 0,
                "medium": 1,
                "low": 1
            }
        }
    
    @staticmethod
    async def get_top_endpoints(user_id: str, limit: int = 10, timeframe: str = "24h") -> Dict[str, Any]:
        """Get top API endpoints by usage"""
        # Mock top endpoints data
        top_endpoints = [
            {
                "endpoint": "/api/dashboard/overview",
                "requests": 1234,
                "avg_response_time": 67,
                "success_rate": 99.0,
                "throttle_rate": 1.2,
                "data_usage_mb": 15.6,
                "trending": "stable"
            },
            {
                "endpoint": "/api/analytics/data",
                "requests": 897,
                "avg_response_time": 145,
                "success_rate": 97.4,
                "throttle_rate": 2.8,
                "data_usage_mb": 45.2,
                "trending": "up"
            },
            {
                "endpoint": "/api/users/profile",
                "requests": 654,
                "avg_response_time": 89,
                "success_rate": 99.5,
                "throttle_rate": 0.5,
                "data_usage_mb": 8.9,
                "trending": "down"
            },
            {
                "endpoint": "/api/workspaces",
                "requests": 432,
                "avg_response_time": 234,
                "success_rate": 98.1,
                "throttle_rate": 0.8,
                "data_usage_mb": 12.3,
                "trending": "stable"
            }
        ]
        
        return {
            "timeframe": timeframe,
            "limit": limit,
            "endpoints": top_endpoints[:limit],
            "total_requests": sum(ep["requests"] for ep in top_endpoints),
            "avg_response_time": sum(ep["avg_response_time"] * ep["requests"] for ep in top_endpoints) / sum(ep["requests"] for ep in top_endpoints)
        }
    
    @staticmethod
    async def get_performance_metrics(user_id: str, timeframe: str = "24h") -> Dict[str, Any]:
        """Get API performance metrics"""
        # Mock performance metrics
        return {
            "timeframe": timeframe,
            "response_time": {
                "average": 134.5,
                "p50": 89.0,
                "p95": 456.0,
                "p99": 1234.0,
                "min": 23.0,
                "max": 5678.0
            },
            "throughput": {
                "requests_per_second": 12.5,
                "requests_per_minute": 750,
                "peak_rps": 45.6,
                "low_rps": 2.3
            },
            "error_rates": {
                "total_errors": 23,
                "error_rate_percentage": 1.8,
                "4xx_errors": 15,
                "5xx_errors": 8,
                "timeout_errors": 2
            },
            "cache_performance": {
                "hit_rate": 76.3,
                "miss_rate": 23.7,
                "cache_size_mb": 245.6,
                "avg_cache_response_time": 12.3
            }
        }
    
    @staticmethod
    async def get_optimization_suggestions(user_id: str) -> Dict[str, Any]:
        """Get API usage optimization suggestions"""
        suggestions = [
            {
                "id": "cache_implementation",
                "category": "performance",
                "priority": "high",
                "title": "Implement Response Caching",
                "description": "Add caching for frequently requested dashboard data to reduce API calls by up to 60%",
                "potential_savings": {
                    "api_calls_reduction": "60%",
                    "response_time_improvement": "80%",
                    "cost_savings": "$45/month"
                },
                "implementation": {
                    "effort": "Medium",
                    "time_estimate": "2-3 days",
                    "resources": ["Redis", "Cache middleware"]
                }
            },
            {
                "id": "request_batching",
                "category": "optimization",
                "priority": "medium",
                "title": "Batch API Requests",
                "description": "Combine multiple small requests into batch operations to reduce overhead",
                "potential_savings": {
                    "api_calls_reduction": "40%",
                    "response_time_improvement": "30%",
                    "cost_savings": "$25/month"
                },
                "implementation": {
                    "effort": "Low",
                    "time_estimate": "1 day",
                    "resources": ["API client refactoring"]
                }
            },
            {
                "id": "subscription_upgrade",
                "category": "scaling",
                "priority": "medium",
                "title": "Consider Plan Upgrade",
                "description": "Your usage patterns suggest you'd benefit from higher rate limits and additional features",
                "potential_savings": {
                    "api_calls_increase": "300%",
                    "response_time_improvement": "50%",
                    "additional_features": "Advanced analytics, Priority support"
                },
                "implementation": {
                    "effort": "None",
                    "time_estimate": "Immediate",
                    "resources": []
                }
            }
        ]
        
        return {
            "suggestions": suggestions,
            "total_potential_savings": {
                "monthly_cost": "$70",
                "performance_improvement": "65%",
                "reliability_increase": "40%"
            }
        }
    
    @staticmethod
    async def reset_rate_limits(user_id: str, limit_type: str) -> Dict[str, Any]:
        """Reset rate limits (admin function)"""
        database = get_database()
        
        # In real implementation, clear rate limit counters
        reset_time = datetime.utcnow()
        
        return {
            "user_id": user_id,
            "limit_type": limit_type,
            "reset_at": reset_time.isoformat(),
            "message": f"{limit_type} rate limits have been reset"
        }
    
    @staticmethod
    async def get_system_health() -> Dict[str, Any]:
        """Get rate limiting system health status"""
        return {
            "status": "healthy",
            "uptime": "99.9%",
            "response_time": "12ms",
            "active_limits": 1247,
            "throttled_requests_24h": 89,
            "system_load": {
                "cpu": 23.5,
                "memory": 45.6,
                "storage": 67.8
            },
            "components": {
                "rate_limiter": {"status": "healthy", "response_time": "8ms"},
                "quota_tracker": {"status": "healthy", "response_time": "15ms"},
                "analytics_engine": {"status": "healthy", "response_time": "45ms"},
                "alert_system": {"status": "healthy", "response_time": "12ms"}
            }
        }
    
    @staticmethod
    def _get_next_tier_info(current_tier: str) -> Optional[Dict[str, Any]]:
        """Get information about the next subscription tier"""
        tier_order = ["free", "basic", "professional", "enterprise"]
        
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                next_tier = tier_order[current_index + 1]
                return {
                    "name": next_tier,
                    "limits": RateLimitingService.SUBSCRIPTION_LIMITS[next_tier],
                    "benefits": [
                        f"Increase API calls from {RateLimitingService.SUBSCRIPTION_LIMITS[current_tier]['api_calls_per_hour']} to {RateLimitingService.SUBSCRIPTION_LIMITS[next_tier]['api_calls_per_hour']} per hour",
                        f"Expand storage from {RateLimitingService.SUBSCRIPTION_LIMITS[current_tier]['storage_gb']}GB to {RateLimitingService.SUBSCRIPTION_LIMITS[next_tier]['storage_gb']}GB",
                        f"Support {RateLimitingService.SUBSCRIPTION_LIMITS[next_tier]['team_members']} team members"
                    ]
                }
        except ValueError:
            pass
        
        return None
    
    @staticmethod
    def _get_usage_warnings(user_limits: Dict, workspace_limits: Dict) -> List[Dict[str, Any]]:
        """Generate usage warnings based on current usage"""
        warnings = []
        
        # Check API usage warnings
        for limit_type, limit_data in user_limits.items():
            usage_percentage = (limit_data["used"] / limit_data["limit"]) * 100
            if usage_percentage > 80:
                warnings.append({
                    "type": "usage_warning",
                    "severity": "high" if usage_percentage > 95 else "medium",
                    "message": f"{limit_type.replace('_', ' ').title()} usage at {usage_percentage:.1f}%",
                    "suggestion": "Consider optimizing usage or upgrading plan"
                })
        
        # Check workspace warnings
        storage_usage = workspace_limits["storage_gb"]["used"] / workspace_limits["storage_gb"]["limit"] * 100
        if storage_usage > 80:
            warnings.append({
                "type": "storage_warning",
                "severity": "medium",
                "message": f"Storage usage at {storage_usage:.1f}%",
                "suggestion": "Clean up files or upgrade storage"
            })
        
        return warnings
    
    @staticmethod
    def _get_optimization_recommendations(success_rate: float, throttled_count: int) -> List[Dict[str, Any]]:
        """Get optimization recommendations based on usage patterns"""
        recommendations = []
        
        if success_rate < 95:
            recommendations.append({
                "type": "performance",
                "message": f"Success rate is {success_rate:.1f}%. Consider implementing caching or optimizing requests.",
                "priority": "high"
            })
        
        if throttled_count > 50:
            recommendations.append({
                "type": "scaling",
                "message": f"{throttled_count} requests were throttled. Consider upgrading your plan for higher limits.",
                "priority": "medium"
            })
        
        if not recommendations:
            recommendations.append({
                "type": "optimization",
                "message": "Great performance! Consider implementing request batching for even better efficiency.",
                "priority": "low"
            })
        
        return recommendations
    
    @staticmethod
    def _get_upgrade_benefits(current_tier: str) -> List[str]:
        """Get benefits of upgrading subscription"""
        if current_tier == "free":
            return [
                "10x more API calls per hour",
                "5 team members support",
                "10GB storage space",
                "Email support"
            ]
        elif current_tier == "basic":
            return [
                "4x more API calls per hour",
                "25 team members support", 
                "100GB storage space",
                "Priority support",
                "Advanced analytics"
            ]
        elif current_tier == "professional":
            return [
                "5x more API calls per hour",
                "100 team members support",
                "1TB storage space",
                "24/7 phone support",
                "Custom rate limits",
                "SLA guarantee"
            ]
        else:
            return ["You're on our highest tier!"]

# Global service instance
rate_limiting_service = RateLimitingService()

    async def create_item(self, user_id: str, item_data: dict):
        """Create new item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            new_item = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                **item_data,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active"
            }
            
            await collections['items'].insert_one(new_item)
            
            return {
                "success": True,
                "data": new_item,
                "message": "Item created successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

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
            
            if not item:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "data": item,
                "message": "Item retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def update_item(self, user_id: str, item_id: str, update_data: dict):
        """Update existing item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collections['items'].update_one(
                {"_id": item_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                return {"success": False, "message": "Item not found or no changes made"}
            
            # Get updated item
            updated_item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            return {
                "success": True,
                "data": updated_item,
                "message": "Item updated successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def delete_item(self, user_id: str, item_id: str):
        """Delete item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['items'].delete_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "message": "Item deleted successfully"
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