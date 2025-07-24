#!/usr/bin/env python3
"""
FOCUSED BACKEND TEST - Testing endpoints that were previously working
Based on the COMPREHENSIVE_FULL_PLATFORM_TEST_RESULTS.json
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://b2614b52-973e-4c52-9dec-e3ec14470901.preview.emergentagent.com"
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

def test_working_endpoints():
    """Test endpoints that were previously working"""
    headers = authenticate()
    if not headers:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test endpoints that were working in the comprehensive results
    working_endpoints = [
        # AI Services
        ("GET", "/api/ai/services", "AI Services"),
        ("GET", "/api/ai/conversations", "AI Conversations"),
        
        # Analytics
        ("GET", "/api/analytics/dashboard", "Analytics Dashboard"),
        ("GET", "/api/analytics/overview", "Analytics Overview"),
        
        # Automation
        ("GET", "/api/automation/workflows", "Automation Workflows"),
        ("GET", "/api/automation/workflows/advanced", "Advanced Workflows"),
        ("GET", "/api/automation/triggers/available", "Available Triggers"),
        ("GET", "/api/automation/actions/available", "Available Actions"),
        
        # Blog
        ("GET", "/api/blog/posts", "Blog Posts"),
        ("GET", "/api/blog/analytics", "Blog Analytics"),
        
        # CRM
        ("GET", "/api/crm/dashboard", "CRM Dashboard"),
        ("GET", "/api/crm/contacts", "CRM Contacts"),
        ("GET", "/api/crm/deals", "CRM Deals"),
        
        # Forms
        ("GET", "/api/forms/dashboard", "Forms Dashboard"),
        ("GET", "/api/forms/forms", "List Forms"),
        
        # Integrations
        ("GET", "/api/integrations/available", "Available Integrations"),
        ("GET", "/api/integrations/connected", "Connected Integrations"),
        ("GET", "/api/integrations/logs", "Integration Logs"),
        
        # Team Management (these were working in previous tests)
        ("GET", "/api/team-management/dashboard", "Team Dashboard"),
        ("GET", "/api/team-management/members", "Team Members"),
        ("GET", "/api/team-management/activity", "Team Activity"),
        
        # Instagram Database
        ("GET", "/api/instagram/profiles", "Instagram Profiles"),
        
        # PWA Features
        ("GET", "/api/pwa/manifest/current", "Get Current Manifest"),
        
        # AI Workflows
        ("GET", "/api/workflows/list", "List AI Workflows"),
        
        # Escrow (specific endpoints that were working)
        ("GET", "/api/escrow/transactions/list", "List Escrow Transactions"),
        
        # Template Marketplace (specific endpoints)
        ("GET", "/api/template-marketplace/browse", "Browse Templates"),
        ("GET", "/api/template-marketplace/creator-earnings", "Creator Earnings"),
        
        # Social Media Posts
        ("GET", "/api/posts/scheduled", "Get Scheduled Posts"),
        
        # Device Management
        ("POST", "/api/device/register", "Register Device"),
        
        # Disputes
        ("GET", "/api/disputes/list", "List Disputes"),
        
        # Email Automation
        ("GET", "/api/email-automation/api/email-automation/campaigns", "Email Campaigns"),
        ("GET", "/api/email-automation/api/email-automation/subscribers", "Email Subscribers"),
    ]
    
    working_count = 0
    total_count = len(working_endpoints)
    
    print(f"\n🧪 TESTING {total_count} PREVIOUSLY WORKING ENDPOINTS")
    print("=" * 80)
    
    for method, endpoint, description in working_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=30)
            elif method == "POST":
                # Simple test data for POST endpoints
                test_data = {"device_id": "test-device", "device_type": "mobile"}
                response = requests.post(f"{BACKEND_URL}{endpoint}", json=test_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                working_count += 1
                print(f"✅ {description} - Status {response.status_code}")
                # Show response size for working endpoints
                try:
                    data = response.json()
                    print(f"   Response size: {len(str(data))} chars")
                except:
                    print(f"   Response size: {len(response.text)} chars")
            else:
                print(f"❌ {description} - Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description} - Error: {str(e)[:100]}")
    
    print(f"\n📊 RESULTS SUMMARY:")
    print("=" * 80)
    success_rate = (working_count / total_count * 100) if total_count > 0 else 0
    print(f"Working Endpoints: {working_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate >= 70:
        print("🟢 EXCELLENT: Most endpoints are working properly")
    elif success_rate >= 50:
        print("🟡 GOOD: Majority of endpoints are working")
    else:
        print("🔴 ISSUES: Many endpoints need attention")

if __name__ == "__main__":
    test_working_endpoints()