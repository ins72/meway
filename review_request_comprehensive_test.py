#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TEST - REVIEW REQUEST ASSESSMENT
Testing ObjectId serialization fixes and overall system improvement
Focus: Authentication, Referral System, Twitter/X API, TikTok API, Stripe, Core Business Systems
Target: Measure improvement from previous 50% success rate to 95%+ production readiness
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveBackendTester:
    def __init__(self):
        # Get backend URL from environment
        self.base_url = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        
        # Admin credentials from review request
        self.admin_email = "tmonnens@outlook.com"
        self.admin_password = "Voetballen5"
        
        # Test results tracking
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_categories": {},
            "critical_issues": [],
            "improvements": [],
            "detailed_results": []
        }
        
        # JWT token for authenticated requests
        self.jwt_token = None
        
    async def run_comprehensive_test(self):
        """Run comprehensive backend testing as per review request"""
        print("🎯 COMPREHENSIVE BACKEND TESTING - REVIEW REQUEST ASSESSMENT - JANUARY 2025 🎯")
        print(f"Backend URL: {self.base_url}")
        print(f"Admin Credentials: {self.admin_email}/{self.admin_password}")
        print("=" * 80)
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            self.session = session
            
            # Test categories as per review request
            test_categories = [
                ("Authentication System", self.test_authentication_system),
                ("Referral System", self.test_referral_system),
                ("Twitter/X API", self.test_twitter_api),
                ("TikTok API", self.test_tiktok_api),
                ("Stripe Integration", self.test_stripe_integration),
                ("Core Business Systems", self.test_core_business_systems),
                ("Overall System Health", self.test_system_health)
            ]
            
            for category_name, test_function in test_categories:
                print(f"\n🔍 TESTING: {category_name}")
                print("-" * 60)
                
                category_results = await test_function()
                self.results["test_categories"][category_name] = category_results
                
                # Update totals
                self.results["total_tests"] += category_results["total"]
                self.results["passed_tests"] += category_results["passed"]
                self.results["failed_tests"] += category_results["failed"]
                
                # Print category summary
                success_rate = (category_results["passed"] / category_results["total"] * 100) if category_results["total"] > 0 else 0
                status = "✅ EXCELLENT" if success_rate >= 90 else "⚠️ NEEDS WORK" if success_rate >= 70 else "❌ CRITICAL ISSUES"
                print(f"   {status} - {success_rate:.1f}% Success ({category_results['passed']}/{category_results['total']} tests passed)")
        
        # Generate final report
        await self.generate_final_report()
        
    async def test_authentication_system(self) -> Dict[str, Any]:
        """Test JWT token generation and validation"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        
        # Test 1: JWT Token Generation
        results["total"] += 1
        try:
            login_data = {
                "email": self.admin_email,
                "password": self.admin_password
            }
            
            async with self.session.post(f"{self.api_url}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if "access_token" in data:
                        self.jwt_token = data["access_token"]
                        results["passed"] += 1
                        results["details"].append("✅ JWT Token Generation - Working perfectly")
                        print(f"   ✅ JWT Token Generation - Working perfectly ({len(str(data))} chars response)")
                    else:
                        results["failed"] += 1
                        results["details"].append("❌ JWT Token Generation - No access_token in response")
                        print("   ❌ JWT Token Generation - No access_token in response")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ JWT Token Generation - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ JWT Token Generation - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ JWT Token Generation - Exception: {str(e)}")
            print(f"   ❌ JWT Token Generation - Exception: {str(e)}")
        
        # Test 2: JWT Token Validation
        results["total"] += 1
        if self.jwt_token:
            try:
                headers = {"Authorization": f"Bearer {self.jwt_token}"}
                async with self.session.get(f"{self.api_url}/auth/me", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        results["passed"] += 1
                        results["details"].append("✅ JWT Token Validation - Working perfectly")
                        print(f"   ✅ JWT Token Validation - Working perfectly ({len(str(data))} chars response)")
                    else:
                        results["failed"] += 1
                        error_text = await response.text()
                        results["details"].append(f"❌ JWT Token Validation - HTTP {response.status}: {error_text[:100]}")
                        print(f"   ❌ JWT Token Validation - HTTP {response.status}: {error_text[:100]}")
            except Exception as e:
                results["failed"] += 1
                results["details"].append(f"❌ JWT Token Validation - Exception: {str(e)}")
                print(f"   ❌ JWT Token Validation - Exception: {str(e)}")
        else:
            results["failed"] += 1
            results["details"].append("❌ JWT Token Validation - No token available")
            print("   ❌ JWT Token Validation - No token available")
        
        return results
    
    async def test_referral_system(self) -> Dict[str, Any]:
        """Test Referral System CRUD operations after fixing syntax errors"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        headers = {"Authorization": f"Bearer {self.jwt_token}"} if self.jwt_token else {}
        
        # Test 1: Health Check
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/referral/health") as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Referral Health Check - Working perfectly")
                    print(f"   ✅ Referral Health Check - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Referral Health Check - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Referral Health Check - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Referral Health Check - Exception: {str(e)}")
            print(f"   ❌ Referral Health Check - Exception: {str(e)}")
        
        # Test 2: List Referrals (READ)
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/referral/referrals", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ List Referrals - Working perfectly")
                    print(f"   ✅ List Referrals - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ List Referrals - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ List Referrals - HTTP {response.status}: {error_text[:100]}")
                    
                    # Check for ObjectId serialization issues
                    if "JSON decode error with text/plain response" in error_text:
                        self.results["critical_issues"].append("ObjectId serialization issue in Referral System")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ List Referrals - Exception: {str(e)}")
            print(f"   ❌ List Referrals - Exception: {str(e)}")
        
        # Test 3: Create Referral (CREATE)
        results["total"] += 1
        try:
            referral_data = {
                "referrer_email": self.admin_email,
                "referred_email": "test.referral@example.com",
                "referral_code": f"REF{int(time.time())}",
                "commission_rate": 0.1
            }
            
            async with self.session.post(f"{self.api_url}/referral/referrals", json=referral_data, headers=headers) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Create Referral - Working perfectly")
                    print(f"   ✅ Create Referral - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Create Referral - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Create Referral - HTTP {response.status}: {error_text[:100]}")
                    
                    # Check for ObjectId serialization issues
                    if "JSON decode error with text/plain response" in error_text:
                        self.results["critical_issues"].append("ObjectId serialization issue in Referral Creation")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Create Referral - Exception: {str(e)}")
            print(f"   ❌ Create Referral - Exception: {str(e)}")
        
        # Test 4: Referral Analytics
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/referral/analytics", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Referral Analytics - Working perfectly")
                    print(f"   ✅ Referral Analytics - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Referral Analytics - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Referral Analytics - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Referral Analytics - Exception: {str(e)}")
            print(f"   ❌ Referral Analytics - Exception: {str(e)}")
        
        return results
    
    async def test_twitter_api(self) -> Dict[str, Any]:
        """Test Twitter/X API including fixed search functionality"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        headers = {"Authorization": f"Bearer {self.jwt_token}"} if self.jwt_token else {}
        
        # Test 1: Health Check
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/twitter/health") as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Twitter Health Check - Working perfectly")
                    print(f"   ✅ Twitter Health Check - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Twitter Health Check - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Twitter Health Check - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Twitter Health Check - Exception: {str(e)}")
            print(f"   ❌ Twitter Health Check - Exception: {str(e)}")
        
        # Test 2: Search Functionality (Fixed)
        results["total"] += 1
        try:
            search_params = {"query": "business marketing", "count": 10}
            async with self.session.get(f"{self.api_url}/twitter/tweets/search", params=search_params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Twitter Search - Working perfectly")
                    print(f"   ✅ Twitter Search - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Twitter Search - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Twitter Search - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Twitter Search - Exception: {str(e)}")
            print(f"   ❌ Twitter Search - Exception: {str(e)}")
        
        # Test 3: Tweet Creation
        results["total"] += 1
        try:
            tweet_data = {
                "content": f"Test tweet from Mewayz platform - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "scheduled": False
            }
            
            async with self.session.post(f"{self.api_url}/twitter/tweets", json=tweet_data, headers=headers) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Tweet Creation - Working perfectly")
                    print(f"   ✅ Tweet Creation - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Tweet Creation - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Tweet Creation - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Tweet Creation - Exception: {str(e)}")
            print(f"   ❌ Tweet Creation - Exception: {str(e)}")
        
        # Test 4: Analytics
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/twitter/analytics", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Twitter Analytics - Working perfectly")
                    print(f"   ✅ Twitter Analytics - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Twitter Analytics - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Twitter Analytics - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Twitter Analytics - Exception: {str(e)}")
            print(f"   ❌ Twitter Analytics - Exception: {str(e)}")
        
        return results
    
    async def test_tiktok_api(self) -> Dict[str, Any]:
        """Test TikTok API including search functionality"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        headers = {"Authorization": f"Bearer {self.jwt_token}"} if self.jwt_token else {}
        
        # Test 1: Health Check
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/tiktok/health") as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ TikTok Health Check - Working perfectly")
                    print(f"   ✅ TikTok Health Check - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ TikTok Health Check - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ TikTok Health Check - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ TikTok Health Check - Exception: {str(e)}")
            print(f"   ❌ TikTok Health Check - Exception: {str(e)}")
        
        # Test 2: Search Functionality
        results["total"] += 1
        try:
            search_params = {"query": "business tips", "count": 10}
            async with self.session.get(f"{self.api_url}/tiktok/posts/search", params=search_params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ TikTok Search - Working perfectly")
                    print(f"   ✅ TikTok Search - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ TikTok Search - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ TikTok Search - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ TikTok Search - Exception: {str(e)}")
            print(f"   ❌ TikTok Search - Exception: {str(e)}")
        
        # Test 3: Video Upload
        results["total"] += 1
        try:
            video_data = {
                "title": f"Test video from Mewayz - {datetime.now().strftime('%Y-%m-%d')}",
                "description": "Automated test video upload",
                "tags": ["business", "marketing", "automation"]
            }
            
            async with self.session.post(f"{self.api_url}/tiktok/posts", json=video_data, headers=headers) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ TikTok Video Upload - Working perfectly")
                    print(f"   ✅ TikTok Video Upload - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ TikTok Video Upload - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ TikTok Video Upload - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ TikTok Video Upload - Exception: {str(e)}")
            print(f"   ❌ TikTok Video Upload - Exception: {str(e)}")
        
        # Test 4: Analytics
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/tiktok/analytics", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ TikTok Analytics - Working perfectly")
                    print(f"   ✅ TikTok Analytics - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ TikTok Analytics - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ TikTok Analytics - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ TikTok Analytics - Exception: {str(e)}")
            print(f"   ❌ TikTok Analytics - Exception: {str(e)}")
        
        return results
    
    async def test_stripe_integration(self) -> Dict[str, Any]:
        """Test Stripe Integration including payment methods"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        headers = {"Authorization": f"Bearer {self.jwt_token}"} if self.jwt_token else {}
        
        # Test 1: Health Check
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/stripe-integration/health") as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Stripe Health Check - Working perfectly")
                    print(f"   ✅ Stripe Health Check - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Stripe Health Check - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Stripe Health Check - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Stripe Health Check - Exception: {str(e)}")
            print(f"   ❌ Stripe Health Check - Exception: {str(e)}")
        
        # Test 2: Create Payment Intent
        results["total"] += 1
        try:
            payment_data = {
                "amount": 2999,  # $29.99
                "currency": "usd",
                "description": "Test payment from Mewayz platform"
            }
            
            async with self.session.post(f"{self.api_url}/stripe-integration/payment-intent", json=payment_data, headers=headers) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Create Payment Intent - Working perfectly")
                    print(f"   ✅ Create Payment Intent - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Create Payment Intent - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Create Payment Intent - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Create Payment Intent - Exception: {str(e)}")
            print(f"   ❌ Create Payment Intent - Exception: {str(e)}")
        
        # Test 3: Payment Methods
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/stripe-integration/payment-methods", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Payment Methods - Working perfectly")
                    print(f"   ✅ Payment Methods - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Payment Methods - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Payment Methods - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Payment Methods - Exception: {str(e)}")
            print(f"   ❌ Payment Methods - Exception: {str(e)}")
        
        # Test 4: Subscription Management
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/stripe/subscriptions", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Subscription Management - Working perfectly")
                    print(f"   ✅ Subscription Management - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Subscription Management - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Subscription Management - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Subscription Management - Exception: {str(e)}")
            print(f"   ❌ Subscription Management - Exception: {str(e)}")
        
        return results
    
    async def test_core_business_systems(self) -> Dict[str, Any]:
        """Test key endpoints like financial, admin dashboard, analytics"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        headers = {"Authorization": f"Bearer {self.jwt_token}"} if self.jwt_token else {}
        
        # Test 1: Financial System
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/financial/dashboard", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Financial System - Working perfectly")
                    print(f"   ✅ Financial System - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Financial System - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Financial System - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Financial System - Exception: {str(e)}")
            print(f"   ❌ Financial System - Exception: {str(e)}")
        
        # Test 2: Admin Dashboard
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/admin/dashboard", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Admin Dashboard - Working perfectly")
                    print(f"   ✅ Admin Dashboard - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Admin Dashboard - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Admin Dashboard - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Admin Dashboard - Exception: {str(e)}")
            print(f"   ❌ Admin Dashboard - Exception: {str(e)}")
        
        # Test 3: Analytics System
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/analytics/overview", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Analytics System - Working perfectly")
                    print(f"   ✅ Analytics System - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Analytics System - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Analytics System - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Analytics System - Exception: {str(e)}")
            print(f"   ❌ Analytics System - Exception: {str(e)}")
        
        # Test 4: Workspace Management
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/workspace/list", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Workspace Management - Working perfectly")
                    print(f"   ✅ Workspace Management - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Workspace Management - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Workspace Management - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Workspace Management - Exception: {str(e)}")
            print(f"   ❌ Workspace Management - Exception: {str(e)}")
        
        return results
    
    async def test_system_health(self) -> Dict[str, Any]:
        """Test general endpoint functionality and error rate"""
        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        
        # Test 1: OpenAPI Specification
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/openapi.json") as response:
                if response.status == 200:
                    data = await response.json()
                    endpoint_count = len(data.get("paths", {}))
                    results["passed"] += 1
                    results["details"].append(f"✅ OpenAPI Specification - {endpoint_count} endpoints available")
                    print(f"   ✅ OpenAPI Specification - {endpoint_count} endpoints available")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ OpenAPI Specification - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ OpenAPI Specification - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ OpenAPI Specification - Exception: {str(e)}")
            print(f"   ❌ OpenAPI Specification - Exception: {str(e)}")
        
        # Test 2: Health Endpoint
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ System Health - Working perfectly")
                    print(f"   ✅ System Health - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ System Health - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ System Health - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ System Health - Exception: {str(e)}")
            print(f"   ❌ System Health - Exception: {str(e)}")
        
        # Test 3: Database Connectivity
        results["total"] += 1
        try:
            async with self.session.get(f"{self.api_url}/database/status") as response:
                if response.status == 200:
                    data = await response.json()
                    results["passed"] += 1
                    results["details"].append("✅ Database Connectivity - Working perfectly")
                    print(f"   ✅ Database Connectivity - Working perfectly ({len(str(data))} chars response)")
                else:
                    results["failed"] += 1
                    error_text = await response.text()
                    results["details"].append(f"❌ Database Connectivity - HTTP {response.status}: {error_text[:100]}")
                    print(f"   ❌ Database Connectivity - HTTP {response.status}: {error_text[:100]}")
        except Exception as e:
            results["failed"] += 1
            results["details"].append(f"❌ Database Connectivity - Exception: {str(e)}")
            print(f"   ❌ Database Connectivity - Exception: {str(e)}")
        
        return results
    
    async def generate_final_report(self):
        """Generate comprehensive final report"""
        overall_success_rate = (self.results["passed_tests"] / self.results["total_tests"] * 100) if self.results["total_tests"] > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BACKEND TESTING - FINAL RESULTS")
        print("=" * 80)
        
        print(f"\n📊 OVERALL PERFORMANCE:")
        print(f"   Total Tests: {self.results['total_tests']}")
        print(f"   Passed Tests: {self.results['passed_tests']}")
        print(f"   Failed Tests: {self.results['failed_tests']}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        
        # Determine overall status
        if overall_success_rate >= 95:
            status = "🏆 PRODUCTION READY - EXCELLENT"
        elif overall_success_rate >= 85:
            status = "✅ GOOD - MINOR IMPROVEMENTS NEEDED"
        elif overall_success_rate >= 70:
            status = "⚠️ NEEDS WORK - SIGNIFICANT ISSUES"
        else:
            status = "❌ CRITICAL ISSUES - NOT PRODUCTION READY"
        
        print(f"   Overall Status: {status}")
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in self.results["test_categories"].items():
            success_rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
            category_status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            print(f"   {category_status} {category}: {success_rate:.1f}% ({results['passed']}/{results['total']})")
        
        # Critical Issues
        if self.results["critical_issues"]:
            print(f"\n🔴 CRITICAL ISSUES IDENTIFIED:")
            for issue in self.results["critical_issues"]:
                print(f"   - {issue}")
        
        # Improvement Assessment
        print(f"\n📈 IMPROVEMENT ASSESSMENT:")
        if overall_success_rate >= 50:
            improvement = overall_success_rate - 50  # Baseline from review request
            print(f"   ✅ Improvement from 50% baseline: +{improvement:.1f} percentage points")
            if overall_success_rate >= 95:
                print(f"   🎯 TARGET ACHIEVED: 95%+ production readiness reached!")
            else:
                print(f"   🎯 TARGET STATUS: {95 - overall_success_rate:.1f} percentage points needed for 95% target")
        else:
            decline = 50 - overall_success_rate
            print(f"   ❌ Decline from 50% baseline: -{decline:.1f} percentage points")
            print(f"   🔧 IMMEDIATE ACTION REQUIRED: System performance below baseline")
        
        # ObjectId Serialization Assessment
        if any("ObjectId serialization" in issue for issue in self.results["critical_issues"]):
            print(f"\n🔧 OBJECTID SERIALIZATION STATUS:")
            print(f"   ❌ ObjectId serialization issues STILL PRESENT")
            print(f"   🔧 'JSON decode error with text/plain response' errors detected")
            print(f"   🔧 ObjectId serialization fixes NOT COMPLETE")
        else:
            print(f"\n✅ OBJECTID SERIALIZATION STATUS:")
            print(f"   ✅ No ObjectId serialization issues detected")
            print(f"   ✅ JSON serialization working properly")
        
        # Production Readiness Assessment
        print(f"\n🏭 PRODUCTION READINESS ASSESSMENT:")
        if overall_success_rate >= 95:
            print(f"   ✅ PRODUCTION READY: Platform meets 95%+ success rate target")
            print(f"   ✅ All critical systems operational")
            print(f"   ✅ Ready for business deployment")
        elif overall_success_rate >= 85:
            print(f"   ⚠️ NEAR PRODUCTION READY: {95 - overall_success_rate:.1f}% improvement needed")
            print(f"   ⚠️ Minor fixes required before deployment")
        else:
            print(f"   ❌ NOT PRODUCTION READY: Major improvements required")
            print(f"   ❌ {95 - overall_success_rate:.1f}% improvement needed for production deployment")
        
        print("\n" + "=" * 80)
        
        # Save results to file
        with open("/app/review_request_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print("📄 Detailed results saved to: /app/review_request_test_results.json")

async def main():
    """Main function to run comprehensive backend testing"""
    tester = ComprehensiveBackendTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())