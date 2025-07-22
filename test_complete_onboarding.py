#!/usr/bin/env python3
"""
Test Complete Onboarding System - Real Data & Full CRUD Verification
Mewayz v2 - July 22, 2025
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class OnboardingSystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.session_id = None
        self.auth_token = None
        self.test_results = []
        
    async def run_comprehensive_test(self):
        """Run comprehensive test of onboarding system"""
        print("🚀 STARTING COMPLETE ONBOARDING SYSTEM TEST")
        print("=" * 80)
        
        # 1. Login and get auth token
        print("\n📋 1. AUTHENTICATING USER...")
        await self._authenticate()
        
        # 2. Test CREATE - Create onboarding session
        print("\n📋 2. TESTING CREATE - Onboarding Session...")
        await self._test_create_session()
        
        # 3. Test READ - Get onboarding session
        print("\n📋 3. TESTING READ - Get Session...")
        await self._test_get_session()
        
        # 4. Test UPDATE - Goals selection
        print("\n📋 4. TESTING UPDATE - Goals Selection...")
        await self._test_update_goals()
        
        # 5. Test UPDATE - Subscription plan
        print("\n📋 5. TESTING UPDATE - Subscription Plan...")
        await self._test_update_subscription()
        
        # 6. Test UPDATE - Team setup
        print("\n📋 6. TESTING UPDATE - Team Setup...")
        await self._test_update_team()
        
        # 7. Test UPDATE - Branding setup
        print("\n📋 7. TESTING UPDATE - Branding Setup...")
        await self._test_update_branding()
        
        # 8. Test UPDATE - Integrations setup
        print("\n📋 8. TESTING UPDATE - Integrations...")
        await self._test_update_integrations()
        
        # 9. Test CREATE - Complete onboarding
        print("\n📋 9. TESTING CREATE - Complete Onboarding...")
        await self._test_complete_onboarding()
        
        # 10. Test READ - Get available goals
        print("\n📋 10. TESTING READ - Available Goals...")
        await self._test_get_goals()
        
        # 11. Test READ - Get subscription plans
        print("\n📋 11. TESTING READ - Subscription Plans...")
        await self._test_get_subscription_plans()
        
        # 12. Test READ - Get analytics
        print("\n📋 12. TESTING READ - Analytics...")
        await self._test_get_analytics()
        
        # 13. Test DELETE - Delete session
        print("\n📋 13. TESTING DELETE - Delete Session...")
        await self._test_delete_session()
        
        # 14. Test health check
        print("\n📋 14. TESTING HEALTH CHECK...")
        await self._test_health_check()
        
        # Generate report
        print("\n📋 15. GENERATING TEST REPORT...")
        await self._generate_test_report()
        
        print("\n✅ COMPLETE ONBOARDING SYSTEM TEST COMPLETED!")
        
    async def _authenticate(self):
        """Authenticate user and get token"""
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "email": "tmonnens@outlook.com",
                    "password": "Voetballen5"
                }
                
                async with session.post(
                    f"{self.base_url}/api/login",
                    json=login_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.auth_token = result.get("access_token")
                        print("   ✅ Authentication successful")
                        self.test_results.append(("Authentication", "SUCCESS"))
                    else:
                        print("   ❌ Authentication failed")
                        self.test_results.append(("Authentication", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            self.test_results.append(("Authentication", "ERROR"))
    
    async def _test_create_session(self):
        """Test creating onboarding session"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                session_data = {
                    "workspace_name": "Test Workspace",
                    "workspace_description": "Test workspace for onboarding",
                    "industry": "Technology"
                }
                
                async with session.post(
                    f"{self.base_url}/api/onboarding/session",
                    json=session_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.session_id = result["data"]["session_id"]
                        print("   ✅ Session created successfully")
                        print(f"   📋 Session ID: {self.session_id}")
                        self.test_results.append(("CREATE Session", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Session creation failed: {error_text}")
                        self.test_results.append(("CREATE Session", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Session creation error: {str(e)}")
            self.test_results.append(("CREATE Session", "ERROR"))
    
    async def _test_get_session(self):
        """Test getting onboarding session"""
        if not self.session_id:
            print("   ❌ No session ID available")
            self.test_results.append(("READ Session", "SKIPPED"))
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with session.get(
                    f"{self.base_url}/api/onboarding/session/{self.session_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Session retrieved successfully")
                        print(f"   📋 Current step: {result['data']['current_step']}")
                        print(f"   📋 Progress: {result['data']['progress_percentage']}%")
                        self.test_results.append(("READ Session", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Session retrieval failed: {error_text}")
                        self.test_results.append(("READ Session", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Session retrieval error: {str(e)}")
            self.test_results.append(("READ Session", "ERROR"))
    
    async def _test_update_goals(self):
        """Test updating goals selection"""
        if not self.session_id:
            print("   ❌ No session ID available")
            self.test_results.append(("UPDATE Goals", "SKIPPED"))
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                goals_data = {
                    "selected_goals": ["social_media", "crm", "analytics"]
                }
                
                async with session.post(
                    f"{self.base_url}/api/onboarding/session/{self.session_id}/goals",
                    json=goals_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Goals selection updated successfully")
                        print(f"   📋 Selected goals: {goals_data['selected_goals']}")
                        self.test_results.append(("UPDATE Goals", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Goals update failed: {error_text}")
                        self.test_results.append(("UPDATE Goals", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Goals update error: {str(e)}")
            self.test_results.append(("UPDATE Goals", "ERROR"))
    
    async def _test_update_subscription(self):
        """Test updating subscription plan"""
        if not self.session_id:
            print("   ❌ No session ID available")
            self.test_results.append(("UPDATE Subscription", "SKIPPED"))
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                subscription_data = {
                    "selected_plan": "pro",
                    "billing_cycle": "monthly",
                    "feature_count": 3
                }
                
                async with session.post(
                    f"{self.base_url}/api/onboarding/session/{self.session_id}/subscription",
                    json=subscription_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Subscription plan updated successfully")
                        print(f"   📋 Selected plan: {subscription_data['selected_plan']}")
                        print(f"   📋 Billing cycle: {subscription_data['billing_cycle']}")
                        self.test_results.append(("UPDATE Subscription", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Subscription update failed: {error_text}")
                        self.test_results.append(("UPDATE Subscription", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Subscription update error: {str(e)}")
            self.test_results.append(("UPDATE Subscription", "ERROR"))
    
    async def _test_update_team(self):
        """Test updating team setup"""
        if not self.session_id:
            print("   ❌ No session ID available")
            self.test_results.append(("UPDATE Team", "SKIPPED"))
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                team_data = {
                    "team_members": [
                        {
                            "email": "test@example.com",
                            "first_name": "Test",
                            "last_name": "User",
                            "role": "editor"
                        }
                    ]
                }
                
                async with session.post(
                    f"{self.base_url}/api/onboarding/session/{self.session_id}/team",
                    json=team_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Team setup updated successfully")
                        print(f"   📋 Team members: {len(team_data['team_members'])}")
                        self.test_results.append(("UPDATE Team", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Team update failed: {error_text}")
                        self.test_results.append(("UPDATE Team", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Team update error: {str(e)}")
            self.test_results.append(("UPDATE Team", "ERROR"))
    
    async def _test_update_branding(self):
        """Test updating branding setup"""
        if not self.session_id:
            print("   ❌ No session ID available")
            self.test_results.append(("UPDATE Branding", "SKIPPED"))
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                branding_data = {
                    "company_name": "Test Company",
                    "primary_color": "#3B82F6",
                    "secondary_color": "#1E40AF",
                    "custom_domain": "test.example.com"
                }
                
                async with session.post(
                    f"{self.base_url}/api/onboarding/session/{self.session_id}/branding",
                    json=branding_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Branding setup updated successfully")
                        print(f"   📋 Company name: {branding_data['company_name']}")
                        self.test_results.append(("UPDATE Branding", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Branding update failed: {error_text}")
                        self.test_results.append(("UPDATE Branding", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Branding update error: {str(e)}")
            self.test_results.append(("UPDATE Branding", "ERROR"))
    
    async def _test_update_integrations(self):
        """Test updating integrations setup"""
        if not self.session_id:
            print("   ❌ No session ID available")
            self.test_results.append(("UPDATE Integrations", "SKIPPED"))
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                integrations_data = {
                    "integrations": {
                        "stripe": {
                            "configured": True,
                            "settings": {}
                        },
                        "openai": {
                            "configured": True,
                            "settings": {}
                        }
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/onboarding/session/{self.session_id}/integrations",
                    json=integrations_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Integrations setup updated successfully")
                        print(f"   📋 Integrations: {list(integrations_data['integrations'].keys())}")
                        self.test_results.append(("UPDATE Integrations", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Integrations update failed: {error_text}")
                        self.test_results.append(("UPDATE Integrations", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Integrations update error: {str(e)}")
            self.test_results.append(("UPDATE Integrations", "ERROR"))
    
    async def _test_complete_onboarding(self):
        """Test completing onboarding"""
        if not self.session_id:
            print("   ❌ No session ID available")
            self.test_results.append(("CREATE Workspace", "SKIPPED"))
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with session.post(
                    f"{self.base_url}/api/onboarding/session/{self.session_id}/complete",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Onboarding completed successfully")
                        print(f"   📋 Workspace created: {result['data']['workspace_name']}")
                        print(f"   📋 Features enabled: {len(result['data']['features_enabled'])}")
                        self.test_results.append(("CREATE Workspace", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Onboarding completion failed: {error_text}")
                        self.test_results.append(("CREATE Workspace", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Onboarding completion error: {str(e)}")
            self.test_results.append(("CREATE Workspace", "ERROR"))
    
    async def _test_get_goals(self):
        """Test getting available goals"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with session.get(
                    f"{self.base_url}/api/onboarding/goals",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Available goals retrieved successfully")
                        print(f"   📋 Total goals: {result['data']['total_goals']}")
                        self.test_results.append(("READ Goals", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Goals retrieval failed: {error_text}")
                        self.test_results.append(("READ Goals", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Goals retrieval error: {str(e)}")
            self.test_results.append(("READ Goals", "ERROR"))
    
    async def _test_get_subscription_plans(self):
        """Test getting subscription plans"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with session.get(
                    f"{self.base_url}/api/onboarding/subscription-plans",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Subscription plans retrieved successfully")
                        print(f"   📋 Available plans: {list(result['data']['plans'].keys())}")
                        self.test_results.append(("READ Subscription Plans", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Subscription plans retrieval failed: {error_text}")
                        self.test_results.append(("READ Subscription Plans", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Subscription plans retrieval error: {str(e)}")
            self.test_results.append(("READ Subscription Plans", "ERROR"))
    
    async def _test_get_analytics(self):
        """Test getting analytics"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with session.get(
                    f"{self.base_url}/api/onboarding/analytics",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Analytics retrieved successfully")
                        print(f"   📋 Total sessions: {result['data']['total_sessions']}")
                        print(f"   📋 Completion rate: {result['data']['completion_rate']}%")
                        self.test_results.append(("READ Analytics", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Analytics retrieval failed: {error_text}")
                        self.test_results.append(("READ Analytics", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Analytics retrieval error: {str(e)}")
            self.test_results.append(("READ Analytics", "ERROR"))
    
    async def _test_delete_session(self):
        """Test deleting onboarding session"""
        if not self.session_id:
            print("   ❌ No session ID available")
            self.test_results.append(("DELETE Session", "SKIPPED"))
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with session.delete(
                    f"{self.base_url}/api/onboarding/session/{self.session_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Session deleted successfully")
                        self.test_results.append(("DELETE Session", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Session deletion failed: {error_text}")
                        self.test_results.append(("DELETE Session", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Session deletion error: {str(e)}")
            self.test_results.append(("DELETE Session", "ERROR"))
    
    async def _test_health_check(self):
        """Test health check"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                async with session.get(
                    f"{self.base_url}/api/onboarding/health",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✅ Health check successful")
                        print(f"   📋 Status: {result['data']['status']}")
                        print(f"   📋 Database: {result['data']['database']}")
                        self.test_results.append(("Health Check", "SUCCESS"))
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Health check failed: {error_text}")
                        self.test_results.append(("Health Check", "FAILED"))
                        
        except Exception as e:
            print(f"   ❌ Health check error: {str(e)}")
            self.test_results.append(("Health Check", "ERROR"))
    
    async def _generate_test_report(self):
        """Generate test report"""
        print("\n" + "=" * 80)
        print("📊 COMPLETE ONBOARDING SYSTEM TEST REPORT")
        print("=" * 80)
        
        success_count = sum(1 for _, status in self.test_results if status == "SUCCESS")
        failed_count = sum(1 for _, status in self.test_results if status == "FAILED")
        error_count = sum(1 for _, status in self.test_results if status == "ERROR")
        skipped_count = sum(1 for _, status in self.test_results if status == "SKIPPED")
        
        print(f"✅ Successful tests: {success_count}")
        print(f"❌ Failed tests: {failed_count}")
        print(f"⚠️  Error tests: {error_count}")
        print(f"⏭️  Skipped tests: {skipped_count}")
        print(f"📊 Total tests: {len(self.test_results)}")
        
        if len(self.test_results) > 0:
            success_rate = (success_count / len(self.test_results)) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, status in self.test_results:
            status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "⚠️" if status == "ERROR" else "⏭️"
            print(f"  {status_icon} {test_name}: {status}")
        
        print("\n" + "=" * 80)
        
        # Save report to file
        report_data = {
            "test_date": datetime.now().isoformat(),
            "test_results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "successful": success_count,
                "failed": failed_count,
                "errors": error_count,
                "skipped": skipped_count,
                "success_rate": success_rate if len(self.test_results) > 0 else 0
            }
        }
        
        with open("/app/onboarding_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print("📄 Test report saved to: /app/onboarding_test_report.json")

async def main():
    """Main test execution"""
    tester = OnboardingSystemTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())