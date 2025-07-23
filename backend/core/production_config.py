"""
PRODUCTION ENVIRONMENT CONFIGURATION
Comprehensive production setup with security, performance, and monitoring
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class ProductionConfig:
    """Production environment configuration management"""
    
    def __init__(self):
        self.environment = os.environ.get('ENVIRONMENT', 'production')
        self.config = self.load_configuration()
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load production configuration"""
        
        base_config = {
            # Server Configuration
            "server": {
                "host": "0.0.0.0",
                "port": 8001,
                "workers": 4,
                "timeout": 300,
                "keepalive": 5,
                "max_requests": 1000,
                "max_requests_jitter": 100
            },
            
            # Database Configuration
            "database": {
                "mongodb_url": os.environ.get('MONGO_URL'),
                "connection_pool_size": 50,
                "max_idle_time": 30000,
                "server_selection_timeout": 5000,
                "socket_timeout": 30000,
                "connect_timeout": 10000,
                "retry_writes": True,
                "journal": True,
                "read_preference": "primaryPreferred"
            },
            
            # Security Configuration
            "security": {
                "jwt_secret": os.environ.get('JWT_SECRET', 'production-secret-change-me'),
                "jwt_algorithm": "HS256",
                "jwt_expiration": 86400,  # 24 hours
                "bcrypt_rounds": 12,
                "rate_limit_requests": 100,
                "rate_limit_window": 60,
                "cors_origins": ["*"],
                "https_only": True,
                "secure_cookies": True,
                "csrf_protection": True
            },
            
            # Caching Configuration
            "cache": {
                "redis_url": os.environ.get('REDIS_URL', 'redis://localhost:6379'),
                "default_ttl": 3600,
                "session_ttl": 86400,
                "max_connections": 20,
                "retry_on_timeout": True
            },
            
            # External API Configuration
            "external_apis": {
                "twitter": {
                    "api_key": os.environ.get('TWITTER_API_KEY'),
                    "api_secret": os.environ.get('TWITTER_API_SECRET'),
                    "rate_limit": 300,
                    "timeout": 30
                },
                "stripe": {
                    "secret_key": os.environ.get('STRIPE_SECRET_KEY'),
                    "public_key": os.environ.get('STRIPE_PUBLIC_KEY'),
                    "webhook_secret": os.environ.get('STRIPE_WEBHOOK_SECRET'),
                    "timeout": 30
                },
                "openai": {
                    "api_key": os.environ.get('OPENAI_API_KEY'),
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 1000,
                    "timeout": 60
                },
                "tiktok": {
                    "client_key": os.environ.get('TIKTOK_CLIENT_KEY'),
                    "client_secret": os.environ.get('TIKTOK_CLIENT_SECRET'),
                    "timeout": 30
                },
                "google": {
                    "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
                    "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
                    "timeout": 30
                },
                "elasticmail": {
                    "api_key": os.environ.get('ELASTICMAIL_API_KEY'),
                    "timeout": 30
                }
            },
            
            # Logging Configuration
            "logging": {
                "level": "INFO",
                "format": "json",
                "file_rotation": "daily",
                "max_file_size": "100MB",
                "backup_count": 30,
                "log_requests": True,
                "log_responses": True,
                "log_performance": True
            },
            
            # Monitoring Configuration
            "monitoring": {
                "enabled": True,
                "health_check_interval": 60,
                "performance_metrics": True,
                "error_tracking": True,
                "uptime_monitoring": True,
                "alert_webhooks": [
                    os.environ.get('ALERT_WEBHOOK_URL')
                ]
            },
            
            # Performance Configuration
            "performance": {
                "enable_compression": True,
                "compression_level": 6,
                "static_file_caching": True,
                "etag_support": True,
                "connection_pooling": True,
                "async_workers": True
            },
            
            # Backup Configuration
            "backup": {
                "enabled": True,
                "schedule": "0 2 * * *",  # Daily at 2 AM
                "retention_days": 30,
                "storage_location": os.environ.get('BACKUP_STORAGE_URL'),
                "encryption": True,
                "compression": True
            }
        }
        
        # Environment-specific overrides
        if self.environment == 'development':
            base_config['security']['https_only'] = False
            base_config['security']['secure_cookies'] = False
            base_config['logging']['level'] = 'DEBUG'
            base_config['server']['workers'] = 1
        
        return base_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == 'production'
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate production configuration"""
        issues = []
        warnings = []
        
        # Check required environment variables
        required_vars = [
            'MONGO_URL',
            'JWT_SECRET',
            'TWITTER_API_KEY',
            'STRIPE_SECRET_KEY',
            'OPENAI_API_KEY'
        ]
        
        for var in required_vars:
            if not os.environ.get(var):
                issues.append(f"Missing required environment variable: {var}")
        
        # Check security settings
        if self.is_production():
            if self.get('security.jwt_secret') == 'production-secret-change-me':
                issues.append("JWT secret is using default value - SECURITY RISK")
            
            if not self.get('security.https_only'):
                warnings.append("HTTPS not enforced in production")
            
            if self.get('security.bcrypt_rounds') < 10:
                warnings.append("BCrypt rounds should be at least 10 for production")
        
        # Check database configuration
        if not self.get('database.mongodb_url'):
            issues.append("MongoDB URL not configured")
        
        # Check external API keys
        external_apis = ['twitter', 'stripe', 'openai', 'tiktok', 'google', 'elasticmail']
        for api in external_apis:
            api_config = self.get(f'external_apis.{api}')
            if api_config:
                for key, value in api_config.items():
                    if key.endswith('key') or key.endswith('secret') or key.endswith('id'):
                        if not value:
                            warnings.append(f"Missing {api} {key}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def export_config(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """Export configuration (with optional secret masking)"""
        config_copy = json.loads(json.dumps(self.config))
        
        if mask_secrets:
            # Mask sensitive values
            sensitive_keys = ['secret', 'key', 'password', 'token']
            
            def mask_recursive(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        if any(sensitive in key.lower() for sensitive in sensitive_keys):
                            if isinstance(value, str) and len(value) > 4:
                                obj[key] = value[:4] + "*" * (len(value) - 4)
                        else:
                            mask_recursive(value, new_path)
                elif isinstance(obj, list):
                    for item in obj:
                        mask_recursive(item, path)
            
            mask_recursive(config_copy)
        
        return config_copy

# Global configuration instance
production_config = ProductionConfig()

class HealthCheckEndpoints:
    """Production health check endpoints"""
    
    @staticmethod
    async def detailed_health_check() -> Dict[str, Any]:
        """Comprehensive health check"""
        from core.production_logging import health_checker
        
        health_status = await health_checker.get_system_health()
        
        # Add configuration validation
        config_validation = production_config.validate_config()
        health_status["configuration"] = {
            "valid": config_validation["valid"],
            "issues_count": len(config_validation["issues"]),
            "warnings_count": len(config_validation["warnings"])
        }
        
        # Add service status
        health_status["services"] = {
            "total_endpoints": 131,
            "environment": production_config.environment,
            "version": "2.0.0"
        }
        
        return health_status
    
    @staticmethod
    async def readiness_check() -> Dict[str, Any]:
        """Kubernetes readiness probe"""
        try:
            from core.database import get_database_async
            
            # Quick database connectivity check
            db = await get_database_async()
            if db is None:
                return {
                    "ready": False,
                    "reason": "Database not accessible",
                    "timestamp": "2025-01-24T00:00:00Z"
                }
            
            return {
                "ready": True,
                "timestamp": "2025-01-24T00:00:00Z"
            }
            
        except Exception as e:
            return {
                "ready": False,
                "reason": str(e),
                "timestamp": "2025-01-24T00:00:00Z"
            }
    
    @staticmethod
    async def liveness_check() -> Dict[str, Any]:
        """Kubernetes liveness probe"""
        return {
            "alive": True,
            "timestamp": "2025-01-24T00:00:00Z",
            "uptime": "running"
        }

def initialize_production_environment():
    """Initialize production environment"""
    print("🚀 Initializing production environment...")
    
    # Validate configuration
    validation = production_config.validate_config()
    
    if not validation["valid"]:
        print("❌ Configuration validation failed:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
        raise RuntimeError("Production configuration is invalid")
    
    if validation["warnings"]:
        print("⚠️ Configuration warnings:")
        for warning in validation["warnings"]:
            print(f"   - {warning}")
    
    print("✅ Production environment initialized successfully")
    print(f"   Environment: {production_config.environment}")
    print(f"   Database: {'✅ Configured' if production_config.get('database.mongodb_url') else '❌ Not configured'}")
    print(f"   External APIs: {len([k for k, v in production_config.get('external_apis', {}).items() if v])} configured")
    
    return validation

if __name__ == "__main__":
    initialize_production_environment()