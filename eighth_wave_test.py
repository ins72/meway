#!/usr/bin/env python3
"""
EIGHTH WAVE TEMPLATE MARKETPLACE & AI CONTENT GENERATION TESTING
Testing newly integrated Template Marketplace and AI Content Generation systems
Testing Agent - December 2024
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://e0710948-4e96-4e5f-9b39-4059da05c0de.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials from review request
ADMIN_EMAIL = "tmonnens@outlook.com"
ADMIN_PASSWORD = "Voetballen5"

class EighthWaveTester:
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
        print("\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        
        auth_data = {
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        start_time = time.time()
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("/auth/login", "POST", response.status_code, response_time, True, 
                            f"Admin authentication successful - Token: {self.auth_token[:20]}...")
                return True
            else:
                self.log_test("/auth/login", "POST", response.status_code, response_time, False, 
                            f"Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("/auth/login", "POST", 0, response_time, False, f"Authentication error: {str(e)}")
            return False

    def test_template_marketplace_system(self):
        """Test Template Marketplace System endpoints"""
        print("\n🎨 TESTING TEMPLATE MARKETPLACE SYSTEM...")
        
        # Test GET /api/templates/marketplace
        self.test_get_endpoint("/templates/marketplace", "Template marketplace with filtering")
        
        # Test GET /api/templates/marketplace/featured
        self.test_get_endpoint("/templates/marketplace/featured", "Featured templates")
        
        # Test GET /api/templates/marketplace/categories
        self.test_get_endpoint("/templates/marketplace/categories", "Template categories with statistics")
        
        # Test POST /api/templates/create
        template_data = {
            "name": "Professional Business Template",
            "description": "A comprehensive business template for professional use with modern design elements",
            "category": "business",
            "price": 29.99,
            "tags": ["business", "professional", "modern"],
            "template_data": {
                "layout": "modern",
                "colors": ["#007bff", "#ffffff", "#f8f9fa"],
                "sections": ["header", "hero", "features", "testimonials", "footer"]
            },
            "is_public": True
        }
        self.test_post_endpoint("/templates/create", template_data, "Template creation")
        
        # Test GET /api/templates/my-templates
        self.test_get_endpoint("/templates/my-templates", "User's templates")
        
        # Test GET /api/templates/analytics/dashboard
        self.test_get_endpoint("/templates/analytics/dashboard", "Creator analytics dashboard")
        
        # Test GET /api/templates/collections
        self.test_get_endpoint("/templates/collections", "Template collections")
        
        # Test GET /api/templates/search
        self.test_get_endpoint("/templates/search?query=business&category=website", "Template search functionality")

    def test_ai_content_generation_system(self):
        """Test AI Content Generation System endpoints"""
        print("\n🤖 TESTING AI CONTENT GENERATION SYSTEM...")
        
        # Test GET /api/ai-content/services
        self.test_get_endpoint("/ai-content/services", "Available AI services")
        
        # Test POST /api/ai-content/generate-content
        content_request = {
            "type": "blog_post",
            "prompt": "Write a comprehensive guide about digital marketing strategies for small businesses",
            "tone": "professional",
            "length": "medium",
            "keywords": ["digital marketing", "small business", "online presence"],
            "target_audience": "small business owners",
            "additional_context": "Focus on cost-effective strategies and practical implementation"
        }
        self.test_post_endpoint("/ai-content/generate-content", content_request, "AI content generation")
        
        # Test POST /api/ai-content/optimize-seo
        seo_request = {
            "content": "Digital marketing is essential for small businesses to grow their online presence and reach more customers. This comprehensive guide covers the most effective strategies that won't break the bank.",
            "target_keywords": ["digital marketing", "small business", "online presence"],
            "meta_title": "Digital Marketing Guide for Small Businesses",
            "meta_description": "Learn cost-effective digital marketing strategies to grow your small business online"
        }
        self.test_post_endpoint("/ai-content/optimize-seo", seo_request, "SEO optimization")
        
        # Test POST /api/ai-content/generate-image
        image_request = {
            "prompt": "Professional business team working together in a modern office environment",
            "style": "professional",
            "size": "1024x1024",
            "quality": "standard"
        }
        self.test_post_endpoint("/ai-content/generate-image", image_request, "AI image generation")
        
        # Test GET /api/ai-content/conversations
        self.test_get_endpoint("/ai-content/conversations", "User conversations")
        
        # Test POST /api/ai-content/conversations
        conversation_data = {
            "title": "Marketing Strategy Discussion",
            "model": "gpt-4",
            "system_prompt": "You are a marketing expert helping with business strategy"
        }
        self.test_post_endpoint("/ai-content/conversations", conversation_data, "Conversation creation")
        
        # Test GET /api/ai-content/content-templates
        self.test_get_endpoint("/ai-content/content-templates", "Content templates")
        
        # Test GET /api/ai-content/analytics
        self.test_get_endpoint("/ai-content/analytics", "AI usage analytics")

    def test_get_endpoint(self, endpoint, description):
        """Test GET endpoint"""
        start_time = time.time()
        try:
            response = self.session.get(f"{API_BASE}{endpoint}", timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                data_size = len(response.text)
                self.log_test(endpoint, "GET", response.status_code, response_time, True, 
                            f"{description} - {data_size} chars", data_size)
            else:
                self.log_test(endpoint, "GET", response.status_code, response_time, False, 
                            f"{description} failed: {response.text[:100]}")
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(endpoint, "GET", 0, response_time, False, f"{description} error: {str(e)}")

    def test_post_endpoint(self, endpoint, data, description):
        """Test POST endpoint"""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{API_BASE}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                data_size = len(response.text)
                self.log_test(endpoint, "POST", response.status_code, response_time, True, 
                            f"{description} successful - {data_size} chars", data_size)
            else:
                self.log_test(endpoint, "POST", response.status_code, response_time, False, 
                            f"{description} failed: {response.text[:100]}")
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(endpoint, "POST", 0, response_time, False, f"{description} error: {str(e)}")

    def run_comprehensive_test(self):
        """Run comprehensive Eighth Wave testing"""
        print("🌊 STARTING COMPREHENSIVE EIGHTH WAVE TESTING...")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing with credentials: {ADMIN_EMAIL}")
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return
        
        # Test Template Marketplace System
        self.test_template_marketplace_system()
        
        # Test AI Content Generation System
        self.test_ai_content_generation_system()
        
        # Print comprehensive results
        self.print_results()

    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("🌊 EIGHTH WAVE COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Calculate performance metrics
        response_times = [float(result['response_time'].replace('s', '')) for result in self.test_results if result['success']]
        total_data = sum(result['data_size'] for result in self.test_results if result['success'])
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Total Data Processed: {total_data:,} bytes")
        
        print(f"\n📋 DETAILED RESULTS:")
        
        # Group by system
        template_tests = [r for r in self.test_results if '/templates/' in r['endpoint']]
        ai_content_tests = [r for r in self.test_results if '/ai-content/' in r['endpoint']]
        
        if template_tests:
            template_success = sum(1 for r in template_tests if r['success'])
            print(f"\n🎨 TEMPLATE MARKETPLACE SYSTEM ({template_success}/{len(template_tests)} passed):")
            for result in template_tests:
                status_icon = "✅" if result['success'] else "❌"
                print(f"   {status_icon} {result['method']} {result['endpoint']} - {result['details']}")
        
        if ai_content_tests:
            ai_success = sum(1 for r in ai_content_tests if r['success'])
            print(f"\n🤖 AI CONTENT GENERATION SYSTEM ({ai_success}/{len(ai_content_tests)} passed):")
            for result in ai_content_tests:
                status_icon = "✅" if result['success'] else "❌"
                print(f"   {status_icon} {result['method']} {result['endpoint']} - {result['details']}")
        
        print("\n" + "="*80)
        print(f"🌊 EIGHTH WAVE TESTING COMPLETED - {success_rate:.1f}% SUCCESS RATE")
        print("="*80)

if __name__ == "__main__":
    tester = EighthWaveTester()
    tester.run_comprehensive_test()