"""
PRODUCTION MONITORING AND HEALTH ENDPOINTS
Comprehensive endpoints for testing production enhancements
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import asyncio
import os
from datetime import datetime

from core.auth import get_current_user, get_current_admin
from core.production_config import get_config, initialize_production_config
from core.production_logging import health_checker, production_logger, performance_monitor
from core.enterprise_security import create_security_suite

router = APIRouter(prefix="/production", tags=["production"])

@router.get("/health")
async def production_health_check():
    """Comprehensive production health check"""
    try:
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "version": "2.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "components": {}
        }
        
        # Test production configuration
        try:
            config_manager = get_config()
            config_summary = config_manager.get_config_summary()
            validation = config_manager.validate_configuration()
            
            health_status["components"]["configuration"] = {
                "status": "healthy",
                "environment": config_summary["environment"],
                "configuration_score": validation["summary"]["configuration_score"],
                "issues_count": validation["summary"]["total_issues"],
                "warnings_count": validation["summary"]["total_warnings"]
            }
        except Exception as e:
            health_status["components"]["configuration"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test enterprise security
        try:
            security_suite = create_security_suite()
            health_status["components"]["enterprise_security"] = {
                "status": "healthy",
                "mfa_required": security_suite.security_policy.require_mfa,
                "password_min_length": security_suite.security_policy.password_min_length,
                "max_login_attempts": security_suite.security_policy.max_login_attempts
            }
        except Exception as e:
            health_status["components"]["enterprise_security"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test performance monitoring
        try:
            metrics_summary = performance_monitor.get_metrics_summary()
            health_status["components"]["performance_monitoring"] = {
                "status": "healthy",
                "metrics_count": len(metrics_summary),
                "latest_metrics": list(metrics_summary.keys())[:5]
            }
        except Exception as e:
            health_status["components"]["performance_monitoring"] = {
                "status": "error", 
                "error": str(e)
            }
        
        # Test production logging
        try:
            production_logger.log_business_event(
                "production_health_check",
                metadata={"timestamp": health_status["timestamp"]}
            )
            
            health_status["components"]["production_logging"] = {
                "status": "healthy",
                "logging_active": True
            }
        except Exception as e:
            health_status["components"]["production_logging"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Check if any components failed
        failed_components = [
            name for name, component in health_status["components"].items()
            if component.get("status") != "healthy"
        ]
        
        if failed_components:
            health_status["status"] = "degraded"
            health_status["failed_components"] = failed_components
        
        return health_status
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/configuration")
async def get_production_configuration(current_user: dict = Depends(get_current_admin)):
    """Get production configuration details"""
    try:
        config_manager = get_config()
        
        return {
            "environment": config_manager.environment.value,
            "configuration_summary": config_manager.get_config_summary(),
            "validation": config_manager.validate_configuration(),
            "user": current_user.get("email", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

@router.get("/security")
async def get_security_status(current_user: dict = Depends(get_current_admin)):
    """Get enterprise security status"""
    try:
        security_suite = create_security_suite()
        
        # Test password validation
        test_passwords = ["weak", "StrongPassword123!", ""]
        password_tests = []
        
        for password in test_passwords:
            is_valid, errors = security_suite.validate_password_strength(password)
            password_tests.append({
                "password": password[:3] + "*" * max(0, len(password) - 3),
                "valid": is_valid,
                "error_count": len(errors)
            })
        
        return {
            "security_policy": {
                "password_min_length": security_suite.security_policy.password_min_length,
                "require_mfa": security_suite.security_policy.require_mfa,
                "max_login_attempts": security_suite.security_policy.max_login_attempts,
                "lockout_duration_minutes": security_suite.security_policy.lockout_duration_minutes,
                "session_timeout_minutes": security_suite.security_policy.session_timeout_minutes
            },
            "password_validation_tests": password_tests,
            "user": current_user.get("email", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security error: {str(e)}")

@router.get("/performance")
async def get_performance_status(current_user: dict = Depends(get_current_admin)):
    """Get performance monitoring status"""
    try:
        # Get performance metrics
        metrics_summary = performance_monitor.get_metrics_summary()
        
        # Test performance optimization
        try:
            from core.performance_optimization import get_performance_optimizer
            
            perf_optimizer = await get_performance_optimizer()
            perf_dashboard = await perf_optimizer.get_performance_dashboard()
            
            return {
                "metrics_summary": metrics_summary,
                "performance_dashboard": perf_dashboard,
                "status": "healthy",
                "user": current_user.get("email", "unknown")
            }
            
        except Exception as perf_error:
            return {
                "metrics_summary": metrics_summary,
                "performance_dashboard": {"error": str(perf_error)},
                "status": "degraded",
                "user": current_user.get("email", "unknown")
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance monitoring error: {str(e)}")

@router.get("/logging")
async def get_logging_status(current_user: dict = Depends(get_current_admin)):
    """Get production logging status"""
    try:
        # Test logging system
        production_logger.log_business_event(
            "logging_status_check",
            user_id=current_user.get("email"),
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
        
        production_logger.log_security_event(
            "admin_logging_access",
            user_id=current_user.get("email"),
            severity="info"
        )
        
        # Get recent metrics
        metrics_summary = performance_monitor.get_metrics_summary()
        
        return {
            "logging_system": {
                "status": "active",
                "business_events": "enabled",
                "security_events": "enabled",
                "performance_metrics": "enabled"
            },
            "recent_metrics": metrics_summary,
            "test_timestamp": datetime.utcnow().isoformat(),
            "user": current_user.get("email", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logging system error: {str(e)}")

@router.post("/initialize")
async def initialize_production_systems(current_user: dict = Depends(get_current_admin)):
    """Initialize all production systems"""
    try:
        initialization_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user.get("email", "unknown"),
            "results": {}
        }
        
        # Initialize production configuration
        try:
            config_manager = initialize_production_config()
            initialization_results["results"]["configuration"] = {
                "status": "success",
                "environment": config_manager.environment.value
            }
        except Exception as e:
            initialization_results["results"]["configuration"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Initialize enterprise security
        try:
            from core.enterprise_security import initialize_enterprise_security
            security_suite = initialize_enterprise_security()
            initialization_results["results"]["enterprise_security"] = {
                "status": "success",
                "mfa_required": security_suite.security_policy.require_mfa
            }
        except Exception as e:
            initialization_results["results"]["enterprise_security"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Initialize performance optimization
        try:
            from core.performance_optimization import initialize_performance_optimization
            perf_optimizer = await initialize_performance_optimization()
            initialization_results["results"]["performance_optimization"] = {
                "status": "success",
                "cache_enabled": True
            }
        except Exception as e:
            initialization_results["results"]["performance_optimization"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Initialize production logging
        try:
            from core.production_logging import initialize_production_logging
            initialize_production_logging()
            initialization_results["results"]["production_logging"] = {
                "status": "success",
                "logging_active": True
            }
        except Exception as e:
            initialization_results["results"]["production_logging"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Count successful initializations
        successful = sum(1 for result in initialization_results["results"].values() 
                        if result.get("status") == "success")
        total = len(initialization_results["results"])
        
        initialization_results["summary"] = {
            "successful_count": successful,
            "total_count": total,
            "success_rate": f"{(successful/total)*100:.1f}%" if total > 0 else "0%",
            "overall_status": "success" if successful == total else "partial"
        }
        
        production_logger.log_business_event(
            "production_systems_initialized",
            user_id=current_user.get("email"),
            metadata=initialization_results["summary"]
        )
        
        return initialization_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization error: {str(e)}")

@router.get("/system-info")
async def get_system_info():
    """Get basic system information (no auth required)"""
    try:
        import psutil
        import platform
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            },
            "application": {
                "name": "Mewayz v2 Platform",
                "version": "2.0.0",
                "environment": os.getenv("ENVIRONMENT", "development")
            },
            "status": "operational"
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "status": "error"
        }