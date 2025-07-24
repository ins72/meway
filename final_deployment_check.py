#!/usr/bin/env python3
"""
Final deployment verification for container environment
"""

import asyncio
import logging
import requests
import time
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deployment_check")

async def check_backend_startup():
    """Verify backend starts correctly"""
    logger.info("🧪 Testing backend startup...")
    
    # Test the minimal import
    try:
        sys.path.insert(0, "/app/backend")
        from main import app
        logger.info("✅ Backend app imports successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Backend import failed: {e}")
        return False

def check_health_endpoints():
    """Test health endpoints are responding"""
    logger.info("🧪 Testing health endpoints...")
    
    endpoints = [
        "http://localhost:8001/",
        "http://localhost:8001/health", 
        "http://localhost:8001/api/health"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {endpoint} responding")
            else:
                logger.warning(f"⚠️ {endpoint} returned {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {endpoint} failed: {e}")
            return False
    
    return True

def check_minimal_mode():
    """Test minimal mode functionality"""
    logger.info("🧪 Testing minimal mode...")
    
    # Set minimal mode
    os.environ["MINIMAL_MODE"] = "true"
    
    try:
        sys.path.insert(0, "/app/backend")
        import importlib
        import main
        importlib.reload(main)
        logger.info("✅ Minimal mode import successful")
        return True
    except Exception as e:
        logger.error(f"❌ Minimal mode failed: {e}")
        return False
    finally:
        # Reset
        os.environ.pop("MINIMAL_MODE", None)

async def main():
    """Run all deployment checks"""
    logger.info("🚀 Starting final deployment verification...")
    
    checks = [
        ("Backend Startup", check_backend_startup()),
        ("Health Endpoints", check_health_endpoints()),
        ("Minimal Mode", check_minimal_mode())
    ]
    
    results = []
    for check_name, check_func in checks:
        logger.info(f"🧪 Running {check_name}...")
        if asyncio.iscoroutine(check_func):
            result = await check_func
        else:
            result = check_func
        results.append((check_name, result))
        
        if result:
            logger.info(f"✅ {check_name} PASSED")
        else:
            logger.error(f"❌ {check_name} FAILED")
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info(f"\n📊 Final Results: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        logger.info("🚀 Container deployment should succeed")
        return True
    else:
        logger.error("❌ Some checks failed - deployment may have issues")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)