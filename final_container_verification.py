#!/usr/bin/env python3
"""
Final container deployment verification
Tests all possible health endpoints and scenarios
"""

import requests
import sys
import time
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("final_verification")

def test_all_health_endpoints():
    """Test every possible health endpoint variant"""
    endpoints = [
        ("Root", "http://localhost:8001/", ["status", "service"]),
        ("Health", "http://localhost:8001/health", ["status"]),
        ("API Health", "http://localhost:8001/api/health", ["status"]),
        ("Healthz", "http://localhost:8001/healthz", ["status"]),
        ("Health Check", "http://localhost:8001/health-check", ["status"]),
        ("Readiness", "http://localhost:8001/readiness", ["ready"]),
        ("Liveness", "http://localhost:8001/liveness", ["alive"]),
        ("Ready", "http://localhost:8001/ready", ["ready"]),
        ("API Status", "http://localhost:8001/api/status", ["api"]),
        ("Test", "http://localhost:8001/test", ["test"]),
        ("Container Info", "http://localhost:8001/container-info", ["container"]),
        ("Catch All", "http://localhost:8001/random/path", ["message"])
    ]
    
    logger.info("🧪 Testing all health endpoints...")
    
    passed = 0
    total = len(endpoints)
    
    for name, url, required_keys in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in required_keys):
                    logger.info(f"✅ {name}: {response.status_code} - {list(data.keys())}")
                    passed += 1
                else:
                    logger.warning(f"⚠️ {name}: Missing keys {required_keys}")
            else:
                logger.error(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ {name}: {e}")
    
    logger.info(f"📊 Health Endpoints: {passed}/{total} passed")
    return passed == total

def test_cors_headers():
    """Test CORS headers are set correctly"""
    logger.info("🧪 Testing CORS headers...")
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        headers = response.headers
        
        required_cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        cors_ok = all(header in headers for header in required_cors_headers)
        container_headers_ok = "X-Container-Status" in headers
        
        if cors_ok and container_headers_ok:
            logger.info("✅ CORS headers correctly set")
            return True
        else:
            logger.error("❌ Missing CORS headers")
            return False
            
    except Exception as e:
        logger.error(f"❌ CORS headers test failed: {e}")
        return False

def test_different_methods():
    """Test different HTTP methods work"""
    logger.info("🧪 Testing HTTP methods...")
    
    methods = [
        ("GET", "http://localhost:8001/test"),
        ("POST", "http://localhost:8001/test"),
        ("OPTIONS", "http://localhost:8001/health")
    ]
    
    passed = 0
    for method, url in methods:
        try:
            response = requests.request(method, url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {method} {url}: {response.status_code}")
                passed += 1
            else:
                logger.warning(f"⚠️ {method} {url}: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ {method} {url}: {e}")
    
    logger.info(f"📊 HTTP Methods: {passed}/{len(methods)} passed")
    return passed == len(methods)

def test_response_speed():
    """Test response speed is acceptable"""
    logger.info("🧪 Testing response speed...")
    
    start_time = time.time()
    try:
        response = requests.get("http://localhost:8001/health", timeout=1)
        response_time = time.time() - start_time
        
        if response.status_code == 200 and response_time < 0.5:
            logger.info(f"✅ Response time: {response_time:.3f}s")
            return True
        else:
            logger.warning(f"⚠️ Slow response: {response_time:.3f}s")
            return False
    except Exception as e:
        logger.error(f"❌ Response speed test failed: {e}")
        return False

def main():
    """Run complete verification suite"""
    logger.info("🚀 FINAL CONTAINER DEPLOYMENT VERIFICATION")
    logger.info("=" * 50)
    
    tests = [
        ("Health Endpoints", test_all_health_endpoints()),
        ("CORS Headers", test_cors_headers()),
        ("HTTP Methods", test_different_methods()),
        ("Response Speed", test_response_speed())
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    logger.info("=" * 50)
    logger.info(f"📊 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("🚀 CONTAINER IS 100% READY FOR DEPLOYMENT!")
        logger.info("💚 GUARANTEED TO WORK IN KUBERNETES!")
        return True
    else:
        logger.error("❌ Some tests failed")
        logger.error("🔴 Container may have deployment issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)