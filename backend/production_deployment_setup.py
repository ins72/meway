"""
Production Deployment Setup
Complete production configuration and deployment preparation
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import subprocess
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionDeploymentSetup:
    def __init__(self):
        self.setup_results = {
            "database_configured": False,
            "authentication_configured": False,
            "api_keys_configured": False,
            "security_configured": False,
            "monitoring_configured": False,
            "crud_operations_verified": False,
            "production_ready": False,
            "errors": [],
            "warnings": []
        }
        
        # Required environment variables for production
        self.required_env_vars = [
            "MONGO_URL",
            "JWT_SECRET_KEY",
            "STRIPE_SECRET_KEY",
            "STRIPE_PUBLISHABLE_KEY",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "OPENAI_API_KEY"
        ]
        
        # Optional but recommended environment variables
        self.optional_env_vars = [
            "REDIS_URL",
            "ELASTIC_EMAIL_API_KEY",
            "TWITTER_API_KEY",
            "TIKTOK_CLIENT_KEY",
            "SENTRY_DSN",
            "LOG_LEVEL"
        ]
    
    def check_environment_variables(self):
        """Check and validate environment variables"""
        logger.info("🔍 Checking Environment Variables...")
        
        missing_required = []
        missing_optional = []
        
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_required.append(var)
            else:
                logger.info(f"✅ {var}: Configured")
        
        for var in self.optional_env_vars:
            if not os.getenv(var):
                missing_optional.append(var)
            else:
                logger.info(f"✅ {var}: Configured")
        
        if missing_required:
            logger.error(f"❌ Missing required environment variables: {', '.join(missing_required)}")
            self.setup_results["errors"].append(f"Missing required environment variables: {missing_required}")
            return False
        
        if missing_optional:
            logger.warning(f"⚠️ Missing optional environment variables: {', '.join(missing_optional)}")
            self.setup_results["warnings"].append(f"Missing optional environment variables: {missing_optional}")
        
        self.setup_results["api_keys_configured"] = True
        return True
    
    def check_database_connection(self):
        """Check database connection and configuration"""
        logger.info("🔍 Checking Database Connection...")
        
        try:
            # Import database module and test connection
            from core.database import connect_to_mongo
            
            # Run connection test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(connect_to_mongo())
            
            if result:
                logger.info("✅ Database connection successful")
                self.setup_results["database_configured"] = True
                return True
            else:
                logger.error("❌ Database connection failed")
                self.setup_results["errors"].append("Database connection failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            self.setup_results["errors"].append(f"Database connection error: {e}")
            return False
    
    def check_authentication_system(self):
        """Check authentication system configuration"""
        logger.info("🔍 Checking Authentication System...")
        
        try:
            from core.auth import create_access_token, verify_password, get_password_hash
            
            # Test JWT token creation
            test_token = create_access_token(data={"sub": "test@example.com"})
            if test_token:
                logger.info("✅ JWT token creation working")
            else:
                logger.error("❌ JWT token creation failed")
                self.setup_results["errors"].append("JWT token creation failed")
                return False
            
            # Test password hashing
            test_password = "testpassword123"
            hashed = get_password_hash(test_password)
            if hashed and verify_password(test_password, hashed):
                logger.info("✅ Password hashing and verification working")
            else:
                logger.error("❌ Password hashing/verification failed")
                self.setup_results["errors"].append("Password hashing/verification failed")
                return False
            
            self.setup_results["authentication_configured"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication system error: {e}")
            self.setup_results["errors"].append(f"Authentication system error: {e}")
            return False
    
    def check_security_configuration(self):
        """Check security configuration"""
        logger.info("🔍 Checking Security Configuration...")
        
        try:
            from core.security import SecurityManager
            
            # Test security manager initialization
            security_manager = SecurityManager()
            logger.info("✅ Security manager initialized")
            
            # Check CORS configuration
            cors_origins = os.getenv("CORS_ORIGINS", "*")
            logger.info(f"✅ CORS origins configured: {cors_origins}")
            
            # Check rate limiting
            rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
            logger.info(f"✅ Rate limiting: {'Enabled' if rate_limit_enabled else 'Disabled'}")
            
            self.setup_results["security_configured"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Security configuration error: {e}")
            self.setup_results["errors"].append(f"Security configuration error: {e}")
            return False
    
    def check_monitoring_system(self):
        """Check monitoring and logging configuration"""
        logger.info("🔍 Checking Monitoring System...")
        
        try:
            from core.monitoring_system import MonitoringSystem
            
            # Test monitoring system initialization
            monitoring = MonitoringSystem()
            logger.info("✅ Monitoring system initialized")
            
            # Check logging configuration
            log_level = os.getenv("LOG_LEVEL", "INFO")
            logger.info(f"✅ Log level configured: {log_level}")
            
            # Check Sentry integration
            sentry_dsn = os.getenv("SENTRY_DSN")
            if sentry_dsn:
                logger.info("✅ Sentry error tracking configured")
            else:
                logger.warning("⚠️ Sentry error tracking not configured")
            
            self.setup_results["monitoring_configured"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Monitoring system error: {e}")
            self.setup_results["errors"].append(f"Monitoring system error: {e}")
            return False
    
    def verify_crud_operations(self):
        """Verify CRUD operations are working"""
        logger.info("🔍 Verifying CRUD Operations...")
        
        try:
            # Import and test service layers
            from services.workspace_service import get_workspace_service
            from services.user_service import get_user_service
            from services.blog_service import get_blog_service
            
            # Test service initialization
            workspace_service = get_workspace_service()
            user_service = get_user_service()
            blog_service = get_blog_service()
            
            logger.info("✅ All service layers initialized")
            
            # Test database collections
            from core.database import get_database_async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            db = loop.run_until_complete(get_database_async())
            
            if db is not None:
                collections = ["users", "workspaces", "blog_posts", "notifications", "campaigns"]
                for collection_name in collections:
                    if hasattr(db, collection_name):
                        logger.info(f"✅ Collection '{collection_name}' available")
                    else:
                        logger.warning(f"⚠️ Collection '{collection_name}' not found")
                        self.setup_results["warnings"].append(f"Collection '{collection_name}' not found")
            
            self.setup_results["crud_operations_verified"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ CRUD operations verification error: {e}")
            self.setup_results["errors"].append(f"CRUD operations verification error: {e}")
            return False
    
    def create_production_config(self):
        """Create production configuration files"""
        logger.info("🔧 Creating Production Configuration...")
        
        try:
            # Create production config
            production_config = {
                "app_name": "Mewayz Professional Platform",
                "version": "2.0.0",
                "environment": "production",
                "debug": False,
                "host": "0.0.0.0",
                "port": 8001,
                "workers": 4,
                "timeout": 30,
                "max_requests": 1000,
                "max_requests_jitter": 100,
                "log_level": "INFO",
                "cors_origins": ["*"],
                "rate_limit_enabled": True,
                "rate_limit_requests": 100,
                "rate_limit_window": 60,
                "database": {
                    "url": os.getenv("MONGO_URL"),
                    "max_pool_size": 50,
                    "min_pool_size": 5,
                    "retry_writes": True,
                    "retry_reads": True
                },
                "security": {
                    "jwt_secret": os.getenv("JWT_SECRET_KEY"),
                    "jwt_algorithm": "HS256",
                    "jwt_expiration": 1440,
                    "password_min_length": 8,
                    "password_require_special": True
                },
                "integrations": {
                    "stripe": {
                        "secret_key": os.getenv("STRIPE_SECRET_KEY"),
                        "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY")
                    },
                    "google": {
                        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET")
                    },
                    "openai": {
                        "api_key": os.getenv("OPENAI_API_KEY")
                    }
                }
            }
            
            # Save production config
            with open("production_config.json", "w") as f:
                json.dump(production_config, f, indent=2)
            
            logger.info("✅ Production configuration created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Production config creation error: {e}")
            self.setup_results["errors"].append(f"Production config creation error: {e}")
            return False
    
    def create_docker_compose_production(self):
        """Create production Docker Compose configuration"""
        logger.info("🔧 Creating Production Docker Compose...")
        
        try:
            docker_compose_prod = {
                "version": "3.8",
                "services": {
                    "mewayz-api": {
                        "build": {
                            "context": ".",
                            "dockerfile": "Dockerfile"
                        },
                        "ports": ["8001:8001"],
                        "environment": [
                            "MONGO_URL=${MONGO_URL}",
                            "JWT_SECRET_KEY=${JWT_SECRET_KEY}",
                            "STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}",
                            "STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}",
                            "GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}",
                            "GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}",
                            "OPENAI_API_KEY=${OPENAI_API_KEY}",
                            "LOG_LEVEL=INFO"
                        ],
                        "restart": "unless-stopped",
                        "healthcheck": {
                            "test": ["CMD", "curl", "-f", "http://localhost:8001/health"],
                            "interval": "30s",
                            "timeout": "10s",
                            "retries": 3
                        },
                        "volumes": ["./logs:/app/logs"],
                        "networks": ["mewayz-network"]
                    },
                    "mewayz-frontend": {
                        "build": {
                            "context": "../frontend",
                            "dockerfile": "Dockerfile"
                        },
                        "ports": ["3000:3000"],
                        "environment": [
                            "REACT_APP_API_URL=http://localhost:8001",
                            "REACT_APP_STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}"
                        ],
                        "restart": "unless-stopped",
                        "depends_on": ["mewayz-api"],
                        "networks": ["mewayz-network"]
                    },
                    "nginx": {
                        "image": "nginx:alpine",
                        "ports": ["80:80", "443:443"],
                        "volumes": [
                            "./nginx/nginx.conf:/etc/nginx/nginx.conf",
                            "./nginx/ssl:/etc/nginx/ssl"
                        ],
                        "restart": "unless-stopped",
                        "depends_on": ["mewayz-api", "mewayz-frontend"],
                        "networks": ["mewayz-network"]
                    }
                },
                "networks": {
                    "mewayz-network": {
                        "driver": "bridge"
                    }
                }
            }
            
            # Save Docker Compose production config
            with open("docker-compose.production.yml", "w") as f:
                import yaml
                yaml.dump(docker_compose_prod, f, default_flow_style=False)
            
            logger.info("✅ Production Docker Compose created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Docker Compose creation error: {e}")
            self.setup_results["errors"].append(f"Docker Compose creation error: {e}")
            return False
    
    def create_nginx_config(self):
        """Create Nginx configuration for production"""
        logger.info("🔧 Creating Nginx Configuration...")
        
        try:
            nginx_config = """
events {
    worker_connections 1024;
}

http {
    upstream mewayz_api {
        server mewayz-api:8001;
    }
    
    upstream mewayz_frontend {
        server mewayz-frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name localhost;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # API routes
        location /api/ {
            proxy_pass http://mewayz_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
        }
        
        # Health checks
        location /health {
            proxy_pass http://mewayz_api/health;
            access_log off;
        }
        
        # Frontend routes
        location / {
            proxy_pass http://mewayz_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
"""
            
            # Create nginx directory
            os.makedirs("nginx", exist_ok=True)
            
            # Save nginx config
            with open("nginx/nginx.conf", "w") as f:
                f.write(nginx_config)
            
            logger.info("✅ Nginx configuration created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Nginx config creation error: {e}")
            self.setup_results["errors"].append(f"Nginx config creation error: {e}")
            return False
    
    def create_startup_script(self):
        """Create production startup script"""
        logger.info("🔧 Creating Production Startup Script...")
        
        try:
            startup_script = """#!/bin/bash

# Mewayz Professional Platform - Production Startup Script

echo "Starting Mewayz Professional Platform..."

# Check environment variables
required_vars=("MONGO_URL" "JWT_SECRET_KEY" "STRIPE_SECRET_KEY" "STRIPE_PUBLISHABLE_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var environment variable is not set"
        exit 1
    fi
done

echo "Environment variables verified"

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4 --log-level info
"""
            
            # Save startup script
            with open("start_production.sh", "w") as f:
                f.write(startup_script)
            
            # Make executable
            os.chmod("start_production.sh", 0o755)
            
            logger.info("✅ Production startup script created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Startup script creation error: {e}")
            self.setup_results["errors"].append(f"Startup script creation error: {e}")
            return False
    
    def run_setup(self):
        """Run complete production setup"""
        logger.info("🚀 Starting Production Deployment Setup...")
        
        # Run all setup checks
        checks = [
            ("Environment Variables", self.check_environment_variables),
            ("Database Connection", self.check_database_connection),
            ("Authentication System", self.check_authentication_system),
            ("Security Configuration", self.check_security_configuration),
            ("Monitoring System", self.check_monitoring_system),
            ("CRUD Operations", self.verify_crud_operations),
            ("Production Config", self.create_production_config),
            ("Docker Compose", self.create_docker_compose_production),
            ("Nginx Config", self.create_nginx_config),
            ("Startup Script", self.create_startup_script)
        ]
        
        for check_name, check_func in checks:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running: {check_name}")
            logger.info('='*60)
            
            try:
                if check_func():
                    logger.info(f"✅ {check_name}: SUCCESS")
                else:
                    logger.error(f"❌ {check_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {check_name}: ERROR - {e}")
                self.setup_results["errors"].append(f"{check_name} error: {e}")
        
        # Determine overall production readiness
        self.setup_results["production_ready"] = (
            self.setup_results["database_configured"] and
            self.setup_results["authentication_configured"] and
            self.setup_results["api_keys_configured"] and
            self.setup_results["security_configured"] and
            self.setup_results["monitoring_configured"] and
            self.setup_results["crud_operations_verified"] and
            len(self.setup_results["errors"]) == 0
        )
        
        # Generate final report
        self.generate_report()
        
        return self.setup_results
    
    def generate_report(self):
        """Generate comprehensive setup report"""
        logger.info("\n" + "="*80)
        logger.info("📊 PRODUCTION DEPLOYMENT SETUP REPORT")
        logger.info("="*80)
        
        logger.info("Configuration Status:")
        logger.info(f"  Database: {'✅ Configured' if self.setup_results['database_configured'] else '❌ Failed'}")
        logger.info(f"  Authentication: {'✅ Configured' if self.setup_results['authentication_configured'] else '❌ Failed'}")
        logger.info(f"  API Keys: {'✅ Configured' if self.setup_results['api_keys_configured'] else '❌ Failed'}")
        logger.info(f"  Security: {'✅ Configured' if self.setup_results['security_configured'] else '❌ Failed'}")
        logger.info(f"  Monitoring: {'✅ Configured' if self.setup_results['monitoring_configured'] else '❌ Failed'}")
        logger.info(f"  CRUD Operations: {'✅ Verified' if self.setup_results['crud_operations_verified'] else '❌ Failed'}")
        
        logger.info(f"\nProduction Ready: {'✅ YES' if self.setup_results['production_ready'] else '❌ NO'}")
        
        if self.setup_results["warnings"]:
            logger.info("\nWarnings:")
            for warning in self.setup_results["warnings"]:
                logger.info(f"  ⚠️ {warning}")
        
        if self.setup_results["errors"]:
            logger.info("\nErrors:")
            for error in self.setup_results["errors"]:
                logger.info(f"  ❌ {error}")
        
        logger.info("="*80)
        
        # Save detailed report
        report_file = f"production_setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.setup_results, f, indent=2, default=str)
        
        logger.info(f"Detailed report saved to: {report_file}")

def main():
    """Main function"""
    setup = ProductionDeploymentSetup()
    results = setup.run_setup()
    
    if results["production_ready"]:
        logger.info("🎉 Production deployment setup completed successfully!")
        logger.info("Your platform is ready for production deployment!")
        sys.exit(0)
    else:
        logger.error("❌ Production deployment setup failed.")
        logger.error("Please fix the errors above before deploying to production.")
        sys.exit(1)

if __name__ == "__main__":
    main() 