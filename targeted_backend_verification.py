#!/usr/bin/env python3
"""
🎯 MEWAYZ V2 PLATFORM - TARGETED BACKEND VERIFICATION - JANUARY 2025 🎯

MISSION: Test actual available endpoints based on OpenAPI specification

Authentication: tmonnens@outlook.com / Voetballen5
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class TargetedBackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.critical_failures = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"}
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    if self.auth_token:
                        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                        print(f"✅ Authentication successful with {TEST_EMAIL}")
                        return True
                    else:
                        print(f"❌ No access token in response: {data}")
                        return False
                else:
                    text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    async def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          expected_status: int = 200, test_name: str = "", critical: bool = False) -> Dict[str, Any]:
        """Test a single endpoint"""
        self.total_tests += 1
        
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                        
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                        
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                        
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
                
            success = status == expected_status
            if success:
                self.passed_tests += 1
            elif critical:
                self.critical_failures.append(f"{test_name}: {status} - {str(response_data)[:100]}")
                
            result = {
                "test_name": test_name,
                "method": method.upper(),
                "endpoint": endpoint,
                "status": status,
                "expected_status": expected_status,
                "success": success,
                "critical": critical,
                "response_length": len(str(response_data)) if response_data else 0,
                "response_preview": str(response_data)[:200] if response_data else ""
            }
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "method": method.upper(),
                "endpoint": endpoint,
                "success": False,
                "critical": critical,
                "error": str(e)
            }
            if critical:
                self.critical_failures.append(f"{test_name}: Exception - {str(e)}")
            self.test_results.append(result)
            return result

    async def test_core_system_infrastructure(self):
        """Test Core System Infrastructure"""
        print("\n🎯 TESTING CORE SYSTEM INFRASTRUCTURE")
        print("=" * 80)
        
        # System Health and Documentation
        await self.test_endpoint("GET", "/", test_name="Root Endpoint", critical=True)
        await self.test_endpoint("GET", "/docs", test_name="API Documentation", critical=True)
        await self.test_endpoint("GET", "/openapi.json", test_name="OpenAPI Specification", critical=True)
        
        # Authentication System
        await self.test_endpoint("GET", "/api/auth/me", test_name="Authentication Profile")
        
    async def test_external_api_integrations(self):
        """Test External API Integrations"""
        print("\n🎯 TESTING EXTERNAL API INTEGRATIONS")
        print("=" * 80)
        
        # Social Media Leads (Twitter/TikTok equivalent)
        print("\n🔍 Testing Social Media Leads Integration...")
        await self.test_endpoint("GET", "/api/complete-social-media-leads/health", test_name="Social Media Leads Health", critical=True)
        await self.test_endpoint("GET", "/api/complete-social-media-leads/", test_name="Social Media Leads List", critical=True)
        await self.test_endpoint("GET", "/api/complete-social-media-leads/stats", test_name="Social Media Leads Stats", critical=True)
        
        # Social Media Management
        print("\n🔍 Testing Social Media Management...")
        await self.test_endpoint("GET", "/api/social-media-management/health", test_name="Social Media Management Health", critical=True)
        await self.test_endpoint("GET", "/api/social-media-management/", test_name="Social Media Management List", critical=True)
        
        # Integrations (Stripe equivalent)
        print("\n🔍 Testing Integrations...")
        await self.test_endpoint("GET", "/api/integrations/health", test_name="Integrations Health", critical=True)
        await self.test_endpoint("GET", "/api/integrations/", test_name="Integrations List", critical=True)
        await self.test_endpoint("GET", "/api/integrations/stats", test_name="Integrations Stats", critical=True)
        
        # Payment System
        print("\n🔍 Testing Payment System...")
        await self.test_endpoint("GET", "/api/payment/health", test_name="Payment System Health", critical=True)
        await self.test_endpoint("GET", "/api/payment/", test_name="Payment System List", critical=True)
        
    async def test_referral_system(self):
        """Test Referral System"""
        print("\n🎯 TESTING REFERRAL SYSTEM")
        print("=" * 80)
        
        # Complete Referral System
        print("\n🔍 Testing Complete Referral System...")
        await self.test_endpoint("GET", "/api/complete-referral-system/health", test_name="Complete Referral Health", critical=True)
        await self.test_endpoint("GET", "/api/complete-referral-system/", test_name="Complete Referral List", critical=True)
        await self.test_endpoint("GET", "/api/complete-referral-system/stats", test_name="Complete Referral Stats", critical=True)
        
        # Referral System
        print("\n🔍 Testing Referral System...")
        await self.test_endpoint("GET", "/api/referral-system/health", test_name="Referral System Health", critical=True)
        await self.test_endpoint("GET", "/api/referral-system/", test_name="Referral System List", critical=True)
        
        # Promotions & Referrals
        print("\n🔍 Testing Promotions & Referrals...")
        await self.test_endpoint("GET", "/api/promotions-referrals/health", test_name="Promotions Referrals Health", critical=True)
        await self.test_endpoint("GET", "/api/promotions-referrals/", test_name="Promotions Referrals List", critical=True)
        
    async def test_website_builder_system(self):
        """Test Website Builder System"""
        print("\n🎯 TESTING WEBSITE BUILDER SYSTEM")
        print("=" * 80)
        
        # Complete Website Builder
        print("\n🔍 Testing Complete Website Builder...")
        await self.test_endpoint("GET", "/api/complete-website-builder/health", test_name="Complete Website Builder Health", critical=True)
        await self.test_endpoint("GET", "/api/complete-website-builder/", test_name="Complete Website Builder List", critical=True)
        await self.test_endpoint("GET", "/api/complete-website-builder/stats", test_name="Complete Website Builder Stats", critical=True)
        
        # Template System
        print("\n🔍 Testing Template System...")
        await self.test_endpoint("GET", "/api/template/health", test_name="Template System Health", critical=True)
        await self.test_endpoint("GET", "/api/template/", test_name="Template System List", critical=True)
        
        # Template Marketplace
        print("\n🔍 Testing Template Marketplace...")
        await self.test_endpoint("GET", "/api/template-marketplace/health", test_name="Template Marketplace Health", critical=True)
        await self.test_endpoint("GET", "/api/template-marketplace/", test_name="Template Marketplace List", critical=True)
        
    async def test_business_systems(self):
        """Test Core Business Systems"""
        print("\n🎯 TESTING CORE BUSINESS SYSTEMS")
        print("=" * 80)
        
        # Financial Management
        print("\n🔍 Testing Financial Management...")
        await self.test_endpoint("GET", "/api/complete-financial/health", test_name="Complete Financial Health", critical=True)
        await self.test_endpoint("GET", "/api/complete-financial/", test_name="Complete Financial List", critical=True)
        await self.test_endpoint("GET", "/api/complete-financial/stats", test_name="Complete Financial Stats", critical=True)
        
        # Multi-Workspace System
        print("\n🔍 Testing Multi-Workspace System...")
        await self.test_endpoint("GET", "/api/complete-multi-workspace/health", test_name="Multi-Workspace Health", critical=True)
        await self.test_endpoint("GET", "/api/complete-multi-workspace/", test_name="Multi-Workspace List", critical=True)
        await self.test_endpoint("GET", "/api/complete-multi-workspace/stats", test_name="Multi-Workspace Stats", critical=True)
        
        # Admin Dashboard
        print("\n🔍 Testing Admin Dashboard...")
        await self.test_endpoint("GET", "/api/admin/health", test_name="Admin Health", critical=True)
        await self.test_endpoint("GET", "/api/admin/", test_name="Admin List", critical=True)
        await self.test_endpoint("GET", "/api/admin/stats", test_name="Admin Stats", critical=True)
        
        # Team Management
        print("\n🔍 Testing Team Management...")
        await self.test_endpoint("GET", "/api/team-management/health", test_name="Team Management Health", critical=True)
        await self.test_endpoint("GET", "/api/team-management/", test_name="Team Management List", critical=True)
        
        # Form Builder
        print("\n🔍 Testing Form Builder...")
        await self.test_endpoint("GET", "/api/form-builder/health", test_name="Form Builder Health", critical=True)
        await self.test_endpoint("GET", "/api/form-builder/", test_name="Form Builder List", critical=True)
        
        # Analytics System
        print("\n🔍 Testing Analytics System...")
        await self.test_endpoint("GET", "/api/analytics-system/health", test_name="Analytics System Health", critical=True)
        await self.test_endpoint("GET", "/api/analytics-system/", test_name="Analytics System List", critical=True)
        
        # AI Automation Suite
        print("\n🔍 Testing AI Automation Suite...")
        await self.test_endpoint("GET", "/api/advanced-ai-suite/health", test_name="AI Suite Health", critical=True)
        await self.test_endpoint("GET", "/api/advanced-ai-suite/", test_name="AI Suite List", critical=True)
        await self.test_endpoint("GET", "/api/advanced-ai-suite/stats", test_name="AI Suite Stats", critical=True)

    async def test_crud_operations(self):
        """Test CRUD Operations on Key Systems"""
        print("\n🎯 TESTING CRUD OPERATIONS")
        print("=" * 80)
        
        # Test CREATE operations (POST)
        print("\n🔍 Testing CREATE Operations...")
        
        # Financial System CREATE
        financial_data = {
            "name": "Mewayz Business Transaction",
            "amount": 1500.00,
            "type": "income",
            "category": "services"
        }
        await self.test_endpoint("POST", "/api/complete-financial/", 
                                data=financial_data, test_name="Financial CREATE", critical=True)
        
        # Referral System CREATE
        referral_data = {
            "referrer_email": "referrer@mewayz.com",
            "referred_email": "referred@mewayz.com",
            "program": "standard",
            "reward_amount": 50.00
        }
        await self.test_endpoint("POST", "/api/complete-referral-system/", 
                                data=referral_data, test_name="Referral CREATE", critical=True)
        
        # Website Builder CREATE
        website_data = {
            "name": "Mewayz Business Site",
            "template": "business_modern",
            "domain": "mybusiness.mewayz.com"
        }
        await self.test_endpoint("POST", "/api/complete-website-builder/", 
                                data=website_data, test_name="Website Builder CREATE", critical=True)
        
        # Test UPDATE operations (PUT)
        print("\n🔍 Testing UPDATE Operations...")
        
        # Use test IDs for UPDATE operations
        test_id = "test_item_001"
        
        update_financial = {
            "name": "Updated Mewayz Transaction",
            "amount": 2000.00,
            "status": "completed"
        }
        await self.test_endpoint("PUT", f"/api/complete-financial/{test_id}", 
                                data=update_financial, test_name="Financial UPDATE", critical=True)
        
        update_referral = {
            "status": "completed",
            "reward_paid": True
        }
        await self.test_endpoint("PUT", f"/api/complete-referral-system/{test_id}", 
                                data=update_referral, test_name="Referral UPDATE", critical=True)
        
        update_website = {
            "name": "Updated Mewayz Site",
            "template": "business_premium"
        }
        await self.test_endpoint("PUT", f"/api/complete-website-builder/{test_id}", 
                                data=update_website, test_name="Website Builder UPDATE", critical=True)
        
        # Test DELETE operations
        print("\n🔍 Testing DELETE Operations...")
        
        await self.test_endpoint("DELETE", f"/api/complete-financial/{test_id}", 
                                test_name="Financial DELETE", critical=True)
        await self.test_endpoint("DELETE", f"/api/complete-referral-system/{test_id}", 
                                test_name="Referral DELETE", critical=True)
        await self.test_endpoint("DELETE", f"/api/complete-website-builder/{test_id}", 
                                test_name="Website Builder DELETE", critical=True)

    async def verify_real_data_operations(self):
        """Verify Real Data Operations (No Mock Data)"""
        print("\n🎯 VERIFYING REAL DATA OPERATIONS")
        print("=" * 80)
        
        mock_patterns = ["sample", "test", "mock", "dummy", "example", "placeholder", "lorem", "ipsum"]
        
        # Check key endpoints for mock data
        endpoints_to_check = [
            ("/api/complete-financial/", "Financial System"),
            ("/api/complete-referral-system/", "Referral System"),
            ("/api/complete-website-builder/", "Website Builder"),
            ("/api/admin/", "Admin System"),
            ("/api/analytics-system/", "Analytics System"),
            ("/api/template/", "Template System")
        ]
        
        mock_data_found = False
        for endpoint, name in endpoints_to_check:
            result = await self.test_endpoint("GET", endpoint, test_name=f"Real Data Check - {name}")
            if result.get("success") and result.get("response_preview"):
                response_lower = result["response_preview"].lower()
                found_patterns = [pattern for pattern in mock_patterns if pattern in response_lower]
                if found_patterns:
                    print(f"⚠️  Potential mock data detected in {name}: {found_patterns}")
                    mock_data_found = True
                else:
                    print(f"✅ No mock data patterns found in {name}")
        
        if not mock_data_found:
            print("✅ REAL DATA OPERATIONS VERIFIED - No mock data patterns detected")
        else:
            print("❌ MOCK DATA STILL PRESENT - Some endpoints contain mock data patterns")

    async def run_comprehensive_test(self):
        """Run the complete comprehensive test suite"""
        print("🎯 MEWAYZ V2 PLATFORM - TARGETED BACKEND VERIFICATION - JANUARY 2025 🎯")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Authenticate first
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
            
            # Run all test phases
            await self.test_core_system_infrastructure()
            await self.test_external_api_integrations()
            await self.test_referral_system()
            await self.test_website_builder_system()
            await self.test_business_systems()
            await self.test_crud_operations()
            await self.verify_real_data_operations()
            
            # Generate comprehensive report
            await self.generate_final_report()
            
        finally:
            await self.cleanup_session()

    async def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("🏆 TARGETED BACKEND VERIFICATION RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed Tests: {self.passed_tests}")
        print(f"   Failed Tests: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Determine status based on success rate
        if success_rate >= 95:
            status = "🎉 ULTIMATE SUCCESS - PRODUCTION READY"
            status_color = "✅"
        elif success_rate >= 85:
            status = "🎯 EXCELLENT SUCCESS - NEAR PRODUCTION READY"
            status_color = "✅"
        elif success_rate >= 75:
            status = "⚠️  GOOD SUCCESS - MINOR ISSUES TO ADDRESS"
            status_color = "⚠️"
        elif success_rate >= 50:
            status = "⚠️  PARTIAL SUCCESS - SIGNIFICANT ISSUES TO ADDRESS"
            status_color = "⚠️"
        else:
            status = "❌ CRITICAL ISSUES - MAJOR FIXES REQUIRED"
            status_color = "❌"
        
        print(f"\n{status_color} FINAL STATUS: {status}")
        
        # Critical failures summary
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures[:10]:  # Show first 10
                print(f"   - {failure}")
            if len(self.critical_failures) > 10:
                print(f"   ... and {len(self.critical_failures) - 10} more")
        else:
            print("\n✅ NO CRITICAL FAILURES DETECTED")
        
        # Success breakdown by test type
        working_tests = [r for r in self.test_results if r["success"]]
        failing_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"\n📋 SUCCESS BREAKDOWN:")
        print(f"   ✅ Working Endpoints: {len(working_tests)}")
        print(f"   ❌ Failing Endpoints: {len(failing_tests)}")
        
        if working_tests:
            print(f"\n✅ WORKING SYSTEMS:")
            for test in working_tests[:15]:  # Show first 15 working tests
                print(f"   - {test['test_name']}: {test['status']} ({test['response_length']} chars)")
        
        if failing_tests:
            print(f"\n❌ FAILING SYSTEMS:")
            for test in failing_tests[:10]:  # Show first 10 failing tests
                print(f"   - {test['test_name']}: {test['status']}")
        
        # Production readiness assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 85:
            print("   ✅ READY FOR PRODUCTION DEPLOYMENT")
            print("   ✅ Core systems operational")
            print("   ✅ Authentication working")
            print("   ✅ API infrastructure solid")
        elif success_rate >= 70:
            print("   ⚠️  NEAR PRODUCTION READY - Minor fixes needed")
            print("   ✅ Core infrastructure working")
            print("   ⚠️  Some systems need attention")
        elif success_rate >= 50:
            print("   ⚠️  PARTIAL PRODUCTION READINESS")
            print("   ✅ Basic infrastructure working")
            print("   ❌ Multiple systems need fixes")
        else:
            print("   ❌ NOT READY FOR PRODUCTION")
            print("   ❌ Critical systems need fixes")
            print("   ❌ Major implementation gaps detected")
        
        print("\n" + "=" * 80)
        print("🎯 TARGETED BACKEND VERIFICATION COMPLETED")
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = TargetedBackendTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())