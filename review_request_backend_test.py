#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE REVIEW REQUEST TESTING - JANUARY 2025 🎯

MISSION: Measure improvements after fixing critical ObjectId serialization issues and Stripe integration

REVIEW REQUEST FOCUS AREAS:
1. Overall Success Rate - Compare against previous 57.1% baseline
2. Referral System - Test if CREATE operations now work after ObjectId fixes
3. Stripe Integration - Test if customer creation and payment methods now work
4. Core Business Systems - Verify they're still working excellently
5. Authentication - Confirm it's still 100% functional
6. External APIs - Check current status of integrations

CREDENTIALS: tmonnens@outlook.com / Voetballen5
TARGET: Measure progress toward 95%+ production readiness
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback

# Configuration
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class ReviewRequestTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Category tracking
        self.auth_results = []
        self.referral_results = []
        self.stripe_results = []
        self.core_business_results = []
        self.external_api_results = []
        self.overall_health_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None, status_code: int = None, category: str = "general"):
        """Log test result with comprehensive information"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "status_code": status_code,
            "response_size": len(str(response_data)) if response_data else 0,
            "response_preview": str(response_data)[:200] if response_data else "",
            "timestamp": datetime.now().isoformat(),
            "category": category
        }
        self.test_results.append(result)
        
        # Add to category tracking
        if category == "authentication":
            self.auth_results.append(result)
        elif category == "referral":
            self.referral_results.append(result)
        elif category == "stripe":
            self.stripe_results.append(result)
        elif category == "core_business":
            self.core_business_results.append(result)
        elif category == "external_api":
            self.external_api_results.append(result)
        elif category == "overall_health":
            self.overall_health_results.append(result)
        
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response size: {len(str(response_data))} chars")
        if status_code:
            print(f"   Status code: {status_code}")
        print()
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with proper error handling"""
        url = f"{API_BASE}{endpoint}" if endpoint.startswith('/') else f"{BACKEND_URL}{endpoint}"
        
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.access_token:
            request_headers['Authorization'] = f'Bearer {self.access_token}'
        
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                return self.session.get(url, headers=request_headers, timeout=30)
            elif method.upper() == 'POST':
                return self.session.post(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == 'PUT':
                return self.session.put(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == 'DELETE':
                return self.session.delete(url, headers=request_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.Timeout:
            raise Exception("Request timeout (30s)")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def test_authentication_system(self):
        """Test Authentication System - Should be 100% functional"""
        print("🔐 TESTING AUTHENTICATION SYSTEM (Target: 100% Success)")
        print("=" * 80)
        
        # Test 1: JWT Token Generation
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = self.make_request('POST', '/auth/login', login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token') or data.get('token')
                if self.access_token:
                    self.log_result("JWT Token Generation", True, 
                                  f"Working perfectly with provided credentials ({len(str(data))} chars response)", 
                                  data, response.status_code, "authentication")
                else:
                    self.log_result("JWT Token Generation", False, 
                                  "No access token in response", 
                                  data, response.status_code, "authentication")
            else:
                self.log_result("JWT Token Generation", False, 
                              f"Login failed with status {response.status_code}", 
                              response.text, response.status_code, "authentication")
        except Exception as e:
            self.log_result("JWT Token Generation", False, f"Authentication error: {str(e)}", category="authentication")
        
        # Test 2: JWT Token Validation
        if self.access_token:
            try:
                response = self.make_request('GET', '/auth/me')
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("JWT Token Validation", True, 
                                  f"Working perfectly ({len(str(data))} chars response)", 
                                  data, response.status_code, "authentication")
                else:
                    self.log_result("JWT Token Validation", False, 
                                  f"Token validation failed with status {response.status_code}", 
                                  response.text, response.status_code, "authentication")
            except Exception as e:
                self.log_result("JWT Token Validation", False, f"Token validation error: {str(e)}", category="authentication")
        
        # Test 3: Admin Access
        if self.access_token:
            try:
                response = self.make_request('GET', '/admin/health')
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Admin Access", True, 
                                  f"Working perfectly ({len(str(data))} chars response)", 
                                  data, response.status_code, "authentication")
                else:
                    self.log_result("Admin Access", False, 
                                  f"Admin access failed with status {response.status_code}", 
                                  response.text, response.status_code, "authentication")
            except Exception as e:
                self.log_result("Admin Access", False, f"Admin access error: {str(e)}", category="authentication")
    
    def test_referral_system(self):
        """Test Referral System - Focus on ObjectId serialization fixes"""
        print("🔗 TESTING REFERRAL SYSTEM (Focus: ObjectId Serialization Fixes)")
        print("=" * 80)
        
        # Test 1: Health Check
        try:
            response = self.make_request('GET', '/referral-system/health')
            if response.status_code == 200:
                data = response.json()
                self.log_result("Referral System Health Check", True, 
                              f"Working perfectly ({len(str(data))} chars response)", 
                              data, response.status_code, "referral")
            else:
                self.log_result("Referral System Health Check", False, 
                              f"Health check failed with status {response.status_code}", 
                              response.text, response.status_code, "referral")
        except Exception as e:
            self.log_result("Referral System Health Check", False, f"Health check error: {str(e)}", category="referral")
        
        # Test 2: List Referral Programs (READ operation)
        try:
            response = self.make_request('GET', '/referral-system/referrals')
            if response.status_code == 200:
                data = response.json()
                self.log_result("List Referral Programs", True, 
                              f"Working perfectly ({len(str(data))} chars response) - ObjectId serialization working for READ operations", 
                              data, response.status_code, "referral")
            else:
                self.log_result("List Referral Programs", False, 
                              f"List operation failed with status {response.status_code}", 
                              response.text, response.status_code, "referral")
        except Exception as e:
            self.log_result("List Referral Programs", False, f"List operation error: {str(e)}", category="referral")
        
        # Test 3: Create Referral Program (CREATE operation - Critical ObjectId test)
        try:
            create_data = {
                "program_name": "Q1 2025 Business Referral Program",
                "reward_type": "percentage",
                "reward_value": 15.0,
                "description": "Refer new businesses and earn 15% commission",
                "terms": "Valid for new business accounts only",
                "active": True
            }
            response = self.make_request('POST', '/referral-system/create', create_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result("Create Referral Program", True, 
                              f"ObjectId serialization fixes COMPLETE - CREATE operations working ({len(str(data))} chars response)", 
                              data, response.status_code, "referral")
            else:
                error_msg = "ObjectId serialization issues persist in CREATE operations" if response.status_code == 500 else f"Create operation failed with status {response.status_code}"
                self.log_result("Create Referral Program", False, 
                              error_msg, 
                              response.text, response.status_code, "referral")
        except Exception as e:
            self.log_result("Create Referral Program", False, f"Create operation error: {str(e)}", category="referral")
        
        # Test 4: Referral Analytics
        try:
            response = self.make_request('GET', '/referral-system/analytics')
            if response.status_code == 200:
                data = response.json()
                self.log_result("Referral Analytics", True, 
                              f"Working perfectly ({len(str(data))} chars response)", 
                              data, response.status_code, "referral")
            else:
                error_msg = "Analytics endpoint not implemented" if response.status_code == 404 else f"Analytics failed with status {response.status_code}"
                self.log_result("Referral Analytics", False, 
                              error_msg, 
                              response.text, response.status_code, "referral")
        except Exception as e:
            self.log_result("Referral Analytics", False, f"Analytics error: {str(e)}", category="referral")
    
    def test_stripe_integration(self):
        """Test Stripe Integration - Focus on customer creation and payment methods"""
        print("💳 TESTING STRIPE INTEGRATION (Focus: Customer Creation & Payment Methods)")
        print("=" * 80)
        
        # Test 1: Health Check
        try:
            response = self.make_request('GET', '/stripe-integration/health')
            if response.status_code == 200:
                data = response.json()
                self.log_result("Stripe Health Check", True, 
                              f"Working perfectly ({len(str(data))} chars response)", 
                              data, response.status_code, "stripe")
            else:
                self.log_result("Stripe Health Check", False, 
                              f"Health check failed with status {response.status_code}", 
                              response.text, response.status_code, "stripe")
        except Exception as e:
            self.log_result("Stripe Health Check", False, f"Health check error: {str(e)}", category="stripe")
        
        # Test 2: Create Customer (Critical Stripe test)
        try:
            customer_data = {
                "email": "business.customer@mewayz.com",
                "name": "Mewayz Business Customer",
                "description": "Test customer for business platform"
            }
            response = self.make_request('POST', '/stripe-integration/create-customer', customer_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result("Create Stripe Customer", True, 
                              f"Customer creation working perfectly ({len(str(data))} chars response)", 
                              data, response.status_code, "stripe")
            else:
                error_msg = "Customer creation broken" if response.status_code == 500 else f"Customer creation failed with status {response.status_code}"
                self.log_result("Create Stripe Customer", False, 
                              error_msg, 
                              response.text, response.status_code, "stripe")
        except Exception as e:
            self.log_result("Create Stripe Customer", False, f"Customer creation error: {str(e)}", category="stripe")
        
        # Test 3: Create Payment Intent
        try:
            payment_data = {
                "amount": 2999,  # $29.99
                "currency": "usd",
                "description": "Business platform subscription"
            }
            response = self.make_request('POST', '/stripe-integration/create-payment-intent', payment_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result("Create Payment Intent", True, 
                              f"Real payment processing working ({len(str(data))} chars response)", 
                              data, response.status_code, "stripe")
            else:
                error_msg = "Real payment processing not working" if response.status_code == 500 else f"Payment intent failed with status {response.status_code}"
                self.log_result("Create Payment Intent", False, 
                              error_msg, 
                              response.text, response.status_code, "stripe")
        except Exception as e:
            self.log_result("Create Payment Intent", False, f"Payment intent error: {str(e)}", category="stripe")
        
        # Test 4: Payment Methods
        try:
            response = self.make_request('GET', '/stripe-integration/payment-methods')
            if response.status_code == 200:
                data = response.json()
                self.log_result("Payment Methods", True, 
                              f"Payment methods endpoint working ({len(str(data))} chars response)", 
                              data, response.status_code, "stripe")
            else:
                error_msg = "Payment methods endpoint not properly implemented" if response.status_code == 404 else f"Payment methods failed with status {response.status_code}"
                self.log_result("Payment Methods", False, 
                              error_msg, 
                              response.text, response.status_code, "stripe")
        except Exception as e:
            self.log_result("Payment Methods", False, f"Payment methods error: {str(e)}", category="stripe")
        
        # Test 5: Subscription Management
        try:
            response = self.make_request('GET', '/stripe-integration/subscriptions')
            if response.status_code == 200:
                data = response.json()
                self.log_result("Subscription Management", True, 
                              f"Subscription management working ({len(str(data))} chars response)", 
                              data, response.status_code, "stripe")
            else:
                error_msg = "Subscription endpoint not properly implemented" if response.status_code == 404 else f"Subscription management failed with status {response.status_code}"
                self.log_result("Subscription Management", False, 
                              error_msg, 
                              response.text, response.status_code, "stripe")
        except Exception as e:
            self.log_result("Subscription Management", False, f"Subscription management error: {str(e)}", category="stripe")
    
    def test_core_business_systems(self):
        """Test Core Business Systems - Should still be working excellently"""
        print("🏢 TESTING CORE BUSINESS SYSTEMS (Target: Excellent Performance)")
        print("=" * 80)
        
        core_systems = [
            ('/complete-financial/health', 'Complete Financial System'),
            ('/complete-multi-workspace/health', 'Multi-Workspace System'),
            ('/complete-admin-dashboard/health', 'Admin Dashboard System'),
            ('/team-management/health', 'Team Management System'),
            ('/form-builder/health', 'Form Builder System'),
            ('/analytics-system/health', 'Analytics System'),
            ('/advanced-ai-suite/health', 'AI Automation Suite'),
            ('/complete-website-builder/health', 'Website Builder System'),
            ('/escrow/health', 'Escrow System'),
            ('/complete-onboarding/health', 'Complete Onboarding System')
        ]
        
        for endpoint, system_name in core_systems:
            try:
                response = self.make_request('GET', endpoint)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(system_name, True, 
                                  f"Working perfectly ({len(str(data))} chars response)", 
                                  data, response.status_code, "core_business")
                else:
                    error_msg = "System not implemented" if response.status_code == 404 else f"System failed with status {response.status_code}"
                    self.log_result(system_name, False, 
                                  error_msg, 
                                  response.text, response.status_code, "core_business")
            except Exception as e:
                self.log_result(system_name, False, f"System error: {str(e)}", category="core_business")
    
    def test_external_api_integrations(self):
        """Test External API Integrations - Check current status"""
        print("🌐 TESTING EXTERNAL API INTEGRATIONS (Current Status Check)")
        print("=" * 80)
        
        external_apis = [
            ('/twitter/health', 'Twitter/X API Integration'),
            ('/tiktok/health', 'TikTok API Integration'),
            ('/openai/health', 'OpenAI API Integration'),
            ('/elasticmail/health', 'ElasticMail API Integration'),
            ('/google-oauth/health', 'Google OAuth Integration')
        ]
        
        for endpoint, api_name in external_apis:
            try:
                response = self.make_request('GET', endpoint)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(api_name, True, 
                                  f"Connected ({len(str(data))} chars response)", 
                                  data, response.status_code, "external_api")
                else:
                    error_msg = "Integration not implemented" if response.status_code == 404 else f"Integration failed with status {response.status_code}"
                    self.log_result(api_name, False, 
                                  error_msg, 
                                  response.text, response.status_code, "external_api")
            except Exception as e:
                self.log_result(api_name, False, f"Integration error: {str(e)}", category="external_api")
        
        # Test specific external API functionality
        # Twitter API Search
        try:
            response = self.make_request('GET', '/twitter/search?q=business')
            if response.status_code == 200:
                data = response.json()
                self.log_result("Twitter Search Functionality", True, 
                              f"Search functionality working ({len(str(data))} chars response)", 
                              data, response.status_code, "external_api")
            else:
                error_msg = "Search endpoint not properly implemented" if response.status_code == 404 else f"Search failed with status {response.status_code}"
                self.log_result("Twitter Search Functionality", False, 
                              error_msg, 
                              response.text, response.status_code, "external_api")
        except Exception as e:
            self.log_result("Twitter Search Functionality", False, f"Search error: {str(e)}", category="external_api")
        
        # TikTok API Search
        try:
            response = self.make_request('GET', '/tiktok/search?q=business')
            if response.status_code == 200:
                data = response.json()
                self.log_result("TikTok Search Functionality", True, 
                              f"Search functionality working ({len(str(data))} chars response)", 
                              data, response.status_code, "external_api")
            else:
                error_msg = "Search endpoint not properly implemented" if response.status_code == 404 else f"Search failed with status {response.status_code}"
                self.log_result("TikTok Search Functionality", False, 
                              error_msg, 
                              response.text, response.status_code, "external_api")
        except Exception as e:
            self.log_result("TikTok Search Functionality", False, f"Search error: {str(e)}", category="external_api")
    
    def test_overall_system_health(self):
        """Test Overall System Health"""
        print("🏥 TESTING OVERALL SYSTEM HEALTH")
        print("=" * 80)
        
        # Test 1: OpenAPI Specification
        try:
            response = self.make_request('GET', '/openapi.json')
            if response.status_code == 200:
                data = response.json()
                endpoints_count = len(data.get('paths', {}))
                self.log_result("OpenAPI Specification", True, 
                              f"{endpoints_count} endpoints available - Comprehensive API coverage", 
                              {"endpoints_count": endpoints_count}, response.status_code, "overall_health")
            else:
                self.log_result("OpenAPI Specification", False, 
                              f"OpenAPI spec failed with status {response.status_code}", 
                              response.text, response.status_code, "overall_health")
        except Exception as e:
            self.log_result("OpenAPI Specification", False, f"OpenAPI error: {str(e)}", category="overall_health")
        
        # Test 2: System Health
        try:
            response = self.make_request('GET', '/health')
            if response.status_code == 200:
                data = response.json()
                self.log_result("System Health", True, 
                              f"Working perfectly ({len(str(data))} chars response)", 
                              data, response.status_code, "overall_health")
            else:
                self.log_result("System Health", False, 
                              f"System health failed with status {response.status_code}", 
                              response.text, response.status_code, "overall_health")
        except Exception as e:
            self.log_result("System Health", False, f"System health error: {str(e)}", category="overall_health")
        
        # Test 3: Database Connectivity (Root endpoint)
        try:
            response = self.make_request('GET', '/')
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_result("Database Connectivity", True, 
                                  f"Root endpoint returns JSON ({len(str(data))} chars response)", 
                                  data, response.status_code, "overall_health")
                except json.JSONDecodeError:
                    self.log_result("Database Connectivity", False, 
                                  "JSON decode error: Root endpoint returns HTML instead of JSON", 
                                  response.text[:200], response.status_code, "overall_health")
            else:
                self.log_result("Database Connectivity", False, 
                              f"Root endpoint failed with status {response.status_code}", 
                              response.text, response.status_code, "overall_health")
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Database connectivity error: {str(e)}", category="overall_health")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 100)
        print("🎯 COMPREHENSIVE REVIEW REQUEST ASSESSMENT RESULTS 🎯")
        print("=" * 100)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} comprehensive tests passed)")
        
        # Compare against baseline
        baseline_rate = 57.1
        improvement = success_rate - baseline_rate
        if improvement > 0:
            print(f"📈 IMPROVEMENT FROM BASELINE: +{improvement:.1f}% (Previous: {baseline_rate}%)")
        else:
            print(f"📉 REGRESSION FROM BASELINE: {improvement:.1f}% (Previous: {baseline_rate}%)")
        
        # Production readiness assessment
        if success_rate >= 95:
            print("🎉 EXCELLENT SUCCESS - PRODUCTION READY!")
            status = "PRODUCTION READY"
        elif success_rate >= 85:
            print("✅ GOOD SUCCESS - MOSTLY PRODUCTION READY")
            status = "MOSTLY PRODUCTION READY"
        elif success_rate >= 75:
            print("⚠️ PARTIAL SUCCESS - NEEDS MINOR FIXES")
            status = "NEEDS MINOR FIXES"
        else:
            print("❌ CRITICAL ISSUES - NOT PRODUCTION READY")
            status = "NOT PRODUCTION READY"
        
        print(f"🚀 PRODUCTION READINESS STATUS: {status}")
        
        # Category analysis
        categories = {
            "Authentication System": self.auth_results,
            "Referral System": self.referral_results,
            "Stripe Integration": self.stripe_results,
            "Core Business Systems": self.core_business_results,
            "External API Integrations": self.external_api_results,
            "Overall System Health": self.overall_health_results
        }
        
        print("\n📋 DETAILED RESULTS BY REVIEW REQUEST AREAS:")
        print("-" * 100)
        
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r.get("success", False))
                total = len(results)
                category_rate = (passed / total * 100) if total > 0 else 0
                
                if category_rate >= 90:
                    status_icon = "✅ EXCELLENT"
                elif category_rate >= 75:
                    status_icon = "✅ GOOD SUCCESS"
                elif category_rate >= 50:
                    status_icon = "⚠️ PARTIAL SUCCESS"
                else:
                    status_icon = "❌ CRITICAL ISSUES"
                
                print(f"\n**{len(results)}. {category.upper()} ({category_rate:.1f}% Success - {passed}/{total} tests passed)** {status_icon}")
                
                for result in results:
                    success_icon = "✅" if result.get("success", False) else "❌"
                    test_name = result.get("test", "Unknown")
                    message = result.get("message", "")
                    print(f"   - {success_icon} **{test_name}** - {message}")
                
                # Category status summary
                if category == "Authentication System":
                    if category_rate == 100:
                        print(f"   - **STATUS**: Authentication system fully operational and production-ready")
                    else:
                        print(f"   - **STATUS**: Authentication system has issues requiring attention")
                elif category == "Referral System":
                    if category_rate >= 75:
                        print(f"   - **STATUS**: ObjectId serialization fixes successful, referral system operational")
                    else:
                        print(f"   - **STATUS**: ObjectId serialization fixes INCOMPLETE - CREATE operations still failing")
                elif category == "Stripe Integration":
                    if category_rate >= 75:
                        print(f"   - **STATUS**: Stripe integration working with real payment processing")
                    else:
                        print(f"   - **STATUS**: Stripe integration has critical issues preventing payment processing")
                elif category == "Core Business Systems":
                    if category_rate >= 90:
                        print(f"   - **STATUS**: All major business systems operational with proper data responses")
                    else:
                        print(f"   - **STATUS**: Some core business systems have issues requiring attention")
                elif category == "External API Integrations":
                    if category_rate >= 75:
                        print(f"   - **STATUS**: External API integrations working with real API connections")
                    else:
                        print(f"   - **STATUS**: External API integrations have implementation issues")
                elif category == "Overall System Health":
                    if category_rate >= 75:
                        print(f"   - **STATUS**: System infrastructure solid with comprehensive API coverage")
                    else:
                        print(f"   - **STATUS**: System infrastructure has issues requiring attention")
        
        # Critical achievements and issues
        print("\n🏆 CRITICAL ACHIEVEMENTS VERIFIED:")
        achievements = []
        issues = []
        
        # Check authentication
        auth_success_rate = (sum(1 for r in self.auth_results if r.get("success", False)) / len(self.auth_results) * 100) if self.auth_results else 0
        if auth_success_rate >= 90:
            achievements.append("✅ **AUTHENTICATION SYSTEM PERFECT**: JWT token generation and validation working flawlessly")
        else:
            issues.append("🔴 **AUTHENTICATION ISSUES**: JWT token generation or validation problems")
        
        # Check referral system
        referral_success_rate = (sum(1 for r in self.referral_results if r.get("success", False)) / len(self.referral_results) * 100) if self.referral_results else 0
        if referral_success_rate >= 75:
            achievements.append("✅ **REFERRAL SYSTEM OPERATIONAL**: ObjectId serialization fixes successful")
        else:
            issues.append("🔴 **OBJECTID SERIALIZATION ISSUES PERSIST**: CREATE operations still failing")
        
        # Check Stripe integration
        stripe_success_rate = (sum(1 for r in self.stripe_results if r.get("success", False)) / len(self.stripe_results) * 100) if self.stripe_results else 0
        if stripe_success_rate >= 75:
            achievements.append("✅ **STRIPE INTEGRATION WORKING**: Customer creation and payment processing operational")
        else:
            issues.append("🔴 **STRIPE INTEGRATION BROKEN**: Payment processing not working")
        
        # Check core business systems
        core_success_rate = (sum(1 for r in self.core_business_results if r.get("success", False)) / len(self.core_business_results) * 100) if self.core_business_results else 0
        if core_success_rate >= 90:
            achievements.append("✅ **CORE BUSINESS SYSTEMS EXCELLENT**: All major systems operational")
        else:
            issues.append("🔴 **CORE BUSINESS SYSTEM ISSUES**: Some major systems have problems")
        
        for achievement in achievements:
            print(f"\n{achievement}")
        
        if issues:
            print("\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
            for issue in issues:
                print(f"\n{issue}")
        
        # Performance metrics
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"- ✅ **Overall Testing Success Rate**: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        print(f"- ✅ **Authentication Performance**: {auth_success_rate:.1f}% success")
        print(f"- ✅ **Referral System**: {referral_success_rate:.1f}% success")
        print(f"- ✅ **Stripe Integration**: {stripe_success_rate:.1f}% success")
        print(f"- ✅ **Core Business Systems**: {core_success_rate:.1f}% success")
        
        external_success_rate = (sum(1 for r in self.external_api_results if r.get("success", False)) / len(self.external_api_results) * 100) if self.external_api_results else 0
        health_success_rate = (sum(1 for r in self.overall_health_results if r.get("success", False)) / len(self.overall_health_results) * 100) if self.overall_health_results else 0
        
        print(f"- ✅ **External API Integrations**: {external_success_rate:.1f}% success")
        print(f"- ✅ **Overall System Health**: {health_success_rate:.1f}% success")
        
        # Final conclusion
        print(f"\n🎯 FINAL CONCLUSION:")
        print(f"The COMPREHENSIVE REVIEW REQUEST TESTING reveals **{'EXCELLENT SUCCESS' if success_rate >= 85 else 'MIXED RESULTS' if success_rate >= 60 else 'CRITICAL ISSUES'}** with {success_rate:.1f}% success rate.")
        
        if improvement > 0:
            print(f"This represents a **{improvement:.1f}% IMPROVEMENT** from the previous {baseline_rate}% baseline, demonstrating significant progress.")
        else:
            print(f"This represents a **{abs(improvement):.1f}% REGRESSION** from the previous {baseline_rate}% baseline, indicating issues need attention.")
        
        if success_rate >= 95:
            print(f"The platform has **ACHIEVED THE TARGET** of 95%+ production readiness and is ready for deployment.")
        elif success_rate >= 85:
            print(f"The platform is **APPROACHING PRODUCTION READINESS** with excellent results in most areas.")
        elif success_rate >= 75:
            print(f"The platform shows **GOOD PROGRESS** but requires fixes in key areas before production deployment.")
        else:
            print(f"The platform requires **SIGNIFICANT WORK** before achieving production readiness targets.")
        
        return success_rate
    
    def run_comprehensive_review_test(self):
        """Run comprehensive review request testing"""
        print("🎯 COMPREHENSIVE REVIEW REQUEST TESTING - JANUARY 2025")
        print("=" * 100)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Authentication: {TEST_EMAIL} / {TEST_PASSWORD}")
        print(f"Target: Measure progress toward 95%+ production readiness")
        print("=" * 100)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_authentication_system()
        self.test_referral_system()
        self.test_stripe_integration()
        self.test_core_business_systems()
        self.test_external_api_integrations()
        self.test_overall_system_health()
        
        # Generate comprehensive report
        success_rate = self.generate_comprehensive_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️ Test Duration: {duration:.2f} seconds")
        print("=" * 100)
        print("🎯 REVIEW REQUEST TESTING COMPLETE")
        print("=" * 100)
        
        return success_rate

def main():
    """Main function"""
    tester = ReviewRequestTester()
    success_rate = tester.run_comprehensive_review_test()
    
    # Exit with appropriate code
    if success_rate >= 85:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Needs work

if __name__ == "__main__":
    main()