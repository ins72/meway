#!/usr/bin/env python3
"""
COMPREHENSIVE TENTH WAVE TESTING - MEWAYZ PLATFORM
Testing Automation System, Advanced AI Suite, and Support System APIs
Testing Agent - December 2024
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://d55219c2-be62-4fb2-bebf-b616faedf109.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class TenthWaveTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
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
        print(f"Backend URL: {BACKEND_URL}")
        
        start_time = time.time()
        try:
            # Use OAuth2PasswordRequestForm format
            auth_data = {
                "username": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=auth_data,  # Use data instead of json for form data
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                auth_result = response.json()
                self.auth_token = auth_result.get("access_token")
                
                if self.auth_token:
                    # Set authorization header for all future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}",
                        "Content-Type": "application/json"
                    })
                    
                    self.log_test("/auth/login", "POST", 200, response_time, True, 
                                f"Authentication successful - Token received")
                    print(f"✅ Authentication successful!")
                    return True
                else:
                    self.log_test("/auth/login", "POST", 200, response_time, False, 
                                "No access token in response")
                    return False
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Authentication failed: {response.text[:200]}")
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/auth/login", "POST", 0, response_time, False, f"Exception: {str(e)}")
            return False

    def test_automation_system(self):
        """Test Automation System APIs"""
        print(f"\n🤖 TESTING AUTOMATION SYSTEM APIs...")
        
        automation_endpoints = [
            # Workflow Management
            ("/automation/workflows/advanced", "GET", "Advanced workflow automation system"),
            ("/automation/workflows", "GET", "User's automation workflows with filtering"),
            ("/automation/triggers/available", "GET", "Available automation triggers"),
            ("/automation/actions/available", "GET", "Available automation actions"),
            ("/automation/analytics/dashboard", "GET", "Automation analytics dashboard"),
            
            # Templates and Performance
            ("/automation/templates", "GET", "Pre-built workflow templates"),
            ("/automation/executions/history", "GET", "Workflow execution history"),
            ("/automation/performance/metrics", "GET", "Automation performance metrics"),
            ("/automation/integrations/available", "GET", "Available third-party integrations"),
        ]
        
        for endpoint, method, description in automation_endpoints:
            self.test_endpoint(endpoint, method, description)
            
        # Test POST endpoints
        self.test_automation_post_endpoints()

    def test_automation_post_endpoints(self):
        """Test Automation System POST endpoints"""
        
        # Test workflow creation
        workflow_data = {
            "name": "Test Lead Nurturing Workflow",
            "description": "Automated lead nurturing sequence for new prospects",
            "trigger_type": "form_submission",
            "trigger_conditions": {
                "form_id": "contact_form",
                "page_url": "/contact"
            },
            "actions": [
                {
                    "type": "send_email",
                    "template": "welcome_email",
                    "delay": 0
                },
                {
                    "type": "add_tag",
                    "tag": "new_lead",
                    "delay": 300
                }
            ],
            "enabled": True
        }
        
        self.test_post_endpoint("/automation/workflows/create", workflow_data, 
                              "Create automation workflow")
        
        # Test automation rule creation
        rule_data = {
            "name": "High-Value Lead Alert",
            "trigger": {
                "type": "score_threshold",
                "threshold": 80
            },
            "conditions": [
                {
                    "field": "lead_score",
                    "operator": "greater_than",
                    "value": 80
                }
            ],
            "actions": [
                {
                    "type": "slack_notification",
                    "channel": "#sales",
                    "message": "High-value lead detected!"
                }
            ]
        }
        
        self.test_post_endpoint("/automation/rules/create", rule_data,
                              "Create automation rule")

    def test_advanced_ai_suite(self):
        """Test Advanced AI Suite APIs"""
        print(f"\n🧠 TESTING ADVANCED AI SUITE APIs...")
        
        ai_endpoints = [
            # Video AI Services
            ("/advanced-ai/video/services", "GET", "Advanced AI video processing services"),
            
            # Voice AI Services  
            ("/advanced-ai/voice/services", "GET", "Voice AI processing services"),
            
            # Image AI Services
            ("/advanced-ai/image/services", "GET", "Image AI processing services"),
            
            # NLP Services
            ("/advanced-ai/nlp/services", "GET", "Natural Language Processing services"),
            
            # AI Models and Analytics
            ("/advanced-ai/models/available", "GET", "Available AI models and capabilities"),
            ("/advanced-ai/usage/analytics", "GET", "AI service usage analytics"),
            ("/advanced-ai/processing/queue", "GET", "Current processing queue status"),
            ("/advanced-ai/innovations/latest", "GET", "Latest AI innovations and features"),
        ]
        
        for endpoint, method, description in ai_endpoints:
            self.test_endpoint(endpoint, method, description)
            
        # Test POST endpoints
        self.test_ai_post_endpoints()

    def test_ai_post_endpoints(self):
        """Test Advanced AI Suite POST endpoints"""
        
        # Test video analysis
        video_analysis_data = {
            "video_url": "https://example.com/sample-video.mp4",
            "analysis_type": ["engagement", "transcription", "sentiment"],
            "language": "en"
        }
        
        self.test_post_endpoint("/advanced-ai/video/analyze", video_analysis_data,
                              "Analyze video content with AI")
        
        # Test voice synthesis
        voice_data = {
            "text": "Welcome to our advanced AI platform. This is a test of our voice synthesis capabilities.",
            "voice_id": "professional_female",
            "language": "en",
            "speed": 1.0,
            "emotion": "friendly"
        }
        
        self.test_form_post_endpoint("/advanced-ai/voice/synthesize", voice_data,
                                   "Synthesize speech from text")
        
        # Test image generation
        image_data = {
            "prompt": "A professional business meeting in a modern office with diverse team members collaborating",
            "style": "realistic",
            "resolution": "1024x1024",
            "variations": 2
        }
        
        self.test_form_post_endpoint("/advanced-ai/image/generate", image_data,
                                   "Generate images from text prompt")
        
        # Test NLP analysis
        nlp_data = {
            "text": "Our quarterly revenue exceeded expectations by 15%, driven by strong performance in the enterprise segment and successful product launches.",
            "analysis_types": "sentiment,entities,topics",
            "language": "auto"
        }
        
        self.test_form_post_endpoint("/advanced-ai/nlp/analyze", nlp_data,
                                   "Analyze text using NLP")
        
        # Test batch processing
        batch_data = [
            {
                "service_type": "text_analysis",
                "input_data": {"text": "Sample text for analysis"},
                "processing_options": {"include_sentiment": True},
                "priority": "normal"
            },
            {
                "service_type": "image_enhancement",
                "input_data": {"image_url": "https://example.com/image.jpg"},
                "processing_options": {"upscale_factor": 2},
                "priority": "high"
            }
        ]
        
        self.test_post_endpoint("/advanced-ai/batch/process", batch_data,
                              "Process multiple AI requests in batch")

    def test_support_system(self):
        """Test Support System APIs"""
        print(f"\n🎧 TESTING SUPPORT SYSTEM APIs...")
        
        support_endpoints = [
            # Support Dashboard and Tickets
            ("/support/dashboard", "GET", "Support system dashboard"),
            ("/support/tickets", "GET", "User's support tickets with filtering"),
            ("/support/categories", "GET", "Available support categories"),
            
            # Knowledge Base and FAQ
            ("/support/knowledge-base", "GET", "Knowledge base articles"),
            ("/support/faq", "GET", "Frequently asked questions"),
            
            # Live Chat and Communication
            ("/support/live-chat/status", "GET", "Live chat availability status"),
            
            # Analytics and System Health
            ("/support/analytics/dashboard", "GET", "Support analytics dashboard"),
            ("/support/escalation/rules", "GET", "Support escalation rules and procedures"),
            ("/support/system/health", "GET", "Support system health and status"),
            
            # Training and Community
            ("/support/training/materials", "GET", "Training materials and tutorials"),
            ("/support/community/forum", "GET", "Community forum information"),
            ("/support/feedback/surveys", "GET", "Available feedback surveys"),
        ]
        
        for endpoint, method, description in support_endpoints:
            self.test_endpoint(endpoint, method, description)
            
        # Test POST endpoints
        self.test_support_post_endpoints()

    def test_support_post_endpoints(self):
        """Test Support System POST endpoints"""
        
        # Test ticket creation
        ticket_data = {
            "subject": "Integration Issue with Advanced AI Suite",
            "description": "I'm experiencing difficulties integrating the Advanced AI Suite with my existing workflow. The API calls are returning unexpected responses and I need assistance with proper configuration.",
            "category": "technical",
            "priority": "high",
            "urgency": "normal"
        }
        
        self.test_post_endpoint("/support/tickets/create", ticket_data,
                              "Create a new support ticket")
        
        # Test live chat initiation
        chat_data = {
            "message": "Hello, I need help with setting up automation workflows for my e-commerce business.",
            "department": "technical"
        }
        
        self.test_form_post_endpoint("/support/live-chat/initiate", chat_data,
                                   "Initiate a live chat session")
        
        # Test feedback submission
        feedback_data = {
            "survey_id": "customer_satisfaction_2024",
            "responses": json.dumps({
                "overall_satisfaction": 4,
                "feature_usefulness": 5,
                "support_quality": 4,
                "recommendation_likelihood": 4
            }),
            "rating": 4,
            "additional_comments": "Great platform with excellent AI capabilities. Support team is very responsive and helpful."
        }
        
        self.test_form_post_endpoint("/support/feedback/submit", feedback_data,
                                   "Submit feedback survey")

    def test_endpoint(self, endpoint, method, description):
        """Test a single GET endpoint"""
        start_time = time.time()
        try:
            url = f"{API_BASE}{endpoint}"
            response = self.session.get(url, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    data_size = len(response.content)
                    
                    # Check if response has expected structure
                    if isinstance(data, dict) and ('success' in data or 'data' in data or len(data) > 0):
                        self.log_test(endpoint, method, 200, response_time, True, 
                                    f"{description} ({data_size} chars)", data_size)
                    else:
                        self.log_test(endpoint, method, 200, response_time, False, 
                                    f"Invalid response structure")
                except json.JSONDecodeError:
                    self.log_test(endpoint, method, 200, response_time, False, 
                                "Invalid JSON response")
            else:
                self.log_test(endpoint, method, response.status_code, response_time, False, 
                            f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(endpoint, method, 0, response_time, False, f"Exception: {str(e)}")

    def test_post_endpoint(self, endpoint, data, description):
        """Test a POST endpoint with JSON data"""
        start_time = time.time()
        try:
            url = f"{API_BASE}{endpoint}"
            response = self.session.post(url, json=data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    data_size = len(response.content)
                    self.log_test(endpoint, "POST", response.status_code, response_time, True, 
                                f"{description} ({data_size} chars)", data_size)
                except json.JSONDecodeError:
                    self.log_test(endpoint, "POST", response.status_code, response_time, False, 
                                "Invalid JSON response")
            else:
                self.log_test(endpoint, "POST", response.status_code, response_time, False, 
                            f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(endpoint, "POST", 0, response_time, False, f"Exception: {str(e)}")

    def test_form_post_endpoint(self, endpoint, data, description):
        """Test a POST endpoint with form data"""
        start_time = time.time()
        try:
            url = f"{API_BASE}{endpoint}"
            # Temporarily change content type for form data
            original_headers = self.session.headers.copy()
            self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
            
            response = self.session.post(url, data=data, timeout=30)
            response_time = time.time() - start_time
            
            # Restore original headers
            self.session.headers.update(original_headers)
            
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    data_size = len(response.content)
                    self.log_test(endpoint, "POST", response.status_code, response_time, True, 
                                f"{description} ({data_size} chars)", data_size)
                except json.JSONDecodeError:
                    self.log_test(endpoint, "POST", response.status_code, response_time, False, 
                                "Invalid JSON response")
            else:
                self.log_test(endpoint, "POST", response.status_code, response_time, False, 
                            f"HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(endpoint, "POST", 0, response_time, False, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run comprehensive Tenth Wave testing"""
        print("=" * 80)
        print("🌊 COMPREHENSIVE TENTH WAVE TESTING - MEWAYZ PLATFORM")
        print("Testing: Automation System, Advanced AI Suite, Support System")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return False
            
        # Step 2: Test all three Tenth Wave systems
        self.test_automation_system()
        self.test_advanced_ai_suite()
        self.test_support_system()
        
        # Step 3: Generate comprehensive report
        self.generate_report()
        
        return True

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 TENTH WAVE TESTING RESULTS SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"✅ Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Calculate average response time
        response_times = []
        total_data_size = 0
        
        for result in self.test_results:
            if result['success']:
                try:
                    response_times.append(float(result['response_time'].replace('s', '')))
                    total_data_size += result['data_size']
                except:
                    pass
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"⚡ Average Response Time: {avg_response_time:.3f}s")
            print(f"📦 Total Data Processed: {total_data_size:,} bytes")
        
        # System-specific results
        automation_tests = [r for r in self.test_results if '/automation/' in r['endpoint']]
        ai_tests = [r for r in self.test_results if '/advanced-ai/' in r['endpoint']]
        support_tests = [r for r in self.test_results if '/support/' in r['endpoint']]
        
        print(f"\n🤖 AUTOMATION SYSTEM: {sum(1 for r in automation_tests if r['success'])}/{len(automation_tests)} passed")
        print(f"🧠 ADVANCED AI SUITE: {sum(1 for r in ai_tests if r['success'])}/{len(ai_tests)} passed")
        print(f"🎧 SUPPORT SYSTEM: {sum(1 for r in support_tests if r['success'])}/{len(support_tests)} passed")
        
        # Failed tests summary
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['method']} {test['endpoint']} - {test['details']}")
        
        print("\n" + "=" * 80)
        print("🌊 TENTH WAVE TESTING COMPLETED")
        print("=" * 80)

def main():
    """Main testing function"""
    tester = TenthWaveTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n✅ Tenth Wave testing completed successfully!")
        return 0
    else:
        print(f"\n❌ Tenth Wave testing failed!")
        return 1

if __name__ == "__main__":
    exit(main())