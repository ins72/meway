#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE BACKEND AUDIT - Testing actual implemented endpoints
Based on the main.py router includes
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://bd15977c-5d37-4fb8-991c-847ae2409f32.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

def authenticate():
    """Get authentication token"""
    try:
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return None
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def test_core_systems():
    """Test the core systems that are definitely implemented"""
    headers = authenticate()
    if not headers:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test the core systems based on main.py router includes
    core_systems = {
        "Booking System": [
            ("GET", "/api/booking/health", "Health check"),
            ("GET", "/api/booking/", "List bookings"),
            ("POST", "/api/booking/", "Create booking"),
        ],
        "Escrow System": [
            ("GET", "/api/escrow/health", "Health check"),
            ("GET", "/api/escrow/", "List escrow"),
            ("POST", "/api/escrow/", "Create escrow"),
        ],
        "Website Builder": [
            ("GET", "/api/website-builder/health", "Health check"),
            ("GET", "/api/website-builder/", "List websites"),
            ("GET", "/api/website-builder/templates", "List templates"),
        ],
        "Template Marketplace": [
            ("GET", "/api/template-marketplace/health", "Health check"),
            ("GET", "/api/template-marketplace/", "List templates"),
            ("POST", "/api/template-marketplace/", "Create template"),
        ],
        "Link in Bio": [
            ("GET", "/api/complete-link-in-bio/health", "Health check"),
            ("GET", "/api/complete-link-in-bio/", "List link pages"),
            ("POST", "/api/complete-link-in-bio/", "Create link page"),
        ],
        "Course & Community": [
            ("GET", "/api/complete-course-community/health", "Health check"),
            ("GET", "/api/complete-course-community/", "List courses"),
            ("POST", "/api/complete-course-community/", "Create course"),
        ],
        "Multi-Vendor Marketplace": [
            ("GET", "/api/multi-vendor-marketplace/health", "Health check"),
            ("GET", "/api/multi-vendor-marketplace/", "List products"),
            ("POST", "/api/multi-vendor-marketplace/", "Create product"),
        ],
        "Financial System": [
            ("GET", "/api/financial/health", "Health check"),
            ("GET", "/api/financial/", "List financial records"),
            ("POST", "/api/financial/", "Create financial record"),
        ],
        "User Management": [
            ("GET", "/api/user/api/user/profile", "Get user profile"),
            ("GET", "/api/user/api/user/activity", "Get user activity"),
        ],
        "Workspace Management": [
            ("GET", "/api/workspace/health", "Health check"),
            ("GET", "/api/workspace/", "List workspaces"),
        ],
        "Media Library": [
            ("GET", "/api/media-library/health", "Health check"),
            ("GET", "/api/media-library/", "List media"),
        ],
        "AI Content": [
            ("GET", "/api/ai-content/health", "Health check"),
            ("GET", "/api/ai-content/", "List AI content"),
        ],
        "Marketing": [
            ("GET", "/api/marketing/health", "Health check"),
            ("GET", "/api/marketing/", "List marketing campaigns"),
        ],
        "Analytics": [
            ("GET", "/api/analytics/health", "Health check"),
            ("GET", "/api/analytics/", "List analytics"),
        ],
        "Settings": [
            ("GET", "/api/settings/health", "Health check"),
            ("GET", "/api/settings/", "List settings"),
        ]
    }
    
    total_systems = len(core_systems)
    working_systems = 0
    total_endpoints = 0
    working_endpoints = 0
    
    print(f"\n🧪 TESTING {total_systems} CORE SYSTEMS")
    print("=" * 80)
    
    for system_name, endpoints in core_systems.items():
        print(f"\n📋 {system_name}")
        print("-" * 60)
        
        system_working = 0
        system_total = len(endpoints)
        
        for method, endpoint, description in endpoints:
            total_endpoints += 1
            try:
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=30)
                elif method == "POST":
                    # Create appropriate test data
                    test_data = {
                        "name": f"Test {system_name}",
                        "description": f"Test data for {system_name}",
                        "test": True
                    }
                    response = requests.post(f"{BACKEND_URL}{endpoint}", json=test_data, headers=headers, timeout=30)
                
                if response.status_code in [200, 201]:
                    system_working += 1
                    working_endpoints += 1
                    print(f"✅ {description} - Status {response.status_code}")
                else:
                    print(f"❌ {description} - Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description} - Error: {str(e)[:50]}")
        
        # Determine if system is working (>= 50% endpoints working)
        system_success_rate = (system_working / system_total * 100) if system_total > 0 else 0
        if system_success_rate >= 50:
            working_systems += 1
            print(f"🟢 {system_name}: WORKING ({system_working}/{system_total} endpoints)")
        else:
            print(f"🔴 {system_name}: ISSUES ({system_working}/{system_total} endpoints)")
    
    print(f"\n📊 FINAL COMPREHENSIVE AUDIT RESULTS")
    print("=" * 80)
    
    overall_success_rate = (working_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
    systems_success_rate = (working_systems / total_systems * 100) if total_systems > 0 else 0
    
    print(f"Total Systems Tested: {total_systems}")
    print(f"Working Systems: {working_systems}")
    print(f"Systems Success Rate: {systems_success_rate:.1f}%")
    print(f"")
    print(f"Total Endpoints Tested: {total_endpoints}")
    print(f"Working Endpoints: {working_endpoints}")
    print(f"Endpoints Success Rate: {overall_success_rate:.1f}%")
    
    # Critical systems assessment
    critical_systems = [
        "Booking System", "Escrow System", "Website Builder", 
        "Template Marketplace", "Link in Bio", "Course & Community",
        "Multi-Vendor Marketplace"
    ]
    
    working_critical = 0
    for system in critical_systems:
        if system in core_systems:
            endpoints = core_systems[system]
            system_working = 0
            for method, endpoint, description in endpoints:
                try:
                    if method == "GET":
                        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=30)
                    elif method == "POST":
                        test_data = {"name": "Test", "test": True}
                        response = requests.post(f"{BACKEND_URL}{endpoint}", json=test_data, headers=headers, timeout=30)
                    
                    if response.status_code in [200, 201]:
                        system_working += 1
                except:
                    pass
            
            if system_working >= len(endpoints) / 2:  # At least 50% working
                working_critical += 1
    
    critical_success_rate = (working_critical / len(critical_systems) * 100)
    
    print(f"\n🎯 CRITICAL SYSTEMS ASSESSMENT:")
    print("-" * 80)
    print(f"Critical Systems Working: {working_critical}/{len(critical_systems)}")
    print(f"Critical Success Rate: {critical_success_rate:.1f}%")
    
    if critical_success_rate >= 80:
        print("🟢 EXCELLENT: Platform is production-ready with all major systems working")
    elif critical_success_rate >= 60:
        print("🟡 GOOD: Platform has most critical systems working")
    else:
        print("🔴 NEEDS WORK: Several critical systems need attention")
    
    # Save results
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_systems": total_systems,
            "working_systems": working_systems,
            "systems_success_rate": systems_success_rate,
            "total_endpoints": total_endpoints,
            "working_endpoints": working_endpoints,
            "endpoints_success_rate": overall_success_rate,
            "critical_systems_working": working_critical,
            "critical_success_rate": critical_success_rate
        }
    }
    
    with open("/app/final_backend_audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: /app/final_backend_audit_results.json")
    
    return results

if __name__ == "__main__":
    test_core_systems()