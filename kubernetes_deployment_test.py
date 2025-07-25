#!/usr/bin/env python3
"""
KUBERNETES DEPLOYMENT VERIFICATION SCRIPT
Bulletproof health check testing for container deployment
"""

import requests
import time
import json
from datetime import datetime

def test_health_endpoint(url, endpoint, expected_status=200):
    """Test a health endpoint and measure response time"""
    try:
        start_time = time.time()
        response = requests.get(f"{url}{endpoint}", timeout=5)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "success": response.status_code == expected_status,
            "content": response.json() if response.status_code == 200 else response.text[:100]
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": 0,
            "response_time_ms": 0,
            "success": False,
            "error": str(e)
        }

def run_deployment_verification():
    """Run comprehensive deployment verification"""
    base_url = "http://localhost:8001"
    
    # Health endpoints to test
    endpoints = [
        "/",
        "/health", 
        "/api/health",
        "/readiness",
        "/liveness"
    ]
    
    print("🚀 KUBERNETES DEPLOYMENT VERIFICATION")
    print("=" * 50)
    print(f"Testing base URL: {base_url}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print()
    
    results = []
    total_success = 0
    
    for endpoint in endpoints:
        print(f"Testing {endpoint}...", end=" ")
        result = test_health_endpoint(base_url, endpoint)
        results.append(result)
        
        if result["success"]:
            print(f"✅ {result['response_time_ms']}ms")
            total_success += 1
        else:
            print(f"❌ FAILED - {result.get('error', 'HTTP ' + str(result['status_code']))}")
    
    print()
    print("📊 SUMMARY")
    print("-" * 30)
    print(f"Total endpoints tested: {len(endpoints)}")
    print(f"Successful responses: {total_success}")
    print(f"Failed responses: {len(endpoints) - total_success}")
    print(f"Success rate: {(total_success/len(endpoints)*100):.1f}%")
    
    # Calculate average response time for successful requests
    successful_times = [r["response_time_ms"] for r in results if r["success"]]
    if successful_times:
        avg_response_time = sum(successful_times) / len(successful_times)
        print(f"Average response time: {avg_response_time:.2f}ms")
    
    print()
    print("📋 DETAILED RESULTS")
    print("-" * 50)
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{result['endpoint']:15} | {status} | {result['response_time_ms']:6.2f}ms | HTTP {result['status_code']}")
    
    print()
    
    # Kubernetes readiness assessment
    readiness_passed = any(r["endpoint"] == "/readiness" and r["success"] for r in results)
    liveness_passed = any(r["endpoint"] == "/liveness" and r["success"] for r in results)
    health_passed = any(r["endpoint"] == "/health" and r["success"] for r in results)
    
    print("🎯 KUBERNETES ASSESSMENT")
    print("-" * 30)
    print(f"Readiness Probe: {'✅ READY' if readiness_passed else '❌ NOT READY'}")
    print(f"Liveness Probe:  {'✅ ALIVE' if liveness_passed else '❌ NOT ALIVE'}")
    print(f"Health Check:    {'✅ HEALTHY' if health_passed else '❌ UNHEALTHY'}")
    
    deployment_ready = readiness_passed and liveness_passed and health_passed
    print(f"Deployment Ready: {'✅ YES' if deployment_ready else '❌ NO'}")
    
    # Speed assessment for Kubernetes
    fast_responses = [r for r in results if r["success"] and r["response_time_ms"] < 100]  # Under 100ms
    speed_ok = len(fast_responses) == total_success
    print(f"Response Speed:   {'✅ FAST (<100ms)' if speed_ok else '❌ SLOW (>100ms)'}")
    
    print()
    if deployment_ready and speed_ok:
        print("🎉 DEPLOYMENT VERDICT: READY FOR KUBERNETES! 🎉")
        print("All health checks passing with fast response times.")
        print("Container should deploy successfully without 503 errors.")
    else:
        print("⚠️ DEPLOYMENT VERDICT: NEEDS FIXES")
        print("Some health checks failing or response times too slow.")
    
    return deployment_ready and speed_ok

if __name__ == "__main__":
    success = run_deployment_verification()
    exit(0 if success else 1)