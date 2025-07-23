#!/usr/bin/env python3
"""
COMPREHENSIVE ELEVENTH WAVE TESTING - MEWAYZ PLATFORM
Testing ELEVENTH WAVE Content Creation Suite, Customer Experience Suite & Social Media Suite
Testing Agent - December 2024
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://a13c5910-1933-45cf-94c7-fffa5182db3b.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class EleventhWaveTester:
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
        
        login_data = {
            "username": ADMIN_EMAIL,  # FastAPI OAuth2PasswordRequestForm uses 'username'
            "password": ADMIN_PASSWORD
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/auth/login", data=login_data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
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
    
    def test_endpoint(self, endpoint, method="GET", data=None, form_data=None, expected_status=200, description=""):
        """Test a single endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                if form_data:
                    response = self.session.post(url, data=form_data, timeout=30)
                else:
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

    def test_content_creation_suite(self):
        """Test ELEVENTH WAVE - CONTENT CREATION SUITE"""
        print(f"\n🌊 TESTING ELEVENTH WAVE - CONTENT CREATION SUITE")
        
        # 1. Video Editor Features and Capabilities
        print(f"\n🎬 Testing Video Editor Features...")
        self.test_endpoint("/content-creation/video-editor/features", "GET", 
                          description="Advanced video editing features and capabilities")
        
        # 2. Video Project Management
        print(f"\n📹 Testing Video Project Management...")
        self.test_endpoint("/content-creation/video-editor/projects", "GET", 
                          description="Get user's video editing projects")
        
        # Test video project creation
        project_data = {
            "name": "Marketing Campaign Video",
            "description": "Promotional video for new product launch",
            "resolution": "1080p",
            "duration_limit": 300
        }
        self.test_endpoint("/content-creation/video-editor/projects/create", "POST", 
                          data=project_data, description="Create new video editing project")
        
        # 3. Video Templates
        self.test_endpoint("/content-creation/video-editor/templates", "GET", 
                          description="Get video editing templates")
        
        # 4. AI Content Generation Capabilities
        print(f"\n🤖 Testing AI Content Generation...")
        self.test_endpoint("/content-creation/content-generator/capabilities", "GET", 
                          description="Get AI content generation capabilities")
        
        # Test text content generation
        text_form_data = {
            "content_type": "blog_post",
            "topic": "Digital Marketing Trends 2024",
            "tone": "professional",
            "length": "medium",
            "keywords": "SEO, social media, content marketing"
        }
        self.test_endpoint("/content-creation/content-generator/text/generate", "POST", 
                          form_data=text_form_data, description="Generate text content using AI")
        
        # Test image content generation
        image_form_data = {
            "description": "Modern office workspace with laptop and coffee",
            "style": "photorealistic",
            "resolution": "1024x1024",
            "variations": 1
        }
        self.test_endpoint("/content-creation/content-generator/image/generate", "POST", 
                          form_data=image_form_data, description="Generate image content using AI")
        
        # 5. Asset Library Management
        print(f"\n📚 Testing Asset Library...")
        self.test_endpoint("/content-creation/asset-library", "GET", 
                          description="Get content asset library")
        
        # 6. Template Marketplace
        print(f"\n🏪 Testing Template Marketplace...")
        self.test_endpoint("/content-creation/templates/marketplace", "GET", 
                          description="Get template marketplace")
        
        # Test template creation
        template_data = {
            "name": "Social Media Post Template",
            "category": "social_media",
            "content_type": "image_post",
            "template_data": {
                "dimensions": "1080x1080",
                "style": "modern",
                "elements": ["text", "image", "logo"]
            },
            "tags": ["social", "marketing", "modern"]
        }
        self.test_endpoint("/content-creation/templates/create", "POST", 
                          data=template_data, description="Create custom content template")
        
        # 7. Content Performance Analytics
        print(f"\n📊 Testing Content Analytics...")
        self.test_endpoint("/content-creation/analytics/content-performance", "GET", 
                          description="Get content performance analytics")
        
        # 8. Collaboration Features
        print(f"\n👥 Testing Collaboration Features...")
        self.test_endpoint("/content-creation/collaboration/projects", "GET", 
                          description="Get collaborative content projects")
        
        # Test collaborator invitation
        collab_form_data = {
            "project_id": "test-project-123",
            "email": "collaborator@example.com",
            "role": "editor"
        }
        self.test_endpoint("/content-creation/collaboration/invite", "POST", 
                          form_data=collab_form_data, description="Invite collaborator to content project")
        
        # 9. Workflow Automation
        print(f"\n⚙️ Testing Workflow Automation...")
        self.test_endpoint("/content-creation/workflow/automation", "GET", 
                          description="Get content workflow automation options")

    def test_customer_experience_suite(self):
        """Test ELEVENTH WAVE - CUSTOMER EXPERIENCE SUITE"""
        print(f"\n🌊 TESTING ELEVENTH WAVE - CUSTOMER EXPERIENCE SUITE")
        
        # 1. Live Chat Overview and Management
        print(f"\n💬 Testing Live Chat System...")
        self.test_endpoint("/customer-experience/live-chat/overview", "GET", 
                          description="Live chat system overview and analytics")
        
        self.test_endpoint("/customer-experience/live-chat/agents", "GET", 
                          description="Get chat agents status and performance")
        
        # Test chat session creation
        chat_data = {
            "department": "support",
            "initial_message": "I need help with my account settings",
            "customer_info": {
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }
        self.test_endpoint("/customer-experience/live-chat/session/start", "POST", 
                          data=chat_data, description="Start new live chat session")
        
        # 2. Chat History
        self.test_endpoint("/customer-experience/live-chat/history", "GET", 
                          description="Get chat history for user")
        
        # 3. Customer Journey Analytics
        print(f"\n🗺️ Testing Customer Journey Analytics...")
        self.test_endpoint("/customer-experience/customer-journey/analytics", "GET", 
                          description="Get customer journey analytics and insights")
        
        self.test_endpoint("/customer-experience/customer-journey/mapping", "GET", 
                          description="Get customer journey mapping data")
        
        # 4. Feedback Surveys Management
        print(f"\n📝 Testing Feedback Surveys...")
        self.test_endpoint("/customer-experience/feedback/surveys", "GET", 
                          description="Get customer feedback surveys")
        
        # Test survey creation
        survey_data = {
            "title": "Customer Satisfaction Survey",
            "questions": [
                {
                    "type": "rating",
                    "question": "How satisfied are you with our service?",
                    "scale": 5
                },
                {
                    "type": "text",
                    "question": "What can we improve?"
                }
            ],
            "target_audience": "all",
            "trigger_conditions": {
                "after_purchase": True,
                "delay_days": 3
            }
        }
        self.test_endpoint("/customer-experience/feedback/surveys/create", "POST", 
                          data=survey_data, description="Create new feedback survey")
        
        # 5. Personalization Engine
        print(f"\n🎯 Testing Personalization Engine...")
        self.test_endpoint("/customer-experience/personalization/engine", "GET", 
                          description="Get personalization engine status and insights")
        
        # 6. Sentiment Analysis
        print(f"\n😊 Testing Sentiment Analysis...")
        self.test_endpoint("/customer-experience/sentiment/analysis", "GET", 
                          description="Get customer sentiment analysis")
        
        # 7. Experience Optimization
        print(f"\n🚀 Testing Experience Optimization...")
        self.test_endpoint("/customer-experience/experience/optimization", "GET", 
                          description="Get customer experience optimization suggestions")
        
        # 8. Comprehensive CX Analytics Dashboard
        print(f"\n📊 Testing CX Analytics Dashboard...")
        self.test_endpoint("/customer-experience/analytics/dashboard", "GET", 
                          description="Get comprehensive customer experience analytics dashboard")

    def test_social_media_suite(self):
        """Test ELEVENTH WAVE - SOCIAL MEDIA SUITE"""
        print(f"\n🌊 TESTING ELEVENTH WAVE - SOCIAL MEDIA SUITE")
        
        # 1. Social Listening Overview and Mentions
        print(f"\n👂 Testing Social Listening...")
        self.test_endpoint("/social-media/listening/overview", "GET", 
                          description="Social media listening and monitoring overview")
        
        self.test_endpoint("/social-media/listening/mentions", "GET", 
                          description="Get brand mentions across social media platforms")
        
        # 2. Sentiment Analysis and Competitor Analysis
        print(f"\n📈 Testing Sentiment & Competitor Analysis...")
        self.test_endpoint("/social-media/listening/sentiment", "GET", 
                          description="Get social media sentiment analysis")
        
        self.test_endpoint("/social-media/listening/competitors", "GET", 
                          description="Get competitor social media analysis")
        
        # 3. Publishing Calendar and Post Creation
        print(f"\n📅 Testing Publishing Calendar...")
        self.test_endpoint("/social-media/publishing/calendar", "GET", 
                          description="Get social media publishing calendar")
        
        self.test_endpoint("/social-media/publishing/posts", "GET", 
                          description="Get social media posts with filtering")
        
        # Test social post creation
        post_data = {
            "content": "Excited to announce our new product launch! 🚀 #innovation #technology",
            "platforms": ["twitter", "facebook", "linkedin"],
            "hashtags": ["innovation", "technology", "launch"],
            "media_urls": []
        }
        self.test_endpoint("/social-media/publishing/posts/create", "POST", 
                          data=post_data, description="Create and schedule social media post")
        
        # 4. Social Media Performance Analytics
        print(f"\n📊 Testing Performance Analytics...")
        self.test_endpoint("/social-media/analytics/performance", "GET", 
                          description="Get social media performance analytics")
        
        # 5. Engagement Analytics
        print(f"\n💬 Testing Engagement Analytics...")
        self.test_endpoint("/social-media/analytics/engagement", "GET", 
                          description="Get detailed engagement analytics")
        
        # 6. Influencer Discovery and Campaigns
        print(f"\n🌟 Testing Influencer Features...")
        self.test_endpoint("/social-media/influencer/discovery", "GET", 
                          description="Discover relevant influencers for collaboration")
        
        self.test_endpoint("/social-media/influencer/campaigns", "GET", 
                          description="Get influencer collaboration campaigns")
        
        # Test campaign creation
        campaign_data = {
            "name": "Summer Product Launch Campaign",
            "description": "Promote our new summer collection",
            "platforms": ["instagram", "tiktok"],
            "start_date": "2024-06-01T00:00:00",
            "end_date": "2024-06-30T23:59:59",
            "budget": 5000.0
        }
        self.test_endpoint("/social-media/campaigns/create", "POST", 
                          data=campaign_data, description="Create new social media campaign")
        
        # 7. Automation Rules
        print(f"\n⚙️ Testing Automation Rules...")
        self.test_endpoint("/social-media/automation/rules", "GET", 
                          description="Get social media automation rules")
        
        # 8. Trends Analysis and Comprehensive Reporting
        print(f"\n📈 Testing Trends & Reporting...")
        self.test_endpoint("/social-media/trends/analysis", "GET", 
                          description="Get social media trends analysis")
        
        self.test_endpoint("/social-media/reporting/comprehensive", "GET", 
                          description="Get comprehensive social media reporting")

    def run_comprehensive_test(self):
        """Run comprehensive test of all Eleventh Wave systems"""
        print("=" * 80)
        print("🌊 COMPREHENSIVE ELEVENTH WAVE TESTING - MEWAYZ PLATFORM")
        print("Testing Content Creation Suite, Customer Experience Suite & Social Media Suite")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return False
        
        print(f"\n✅ Authentication successful! Testing all Eleventh Wave systems...")
        
        # Test all three Eleventh Wave systems
        self.test_content_creation_suite()
        self.test_customer_experience_suite()
        self.test_social_media_suite()
        
        # Print comprehensive results
        self.print_results()
        
        return self.passed_tests == self.total_tests

    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🌊 ELEVENTH WAVE TESTING RESULTS SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Calculate total data processed
        total_data_size = sum(result['data_size'] for result in self.test_results if result['success'])
        print(f"   Total Data Processed: {total_data_size:,} bytes")
        
        # Calculate average response time
        successful_tests = [result for result in self.test_results if result['success']]
        if successful_tests:
            avg_response_time = sum(float(result['response_time'].replace('s', '')) for result in successful_tests) / len(successful_tests)
            print(f"   Average Response Time: {avg_response_time:.3f}s")
        
        print(f"\n🌊 ELEVENTH WAVE SYSTEMS TESTED:")
        
        # Content Creation Suite Results
        content_tests = [r for r in self.test_results if '/content-creation/' in r['endpoint']]
        content_passed = sum(1 for r in content_tests if r['success'])
        print(f"   ✅ Content Creation Suite: {content_passed}/{len(content_tests)} tests passed")
        
        # Customer Experience Suite Results
        cx_tests = [r for r in self.test_results if '/customer-experience/' in r['endpoint']]
        cx_passed = sum(1 for r in cx_tests if r['success'])
        print(f"   ✅ Customer Experience Suite: {cx_passed}/{len(cx_tests)} tests passed")
        
        # Social Media Suite Results
        social_tests = [r for r in self.test_results if '/social-media/' in r['endpoint']]
        social_passed = sum(1 for r in social_tests if r['success'])
        print(f"   ✅ Social Media Suite: {social_passed}/{len(social_tests)} tests passed")
        
        # Show failed tests if any
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   {test['method']} {test['endpoint']} - {test['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate == 100:
            print("🎉 ALL ELEVENTH WAVE SYSTEMS WORKING PERFECTLY!")
            print("✅ Content Creation Suite, Customer Experience Suite & Social Media Suite")
            print("✅ All endpoints operational with comprehensive business functionality")
            print("✅ Professional implementation ready for enterprise deployment")
        elif success_rate >= 90:
            print("✅ ELEVENTH WAVE SYSTEMS MOSTLY OPERATIONAL")
            print("⚠️  Minor issues detected - see failed tests above")
        else:
            print("❌ ELEVENTH WAVE SYSTEMS NEED ATTENTION")
            print("🔧 Multiple issues detected - review failed tests above")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = EleventhWaveTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All Eleventh Wave systems are working perfectly!")
        exit(0)
    else:
        print("\n⚠️  Some Eleventh Wave systems need attention.")
        exit(1)