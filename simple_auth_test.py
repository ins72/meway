#!/usr/bin/env python3
"""
Simple authentication test for Mewayz backend
"""
import requests
import json

BACKEND_URL = "https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

def test_auth_endpoints():
    """Test various authentication endpoints"""
    
    # Test health endpoint first
    print("Testing health endpoint...")
    response = requests.get(f"{BACKEND_URL}/health")
    print(f"Health: {response.status_code} - {response.text[:200]}")
    
    # Test OpenAPI docs
    print("\nTesting OpenAPI docs...")
    response = requests.get(f"{BACKEND_URL}/docs")
    print(f"Docs: {response.status_code} - Available")
    
    # Test auth endpoints
    auth_endpoints = [
        "/api/auth/login",
        "/api/auth/register", 
        "/auth/login",
        "/login"
    ]
    
    for endpoint in auth_endpoints:
        print(f"\nTesting {endpoint}...")
        
        # Test GET first to see if endpoint exists
        response = requests.get(f"{BACKEND_URL}{endpoint}")
        print(f"GET {endpoint}: {response.status_code}")
        
        # Test POST with login data
        login_data = {
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(f"{BACKEND_URL}{endpoint}", data=login_data)
        print(f"POST {endpoint}: {response.status_code} - {response.text[:200]}")
        
        # Also try with JSON
        response = requests.post(f"{BACKEND_URL}{endpoint}", json=login_data)
        print(f"POST JSON {endpoint}: {response.status_code} - {response.text[:200]}")

if __name__ == "__main__":
    test_auth_endpoints()