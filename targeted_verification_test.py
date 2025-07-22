#!/usr/bin/env python3
"""
TARGETED VERIFICATION TEST - CRITICAL SYSTEMS FOCUS
Testing ONLY the systems that showed critical failures in previous tests:
1. Complete Booking System (Previously 12.5% success)
2. Complete Social Media Leads (Previously 50% success) 
3. Complete Subscription Management (Previously 50% success)
4. External API Integration Verification (should maintain 100% success)
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import uuid

# Backend URL from environment
BACKEND_URL = "https://35b0c12d-8622-4a0d-9b9c-d891d48a2c32.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class TargetedVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.booking_results = []
        self.social_media_results = []
        self.subscription_results = []
        self.external_api_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None, category: str = "general"):
        """Log test result with category"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "response_size": len(str(response_data)) if response_data else 0,
            "category": category
        }
        self.test_results.append(result)
        
        # Add to category-specific results
        if category == "booking":
            self.booking_results.append(result)
        elif category == "social_media":
            self.social_media_results.append(result)
        elif category == "subscription":
            self.subscription_results.append(result)
        elif category == "external_api":
            self.external_api_results.append(result)
            
        print(f"{status}: {test_name} - {message}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response size: {len(str(response_data))} chars")
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            print("\n🔐 TESTING AUTHENTICATION...")
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,  # OAuth2PasswordRequestForm expects form data
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    # Set authorization header for future requests
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_result("Authentication", True, f"Login successful - Token received", data)
                    return True
                else:
                    self.log_result("Authentication", False, "Login response missing access_token")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, test_name: str = None, category: str = "general"):
        """Test a specific API endpoint"""
        if not test_name:
            test_name = f"{method} {endpoint}"
            
        try:
            url = f"{API_BASE}{endpoint}"
            
            # Ensure we have authentication headers if we have a token
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                self.log_result(test_name, False, f"Unsupported method: {method}", category=category)
                return False, None
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code}", data, category=category)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code} (non-JSON response)", category=category)
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404) - May not be implemented", category=category)
                return False, None
            elif response.status_code == 401:
                self.log_result(test_name, False, f"Authentication required (401)", category=category)
                return False, None
            elif response.status_code == 403:
                self.log_result(test_name, False, f"Access forbidden (403)", category=category)
                return False, None
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Validation error')
                    self.log_result(test_name, False, f"Validation error (422): {error_msg}", category=category)
                except:
                    self.log_result(test_name, False, f"Validation error (422): {response.text}", category=category)
                return False, None
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Internal server error')
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}", category=category)
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}", category=category)
                return False, None
            else:
                self.log_result(test_name, False, f"Endpoint error - Status {response.status_code}: {response.text}", category=category)
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}", category=category)
            return False, None

    def test_complete_booking_system(self):
        """Test ALL booking endpoints - CRITICAL PRIORITY"""
        print("\n📅 TESTING COMPLETE BOOKING SYSTEM (CRITICAL PRIORITY)...")
        
        # Test service management endpoints (try both path variations)
        self.test_endpoint("/bookings/services", "GET", test_name="Booking - List Services (v1)", category="booking")
        self.test_endpoint("/booking/api/booking/services", "GET", test_name="Booking - List Services (v2)", category="booking")
        
        # Test service creation with realistic data
        service_data = {
            "name": "Business Consultation",
            "description": "Professional business consultation service",
            "duration": 60,
            "price": 150.00,
            "category": "consulting"
        }
        success, response = self.test_endpoint("/bookings/services", "POST", data=service_data, test_name="Booking - Create Service (v1)", category="booking")
        if not success:
            success, response = self.test_endpoint("/booking/api/booking/services", "POST", data=service_data, test_name="Booking - Create Service (v2)", category="booking")
        
        service_id = None
        if success and response:
            service_id = response.get("id") or response.get("service_id")
        
        # Test availability management
        self.test_endpoint("/booking/api/booking/availability", "GET", test_name="Booking - Get Availability", category="booking")
        
        # Test appointments/bookings
        self.test_endpoint("/bookings/appointments", "GET", test_name="Booking - List Appointments (v1)", category="booking")
        self.test_endpoint("/booking/api/booking/appointments", "GET", test_name="Booking - List Appointments (v2)", category="booking")
        
        # Test booking dashboard
        self.test_endpoint("/bookings/dashboard", "GET", test_name="Booking - Dashboard", category="booking")
        
        # Test booking analytics
        self.test_endpoint("/booking/api/booking/analytics", "GET", test_name="Booking - Analytics Overview", category="booking")

    def test_complete_social_media_leads(self):
        """Test ALL social media leads endpoints"""
        print("\n📱 TESTING COMPLETE SOCIAL MEDIA LEADS SYSTEM...")
        
        # Test TikTok discovery - CRITICAL
        tiktok_data = {
            "hashtag": "businesstips",
            "location": "United States",
            "limit": 10
        }
        self.test_endpoint("/social-media-leads/discover/tiktok", "POST", data=tiktok_data, test_name="Social Media - TikTok Discovery", category="social_media")
        
        # Test Twitter discovery - CRITICAL  
        twitter_data = {
            "keywords": "business consulting",
            "location": "New York",
            "limit": 10
        }
        self.test_endpoint("/social-media-leads/discover/twitter", "POST", data=twitter_data, test_name="Social Media - Twitter Discovery", category="social_media")
        
        # Test lead management
        self.test_endpoint("/social-media-leads/leads", "GET", test_name="Social Media - List Leads", category="social_media")
        
        # Test lead creation
        lead_data = {
            "platform": "tiktok",
            "username": "businesspro123",
            "profile_url": "https://tiktok.com/@businesspro123",
            "follower_count": 5000,
            "engagement_rate": 3.5,
            "location": "New York",
            "interests": ["business", "consulting"]
        }
        success, response = self.test_endpoint("/social-media-leads/leads", "POST", data=lead_data, test_name="Social Media - Create Lead", category="social_media")
        
        if success and response:
            lead_id = response.get("id") or response.get("lead_id")
            if lead_id:
                # Test lead details and updates
                self.test_endpoint(f"/social-media-leads/leads/{lead_id}", "GET", test_name="Social Media - Get Lead Details", category="social_media")
                
                update_data = {
                    "status": "contacted",
                    "notes": "Initial contact made via DM"
                }
                self.test_endpoint(f"/social-media-leads/leads/{lead_id}", "PUT", data=update_data, test_name="Social Media - Update Lead", category="social_media")
        
        # Test analytics
        self.test_endpoint("/social-media-leads/analytics", "GET", test_name="Social Media - Analytics Overview", category="social_media")
        self.test_endpoint("/social-media-leads/analytics/platforms", "GET", test_name="Social Media - Platform Analytics", category="social_media")

    def test_complete_subscription_management(self):
        """Test ALL subscription endpoints"""
        print("\n💳 TESTING COMPLETE SUBSCRIPTION MANAGEMENT SYSTEM...")
        
        # Test subscription plans
        self.test_endpoint("/subscriptions/plans", "GET", test_name="Subscriptions - List Plans", category="subscription")
        
        # Test current subscription
        self.test_endpoint("/subscriptions/current", "GET", test_name="Subscriptions - Current Subscription", category="subscription")
        
        # Test subscription creation with realistic data
        subscription_data = {
            "plan_id": "pro_monthly",
            "payment_method_id": "pm_test_card_visa"  # Test payment method
        }
        success, response = self.test_endpoint("/subscriptions/create", "POST", data=subscription_data, test_name="Subscriptions - Create Subscription", category="subscription")
        
        # Test billing history
        self.test_endpoint("/subscriptions/billing-history", "GET", test_name="Subscriptions - Billing History", category="subscription")
        
        # Test subscription management endpoints
        self.test_endpoint("/enhanced-ecommerce/subscription/management", "GET", test_name="Subscriptions - Management Dashboard", category="subscription")

    def test_external_api_integrations(self):
        """Test external API integrations - should maintain 100% success"""
        print("\n🔗 TESTING EXTERNAL API INTEGRATIONS...")
        
        # Test external API integrations using correct admin-config paths
        self.test_endpoint("/admin-config/integrations/tiktok/test", "POST", test_name="External API - TikTok Integration", category="external_api")
        
        # Test Twitter API integration  
        self.test_endpoint("/admin-config/integrations/twitter/test", "POST", test_name="External API - Twitter Integration", category="external_api")
        
        # Test OpenAI integration
        self.test_endpoint("/admin-config/integrations/openai/test", "POST", test_name="External API - OpenAI Integration", category="external_api")
        
        # Test ElasticMail integration
        self.test_endpoint("/admin-config/integrations/elasticmail/test", "POST", test_name="External API - ElasticMail Integration", category="external_api")
        
        # Test Stripe integration
        self.test_endpoint("/admin-config/integrations/stripe/test", "POST", test_name="External API - Stripe Integration", category="external_api")
        
        # Test integration status
        self.test_endpoint("/admin-config/integrations/status", "GET", test_name="External API - Integration Status", category="external_api")

    def calculate_success_rates(self):
        """Calculate success rates for each category"""
        categories = {
            "booking": self.booking_results,
            "social_media": self.social_media_results, 
            "subscription": self.subscription_results,
            "external_api": self.external_api_results
        }
        
        results = {}
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for test in tests if test["success"])
                total = len(tests)
                success_rate = (passed / total) * 100
                results[category] = {
                    "passed": passed,
                    "total": total,
                    "success_rate": success_rate
                }
            else:
                results[category] = {
                    "passed": 0,
                    "total": 0,
                    "success_rate": 0
                }
        
        return results

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 TARGETED VERIFICATION TEST RESULTS")
        print("="*80)
        
        success_rates = self.calculate_success_rates()
        
        print(f"\n📊 OVERALL RESULTS:")
        total_passed = sum(1 for test in self.test_results if test["success"])
        total_tests = len(self.test_results)
        overall_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"   Overall Success Rate: {overall_rate:.1f}% ({total_passed}/{total_tests} tests passed)")
        
        print(f"\n🎯 CRITICAL SYSTEMS RESULTS:")
        
        # Booking System Results
        booking = success_rates["booking"]
        status = "✅ TARGET MET" if booking["success_rate"] >= 75 else "❌ BELOW TARGET"
        print(f"   📅 Complete Booking System: {booking['success_rate']:.1f}% ({booking['passed']}/{booking['total']}) {status}")
        print(f"      Previous: 12.5% → Current: {booking['success_rate']:.1f}% (Target: 75%+)")
        
        # Social Media Results
        social = success_rates["social_media"]
        status = "✅ TARGET MET" if social["success_rate"] >= 80 else "❌ BELOW TARGET"
        print(f"   📱 Complete Social Media Leads: {social['success_rate']:.1f}% ({social['passed']}/{social['total']}) {status}")
        print(f"      Previous: 50% → Current: {social['success_rate']:.1f}% (Target: 80%+)")
        
        # Subscription Results
        subscription = success_rates["subscription"]
        status = "✅ TARGET MET" if subscription["success_rate"] >= 80 else "❌ BELOW TARGET"
        print(f"   💳 Complete Subscription Management: {subscription['success_rate']:.1f}% ({subscription['passed']}/{subscription['total']}) {status}")
        print(f"      Previous: 50% → Current: {subscription['success_rate']:.1f}% (Target: 80%+)")
        
        # External API Results
        external = success_rates["external_api"]
        status = "✅ MAINTAINED" if external["success_rate"] == 100 else "⚠️ DEGRADED"
        print(f"   🔗 External API Integrations: {external['success_rate']:.1f}% ({external['passed']}/{external['total']}) {status}")
        print(f"      Previous: 100% → Current: {external['success_rate']:.1f}% (Target: Maintain 100%)")
        
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        for category, tests in [("booking", self.booking_results), ("social_media", self.social_media_results), 
                               ("subscription", self.subscription_results), ("external_api", self.external_api_results)]:
            if tests:
                print(f"\n   {category.upper().replace('_', ' ')} TESTS:")
                for test in tests:
                    print(f"      {test['status']}: {test['test']} - {test['message']}")
        
        print(f"\n🎯 SUCCESS CRITERIA ASSESSMENT:")
        booking_met = booking["success_rate"] >= 75
        social_met = social["success_rate"] >= 80
        subscription_met = subscription["success_rate"] >= 80
        external_met = external["success_rate"] == 100
        
        criteria_met = sum([booking_met, social_met, subscription_met, external_met])
        print(f"   Criteria Met: {criteria_met}/4")
        print(f"   ✅ Booking System ≥75%: {'YES' if booking_met else 'NO'}")
        print(f"   ✅ Social Media ≥80%: {'YES' if social_met else 'NO'}")
        print(f"   ✅ Subscription ≥80%: {'YES' if subscription_met else 'NO'}")
        print(f"   ✅ External APIs 100%: {'YES' if external_met else 'NO'}")
        
        if criteria_met >= 3:
            print(f"\n🎉 RESULT: TARGETED VERIFICATION SUCCESSFUL - {criteria_met}/4 critical systems meet targets!")
        else:
            print(f"\n⚠️ RESULT: TARGETED VERIFICATION NEEDS IMPROVEMENT - Only {criteria_met}/4 critical systems meet targets")

def main():
    """Main test execution"""
    print("🎯 STARTING TARGETED VERIFICATION TEST")
    print("Focus: Critical systems that showed failures in previous tests")
    print("="*80)
    
    tester = TargetedVerificationTester()
    
    # Test authentication first
    if not tester.test_authentication():
        print("❌ Authentication failed - cannot proceed with tests")
        sys.exit(1)
    
    # Test critical systems
    tester.test_complete_booking_system()
    tester.test_complete_social_media_leads()
    tester.test_complete_subscription_management()
    tester.test_external_api_integrations()
    
    # Print comprehensive summary
    tester.print_summary()
    
    return tester

if __name__ == "__main__":
    tester = main()