#!/usr/bin/env python3
"""
COMPREHENSIVE SUPPORT SYSTEM WITH LIVE CHAT AND AI GUIDANCE TESTING
Phase 3 Support System Testing - July 20, 2025
Testing Agent - Comprehensive Support System Verification
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Backend URL from frontend .env
BACKEND_URL = "https://d70b9379-58ef-4e6d-9a10-f0eebb21d382.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class SupportSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.session_id = None
        self.agent_id = None
        
    def log_test(self, endpoint, method, status, response_time, success, details="", data_size=0):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            
        result = {
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'response_time': f"{response_time:.3f}s",
            'success': success,
            'details': details,
            'data_size': data_size
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {method} {endpoint} - {status} ({response_time:.3f}s) - {details}")
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print(f"\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        print(f"Email: {ADMIN_EMAIL}")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                if self.auth_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("/auth/login", "POST", response.status_code, response_time, True, 
                                f"Admin authentication successful, token: {self.auth_token[:20]}...")
                    return True
                else:
                    self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                                "No access token in response")
                    return False
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Login failed: {response.text[:100]}")
                return False
                
        except Exception as e:
            self.log_test("/auth/login", "POST", 0, 0, False, f"Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, endpoint, method="GET", data=None, expected_status=200, description=""):
        """Test a single endpoint with JSON data"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            # Check if response is successful
            success = response.status_code == expected_status
            
            # Get response details
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    details += f" - Error: {response_data.get('detail', 'Unknown error')}"
                
                # Store important IDs for subsequent tests
                if success and 'data' in response_data:
                    if 'session_id' in response_data['data']:
                        self.session_id = response_data['data']['session_id']
                    if 'agent_id' in response_data['data']:
                        self.agent_id = response_data['data']['agent_id']
                    
            except:
                data_size = len(response.text)
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    details += f" - Error: {response.text[:100]}"
            
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size)
            return success, response
            
        except requests.exceptions.Timeout:
            self.log_test(endpoint, method, 0, 30.0, False, f"{description} - Request timeout")
            return False, None
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"{description} - Error: {str(e)}")
            return False, None

    def test_endpoint_form(self, endpoint, method="GET", data=None, expected_status=200, description=""):
        """Test a single endpoint with form data"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, data=data, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, data=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            # Check if response is successful
            success = response.status_code == expected_status
            
            # Get response details
            try:
                response_data = response.json()
                data_size = len(json.dumps(response_data))
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    details += f" - Error: {response_data.get('detail', 'Unknown error')}"
                
                # Store important IDs for subsequent tests
                if success and 'data' in response_data:
                    if 'session_id' in response_data['data']:
                        self.session_id = response_data['data']['session_id']
                    if 'agent_id' in response_data['data']:
                        self.agent_id = response_data['data']['agent_id']
                    
            except:
                data_size = len(response.text)
                details = f"{description} - Response size: {data_size} chars"
                if not success:
                    details += f" - Error: {response.text[:100]}"
            
            self.log_test(endpoint, method, response.status_code, response_time, success, details, data_size)
            return success, response
            
        except requests.exceptions.Timeout:
            self.log_test(endpoint, method, 0, 30.0, False, f"{description} - Request timeout")
            return False, None
        except Exception as e:
            self.log_test(endpoint, method, 0, 0, False, f"{description} - Error: {str(e)}")
            return False, None

    def test_support_admin_dashboard(self):
        """Test Support Admin Dashboard"""
        print(f"\n📊 TESTING SUPPORT ADMIN DASHBOARD")
        
        self.test_endpoint("/support/admin/dashboard", "GET", 
                         description="Support admin dashboard with comprehensive support metrics")

    def test_agent_management(self):
        """Test Agent Management"""
        print(f"\n👥 TESTING AGENT MANAGEMENT")
        
        # Create support agent - using Form data format as expected by API
        agent_data = {
            "name": "Test Support Agent",
            "email": "agent@mewayz.com",
            "role": "senior_support",
            "specialties": ["technical_support", "billing"],
            "languages": ["en", "es"],
            "timezone": "UTC"
        }
        
        success, response = self.test_endpoint_form("/support/agents/create", "POST", data=agent_data,
                                                   description="Create support agent with skills and availability")
        
        # Store agent_id if successful
        if success and response:
            try:
                response_data = response.json()
                if 'data' in response_data and 'agent_id' in response_data['data']:
                    self.agent_id = response_data['data']['agent_id']
            except:
                pass

    def test_live_chat_system(self):
        """Test Live Chat System"""
        print(f"\n💬 TESTING LIVE CHAT SYSTEM")
        
        # Generate session ID for testing
        test_session_id = str(uuid.uuid4())
        test_agent_id = self.agent_id or str(uuid.uuid4())
        
        # Agent connect to live chat - using Form data format
        connect_data = {
            "session_id": test_session_id,
            "agent_id": test_agent_id
        }
        
        success, response = self.test_endpoint_form("/support/live-chat/agent/connect", "POST", data=connect_data,
                                                   description="Agent connect to live chat system")
        
        # Send message in live chat - using Form data format
        message_data = {
            "session_id": test_session_id,
            "message": "Hello! How can I help you today?",
            "sender_type": "agent",
            "sender_id": test_agent_id,
            "message_type": "text"
        }
        
        self.test_endpoint_form("/support/live-chat/message/send", "POST", data=message_data,
                               description="Send message in live chat session")
        
        # Get chat messages
        self.test_endpoint(f"/support/live-chat/{test_session_id}/messages", "GET",
                         description="Retrieve live chat session messages")

    def test_ai_guidance_system(self):
        """Test AI-Powered Support Guidance"""
        print(f"\n🤖 TESTING AI-POWERED SUPPORT GUIDANCE")
        
        # AI guidance suggestion - using Form data format with correct field name
        guidance_data = {
            "customer_message": "I'm having trouble with my subscription billing",
            "context": "billing",
            "ticket_id": str(uuid.uuid4()),
            "session_id": str(uuid.uuid4())
        }
        
        self.test_endpoint_form("/support/ai-guidance/suggest", "POST", data=guidance_data,
                               description="AI-powered support guidance and suggestions")

    def test_knowledge_base(self):
        """Test Knowledge Base"""
        print(f"\n📚 TESTING KNOWLEDGE BASE")
        
        # Search knowledge base
        search_params = {
            "query": "billing issues",
            "category": "billing",
            "limit": 10
        }
        
        # Convert to query string for GET request
        query_string = "&".join([f"{k}={v}" for k, v in search_params.items()])
        
        self.test_endpoint(f"/support/knowledge-base/search?{query_string}", "GET",
                         description="Search knowledge base for support articles")

    def test_escalation_system(self):
        """Test Escalation & Satisfaction"""
        print(f"\n⚡ TESTING ESCALATION & SATISFACTION SYSTEM")
        
        # Create escalation - using Form data format with correct field names
        escalation_data = {
            "ticket_id": str(uuid.uuid4()),
            "escalation_reason": "complex_technical_issue",
            "escalation_level": "level_2",
            "notes": "Customer experiencing complex billing integration issues requiring senior technical support",
            "urgency": "high"
        }
        
        self.test_endpoint_form("/support/escalation/create", "POST", data=escalation_data,
                               description="Create support escalation for complex issues")
        
        # Submit satisfaction survey - using Form data format with correct field names
        satisfaction_data = {
            "ticket_id": str(uuid.uuid4()),
            "session_id": str(uuid.uuid4()),
            "agent_id": self.agent_id or str(uuid.uuid4()),
            "overall_rating": 5,
            "agent_rating": 5,
            "resolution_rating": 5,
            "response_time_rating": 5,
            "feedback": "Excellent support! Agent was very helpful and resolved my issue quickly.",
            "would_recommend": True
        }
        
        self.test_endpoint_form("/support/satisfaction/submit", "POST", data=satisfaction_data,
                               description="Submit customer satisfaction survey")
        
        # Get satisfaction analytics
        self.test_endpoint("/support/analytics/satisfaction", "GET",
                         description="Support satisfaction analytics and metrics")

    def run_comprehensive_support_test(self):
        """Run comprehensive testing of support system"""
        print(f"🎯 COMPREHENSIVE SUPPORT SYSTEM WITH LIVE CHAT AND AI GUIDANCE TESTING")
        print(f"Phase 3 Support System Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with testing")
            return
        
        # Step 2: Test Support Admin Dashboard
        self.test_support_admin_dashboard()
        
        # Step 3: Test Agent Management
        self.test_agent_management()
        
        # Step 4: Test Live Chat System
        self.test_live_chat_system()
        
        # Step 5: Test AI Guidance System
        self.test_ai_guidance_system()
        
        # Step 6: Test Knowledge Base
        self.test_knowledge_base()
        
        # Step 7: Test Escalation & Satisfaction
        self.test_escalation_system()
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print(f"\n" + "="*80)
        print(f"📊 COMPREHENSIVE SUPPORT SYSTEM TESTING REPORT")
        print(f"="*80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        
        # Group results by feature category
        auth_tests = [r for r in self.test_results if '/auth/' in r['endpoint']]
        admin_tests = [r for r in self.test_results if '/support/admin/' in r['endpoint']]
        agent_tests = [r for r in self.test_results if '/support/agents/' in r['endpoint']]
        chat_tests = [r for r in self.test_results if '/support/live-chat/' in r['endpoint']]
        ai_tests = [r for r in self.test_results if '/support/ai-guidance/' in r['endpoint']]
        kb_tests = [r for r in self.test_results if '/support/knowledge-base/' in r['endpoint']]
        escalation_tests = [r for r in self.test_results if '/support/escalation/' in r['endpoint'] or '/support/satisfaction/' in r['endpoint'] or '/support/analytics/' in r['endpoint']]
        
        def print_category_results(category_name, tests):
            if tests:
                passed = sum(1 for t in tests if t['success'])
                total = len(tests)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"\n   {category_name}: {passed}/{total} ({rate:.1f}%)")
                for test in tests:
                    status_icon = "✅" if test['success'] else "❌"
                    print(f"     {status_icon} {test['method']} {test['endpoint']} - {test['status']} ({test['response_time']})")
        
        print_category_results("🔐 AUTHENTICATION", auth_tests)
        print_category_results("📊 SUPPORT ADMIN DASHBOARD", admin_tests)
        print_category_results("👥 AGENT MANAGEMENT", agent_tests)
        print_category_results("💬 LIVE CHAT SYSTEM", chat_tests)
        print_category_results("🤖 AI GUIDANCE", ai_tests)
        print_category_results("📚 KNOWLEDGE BASE", kb_tests)
        print_category_results("⚡ ESCALATION & SATISFACTION", escalation_tests)
        
        # Performance metrics
        successful_tests = [r for r in self.test_results if r['success']]
        if successful_tests:
            response_times = [float(r['response_time'].replace('s', '')) for r in successful_tests]
            avg_response_time = sum(response_times) / len(response_times)
            fastest_response = min(response_times)
            slowest_response = max(response_times)
            total_data = sum(r['data_size'] for r in successful_tests)
            
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Fastest Response: {fastest_response:.3f}s")
            print(f"   Slowest Response: {slowest_response:.3f}s")
            print(f"   Total Data Processed: {total_data:,} bytes")
        
        # Support system capabilities assessment
        print(f"\n🎯 SUPPORT SYSTEM CAPABILITIES VERIFIED:")
        capabilities = [
            ("Support Admin Dashboard", any(t['success'] for t in admin_tests)),
            ("Agent Management", any(t['success'] for t in agent_tests)),
            ("Live Chat System", any(t['success'] for t in chat_tests)),
            ("AI-Powered Guidance", any(t['success'] for t in ai_tests)),
            ("Knowledge Base Search", any(t['success'] for t in kb_tests)),
            ("Escalation & Satisfaction", any(t['success'] for t in escalation_tests))
        ]
        
        for capability, working in capabilities:
            status = "✅ WORKING" if working else "❌ NOT WORKING"
            print(f"   - {capability}: {status}")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 90:
            print(f"   ✅ EXCELLENT - Phase 3 Support System is production-ready!")
            print(f"   🚀 Comprehensive support system with live chat and AI guidance operational")
        elif success_rate >= 75:
            print(f"   ⚠️  GOOD - Most support features working, minor issues to address")
        elif success_rate >= 50:
            print(f"   ⚠️  MODERATE - Significant support system issues need attention")
        else:
            print(f"   ❌ CRITICAL - Major support system issues require immediate attention")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"="*80)

if __name__ == "__main__":
    tester = SupportSystemTester()
    tester.run_comprehensive_support_test()