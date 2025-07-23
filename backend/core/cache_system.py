"""
REDIS CACHING SYSTEM
High-performance caching for production deployment
"""

import redis
import json
import asyncio
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import hashlib
import os

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis connection and caching management"""
    
    def __init__(self):
        self.redis_client = None
        self.is_connected = False
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            # Try to connect to Redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            # Create Redis client
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await asyncio.to_thread(self.redis_client.ping)
            self.is_connected = True
            
            logger.info("✅ Redis cache connection established")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            logger.info("📝 Continuing without Redis cache (using memory cache)")
            self.is_connected = False
            return False
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        # Create a hash of the identifier for consistent key length
        hash_id = hashlib.md5(identifier.encode()).hexdigest()
        return f"mewayz:{prefix}:{hash_id}"
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        if not self.is_connected or not self.redis_client:
            return default
        
        try:
            cached_value = await asyncio.to_thread(self.redis_client.get, key)
            if cached_value:
                return json.loads(cached_value)
            return default
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        if not self.is_connected or not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            await asyncio.to_thread(
                self.redis_client.setex, 
                key, 
                ttl, 
                serialized_value
            )
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_connected or not self.redis_client:
            return False
        
        try:
            await asyncio.to_thread(self.redis_client.delete, key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.is_connected or not self.redis_client:
            return 0
        
        try:
            keys = await asyncio.to_thread(self.redis_client.keys, pattern)
            if keys:
                deleted = await asyncio.to_thread(self.redis_client.delete, *keys)
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis CLEAR error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        if not self.is_connected or not self.redis_client:
            return {
                "connected": False,
                "error": "Redis not connected"
            }
        
        try:
            info = await asyncio.to_thread(self.redis_client.info)
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.error(f"Redis STATS error: {e}")
            return {
                "connected": False,
                "error": str(e)
            }

# Global Redis manager
redis_manager = RedisManager()

class CacheService:
    """High-level caching service"""
    
    def __init__(self):
        self.memory_cache = {}  # Fallback memory cache
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    async def initialize(self):
        """Initialize caching service"""
        await redis_manager.initialize()
        return redis_manager.is_connected
    
    async def cache_api_response(self, endpoint: str, params: Dict, response: Any, ttl: int = 300):
        """Cache API response"""
        try:
            # Create cache key from endpoint and parameters
            cache_key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
            cache_key = redis_manager._generate_key("api", cache_key_data)
            
            # Cache the response
            success = await redis_manager.set(cache_key, {
                "response": response,
                "cached_at": datetime.utcnow().isoformat(),
                "endpoint": endpoint,
                "params": params
            }, ttl)
            
            if success:
                self.cache_stats["sets"] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Cache API response error: {e}")
            return False
    
    async def get_cached_api_response(self, endpoint: str, params: Dict) -> Optional[Any]:
        """Get cached API response"""
        try:
            # Create cache key from endpoint and parameters
            cache_key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
            cache_key = redis_manager._generate_key("api", cache_key_data)
            
            # Get cached response
            cached_data = await redis_manager.get(cache_key)
            
            if cached_data:
                self.cache_stats["hits"] += 1
                return cached_data.get("response")
            else:
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Get cached API response error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def cache_user_data(self, user_id: str, data: Dict, ttl: int = 1800):
        """Cache user-specific data"""
        try:
            cache_key = redis_manager._generate_key("user", user_id)
            
            success = await redis_manager.set(cache_key, {
                "data": data,
                "cached_at": datetime.utcnow().isoformat(),
                "user_id": user_id
            }, ttl)
            
            if success:
                self.cache_stats["sets"] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Cache user data error: {e}")
            return False
    
    async def get_cached_user_data(self, user_id: str) -> Optional[Dict]:
        """Get cached user data"""
        try:
            cache_key = redis_manager._generate_key("user", user_id)
            cached_data = await redis_manager.get(cache_key)
            
            if cached_data:
                self.cache_stats["hits"] += 1
                return cached_data.get("data")
            else:
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Get cached user data error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache for a user"""
        try:
            pattern = f"mewayz:user:*{user_id[:8]}*"
            deleted = await redis_manager.clear_pattern(pattern)
            
            if deleted > 0:
                self.cache_stats["deletes"] += deleted
            
            return deleted
            
        except Exception as e:
            logger.error(f"Invalidate user cache error: {e}")
            return 0
    
    async def cache_business_data(self, data_type: str, identifier: str, data: Any, ttl: int = 600):
        """Cache business data (financial, analytics, etc.)"""
        try:
            cache_key = redis_manager._generate_key(data_type, identifier)
            
            success = await redis_manager.set(cache_key, {
                "data": data,
                "cached_at": datetime.utcnow().isoformat(),
                "type": data_type,
                "identifier": identifier
            }, ttl)
            
            if success:
                self.cache_stats["sets"] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Cache business data error: {e}")
            return False
    
    async def get_cached_business_data(self, data_type: str, identifier: str) -> Optional[Any]:
        """Get cached business data"""
        try:
            cache_key = redis_manager._generate_key(data_type, identifier)
            cached_data = await redis_manager.get(cache_key)
            
            if cached_data:
                self.cache_stats["hits"] += 1
                return cached_data.get("data")
            else:
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Get cached business data error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        redis_stats = await redis_manager.get_stats()
        
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "redis": redis_stats,
            "service_stats": {
                **self.cache_stats,
                "total_requests": total_requests,
                "hit_rate_percentage": round(hit_rate, 2)
            },
            "status": "healthy" if redis_stats.get("connected") else "degraded"
        }

# Global cache service
cache_service = CacheService()

def cache_decorator(ttl: int = 300, key_prefix: str = "default"):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            func_name = func.__name__
            cache_key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache first
            cached_result = await cache_service.get_cached_business_data(key_prefix, cache_key_data)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.cache_business_data(key_prefix, cache_key_data, result, ttl)
            
            return result
        
        return wrapper
    return decorator

async def initialize_cache_system():
    """Initialize the caching system"""
    logger.info("🚀 Initializing caching system...")
    
    success = await cache_service.initialize()
    
    if success:
        logger.info("✅ Redis caching system initialized successfully")
    else:
        logger.info("⚠️ Fallback to memory caching (Redis unavailable)")
    
    return cache_service

if __name__ == "__main__":
    asyncio.run(initialize_cache_system())