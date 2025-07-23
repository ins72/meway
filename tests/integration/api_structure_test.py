#!/usr/bin/env python3
"""
GLOBALIZATION API STRUCTURE INVESTIGATION
"""

import requests
import json

# Backend URL from frontend .env
BACKEND_URL = "https://227a6971-09fc-47c6-b443-58c2c19d4c11.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

def authenticate():
    """Get auth token"""
    session = requests.Session()
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json().get('token')
        session.headers.update({'Authorization': f'Bearer {token}'})
        return session
    return None

def test_contribution_variations():
    """Test different data structures for translation contribution"""
    session = authenticate()
    if not session:
        print("Authentication failed")
        return
    
    print("Testing translation contribution with different structures...")
    
    # Try structure 1 - direct fields
    data1 = {
        "language_code": "de",
        "key": "welcome_message", 
        "translation": "Willkommen bei Mewayz Platform"
    }
    
    response = session.post(f"{API_BASE}/globalization/translations/contribute", json=data1)
    print(f"Structure 1: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Try structure 2 - nested in contribution object
    data2 = {
        "contribution": {
            "language_code": "de",
            "key": "welcome_message",
            "translation": "Willkommen bei Mewayz Platform"
        }
    }
    
    response = session.post(f"{API_BASE}/globalization/translations/contribute", json=data2)
    print(f"Structure 2: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")

def test_preferences_variations():
    """Test different data structures for user preferences"""
    session = authenticate()
    if not session:
        print("Authentication failed")
        return
    
    print("Testing user preferences with different structures...")
    
    # Try structure 1 - direct fields
    data1 = {
        "language": "fr",
        "region": "EU", 
        "currency": "EUR",
        "timezone": "Europe/Paris",
        "date_format": "DD/MM/YYYY",
        "number_format": "european"
    }
    
    response = session.post(f"{API_BASE}/globalization/user-preferences/update", json=data1)
    print(f"Structure 1: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Try structure 2 - nested in preferences object
    data2 = {
        "preferences": {
            "language": "fr",
            "region": "EU",
            "currency": "EUR", 
            "timezone": "Europe/Paris",
            "date_format": "DD/MM/YYYY",
            "number_format": "european"
        }
    }
    
    response = session.post(f"{API_BASE}/globalization/user-preferences/update", json=data2)
    print(f"Structure 2: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_contribution_variations()
    test_preferences_variations()