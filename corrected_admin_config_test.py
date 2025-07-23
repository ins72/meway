#!/usr/bin/env python3
"""
Corrected Admin Configuration Endpoints Test
Testing the actual admin-config endpoints from OpenAPI spec
"""

import requests
import json
import sys

# Backend URL from environment
BACKEND_URL = "https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

def authenticate():
    """Authenticate with the backend"""
    session = requests.Session()
    
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = session.post(
        f"{API_BASE}/auth/login",
        data=login_data,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        if access_token:
            session.headers.update({"Authorization": f"Bearer {access_token}"})
            print(f"✅ Authentication successful")
            return session
    
    print(f"❌ Authentication failed")
    return None

def test_corrected_admin_config_endpoints():
    """Test the corrected admin-config endpoints from OpenAPI spec"""
    session = authenticate()
    if not session:
        return
    
    print("\n=== CORRECTED ADMIN CONFIGURATION ENDPOINTS TEST ===")
    
    # Corrected admin-config endpoints from OpenAPI spec
    admin_endpoints = [
        ("/admin-config/configuration", "GET", "Admin Configuration"),
        ("/admin-config/integrations/status", "GET", "Integration Status"),
        ("/admin-config/system/health", "GET", "System Health"),
        ("/admin-config/logs", "GET", "System Logs"),
        ("/admin-config/available-services", "GET", "Available Services"),
        ("/admin-config/analytics/dashboard", "GET", "Analytics Dashboard"),
        ("/admin-config/logs/statistics", "GET", "Log Statistics"),
        ("/admin-config/integrations/stripe/test", "POST", "Test Stripe Integration"),
        ("/admin-config/integrations/openai/test", "POST", "Test OpenAI Integration"),
        ("/admin-config/integrations/sendgrid/test", "POST", "Test SendGrid Integration"),
        ("/admin-config/integrations/twitter/test", "POST", "Test Twitter Integration")
    ]
    
    results = []
    
    for endpoint, method, name in admin_endpoints:
        try:
            if method == "GET":
                response = session.get(f"{API_BASE}{endpoint}", timeout=10)
            else:  # POST
                response = session.post(f"{API_BASE}{endpoint}", json={}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name} - Working ({len(str(data))} chars)")
                results.append((name, True, len(str(data))))
            else:
                print(f"❌ {name} - Failed (Status {response.status_code})")
                results.append((name, False, 0))
                
        except Exception as e:
            print(f"❌ {name} - Error: {str(e)}")
            results.append((name, False, 0))
    
    # Summary
    working = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"\n=== CORRECTED ADMIN CONFIG SUMMARY ===")
    print(f"Working endpoints: {working}/{total} ({working/total*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    test_corrected_admin_config_endpoints()