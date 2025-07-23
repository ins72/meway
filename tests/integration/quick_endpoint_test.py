#!/usr/bin/env python3
"""
Quick test to check available endpoints and authentication
"""

import requests
import json

# Backend URL from frontend .env
BACKEND_URL = "https://227a6971-09fc-47c6-b443-58c2c19d4c11.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

def test_auth_and_endpoints():
    session = requests.Session()
    
    print("Testing authentication...")
    try:
        response = session.post(
            f"{API_BASE}/auth/login",
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            },
            timeout=30
        )
        print(f"Auth response status: {response.status_code}")
        print(f"Auth response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token') or data.get('token')
            print(f"Token found: {token[:50] if token else 'None'}...")
            
            if token:
                session.headers.update({
                    'Authorization': f'Bearer {token}'
                })
                
                # Test some known endpoints
                test_endpoints = [
                    "/health",
                    "/admin/dashboard", 
                    "/workspaces",
                    "/ai/services",
                    "/bio-sites/themes"
                ]
                
                for endpoint in test_endpoints:
                    try:
                        resp = session.get(f"{API_BASE}{endpoint}", timeout=10)
                        print(f"GET {endpoint}: {resp.status_code} - {len(resp.text)} bytes")
                    except Exception as e:
                        print(f"GET {endpoint}: Error - {e}")
                        
    except Exception as e:
        print(f"Auth error: {e}")

if __name__ == "__main__":
    test_auth_and_endpoints()