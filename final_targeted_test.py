#!/usr/bin/env python3
"""
FINAL TARGETED TEST - REVIEW REQUEST VERIFICATION
Testing specific systems mentioned in the review request to verify fixes and target success rates:

1. Complete Booking System (Target: 75%+ from 44.4%)
2. Complete Subscription Management (Target: 80%+ from 42.9%)
3. Complete Social Media Leads (Maintain: 80%+)
4. External API Integration (Maintain: 100%)

Authentication: tmonnens@outlook.com/Voetballen5
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
import uuid

# Backend URL from environment
BACKEND_URL = "https://77bda007-61bd-44ee-b130-58b448ff1a90.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class FinalTargetedTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.system_results = {
            "booking_system": {"passed": 0, "total": 0},
            "subscription_management": {"passed": 0, "total": 0},
            "social_media_leads": {"passed": 0, "total": 0},
            "external_api_integration": {"passed": 0, "total": 0}
        }
        
    def log_result(self, test_name: str, success: bool, message: str, system: str = None, response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "system": system,
            "response_size": len(str(response_data)) if response_data else 0
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response size: {len(str(response_data))} chars")
            
        # Update system results
        if system and system in self.system_results:
            self.system_results[system]["total"] += 1
            if success:
                self.system_results[system]["passed"] += 1
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            # Test login
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
                    print(f"✅ Authentication successful - Token received")
                    return True
                else:
                    print(f"❌ Authentication failed - No access token in response")
                    return False
            else:
                print(f"❌ Authentication failed - Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, test_name: str = None, system: str = None):
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
                self.log_result(test_name, False, f"Unsupported method: {method}", system)
                return False, None
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Working perfectly - Status {response.status_code}", system, data)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Working perfectly - Status {response.status_code} (non-JSON response)", system)
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404) - Not implemented", system)
                return False, None
            elif response.status_code == 401:
                self.log_result(test_name, False, f"Authentication required (401)", system)
                return False, None
            elif response.status_code == 403:
                self.log_result(test_name, False, f"Access forbidden (403)", system)
                return False, None
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Validation error')
                    self.log_result(test_name, False, f"Validation error (422): {error_msg}", system)
                except:
                    self.log_result(test_name, False, f"Validation error (422): {response.text}", system)
                return False, None
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Internal server error')
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}", system)
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}", system)
                return False, None
            else:
                self.log_result(test_name, False, f"Error - Status {response.status_code}: {response.text}", system)
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}", system)
            return False, None

    def test_booking_system(self):
        """Test Complete Booking System - Target: 75%+ from 44.4%"""
        print("\n📅 TESTING COMPLETE BOOKING SYSTEM")
        print("=" * 60)
        print("Target: 75%+ success rate (up from 44.4%)")
        
        # Test booking services endpoints
        print("\n🔧 Testing Booking Services...")
        self.test_endpoint("/booking/services", "GET", test_name="Booking - Get Services", system="booking_system")
        
        # Test creating a service
        service_data = {
            "name": "Business Consultation",
            "description": "Professional business strategy consultation",
            "duration": 60,
            "price": 150.00,
            "category": "consulting"
        }
        self.test_endpoint("/booking/services", "POST", service_data, "Booking - Create Service", "booking_system")
        
        # Test booking management
        print("\n📋 Testing Booking Management...")
        self.test_endpoint("/booking/bookings", "GET", test_name="Booking - Get Bookings", system="booking_system")
        
        # Test creating a booking
        booking_data = {
            "service_id": "test-service-id",
            "client_name": "John Smith",
            "client_email": "john.smith@email.com",
            "client_phone": "+1-555-0123",
            "appointment_date": "2025-01-15T14:00:00",
            "notes": "Initial business consultation"
        }
        self.test_endpoint("/booking/bookings", "POST", booking_data, "Booking - Create Booking", "booking_system")
        
        # Test booking dashboard
        print("\n📊 Testing Booking Dashboard...")
        self.test_endpoint("/booking/dashboard", "GET", test_name="Booking - Dashboard", system="booking_system")
        
        # Test booking analytics
        print("\n📈 Testing Booking Analytics...")
        self.test_endpoint("/booking/analytics/provider", "GET", test_name="Booking - Provider Analytics", system="booking_system")

    def test_subscription_management(self):
        """Test Complete Subscription Management - Target: 80%+ from 42.9%"""
        print("\n💳 TESTING COMPLETE SUBSCRIPTION MANAGEMENT")
        print("=" * 60)
        print("Target: 80%+ success rate (up from 42.9%)")
        
        # Test subscription plans with both "professional" and "pro" plan tiers
        print("\n📋 Testing Subscription Plans...")
        self.test_endpoint("/subscriptions/plans", "GET", test_name="Subscriptions - Get Plans", system="subscription_management")
        
        # Test creating subscription with "professional" plan tier (with workspace_id)
        print("\n✨ Testing Subscription Creation (professional)...")
        subscription_data_professional = {
            "plan_tier": "professional",
            "payment_method_id": "pm_test_card_visa",
            "billing_cycle": "monthly",
            "workspace_id": "default-workspace-id"
        }
        self.test_endpoint("/subscriptions/subscriptions", "POST", subscription_data_professional, "Subscriptions - Create (professional)", "subscription_management")
        
        # Test creating subscription with "pro" plan tier (should work as alias)
        print("\n✨ Testing Subscription Creation (pro alias)...")
        subscription_data_pro = {
            "plan_tier": "pro",
            "payment_method_id": "pm_test_card_visa",
            "billing_cycle": "monthly",
            "workspace_id": "default-workspace-id"
        }
        self.test_endpoint("/subscriptions/subscriptions", "POST", subscription_data_pro, "Subscriptions - Create (pro)", "subscription_management")
        
        # Test getting subscriptions
        print("\n📋 Testing Subscription Retrieval...")
        self.test_endpoint("/subscriptions/subscriptions", "GET", test_name="Subscriptions - Get Subscriptions", system="subscription_management")
        
        # Test newly added subscription management dashboard
        print("\n📊 Testing Subscription Management Dashboard...")
        self.test_endpoint("/subscriptions/management/dashboard", "GET", test_name="Subscriptions - Management Dashboard", system="subscription_management")
        
        # Test newly added reactivate subscription endpoint
        print("\n🔄 Testing Subscription Reactivation...")
        test_subscription_id = "test-subscription-id"
        self.test_endpoint(f"/subscriptions/subscriptions/{test_subscription_id}/reactivate", "POST", {}, "Subscriptions - Reactivate", "subscription_management")

    def test_social_media_leads(self):
        """Test Complete Social Media Leads - Maintain: 80%+"""
        print("\n📱 TESTING COMPLETE SOCIAL MEDIA LEADS")
        print("=" * 60)
        print("Target: Maintain 80%+ success rate")
        
        # Test TikTok lead discovery with fixed authentication
        print("\n🎵 Testing TikTok Lead Discovery...")
        tiktok_params = {
            "keywords": ["business coaching", "entrepreneur"],
            "location": "United States",
            "limit": 10
        }
        self.test_endpoint("/social-media-leads/discover/tiktok", "POST", tiktok_params, "Social Media - TikTok Discovery", "social_media_leads")
        
        # Test Twitter lead discovery
        print("\n🐦 Testing Twitter Lead Discovery...")
        twitter_params = {
            "keywords": ["startup founder", "business owner"],
            "location": "New York",
            "limit": 10
        }
        self.test_endpoint("/social-media-leads/discover/twitter", "POST", twitter_params, "Social Media - Twitter Discovery", "social_media_leads")
        
        # Test social media analytics
        print("\n📊 Testing Social Media Analytics...")
        self.test_endpoint("/social-media-leads/analytics/overview", "GET", test_name="Social Media - Analytics", system="social_media_leads")

    def test_external_api_integration(self):
        """Test External API Integration - Maintain: 100%"""
        print("\n🔗 TESTING EXTERNAL API INTEGRATION")
        print("=" * 60)
        print("Target: Maintain 100% success rate")
        
        # Test all external API integrations
        print("\n🧪 Testing External API Connections...")
        
        # Test Stripe API
        self.test_endpoint("/admin-config/integrations/stripe/test", "POST", {}, "External API - Stripe Test", "external_api_integration")
        
        # Test OpenAI API
        self.test_endpoint("/admin-config/integrations/openai/test", "POST", {}, "External API - OpenAI Test", "external_api_integration")
        
        # Test ElasticMail API
        self.test_endpoint("/admin-config/integrations/elasticmail/test", "POST", {}, "External API - ElasticMail Test", "external_api_integration")
        
        # Test Twitter API
        self.test_endpoint("/admin-config/integrations/twitter/test", "POST", {}, "External API - Twitter Test", "external_api_integration")
        
        # Test TikTok API (if available)
        self.test_endpoint("/admin-config/integrations/tiktok/test", "POST", {}, "External API - TikTok Test", "external_api_integration")

    def calculate_success_rates(self):
        """Calculate and display success rates for each system"""
        print("\n🎯 FINAL TARGETED TEST RESULTS")
        print("=" * 80)
        
        overall_passed = sum(result["success"] for result in self.test_results)
        overall_total = len(self.test_results)
        overall_rate = (overall_passed / overall_total * 100) if overall_total > 0 else 0
        
        print(f"\n📊 OVERALL SUCCESS RATE: {overall_rate:.1f}% ({overall_passed}/{overall_total} tests passed)")
        
        print(f"\n🎯 SYSTEM-SPECIFIC RESULTS:")
        
        # Booking System
        booking_passed = self.system_results["booking_system"]["passed"]
        booking_total = self.system_results["booking_system"]["total"]
        booking_rate = (booking_passed / booking_total * 100) if booking_total > 0 else 0
        booking_status = "✅ TARGET MET" if booking_rate >= 75 else "❌ BELOW TARGET"
        print(f"📅 Complete Booking System: {booking_rate:.1f}% ({booking_passed}/{booking_total}) - {booking_status} (Target: 75%+)")
        
        # Subscription Management
        sub_passed = self.system_results["subscription_management"]["passed"]
        sub_total = self.system_results["subscription_management"]["total"]
        sub_rate = (sub_passed / sub_total * 100) if sub_total > 0 else 0
        sub_status = "✅ TARGET MET" if sub_rate >= 80 else "❌ BELOW TARGET"
        print(f"💳 Complete Subscription Management: {sub_rate:.1f}% ({sub_passed}/{sub_total}) - {sub_status} (Target: 80%+)")
        
        # Social Media Leads
        social_passed = self.system_results["social_media_leads"]["passed"]
        social_total = self.system_results["social_media_leads"]["total"]
        social_rate = (social_passed / social_total * 100) if social_total > 0 else 0
        social_status = "✅ TARGET MET" if social_rate >= 80 else "❌ BELOW TARGET"
        print(f"📱 Complete Social Media Leads: {social_rate:.1f}% ({social_passed}/{social_total}) - {social_status} (Target: 80%+)")
        
        # External API Integration
        api_passed = self.system_results["external_api_integration"]["passed"]
        api_total = self.system_results["external_api_integration"]["total"]
        api_rate = (api_passed / api_total * 100) if api_total > 0 else 0
        api_status = "✅ TARGET MET" if api_rate >= 100 else "❌ BELOW TARGET"
        print(f"🔗 External API Integration: {api_rate:.1f}% ({api_passed}/{api_total}) - {api_status} (Target: 100%)")
        
        # Summary
        targets_met = sum([
            booking_rate >= 75,
            sub_rate >= 80,
            social_rate >= 80,
            api_rate >= 100
        ])
        
        print(f"\n🏆 TARGETS ACHIEVED: {targets_met}/4 systems meet their target success rates")
        
        if targets_met == 4:
            print("🎉 ALL TARGETS ACHIEVED! Platform is production ready.")
        else:
            print("⚠️  Some targets not met. Additional fixes needed.")
            
        return {
            "overall": {"rate": overall_rate, "passed": overall_passed, "total": overall_total},
            "booking_system": {"rate": booking_rate, "passed": booking_passed, "total": booking_total, "target_met": booking_rate >= 75},
            "subscription_management": {"rate": sub_rate, "passed": sub_passed, "total": sub_total, "target_met": sub_rate >= 80},
            "social_media_leads": {"rate": social_rate, "passed": social_passed, "total": social_total, "target_met": social_rate >= 80},
            "external_api_integration": {"rate": api_rate, "passed": api_passed, "total": api_total, "target_met": api_rate >= 100},
            "targets_met": targets_met
        }

    def run_final_targeted_test(self):
        """Run the complete final targeted test"""
        print("🎯 FINAL TARGETED TEST - REVIEW REQUEST VERIFICATION")
        print("=" * 80)
        print("Testing specific systems to verify fixes and target success rates:")
        print("1. Complete Booking System (Target: 75%+ from 44.4%)")
        print("2. Complete Subscription Management (Target: 80%+ from 42.9%)")
        print("3. Complete Social Media Leads (Maintain: 80%+)")
        print("4. External API Integration (Maintain: 100%)")
        print(f"Authentication: {TEST_EMAIL}/{TEST_PASSWORD}")
        print("=" * 80)
        
        # Test authentication first
        if not self.test_authentication():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all targeted tests
        self.test_booking_system()
        self.test_subscription_management()
        self.test_social_media_leads()
        self.test_external_api_integration()
        
        # Calculate and display results
        results = self.calculate_success_rates()
        
        return results

def main():
    """Main function to run the final targeted test"""
    tester = FinalTargetedTester()
    results = tester.run_final_targeted_test()
    
    # Exit with appropriate code
    if results["targets_met"] == 4:
        print("\n✅ All targets achieved! Exiting with success code.")
        sys.exit(0)
    else:
        print(f"\n⚠️  Only {results['targets_met']}/4 targets achieved. Exiting with warning code.")
        sys.exit(1)

if __name__ == "__main__":
    main()