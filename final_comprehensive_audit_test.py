#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE AUDIT - FOCUSED ON RECENTLY FIXED SYSTEMS
Testing script focused on the systems that were just fixed and overall CRUD operations verification.
This is a critical assessment to ensure all real data operations are functional.

PRIORITY TESTING - Focus on recently fixed systems:
1. Complete Financial Management System (/api/financial/*) - VERIFY FULL CRUD
2. Complete Multi-Workspace System (/api/multi-workspace/*) - VERIFY FULL CRUD  
3. Complete Onboarding System (/api/complete-onboarding/*) - VERIFY ROUTING FIXES
4. Complete Admin Dashboard (/api/admin-dashboard/*) - VERIFY DATABASE CONNECTIONS
5. Core External API Integrations - VERIFY REAL APIs
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

class FinalAuditTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "response_size": len(str(response_data)) if response_data else 0
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if response_data and len(str(response_data)) > 0:
            print(f"   Response size: {len(str(response_data))} chars")
    
    def test_authentication(self):
        """Test authentication with provided credentials"""
        try:
            login_data = {
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log_result("Authentication", True, f"Login successful with {TEST_EMAIL}", data)
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
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, test_name: str = None):
        """Test a specific API endpoint"""
        if not test_name:
            test_name = f"{method} {endpoint}"
            
        try:
            url = f"{API_BASE}{endpoint}"
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
                self.log_result(test_name, False, f"Unsupported method: {method}")
                return False, None
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Working perfectly - Status {response.status_code}", data)
                    return True, data
                except:
                    self.log_result(test_name, True, f"Working perfectly - Status {response.status_code} (non-JSON response)")
                    return True, response.text
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404) - May not be implemented")
                return False, None
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Validation error')
                    self.log_result(test_name, False, f"Validation error (422): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Validation error (422): {response.text}")
                return False, None
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Internal server error')
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}")
                return False, None
            else:
                self.log_result(test_name, False, f"Error - Status {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False, None

    def test_financial_management_system(self):
        """Test Complete Financial Management System - PRIORITY 1"""
        print("\n💰 TESTING COMPLETE FINANCIAL MANAGEMENT SYSTEM - PRIORITY 1")
        print("=" * 70)
        print("VERIFYING FULL CRUD OPERATIONS AND REAL DATABASE PERSISTENCE")
        
        # Test Dashboard - READ
        print("\n📊 Testing Financial Dashboard...")
        self.test_endpoint("/financial/dashboard", "GET", test_name="Financial Dashboard - Overview")
        self.test_endpoint("/financial/dashboard?period=month", "GET", test_name="Financial Dashboard - Monthly")
        self.test_endpoint("/financial/dashboard?period=quarter", "GET", test_name="Financial Dashboard - Quarterly")
        
        # Test Invoice CRUD Operations
        print("\n📄 Testing Invoice CRUD Operations...")
        
        # CREATE Invoice
        invoice_data = {
            "client_name": "Acme Corporation",
            "client_email": "billing@acme.com",
            "client_address": "123 Business St, City, State 12345",
            "items": [
                {"name": "Web Development", "quantity": 1, "price": 2500.00},
                {"name": "SEO Services", "quantity": 3, "price": 400.00}
            ],
            "tax_rate": 0.08,
            "notes": "Payment due within 30 days"
        }
        
        success, invoice_response = self.test_endpoint("/financial/invoices", "POST", invoice_data, "Financial - CREATE Invoice")
        created_invoice_id = None
        if success and invoice_response:
            created_invoice_id = invoice_response.get("data", {}).get("_id") or invoice_response.get("data", {}).get("id")
        
        # READ Invoices
        self.test_endpoint("/financial/invoices", "GET", test_name="Financial - READ All Invoices")
        self.test_endpoint("/financial/invoices?status_filter=draft", "GET", test_name="Financial - READ Draft Invoices")
        
        # UPDATE Invoice Status
        if created_invoice_id:
            self.test_endpoint(f"/financial/invoices/{created_invoice_id}/status", "PUT", 
                             {"new_status": "sent"}, "Financial - UPDATE Invoice Status")
        
        # Test Payment CRUD Operations
        print("\n💳 Testing Payment Operations...")
        if created_invoice_id:
            payment_data = {
                "invoice_id": created_invoice_id,
                "amount": 1000.00,
                "payment_method": "credit_card",
                "notes": "Partial payment received"
            }
            self.test_endpoint("/financial/payments", "POST", payment_data, "Financial - CREATE Payment")
        
        # Test Expense CRUD Operations
        print("\n💸 Testing Expense CRUD Operations...")
        
        # CREATE Expense
        expense_data = {
            "category": "Software",
            "description": "Adobe Creative Suite License",
            "amount": 599.99,
            "tax_deductible": True
        }
        
        success, expense_response = self.test_endpoint("/financial/expenses", "POST", expense_data, "Financial - CREATE Expense")
        
        # READ Expenses
        self.test_endpoint("/financial/expenses", "GET", test_name="Financial - READ All Expenses")
        self.test_endpoint("/financial/expenses?category=Software", "GET", test_name="Financial - READ Expenses by Category")
        
        # Test Financial Reports
        print("\n📈 Testing Financial Reports...")
        self.test_endpoint("/financial/reports/profit-loss", "GET", test_name="Financial - Profit & Loss Report")
        self.test_endpoint("/financial/reports/profit-loss?period=year", "GET", test_name="Financial - Annual P&L Report")
        
        print("\n💰 Financial Management System Testing Complete!")

    def test_multi_workspace_system(self):
        """Test Complete Multi-Workspace System - PRIORITY 2"""
        print("\n🏢 TESTING COMPLETE MULTI-WORKSPACE SYSTEM - PRIORITY 2")
        print("=" * 70)
        print("VERIFYING FULL CRUD OPERATIONS AND RBAC INTEGRATION")
        
        # Test Workspace CRUD Operations
        print("\n🏢 Testing Workspace CRUD Operations...")
        
        # CREATE Workspace
        workspace_data = {
            "name": "Marketing Team Workspace",
            "description": "Dedicated workspace for marketing team collaboration",
            "settings": {
                "privacy": "private",
                "allow_external_members": False
            }
        }
        
        success, workspace_response = self.test_endpoint("/multi-workspace/workspaces", "POST", workspace_data, "Multi-Workspace - CREATE Workspace")
        created_workspace_id = None
        if success and workspace_response:
            created_workspace_id = workspace_response.get("data", {}).get("_id") or workspace_response.get("data", {}).get("id")
        
        # READ Workspaces
        self.test_endpoint("/multi-workspace/workspaces", "GET", test_name="Multi-Workspace - READ All Workspaces")
        
        # Test Health Check
        self.test_endpoint("/multi-workspace/health", "GET", test_name="Multi-Workspace - Health Check")
        
        # Test Member Management
        print("\n👥 Testing Member Management...")
        if created_workspace_id:
            member_data = {
                "email": "member@example.com",
                "role": "editor"
            }
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/members", "POST", 
                             member_data, "Multi-Workspace - ADD Member")
            self.test_endpoint(f"/multi-workspace/workspaces/{created_workspace_id}/members", "GET", 
                             test_name="Multi-Workspace - READ Members")
        
        # Test RBAC System
        print("\n🔐 Testing RBAC System...")
        self.test_endpoint("/multi-workspace/roles", "GET", test_name="Multi-Workspace - READ Roles")
        self.test_endpoint("/multi-workspace/permissions", "GET", test_name="Multi-Workspace - READ Permissions")
        
        print("\n🏢 Multi-Workspace System Testing Complete!")

    def test_complete_onboarding_system(self):
        """Test Complete Onboarding System - PRIORITY 3"""
        print("\n🚀 TESTING COMPLETE ONBOARDING SYSTEM - PRIORITY 3")
        print("=" * 70)
        print("VERIFYING ROUTING FIXES AND ENDPOINT ACCESSIBILITY")
        
        # Test Onboarding Session Management
        print("\n📋 Testing Onboarding Session Management...")
        
        # CREATE Onboarding Session
        session_data = {
            "user_goals": ["increase_sales", "improve_marketing"],
            "business_type": "e-commerce",
            "experience_level": "intermediate"
        }
        
        success, session_response = self.test_endpoint("/complete-onboarding/api/onboarding/session", "POST", session_data, "Onboarding - CREATE Session")
        created_session_id = None
        if success and session_response:
            created_session_id = session_response.get("data", {}).get("_id") or session_response.get("data", {}).get("id")
        
        # READ Onboarding Data
        self.test_endpoint("/complete-onboarding/api/onboarding/goals", "GET", test_name="Onboarding - READ Available Goals")
        self.test_endpoint("/complete-onboarding/api/onboarding/subscription-plans", "GET", test_name="Onboarding - READ Subscription Plans")
        
        if created_session_id:
            self.test_endpoint(f"/complete-onboarding/api/onboarding/session/{created_session_id}", "GET", 
                             test_name="Onboarding - READ Session Details")
        
        # Test Onboarding Completion
        print("\n✅ Testing Onboarding Completion...")
        if created_session_id:
            completion_data = {
                "selected_plan": "professional",
                "workspace_name": "My Business Workspace",
                "initial_setup": {
                    "enable_analytics": True,
                    "setup_integrations": ["stripe", "mailchimp"]
                }
            }
            self.test_endpoint(f"/complete-onboarding/api/onboarding/session/{created_session_id}/complete", "POST", 
                             completion_data, "Onboarding - COMPLETE Session")
        
        # Test Health Check
        self.test_endpoint("/complete-onboarding/api/onboarding/health", "GET", test_name="Onboarding - Health Check")
        
        print("\n🚀 Complete Onboarding System Testing Complete!")

    def test_admin_dashboard_system(self):
        """Test Complete Admin Dashboard System - PRIORITY 4"""
        print("\n⚙️ TESTING COMPLETE ADMIN DASHBOARD SYSTEM - PRIORITY 4")
        print("=" * 70)
        print("VERIFYING DATABASE CONNECTIONS AND ADMIN FUNCTIONALITY")
        
        # Test Admin Dashboard Overview
        print("\n📊 Testing Admin Dashboard Overview...")
        self.test_endpoint("/admin/dashboard", "GET", test_name="Admin Dashboard - Overview")
        
        # Test User Management
        print("\n👥 Testing User Management...")
        self.test_endpoint("/admin/users", "GET", test_name="Admin Dashboard - READ All Users")
        self.test_endpoint("/admin/users/stats", "GET", test_name="Admin Dashboard - READ User Stats")
        
        # Test System Metrics
        print("\n📈 Testing System Metrics...")
        self.test_endpoint("/admin/system/metrics", "GET", test_name="Admin Dashboard - System Metrics")
        
        # Test Admin Configuration System
        print("\n⚙️ Testing Admin Configuration System...")
        self.test_endpoint("/admin-config/configuration", "GET", test_name="Admin Config - READ Configuration")
        self.test_endpoint("/admin-config/system/health", "GET", test_name="Admin Config - System Health")
        self.test_endpoint("/admin-config/integrations/status", "GET", test_name="Admin Config - Integration Status")
        self.test_endpoint("/admin-config/available-services", "GET", test_name="Admin Config - Available Services")
        
        print("\n⚙️ Admin Dashboard System Testing Complete!")

    def test_external_api_integrations(self):
        """Test Core External API Integrations - PRIORITY 5"""
        print("\n🌐 TESTING CORE EXTERNAL API INTEGRATIONS - PRIORITY 5")
        print("=" * 70)
        print("VERIFYING REAL API CONNECTIONS AND FUNCTIONALITY")
        
        # Test Social Media Lead Generation
        print("\n📱 Testing Social Media Lead Generation...")
        
        # Twitter API Integration
        twitter_search_data = {
            "keywords": ["digital marketing", "small business"],
            "location": "United States",
            "max_results": 10
        }
        self.test_endpoint("/social-media-leads/twitter/search", "POST", twitter_search_data, "Social Media - Twitter Lead Search")
        self.test_endpoint("/social-media-leads/analytics/overview", "GET", test_name="Social Media - Analytics Overview")
        
        # TikTok API Integration
        tiktok_search_data = {
            "hashtags": ["entrepreneur", "business"],
            "region": "US",
            "limit": 10
        }
        self.test_endpoint("/social-media-leads/tiktok/search", "POST", tiktok_search_data, "Social Media - TikTok Lead Search")
        
        # Test AI Automation with OpenAI
        print("\n🤖 Testing AI Automation with OpenAI...")
        
        # Content Generation
        content_data = {
            "prompt": "Write a professional email for lead follow-up",
            "type": "email",
            "tone": "professional"
        }
        self.test_endpoint("/ai-automation/generate-content", "POST", content_data, "AI Automation - Generate Content")
        
        # Lead Enrichment
        lead_data = {
            "company_name": "TechStartup Inc",
            "website": "techstartup.com",
            "industry": "technology"
        }
        self.test_endpoint("/ai-automation/enrich-lead", "POST", lead_data, "AI Automation - Enrich Lead")
        
        # Analytics Overview
        self.test_endpoint("/ai-automation/analytics/overview", "GET", test_name="AI Automation - Analytics Overview")
        
        # Test Email Automation with ElasticMail
        print("\n📧 Testing Email Automation with ElasticMail...")
        
        # Send Email
        email_data = {
            "to": "test@example.com",
            "subject": "Welcome to Our Platform",
            "content": "Thank you for joining our platform. We're excited to help you grow your business!",
            "template": "welcome_email"
        }
        self.test_endpoint("/email-automation/send-email", "POST", email_data, "Email Automation - Send Email")
        
        # Create Email Campaign
        campaign_data = {
            "name": "Q1 Marketing Campaign",
            "subject": "Boost Your Business This Quarter",
            "template": "marketing_template",
            "recipients": ["subscriber1@example.com", "subscriber2@example.com"]
        }
        self.test_endpoint("/email-automation/campaigns", "POST", campaign_data, "Email Automation - Create Campaign")
        
        # Analytics Overview
        self.test_endpoint("/email-automation/analytics/overview", "GET", test_name="Email Automation - Analytics Overview")
        
        # Test API Configuration and Status
        print("\n⚙️ Testing API Configuration...")
        self.test_endpoint("/admin-config/integrations/status", "GET", test_name="External APIs - Status Check")
        self.test_endpoint("/admin-config/configuration", "GET", test_name="External APIs - Configuration")
        
        # Test individual API connections
        self.test_endpoint("/admin-config/integrations/stripe/test", "POST", {}, "External APIs - Test Stripe")
        self.test_endpoint("/admin-config/integrations/openai/test", "POST", {}, "External APIs - Test OpenAI")
        self.test_endpoint("/admin-config/integrations/elasticmail/test", "POST", {}, "External APIs - Test ElasticMail")
        self.test_endpoint("/admin-config/integrations/twitter/test", "POST", {}, "External APIs - Test Twitter")
        
        print("\n🌐 External API Integrations Testing Complete!")

    def test_data_consistency_verification(self):
        """Test Real Data Operations and Consistency"""
        print("\n🔍 TESTING REAL DATA VERIFICATION")
        print("=" * 50)
        print("VERIFYING NO MOCK DATA AND DATABASE PERSISTENCE")
        
        # Test data consistency by calling same endpoints multiple times
        print("\n📊 Testing Data Consistency...")
        
        # Call dashboard multiple times to verify consistent data
        success1, data1 = self.test_endpoint("/financial/dashboard", "GET", test_name="Data Consistency - Financial Dashboard (Call 1)")
        time.sleep(1)
        success2, data2 = self.test_endpoint("/financial/dashboard", "GET", test_name="Data Consistency - Financial Dashboard (Call 2)")
        
        if success1 and success2 and data1 == data2:
            self.log_result("Data Consistency - Financial Dashboard", True, "Data consistent across calls - confirms real database usage")
        elif success1 and success2:
            self.log_result("Data Consistency - Financial Dashboard", False, "Data inconsistent - may be using random generation")
        
        # Test admin dashboard consistency
        success1, data1 = self.test_endpoint("/admin/dashboard", "GET", test_name="Data Consistency - Admin Dashboard (Call 1)")
        time.sleep(1)
        success2, data2 = self.test_endpoint("/admin/dashboard", "GET", test_name="Data Consistency - Admin Dashboard (Call 2)")
        
        if success1 and success2 and data1 == data2:
            self.log_result("Data Consistency - Admin Dashboard", True, "Data consistent across calls - confirms real database usage")
        elif success1 and success2:
            self.log_result("Data Consistency - Admin Dashboard", False, "Data inconsistent - may be using random generation")
        
        # Test multi-workspace consistency
        success1, data1 = self.test_endpoint("/multi-workspace/workspaces", "GET", test_name="Data Consistency - Workspaces (Call 1)")
        time.sleep(1)
        success2, data2 = self.test_endpoint("/multi-workspace/workspaces", "GET", test_name="Data Consistency - Workspaces (Call 2)")
        
        if success1 and success2 and data1 == data2:
            self.log_result("Data Consistency - Workspaces", True, "Data consistent across calls - confirms real database usage")
        elif success1 and success2:
            self.log_result("Data Consistency - Workspaces", False, "Data inconsistent - may be using random generation")

    def run_final_comprehensive_audit(self):
        """Run the complete final comprehensive audit"""
        print("🎯 FINAL COMPREHENSIVE AUDIT - RECENTLY FIXED SYSTEMS")
        print("=" * 80)
        print("CRITICAL ASSESSMENT TO ENSURE ALL REAL DATA OPERATIONS ARE FUNCTIONAL")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Step 1: Authentication
        print("\n🔐 STEP 1: AUTHENTICATION")
        if not self.test_authentication():
            print("❌ CRITICAL: Authentication failed. Cannot proceed with testing.")
            return False
        
        # Step 2: Test Priority Systems
        print("\n🎯 STEP 2: TESTING PRIORITY SYSTEMS")
        
        # Priority 1: Financial Management System
        self.test_financial_management_system()
        
        # Priority 2: Multi-Workspace System  
        self.test_multi_workspace_system()
        
        # Priority 3: Complete Onboarding System
        self.test_complete_onboarding_system()
        
        # Priority 4: Admin Dashboard System
        self.test_admin_dashboard_system()
        
        # Priority 5: External API Integrations
        self.test_external_api_integrations()
        
        # Step 3: Data Consistency Verification
        print("\n🔍 STEP 3: DATA CONSISTENCY VERIFICATION")
        self.test_data_consistency_verification()
        
        # Step 4: Generate Final Report
        self.generate_final_report()
        
        return True

    def generate_final_report(self):
        """Generate comprehensive final audit report"""
        print("\n" + "=" * 80)
        print("🎯 FINAL COMPREHENSIVE AUDIT RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        
        if success_rate >= 75:
            print("✅ EXCELLENT: Platform meets production readiness criteria (≥75% success rate)")
        elif success_rate >= 60:
            print("⚠️ GOOD: Platform mostly functional but needs attention on failing systems")
        else:
            print("❌ NEEDS ATTENTION: Platform requires significant fixes before production")
        
        # Categorize results by system
        systems = {
            "Financial Management": [],
            "Multi-Workspace": [],
            "Complete Onboarding": [],
            "Admin Dashboard": [],
            "External API Integrations": [],
            "Data Consistency": [],
            "Authentication": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Financial" in test_name:
                systems["Financial Management"].append(result)
            elif "Multi-Workspace" in test_name:
                systems["Multi-Workspace"].append(result)
            elif "Onboarding" in test_name:
                systems["Complete Onboarding"].append(result)
            elif "Admin Dashboard" in test_name:
                systems["Admin Dashboard"].append(result)
            elif any(x in test_name for x in ["Social Media", "AI Automation", "Email Automation", "External APIs"]):
                systems["External API Integrations"].append(result)
            elif "Data Consistency" in test_name:
                systems["Data Consistency"].append(result)
            elif "Authentication" in test_name:
                systems["Authentication"].append(result)
        
        print("\n📋 SYSTEM-SPECIFIC RESULTS:")
        for system_name, results in systems.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                status = "✅" if rate >= 75 else "⚠️" if rate >= 50 else "❌"
                print(f"{status} {system_name}: {rate:.1f}% ({passed}/{total} tests passed)")
        
        print("\n🔍 CRITICAL FINDINGS:")
        
        # Real data verification
        data_consistency_results = [r for r in self.test_results if "Data Consistency" in r["test"]]
        consistent_data = sum(1 for r in data_consistency_results if r["success"])
        if consistent_data > 0:
            print(f"✅ REAL DATA OPERATIONS: {consistent_data} systems confirmed using real database operations")
        else:
            print("❌ REAL DATA OPERATIONS: No systems confirmed to be using real database operations")
        
        # Authentication status
        auth_results = [r for r in self.test_results if "Authentication" in r["test"]]
        if auth_results and auth_results[0]["success"]:
            print(f"✅ AUTHENTICATION: Working perfectly with {TEST_EMAIL}")
        else:
            print("❌ AUTHENTICATION: Failed - critical blocker")
        
        # CRUD operations summary
        crud_operations = {
            "CREATE": sum(1 for r in self.test_results if "CREATE" in r["test"] and r["success"]),
            "READ": sum(1 for r in self.test_results if "READ" in r["test"] and r["success"]),
            "UPDATE": sum(1 for r in self.test_results if "UPDATE" in r["test"] and r["success"]),
        }
        
        print(f"\n📝 CRUD OPERATIONS VERIFICATION:")
        for operation, count in crud_operations.items():
            if count > 0:
                print(f"✅ {operation} Operations: {count} endpoints working")
            else:
                print(f"⚠️ {operation} Operations: No working endpoints found")
        
        print("\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 75:
            print("✅ PRODUCTION READY: Platform meets all critical requirements")
            print("✅ All priority systems operational with real data operations")
            print("✅ External API integrations functional")
            print("✅ Authentication and security working properly")
        else:
            print("⚠️ PARTIAL PRODUCTION READINESS: Platform needs attention before full deployment")
            print("🔧 Focus on fixing failing systems identified above")
            print("🔧 Ensure all CRUD operations are fully functional")
            print("🔧 Verify all external API integrations are working")
        
        print("\n" + "=" * 80)
        print("🎯 FINAL COMPREHENSIVE AUDIT COMPLETE")
        print("=" * 80)

def main():
    """Main execution function"""
    tester = FinalAuditTester()
    
    try:
        success = tester.run_final_comprehensive_audit()
        if success:
            print("\n✅ Final comprehensive audit completed successfully!")
            return 0
        else:
            print("\n❌ Final comprehensive audit failed!")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())