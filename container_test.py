#!/usr/bin/env python3
"""
Ultra-minimal deployment test for container readiness
"""

import requests
import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("container_test")

def test_container_endpoints():
    """Test all container endpoints"""
    endpoints = [
        ("Root", "http://localhost:8001/", "status", "running"),
        ("Health", "http://localhost:8001/health", "status", "healthy"),
        ("API Health", "http://localhost:8001/api/health", "status", "healthy"),
        ("Readiness", "http://localhost:8001/readiness", "ready", True),
        ("Liveness", "http://localhost:8001/liveness", "alive", True),
        ("API Status", "http://localhost:8001/api/status", "api", "operational")
    ]
    
    logger.info("🧪 Testing container endpoints...")
    
    all_passed = True
    for name, url, key, expected in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get(key) == expected:
                    logger.info(f"✅ {name}: {data.get(key)}")
                else:
                    logger.error(f"❌ {name}: Expected {expected}, got {data.get(key)}")
                    all_passed = False
            else:
                logger.error(f"❌ {name}: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {name}: {e}")
            all_passed = False
    
    return all_passed

def test_startup_speed():
    """Test how fast the service starts"""
    logger.info("🧪 Testing startup speed...")
    
    start_time = time.time()
    max_attempts = 30
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8001/health", timeout=1)
            if response.status_code == 200:
                startup_time = time.time() - start_time
                logger.info(f"✅ Service ready in {startup_time:.2f} seconds")
                return startup_time < 10  # Should start in under 10 seconds
        except:
            time.sleep(0.5)
    
    logger.error("❌ Service failed to start in time")
    return False

def main():
    """Run container readiness tests"""
    logger.info("🚀 Container Readiness Test")
    
    tests = [
        ("Endpoint Test", test_container_endpoints()),
        ("Startup Speed", test_startup_speed())
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    logger.info(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 CONTAINER READY FOR DEPLOYMENT!")
        return True
    else:
        logger.error("❌ Container not ready")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)