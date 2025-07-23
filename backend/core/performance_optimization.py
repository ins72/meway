"""
PERFORMANCE OPTIMIZATION SYSTEM
Advanced caching, database optimization, and performance monitoring
"""

import asyncio
import time
import hashlib
import json
import redis
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
from contextlib import asynccontextmanager
import logging
from core.production_logging import performance_monitor, production_logger

@dataclass
class CacheConfig:
    """Cache configuration settings"""
    redis_url: str
    default_ttl: int = 300  # 5 minutes
    max_connections: int = 20
    retry_attempts: int = 3
    timeout: int = 5
    enable_compression: bool = True
    key_prefix: str = "mewayz"

class RedisCache:
    """Advanced Redis caching system"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client = None
        self._connection_pool = None
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio as redis_async
            
            self._connection_pool = redis_async.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.max_connections,
                retry_on_timeout=True,
                socket_timeout=self.config.timeout
            )
            
            self.redis_client = redis_async.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self.redis_client.ping()
            
            production_logger.log_business_event(
                "cache_initialized",
                metadata={"redis_url": self.config.redis_url}
            )
            
            print("✅ Redis cache initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Redis cache initialization failed: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, key: str, namespace: str = "default") -> str:
        """Generate standardized cache key"""
        return f"{self.config.key_prefix}:{namespace}:{key}"
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            start_time = time.time()
            cache_key = self._generate_cache_key(key, namespace)
            
            raw_value = await self.redis_client.get(cache_key)
            
            if raw_value:
                response_time = time.time() - start_time
                performance_monitor.record_metric(
                    "cache_hit_time", 
                    response_time * 1000,
                    {"namespace": namespace, "type": "hit"}
                )
                
                # Decompress and deserialize if needed
                if self.config.enable_compression:
                    import gzip
                    raw_value = gzip.decompress(raw_value)
                
                value = json.loads(raw_value.decode('utf-8'))
                
                production_logger.log_business_event(
                    "cache_hit",
                    metadata={"key": key, "namespace": namespace}
                )
                
                return value
            else:
                performance_monitor.record_metric(
                    "cache_miss", 
                    1,
                    {"namespace": namespace}
                )
                return None
                
        except Exception as e:
            production_logger.log_business_event(
                "cache_error",
                metadata={"error": str(e), "operation": "get"}
            )
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None, namespace: str = "default") -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
        
        try:
            start_time = time.time()
            cache_key = self._generate_cache_key(key, namespace)
            ttl = ttl or self.config.default_ttl
            
            # Serialize value
            serialized_value = json.dumps(value, default=str).encode('utf-8')
            
            # Compress if enabled
            if self.config.enable_compression:
                import gzip
                serialized_value = gzip.compress(serialized_value)
            
            await self.redis_client.setex(cache_key, ttl, serialized_value)
            
            response_time = time.time() - start_time
            performance_monitor.record_metric(
                "cache_set_time",
                response_time * 1000,
                {"namespace": namespace}
            )
            
            production_logger.log_business_event(
                "cache_set",
                metadata={"key": key, "namespace": namespace, "ttl": ttl}
            )
            
            return True
            
        except Exception as e:
            production_logger.log_business_event(
                "cache_error",
                metadata={"error": str(e), "operation": "set"}
            )
            return False
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(key, namespace)
            result = await self.redis_client.delete(cache_key)
            
            production_logger.log_business_event(
                "cache_delete",
                metadata={"key": key, "namespace": namespace}
            )
            
            return result > 0
            
        except Exception as e:
            production_logger.log_business_event(
                "cache_error",
                metadata={"error": str(e), "operation": "delete"}
            )
            return False
    
    async def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace"""
        if not self.redis_client:
            return 0
        
        try:
            pattern = self._generate_cache_key("*", namespace)
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                deleted_count = await self.redis_client.delete(*keys)
                
                production_logger.log_business_event(
                    "cache_namespace_cleared",
                    metadata={"namespace": namespace, "deleted_count": deleted_count}
                )
                
                return deleted_count
            
            return 0
            
        except Exception as e:
            production_logger.log_business_event(
                "cache_error",
                metadata={"error": str(e), "operation": "clear_namespace"}
            )
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        try:
            info = await self.redis_client.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100

class DatabaseOptimizer:
    """Database performance optimization"""
    
    def __init__(self, database):
        self.database = database
        self.query_cache = {}
        self.performance_stats = {}
    
    async def create_indexes(self):
        """Create performance indexes"""
        try:
            indexes_to_create = [
                # User collection indexes
                ("users", [("email", 1)], {"unique": True}),
                ("users", [("username", 1)], {"unique": True}),
                ("users", [("created_at", -1)]),
                
                # Workspace collection indexes
                ("workspaces", [("owner_id", 1)]),
                ("workspaces", [("created_at", -1)]),
                ("workspaces", [("name", "text")]),
                
                # Financial collection indexes
                ("financial_records", [("user_id", 1), ("created_at", -1)]),
                ("financial_records", [("type", 1), ("status", 1)]),
                
                # Analytics collection indexes
                ("analytics", [("user_id", 1), ("date", -1)]),
                ("analytics", [("event_type", 1), ("timestamp", -1)]),
                
                # Session collection indexes
                ("sessions", [("session_id", 1)], {"unique": True}),
                ("sessions", [("user_id", 1)]),
                ("sessions", [("expires_at", 1)]),
                
                # Template collection indexes
                ("templates", [("category", 1), ("featured", -1)]),
                ("templates", [("creator_id", 1)]),
                ("templates", [("created_at", -1)]),
            ]
            
            created_count = 0
            for collection_name, keys, options in indexes_to_create:
                try:
                    collection = self.database[collection_name]
                    await collection.create_index(keys, **options)
                    created_count += 1
                except Exception as e:
                    print(f"⚠️ Failed to create index on {collection_name}: {e}")
            
            production_logger.log_business_event(
                "database_indexes_created",
                metadata={"created_count": created_count, "total_requested": len(indexes_to_create)}
            )
            
            print(f"✅ Created {created_count}/{len(indexes_to_create)} database indexes")
            
        except Exception as e:
            print(f"❌ Database index creation failed: {e}")
    
    async def analyze_query_performance(self, collection_name: str, query: Dict) -> Dict[str, Any]:
        """Analyze query performance"""
        try:
            collection = self.database[collection_name]
            
            # Execute explain plan
            start_time = time.time()
            explain_result = await collection.find(query).explain()
            execution_time = time.time() - start_time
            
            performance_info = {
                "collection": collection_name,
                "query": query,
                "execution_time_ms": round(execution_time * 1000, 2),
                "documents_examined": explain_result.get("executionStats", {}).get("totalDocsExamined", 0),
                "documents_returned": explain_result.get("executionStats", {}).get("totalDocsReturned", 0),
                "index_used": explain_result.get("executionStats", {}).get("executionSuccess", False),
                "stage": explain_result.get("executionStats", {}).get("executionStages", {}).get("stage", "unknown")
            }
            
            # Log slow queries
            if execution_time > 0.1:  # Log queries slower than 100ms
                production_logger.log_business_event(
                    "slow_query_detected",
                    metadata=performance_info
                )
            
            return performance_info
            
        except Exception as e:
            return {"error": str(e)}
    
    @asynccontextmanager
    async def optimized_connection(self):
        """Context manager for optimized database connections"""
        start_time = time.time()
        
        try:
            # Connection optimization could go here
            # For now, just yield the database
            yield self.database
            
        finally:
            connection_time = time.time() - start_time
            performance_monitor.record_metric(
                "database_connection_time",
                connection_time * 1000
            )

class PerformanceCache:
    """Decorator-based caching system"""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
    
    def cached(self, ttl: int = 300, namespace: str = "api", key_func: Callable = None):
        """Caching decorator for functions"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_function_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = await self.cache.get(cache_key, namespace)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Cache the result
                await self.cache.set(cache_key, result, ttl, namespace)
                
                # Record performance metrics
                performance_monitor.record_metric(
                    f"function_execution_time",
                    execution_time * 1000,
                    {"function": func.__name__, "cached": False}
                )
                
                return result
            
            return wrapper
        return decorator
    
    def _generate_function_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key for function call"""
        # Create a stable hash of the arguments
        key_data = {
            "function": func_name,
            "args": args,
            "kwargs": kwargs
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

class PerformanceMonitor:
    """Advanced performance monitoring"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = []
    
    async def monitor_system_resources(self) -> Dict[str, Any]:
        """Monitor system resource usage"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "percent": memory_percent,
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2)
                },
                "disk": {
                    "percent": disk_percent,
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
            
            # Check for performance alerts
            self._check_performance_alerts(metrics)
            
            # Record metrics
            performance_monitor.record_metric("cpu_usage", cpu_percent)
            performance_monitor.record_metric("memory_usage", memory_percent)
            performance_monitor.record_metric("disk_usage", disk_percent)
            
            return metrics
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_performance_alerts(self, metrics: Dict[str, Any]):
        """Check for performance issues and create alerts"""
        alerts = []
        
        # CPU alert
        if metrics["cpu"]["percent"] > 90:
            alerts.append({
                "type": "high_cpu_usage",
                "severity": "critical",
                "message": f"CPU usage is {metrics['cpu']['percent']}%",
                "timestamp": metrics["timestamp"]
            })
        
        # Memory alert
        if metrics["memory"]["percent"] > 85:
            alerts.append({
                "type": "high_memory_usage",
                "severity": "warning",
                "message": f"Memory usage is {metrics['memory']['percent']}%",
                "timestamp": metrics["timestamp"]
            })
        
        # Disk alert
        if metrics["disk"]["percent"] > 80:
            alerts.append({
                "type": "high_disk_usage",
                "severity": "warning",
                "message": f"Disk usage is {metrics['disk']['percent']}%",
                "timestamp": metrics["timestamp"]
            })
        
        # Log alerts
        for alert in alerts:
            production_logger.log_business_event(
                "performance_alert",
                metadata=alert
            )
        
        self.alerts.extend(alerts)
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        system_metrics = await self.monitor_system_resources()
        cache_stats = {}
        
        # Get cache stats if available
        if hasattr(self, 'cache') and self.cache:
            cache_stats = await self.cache.get_stats()
        
        # Get recent alerts
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > datetime.utcnow() - timedelta(hours=1)
        ]
        
        return {
            "system": system_metrics,
            "cache": cache_stats,
            "alerts": {
                "recent_count": len(recent_alerts),
                "total_count": len(self.alerts),
                "alerts": recent_alerts[-10:]  # Last 10 alerts
            },
            "performance_score": self._calculate_performance_score(system_metrics)
        }
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate overall performance score (0-100)"""
        if "error" in metrics:
            return 0
        
        score = 100
        
        # Deduct points for high resource usage
        score -= max(0, metrics["cpu"]["percent"] - 70)
        score -= max(0, metrics["memory"]["percent"] - 70)
        score -= max(0, metrics["disk"]["percent"] - 70)
        
        return max(0, int(score))

class PerformanceOptimizer:
    """Main performance optimization orchestrator"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.cache_config = CacheConfig(redis_url=redis_url)
        self.cache = RedisCache(self.cache_config)
        self.performance_cache = PerformanceCache(self.cache)
        self.performance_monitor = PerformanceMonitor()
        self.database_optimizer = None
    
    async def initialize(self, database=None):
        """Initialize all performance systems"""
        print("🚀 Initializing Performance Optimization System...")
        
        # Initialize cache
        await self.cache.initialize()
        
        # Initialize database optimizer
        if database:
            self.database_optimizer = DatabaseOptimizer(database)
            await self.database_optimizer.create_indexes()
        
        # Set up performance monitoring
        self.performance_monitor.cache = self.cache
        
        print("✅ Performance Optimization System initialized")
        
        return self
    
    def cached(self, ttl: int = 300, namespace: str = "api", key_func: Callable = None):
        """Caching decorator"""
        return self.performance_cache.cached(ttl, namespace, key_func)
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard"""
        return await self.performance_monitor.get_performance_summary()
    
    async def optimize_query(self, collection_name: str, query: Dict) -> Dict[str, Any]:
        """Analyze and optimize query performance"""
        if self.database_optimizer:
            return await self.database_optimizer.analyze_query_performance(collection_name, query)
        return {"error": "Database optimizer not initialized"}

# Global performance optimizer instance
performance_optimizer = None

async def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance"""
    global performance_optimizer
    
    if not performance_optimizer:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        performance_optimizer = PerformanceOptimizer(redis_url)
        
        # Try to initialize with database
        try:
            from core.database import get_database_async
            database = await get_database_async()
            await performance_optimizer.initialize(database)
        except Exception as e:
            print(f"⚠️ Performance optimizer initialized without database: {e}")
            await performance_optimizer.initialize()
    
    return performance_optimizer

async def initialize_performance_optimization():
    """Initialize performance optimization system"""
    global performance_optimizer
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    performance_optimizer = PerformanceOptimizer(redis_url)
    
    try:
        from core.database import get_database_async
        database = await get_database_async()
        await performance_optimizer.initialize(database)
    except Exception as e:
        print(f"⚠️ Performance optimizer initialized without database: {e}")
        await performance_optimizer.initialize()
    
    return performance_optimizer

if __name__ == "__main__":
    import os
    asyncio.run(initialize_performance_optimization())