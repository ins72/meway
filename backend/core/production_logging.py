"""
COMPREHENSIVE ERROR LOGGING SYSTEM
Advanced logging, monitoring, and error tracking for production
"""

import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import asyncio
import time

class ProductionLogger:
    """Enhanced production logging system"""
    
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Configure comprehensive logging"""
        # Create formatters
        json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s", "filename": "%(filename)s", "line": %(lineno)d}'
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Console handler with JSON format
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(json_formatter)
        root_logger.addHandler(console_handler)
        
        # File handlers for different log levels
        error_handler = logging.FileHandler('/var/log/mewayz_errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        root_logger.addHandler(error_handler)
        
        performance_handler = logging.FileHandler('/var/log/mewayz_performance.log')
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(json_formatter)
        root_logger.addHandler(performance_handler)
    
    def log_api_request(self, endpoint: str, method: str, user_id: str = None, request_data: Dict = None):
        """Log API requests with detailed information"""
        log_data = {
            "type": "api_request",
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "request_size": len(str(request_data)) if request_data else 0
        }
        logging.info(f"API_REQUEST: {json.dumps(log_data)}")
    
    def log_api_response(self, endpoint: str, status_code: int, response_time: float, error: str = None):
        """Log API responses with performance metrics"""
        log_data = {
            "type": "api_response", 
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "error": error
        }
        
        if status_code >= 500:
            logging.error(f"API_ERROR: {json.dumps(log_data)}")
        elif status_code >= 400:
            logging.warning(f"API_WARNING: {json.dumps(log_data)}")
        else:
            logging.info(f"API_SUCCESS: {json.dumps(log_data)}")
    
    def log_database_operation(self, operation: str, collection: str, query: Dict = None, execution_time: float = None):
        """Log database operations"""
        log_data = {
            "type": "database_operation",
            "operation": operation,
            "collection": collection,
            "execution_time_ms": round(execution_time * 1000, 2) if execution_time else None,
            "timestamp": datetime.utcnow().isoformat(),
            "query_hash": hash(str(query)) if query else None
        }
        logging.info(f"DB_OPERATION: {json.dumps(log_data)}")
    
    def log_external_api_call(self, service: str, endpoint: str, response_time: float, status_code: int = None):
        """Log external API calls"""
        log_data = {
            "type": "external_api_call",
            "service": service,
            "endpoint": endpoint,
            "response_time_ms": round(response_time * 1000, 2),
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        logging.info(f"EXTERNAL_API: {json.dumps(log_data)}")
    
    def log_business_event(self, event_type: str, user_id: str = None, metadata: Dict = None):
        """Log business events for analytics"""
        log_data = {
            "type": "business_event",
            "event_type": event_type,
            "user_id": user_id,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
        logging.info(f"BUSINESS_EVENT: {json.dumps(log_data)}")
    
    def log_security_event(self, event_type: str, user_id: str = None, ip_address: str = None, severity: str = "info"):
        """Log security events"""
        log_data = {
            "type": "security_event",
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if severity == "critical":
            logging.error(f"SECURITY_CRITICAL: {json.dumps(log_data)}")
        elif severity == "high":
            logging.warning(f"SECURITY_WARNING: {json.dumps(log_data)}")
        else:
            logging.info(f"SECURITY_INFO: {json.dumps(log_data)}")

# Global logger instance
production_logger = ProductionLogger()

def log_api_calls(func):
    """Decorator to automatically log API calls"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        endpoint = getattr(func, '__name__', 'unknown')
        
        try:
            # Log request
            production_logger.log_api_request(endpoint, "API_CALL")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Log successful response
            response_time = time.time() - start_time
            production_logger.log_api_response(endpoint, 200, response_time)
            
            return result
            
        except Exception as e:
            # Log error response
            response_time = time.time() - start_time
            production_logger.log_api_response(endpoint, 500, response_time, str(e))
            
            # Log detailed error information
            error_data = {
                "type": "exception",
                "function": endpoint,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.utcnow().isoformat()
            }
            logging.error(f"EXCEPTION: {json.dumps(error_data)}")
            
            raise
    
    return wrapper

def log_database_calls(func):
    """Decorator to automatically log database calls"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        operation = getattr(func, '__name__', 'unknown')
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Extract collection name from self if available
            collection = getattr(args[0], 'collection_name', 'unknown') if args else 'unknown'
            
            production_logger.log_database_operation(operation, collection, execution_time=execution_time)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            collection = getattr(args[0], 'collection_name', 'unknown') if args else 'unknown'
            
            production_logger.log_database_operation(operation, collection, execution_time=execution_time)
            
            error_data = {
                "type": "database_error", 
                "operation": operation,
                "collection": collection,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            logging.error(f"DB_ERROR: {json.dumps(error_data)}")
            
            raise
    
    return wrapper

class PerformanceMonitor:
    """Monitor system performance metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric"""
        timestamp = datetime.utcnow().isoformat()
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": timestamp,
            "tags": tags or {}
        })
        
        # Log metric
        metric_data = {
            "type": "performance_metric",
            "metric": metric_name,
            "value": value,
            "tags": tags,
            "timestamp": timestamp
        }
        logging.info(f"METRIC: {json.dumps(metric_data)}")
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of recorded metrics"""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                metric_values = [v["value"] for v in values]
                summary[metric_name] = {
                    "count": len(metric_values),
                    "avg": sum(metric_values) / len(metric_values),
                    "min": min(metric_values),
                    "max": max(metric_values),
                    "latest": values[-1]["value"],
                    "latest_timestamp": values[-1]["timestamp"]
                }
        
        return summary

# Global performance monitor
performance_monitor = PerformanceMonitor()

class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.health_checks = {}
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            from core.database import get_database_async
            
            start_time = time.time()
            db = await get_database_async()
            
            if db is not None:
                # Test basic operation
                await db.command("ping")
                response_time = time.time() - start_time
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time * 1000, 2),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Database connection unavailable",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_external_api_health(self, service_name: str, health_url: str) -> Dict[str, Any]:
        """Check external API health"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(health_url, timeout=5) as response:
                    response_time = time.time() - start_time
                    
                    return {
                        "service": service_name,
                        "status": "healthy" if response.status == 200 else "degraded",
                        "status_code": response.status,
                        "response_time_ms": round(response_time * 1000, 2),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            return {
                "service": service_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy"
        }
        
        # Check database
        db_health = await self.check_database_health()
        health_status["database"] = db_health
        
        if db_health["status"] != "healthy":
            health_status["overall_status"] = "degraded"
        
        # Check external APIs (if configured)
        external_apis = [
            ("stripe", "https://status.stripe.com"),
            ("twitter", "https://api.twitterstat.us/api/status")
        ]
        
        health_status["external_apis"] = {}
        for service, url in external_apis:
            try:
                api_health = await self.check_external_api_health(service, url)
                health_status["external_apis"][service] = api_health
                
                if api_health["status"] != "healthy":
                    health_status["overall_status"] = "degraded"
            except:
                health_status["external_apis"][service] = {
                    "status": "unknown",
                    "error": "Health check failed"
                }
        
        # Log health status
        production_logger.log_business_event("system_health_check", metadata=health_status)
        
        return health_status

# Global health checker
health_checker = HealthChecker()

def initialize_production_logging():
    """Initialize all production logging systems"""
    print("🔧 Initializing production logging systems...")
    
    # Test logging
    production_logger.log_business_event("system_startup", metadata={"component": "logging_system"})
    
    # Test performance monitoring
    performance_monitor.record_metric("system_startup_time", 1.0, {"component": "initialization"})
    
    print("✅ Production logging systems initialized")

if __name__ == "__main__":
    initialize_production_logging()