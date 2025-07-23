"""
COMPREHENSIVE PRODUCTION ENVIRONMENT CONFIGURATION SYSTEM
Advanced environment management for development, staging, and production
"""

import os
import json
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    name: str
    max_connections: int = 100
    min_connections: int = 10
    connection_timeout: int = 30
    enable_ssl: bool = False
    replica_set: Optional[str] = None
    read_preference: str = "primary"
    write_concern: int = 1

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_hash_rounds: int = 12
    enable_mfa: bool = False
    session_timeout_minutes: int = 30
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 100

@dataclass
class ExternalApiConfig:
    """External API configuration"""
    openai_api_key: Optional[str] = None
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    tiktok_app_id: Optional[str] = None
    tiktok_app_secret: Optional[str] = None
    elastic_mail_api_key: Optional[str] = None
    google_oauth_client_id: Optional[str] = None
    google_oauth_client_secret: Optional[str] = None

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    log_level: str = "INFO"
    enable_structured_logging: bool = True
    enable_file_logging: bool = True
    log_retention_days: int = 30
    enable_metrics: bool = True
    enable_health_checks: bool = True
    health_check_interval: int = 60

@dataclass
class PerformanceConfig:
    """Performance optimization settings"""
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    max_request_size_mb: int = 50
    request_timeout_seconds: int = 30
    worker_processes: int = 4
    max_concurrent_requests: int = 1000
    enable_compression: bool = True

class ProductionConfigManager:
    """Comprehensive production configuration management"""
    
    def __init__(self, environment: Environment = None):
        self.environment = environment or self._detect_environment()
        self.config_path = Path("/app/config")
        self.config_path.mkdir(exist_ok=True)
        
        # Load configuration
        self.database = self._load_database_config()
        self.security = self._load_security_config()
        self.external_apis = self._load_external_api_config()
        self.monitoring = self._load_monitoring_config()
        self.performance = self._load_performance_config()
        
        # Initialize logging for this environment
        self._setup_environment_logging()
    
    def _detect_environment(self) -> Environment:
        """Auto-detect current environment"""
        env_var = os.getenv("ENVIRONMENT", "development").lower()
        
        try:
            return Environment(env_var)
        except ValueError:
            print(f"⚠️ Unknown environment '{env_var}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration for current environment"""
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        
        if self.environment == Environment.PRODUCTION:
            return DatabaseConfig(
                url=mongo_url,
                name="mewayz_production",
                max_connections=200,
                min_connections=20,
                connection_timeout=60,
                enable_ssl=True,
                replica_set="rs0",
                read_preference="primaryPreferred",
                write_concern=1
            )
        elif self.environment == Environment.STAGING:
            return DatabaseConfig(
                url=mongo_url,
                name="mewayz_staging", 
                max_connections=100,
                min_connections=10,
                connection_timeout=30,
                enable_ssl=True,
                replica_set="rs0",
                read_preference="primaryPreferred"
            )
        else:  # Development/Testing
            return DatabaseConfig(
                url=mongo_url,
                name="mewayz_development",
                max_connections=50,
                min_connections=5,
                connection_timeout=15
            )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration for current environment"""
        jwt_secret = os.getenv("JWT_SECRET_KEY", "development-secret-key")
        
        if self.environment == Environment.PRODUCTION:
            return SecurityConfig(
                jwt_secret_key=jwt_secret,
                jwt_expiration_hours=12,
                password_hash_rounds=14,
                enable_mfa=True,
                session_timeout_minutes=15,
                max_login_attempts=3,
                lockout_duration_minutes=30,
                rate_limit_per_minute=60
            )
        elif self.environment == Environment.STAGING:
            return SecurityConfig(
                jwt_secret_key=jwt_secret,
                jwt_expiration_hours=24,
                password_hash_rounds=12,
                enable_mfa=False,
                session_timeout_minutes=30,
                max_login_attempts=5,
                rate_limit_per_minute=100
            )
        else:
            return SecurityConfig(
                jwt_secret_key=jwt_secret,
                jwt_expiration_hours=48,
                password_hash_rounds=10,
                enable_mfa=False,
                session_timeout_minutes=60,
                max_login_attempts=10,
                rate_limit_per_minute=200
            )
    
    def _load_external_api_config(self) -> ExternalApiConfig:
        """Load external API configuration"""
        return ExternalApiConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            stripe_api_key=os.getenv("STRIPE_API_KEY"),
            stripe_webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
            twitter_api_key=os.getenv("TWITTER_API_KEY"),
            twitter_api_secret=os.getenv("TWITTER_API_SECRET"),
            tiktok_app_id=os.getenv("TIKTOK_APP_ID"),
            tiktok_app_secret=os.getenv("TIKTOK_APP_SECRET"),
            elastic_mail_api_key=os.getenv("ELASTIC_MAIL_API_KEY"),
            google_oauth_client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
            google_oauth_client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        )
    
    def _load_monitoring_config(self) -> MonitoringConfig:
        """Load monitoring configuration for current environment"""
        if self.environment == Environment.PRODUCTION:
            return MonitoringConfig(
                log_level="WARNING",
                enable_structured_logging=True,
                enable_file_logging=True,
                log_retention_days=90,
                enable_metrics=True,
                enable_health_checks=True,
                health_check_interval=30
            )
        elif self.environment == Environment.STAGING:
            return MonitoringConfig(
                log_level="INFO",
                enable_structured_logging=True,
                enable_file_logging=True,
                log_retention_days=30,
                enable_metrics=True,
                enable_health_checks=True,
                health_check_interval=60
            )
        else:
            return MonitoringConfig(
                log_level="DEBUG",
                enable_structured_logging=False,
                enable_file_logging=False,
                log_retention_days=7,
                enable_metrics=False,
                enable_health_checks=True,
                health_check_interval=120
            )
    
    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance configuration for current environment"""
        if self.environment == Environment.PRODUCTION:
            return PerformanceConfig(
                enable_caching=True,
                cache_ttl_seconds=600,
                max_request_size_mb=100,
                request_timeout_seconds=60,
                worker_processes=8,
                max_concurrent_requests=2000,
                enable_compression=True
            )
        elif self.environment == Environment.STAGING:
            return PerformanceConfig(
                enable_caching=True,
                cache_ttl_seconds=300,
                max_request_size_mb=50,
                request_timeout_seconds=30,
                worker_processes=4,
                max_concurrent_requests=1000,
                enable_compression=True
            )
        else:
            return PerformanceConfig(
                enable_caching=False,
                cache_ttl_seconds=60,
                max_request_size_mb=25,
                request_timeout_seconds=15,
                worker_processes=2,
                max_concurrent_requests=100,
                enable_compression=False
            )
    
    def _setup_environment_logging(self):
        """Configure logging for current environment"""
        log_level = getattr(logging, self.monitoring.log_level.upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if not self.monitoring.enable_structured_logging 
                   else '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"🔧 Production configuration loaded for {self.environment.value} environment")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get comprehensive configuration summary"""
        return {
            "environment": self.environment.value,
            "database": {
                "name": self.database.name,
                "max_connections": self.database.max_connections,
                "enable_ssl": self.database.enable_ssl,
                "replica_set": self.database.replica_set
            },
            "security": {
                "jwt_expiration_hours": self.security.jwt_expiration_hours,
                "enable_mfa": self.security.enable_mfa,
                "enable_rate_limiting": self.security.enable_rate_limiting,
                "rate_limit_per_minute": self.security.rate_limit_per_minute
            },
            "external_apis": {
                "openai_configured": bool(self.external_apis.openai_api_key),
                "stripe_configured": bool(self.external_apis.stripe_api_key),
                "twitter_configured": bool(self.external_apis.twitter_api_key),
                "tiktok_configured": bool(self.external_apis.tiktok_app_id),
                "google_oauth_configured": bool(self.external_apis.google_oauth_client_id)
            },
            "monitoring": {
                "log_level": self.monitoring.log_level,
                "enable_metrics": self.monitoring.enable_metrics,
                "enable_health_checks": self.monitoring.enable_health_checks
            },
            "performance": {
                "enable_caching": self.performance.enable_caching,
                "worker_processes": self.performance.worker_processes,
                "max_concurrent_requests": self.performance.max_concurrent_requests
            }
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and identify issues"""
        issues = []
        warnings = []
        
        # Database validation
        if not self.database.url or self.database.url == "mongodb://localhost:27017":
            if self.environment == Environment.PRODUCTION:
                issues.append("Production database URL not configured")
            else:
                warnings.append("Using default database URL")
        
        # Security validation
        if self.security.jwt_secret_key == "development-secret-key":
            if self.environment == Environment.PRODUCTION:
                issues.append("Production JWT secret key not configured")
            else:
                warnings.append("Using default JWT secret key")
        
        if self.environment == Environment.PRODUCTION and not self.security.enable_mfa:
            warnings.append("MFA not enabled for production environment")
        
        # External API validation
        api_configs = asdict(self.external_apis)
        missing_apis = [key for key, value in api_configs.items() if not value and "key" in key.lower()]
        
        if missing_apis:
            if self.environment == Environment.PRODUCTION:
                warnings.append(f"Missing external API configurations: {', '.join(missing_apis)}")
        
        # Performance validation
        if self.environment == Environment.PRODUCTION:
            if self.performance.worker_processes < 4:
                warnings.append("Low worker process count for production")
            
            if not self.performance.enable_caching:
                warnings.append("Caching disabled in production")
        
        return {
            "environment": self.environment.value,
            "status": "valid" if not issues else "invalid",
            "issues": issues,
            "warnings": warnings,
            "summary": {
                "total_issues": len(issues),
                "total_warnings": len(warnings),
                "configuration_score": max(0, 100 - (len(issues) * 20) - (len(warnings) * 5))
            }
        }

class ProductionConfig:
    """Legacy compatibility class - DEPRECATED"""
    
    def __init__(self):
        self.environment = os.environ.get('ENVIRONMENT', 'production')
        self.config = self.load_configuration()
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load production configuration - DEPRECATED"""
        
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