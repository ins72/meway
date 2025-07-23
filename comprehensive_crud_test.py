#!/usr/bin/env python3
"""
COMPREHENSIVE CRUD VERIFICATION FOR MEWAYZ V2 PLATFORM - JANUARY 2025
Testing all 10 critical services mentioned in the review request:

1. complete_ecommerce_service (products)
2. complete_social_media_leads_service (leads)
3. advanced_template_marketplace_service (templates)
4. complete_financial_service (transactions)
5. complete_course_community_service (courses)
6. complete_multi_workspace_service (workspaces)
7. email_marketing_service (campaigns)
8. complete_booking_service (appointments)
9. complete_escrow_service (escrow transactions)
10. mobile_pwa_service (devices)

SUCCESS CRITERIA:
- All CRUD operations working for critical services
- No mock/hardcoded data in any responses
- All endpoints return 200 status codes
- Proper JSON response formats
- Authentication working across all endpoints
- Database operations completing successfully
"""

import requests
import json
import sys
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = "https://0b0b9ebf-d7aa-41df-aa42-dd8ab4b72b68.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class CRUDTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.created_resources = {}  # Track created resources for cleanup
        
    def log_result(self, test_name: str, success: bool, message: str, response_data: Any = None):
        """Log test result"""
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
    
    def authenticate(self):
        """Authenticate and get access token"""
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
                    self.log_result("Authentication", True, "Login successful - Token received", data)
                    return True
                else:
                    self.log_result("Authentication", False, "Login response missing access_token")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, test_name: str = None):
        """Make authenticated API request"""
        if not test_name:
            test_name = f"{method} {endpoint}"
            
        try:
            url = f"{API_BASE}{endpoint}"
            headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
            
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
                    return True, data
                except:
                    return True, response.text
            else:
                error_msg = f"Status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', response.text)}"
                except:
                    error_msg += f": {response.text}"
                return False, error_msg
                
        except Exception as e:
            return False, f"Request error: {str(e)}"
    
    def check_for_mock_data(self, data: Any, service_name: str) -> bool:
        """Check if response contains mock/hardcoded data"""
        data_str = str(data).lower()
        mock_indicators = [
            "sample", "mock", "test", "dummy", "fake", "example",
            "lorem ipsum", "placeholder", "default", "hardcoded"
        ]
        
        for indicator in mock_indicators:
            if indicator in data_str:
                self.log_result(f"{service_name} - Mock Data Check", False, f"MOCK DATA DETECTED: Contains '{indicator}'")
                return True
        
        self.log_result(f"{service_name} - Mock Data Check", True, "NO MOCK DATA: Response appears to use real data")
        return False
    
    def test_ecommerce_service(self):
        """Test complete_ecommerce_service (products)"""
        print("\n🛒 TESTING COMPLETE E-COMMERCE SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new product
        print("\n📦 Testing Product Creation (CREATE)...")
        product_data = {
            "name": "Premium Business Analytics Dashboard",
            "description": "Advanced analytics dashboard with real-time insights and custom reporting capabilities",
            "price": 299.99,
            "category": "software",
            "sku": f"PROD-{uuid.uuid4().hex[:8].upper()}",
            "stock_quantity": 50,
            "tags": ["analytics", "dashboard", "business", "premium"],
            "specifications": {
                "features": ["Real-time data", "Custom reports", "API integration"],
                "compatibility": ["Web", "Mobile", "Desktop"]
            }
        }
        
        success, response = self.make_request("POST", "/ecommerce/products", product_data, "E-commerce - Create Product")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "E-commerce CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["product_id"] = response["id"]
        
        # READ - Get products list
        print("\n📋 Testing Products List (READ)...")
        success, response = self.make_request("GET", "/ecommerce/products", test_name="E-commerce - Get Products")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "E-commerce READ")
        
        # READ - Get specific product
        if "product_id" in self.created_resources:
            success, response = self.make_request("GET", f"/ecommerce/products/{self.created_resources['product_id']}", 
                                                test_name="E-commerce - Get Product Details")
        
        # UPDATE - Update product
        print("\n✏️ Testing Product Update (UPDATE)...")
        if "product_id" in self.created_resources:
            update_data = {
                "name": "Premium Business Analytics Dashboard - Updated",
                "price": 349.99,
                "stock_quantity": 45
            }
            success, response = self.make_request("PUT", f"/ecommerce/products/{self.created_resources['product_id']}", 
                                                update_data, "E-commerce - Update Product")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "E-commerce UPDATE")
        
        # DELETE - Remove product
        print("\n🗑️ Testing Product Deletion (DELETE)...")
        if "product_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/ecommerce/products/{self.created_resources['product_id']}", 
                                                test_name="E-commerce - Delete Product")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_social_media_leads_service(self):
        """Test complete_social_media_leads_service (leads)"""
        print("\n📱 TESTING COMPLETE SOCIAL MEDIA LEADS SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new lead
        print("\n👤 Testing Lead Creation (CREATE)...")
        lead_data = {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@techstartup.com",
            "phone": "+1-555-0123",
            "company": "TechStartup Inc.",
            "position": "Marketing Director",
            "source": "twitter",
            "social_profiles": {
                "twitter": "@sarahj_marketing",
                "linkedin": "linkedin.com/in/sarahjohnson"
            },
            "lead_score": 85,
            "interests": ["digital marketing", "analytics", "automation"],
            "notes": "Highly engaged with our content, potential enterprise client"
        }
        
        success, response = self.make_request("POST", "/social-media-leads/leads", lead_data, "Social Media Leads - Create Lead")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Social Media Leads CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["lead_id"] = response["id"]
        
        # READ - Get leads list
        print("\n📋 Testing Leads List (READ)...")
        success, response = self.make_request("GET", "/social-media-leads/leads", test_name="Social Media Leads - Get Leads")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Social Media Leads READ")
        
        # UPDATE - Update lead
        print("\n✏️ Testing Lead Update (UPDATE)...")
        if "lead_id" in self.created_resources:
            update_data = {
                "lead_score": 90,
                "status": "qualified",
                "notes": "Scheduled demo call for next week"
            }
            success, response = self.make_request("PUT", f"/social-media-leads/leads/{self.created_resources['lead_id']}", 
                                                update_data, "Social Media Leads - Update Lead")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Social Media Leads UPDATE")
        
        # DELETE - Remove lead
        print("\n🗑️ Testing Lead Deletion (DELETE)...")
        if "lead_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/social-media-leads/leads/{self.created_resources['lead_id']}", 
                                                test_name="Social Media Leads - Delete Lead")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_template_marketplace_service(self):
        """Test advanced_template_marketplace_service (templates)"""
        print("\n🛍️ TESTING ADVANCED TEMPLATE MARKETPLACE SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new template
        print("\n📄 Testing Template Creation (CREATE)...")
        template_data = {
            "title": "Modern Business Landing Page Template",
            "description": "Professional, conversion-optimized landing page template with modern design",
            "category": "website_templates",
            "price": 79.99,
            "creator_id": "creator_12345",
            "tags": ["landing-page", "business", "modern", "responsive", "conversion"],
            "preview_images": [
                "https://example.com/preview1.jpg",
                "https://example.com/preview2.jpg"
            ],
            "files": [
                {"name": "template.zip", "size": 2048000, "type": "application/zip"},
                {"name": "documentation.pdf", "size": 512000, "type": "application/pdf"}
            ],
            "license_type": "commercial",
            "features": ["Responsive Design", "SEO Optimized", "Fast Loading", "Cross-browser Compatible"]
        }
        
        success, response = self.make_request("POST", "/template-marketplace/templates", template_data, "Template Marketplace - Create Template")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Template Marketplace CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["template_id"] = response["id"]
        
        # READ - Get templates list
        print("\n📋 Testing Templates List (READ)...")
        success, response = self.make_request("GET", "/template-marketplace/templates", test_name="Template Marketplace - Get Templates")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Template Marketplace READ")
        
        # UPDATE - Update template
        print("\n✏️ Testing Template Update (UPDATE)...")
        if "template_id" in self.created_resources:
            update_data = {
                "price": 89.99,
                "description": "Professional, conversion-optimized landing page template with modern design - Updated with new features"
            }
            success, response = self.make_request("PUT", f"/template-marketplace/templates/{self.created_resources['template_id']}", 
                                                update_data, "Template Marketplace - Update Template")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Template Marketplace UPDATE")
        
        # DELETE - Remove template
        print("\n🗑️ Testing Template Deletion (DELETE)...")
        if "template_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/template-marketplace/templates/{self.created_resources['template_id']}", 
                                                test_name="Template Marketplace - Delete Template")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_financial_service(self):
        """Test complete_financial_service (transactions)"""
        print("\n💰 TESTING COMPLETE FINANCIAL SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new transaction
        print("\n💳 Testing Transaction Creation (CREATE)...")
        transaction_data = {
            "type": "income",
            "amount": 2500.00,
            "currency": "USD",
            "description": "Website development project payment",
            "client_name": "TechCorp Solutions",
            "category": "web_development",
            "payment_method": "bank_transfer",
            "invoice_number": f"INV-{uuid.uuid4().hex[:8].upper()}",
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "tax_amount": 200.00,
            "status": "pending"
        }
        
        success, response = self.make_request("POST", "/financial/transactions", transaction_data, "Financial - Create Transaction")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Financial CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["transaction_id"] = response["id"]
        
        # READ - Get transactions list
        print("\n📋 Testing Transactions List (READ)...")
        success, response = self.make_request("GET", "/financial/transactions", test_name="Financial - Get Transactions")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Financial READ")
        
        # UPDATE - Update transaction
        print("\n✏️ Testing Transaction Update (UPDATE)...")
        if "transaction_id" in self.created_resources:
            update_data = {
                "status": "completed",
                "payment_date": datetime.now().isoformat()
            }
            success, response = self.make_request("PUT", f"/financial/transactions/{self.created_resources['transaction_id']}", 
                                                update_data, "Financial - Update Transaction")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Financial UPDATE")
        
        # DELETE - Remove transaction
        print("\n🗑️ Testing Transaction Deletion (DELETE)...")
        if "transaction_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/financial/transactions/{self.created_resources['transaction_id']}", 
                                                test_name="Financial - Delete Transaction")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_course_community_service(self):
        """Test complete_course_community_service (courses)"""
        print("\n🎓 TESTING COMPLETE COURSE COMMUNITY SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new course
        print("\n📚 Testing Course Creation (CREATE)...")
        course_data = {
            "title": "Advanced Digital Marketing Strategies",
            "description": "Comprehensive course covering modern digital marketing techniques and tools",
            "instructor": "Marketing Expert Pro",
            "category": "marketing",
            "price": 199.99,
            "duration_hours": 12,
            "difficulty_level": "intermediate",
            "modules": [
                {"title": "Introduction to Digital Marketing", "duration": 2},
                {"title": "Social Media Marketing", "duration": 3},
                {"title": "Content Marketing", "duration": 3},
                {"title": "Analytics and Optimization", "duration": 4}
            ],
            "prerequisites": ["Basic marketing knowledge", "Computer literacy"],
            "learning_outcomes": ["Master social media strategies", "Create effective content", "Analyze marketing data"],
            "tags": ["marketing", "digital", "social-media", "analytics"]
        }
        
        success, response = self.make_request("POST", "/courses/courses", course_data, "Course Community - Create Course")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Course Community CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["course_id"] = response["id"]
        
        # READ - Get courses list
        print("\n📋 Testing Courses List (READ)...")
        success, response = self.make_request("GET", "/courses/courses", test_name="Course Community - Get Courses")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Course Community READ")
        
        # UPDATE - Update course
        print("\n✏️ Testing Course Update (UPDATE)...")
        if "course_id" in self.created_resources:
            update_data = {
                "price": 249.99,
                "description": "Comprehensive course covering modern digital marketing techniques and tools - Updated with new content"
            }
            success, response = self.make_request("PUT", f"/courses/courses/{self.created_resources['course_id']}", 
                                                update_data, "Course Community - Update Course")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Course Community UPDATE")
        
        # DELETE - Remove course
        print("\n🗑️ Testing Course Deletion (DELETE)...")
        if "course_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/courses/courses/{self.created_resources['course_id']}", 
                                                test_name="Course Community - Delete Course")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_multi_workspace_service(self):
        """Test complete_multi_workspace_service (workspaces)"""
        print("\n🏢 TESTING COMPLETE MULTI-WORKSPACE SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new workspace
        print("\n🏗️ Testing Workspace Creation (CREATE)...")
        workspace_data = {
            "name": "Marketing Team Workspace",
            "description": "Dedicated workspace for marketing team collaboration and project management",
            "type": "team",
            "settings": {
                "privacy": "private",
                "allow_guests": False,
                "default_permissions": ["read", "write"]
            },
            "members": [
                {"email": "team.lead@company.com", "role": "admin"},
                {"email": "designer@company.com", "role": "member"}
            ],
            "features": ["project_management", "file_sharing", "analytics"],
            "billing_plan": "professional"
        }
        
        success, response = self.make_request("POST", "/workspaces/workspaces", workspace_data, "Multi-Workspace - Create Workspace")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Multi-Workspace CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["workspace_id"] = response["id"]
        
        # READ - Get workspaces list
        print("\n📋 Testing Workspaces List (READ)...")
        success, response = self.make_request("GET", "/workspaces/workspaces", test_name="Multi-Workspace - Get Workspaces")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Multi-Workspace READ")
        
        # UPDATE - Update workspace
        print("\n✏️ Testing Workspace Update (UPDATE)...")
        if "workspace_id" in self.created_resources:
            update_data = {
                "description": "Dedicated workspace for marketing team collaboration and project management - Updated with new features",
                "billing_plan": "enterprise"
            }
            success, response = self.make_request("PUT", f"/workspaces/workspaces/{self.created_resources['workspace_id']}", 
                                                update_data, "Multi-Workspace - Update Workspace")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Multi-Workspace UPDATE")
        
        # DELETE - Remove workspace
        print("\n🗑️ Testing Workspace Deletion (DELETE)...")
        if "workspace_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/workspaces/workspaces/{self.created_resources['workspace_id']}", 
                                                test_name="Multi-Workspace - Delete Workspace")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_email_marketing_service(self):
        """Test email_marketing_service (campaigns)"""
        print("\n📧 TESTING EMAIL MARKETING SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new campaign
        print("\n📮 Testing Campaign Creation (CREATE)...")
        campaign_data = {
            "name": "Q1 2025 Product Launch Campaign",
            "subject": "Introducing Our Revolutionary Business Platform",
            "content": {
                "html": "<h1>Welcome to the Future of Business</h1><p>Discover our new platform features...</p>",
                "text": "Welcome to the Future of Business. Discover our new platform features..."
            },
            "sender": {
                "name": "Mewayz Team",
                "email": "hello@mewayz.com"
            },
            "recipients": [
                {"email": "subscriber1@example.com", "name": "John Doe"},
                {"email": "subscriber2@example.com", "name": "Jane Smith"}
            ],
            "schedule_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "campaign_type": "promotional",
            "tags": ["product-launch", "q1-2025", "promotional"]
        }
        
        success, response = self.make_request("POST", "/email-marketing/campaigns", campaign_data, "Email Marketing - Create Campaign")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Email Marketing CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["campaign_id"] = response["id"]
        
        # READ - Get campaigns list
        print("\n📋 Testing Campaigns List (READ)...")
        success, response = self.make_request("GET", "/email-marketing/campaigns", test_name="Email Marketing - Get Campaigns")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Email Marketing READ")
        
        # UPDATE - Update campaign
        print("\n✏️ Testing Campaign Update (UPDATE)...")
        if "campaign_id" in self.created_resources:
            update_data = {
                "subject": "Introducing Our Revolutionary Business Platform - Limited Time Offer",
                "status": "scheduled"
            }
            success, response = self.make_request("PUT", f"/email-marketing/campaigns/{self.created_resources['campaign_id']}", 
                                                update_data, "Email Marketing - Update Campaign")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Email Marketing UPDATE")
        
        # DELETE - Remove campaign
        print("\n🗑️ Testing Campaign Deletion (DELETE)...")
        if "campaign_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/email-marketing/campaigns/{self.created_resources['campaign_id']}", 
                                                test_name="Email Marketing - Delete Campaign")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_booking_service(self):
        """Test complete_booking_service (appointments)"""
        print("\n📅 TESTING COMPLETE BOOKING SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new appointment
        print("\n🗓️ Testing Appointment Creation (CREATE)...")
        appointment_data = {
            "title": "Business Strategy Consultation",
            "description": "One-on-one consultation to discuss business growth strategies and digital transformation",
            "client_name": "Michael Chen",
            "client_email": "michael.chen@startup.com",
            "client_phone": "+1-555-0199",
            "service_type": "consultation",
            "duration_minutes": 60,
            "scheduled_time": (datetime.now() + timedelta(days=3)).isoformat(),
            "location": "Virtual Meeting (Zoom)",
            "price": 150.00,
            "status": "confirmed",
            "notes": "Client interested in e-commerce platform development",
            "reminders": [
                {"type": "email", "time_before_minutes": 1440},  # 24 hours
                {"type": "sms", "time_before_minutes": 60}       # 1 hour
            ]
        }
        
        success, response = self.make_request("POST", "/booking/appointments", appointment_data, "Booking - Create Appointment")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Booking CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["appointment_id"] = response["id"]
        
        # READ - Get appointments list
        print("\n📋 Testing Appointments List (READ)...")
        success, response = self.make_request("GET", "/booking/appointments", test_name="Booking - Get Appointments")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Booking READ")
        
        # UPDATE - Update appointment
        print("\n✏️ Testing Appointment Update (UPDATE)...")
        if "appointment_id" in self.created_resources:
            update_data = {
                "status": "completed",
                "notes": "Client interested in e-commerce platform development - Follow-up scheduled"
            }
            success, response = self.make_request("PUT", f"/booking/appointments/{self.created_resources['appointment_id']}", 
                                                update_data, "Booking - Update Appointment")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Booking UPDATE")
        
        # DELETE - Remove appointment
        print("\n🗑️ Testing Appointment Deletion (DELETE)...")
        if "appointment_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/booking/appointments/{self.created_resources['appointment_id']}", 
                                                test_name="Booking - Delete Appointment")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_escrow_service(self):
        """Test complete_escrow_service (escrow transactions)"""
        print("\n🔒 TESTING COMPLETE ESCROW SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Add new escrow transaction
        print("\n💼 Testing Escrow Transaction Creation (CREATE)...")
        escrow_data = {
            "buyer_id": "buyer_67890",
            "seller_id": "seller_12345",
            "project_title": "Custom E-commerce Platform Development",
            "project_description": "Development of a custom e-commerce platform with advanced features",
            "total_amount": 8000.00,
            "currency": "USD",
            "milestones": [
                {
                    "title": "Project Planning & Design",
                    "description": "Requirements gathering, wireframes, and UI/UX design",
                    "amount": 2000.00,
                    "due_date": (datetime.now() + timedelta(days=14)).isoformat()
                },
                {
                    "title": "Backend Development",
                    "description": "API development, database setup, and server configuration",
                    "amount": 3000.00,
                    "due_date": (datetime.now() + timedelta(days=35)).isoformat()
                },
                {
                    "title": "Frontend Development & Testing",
                    "description": "User interface development, testing, and deployment",
                    "amount": 3000.00,
                    "due_date": (datetime.now() + timedelta(days=56)).isoformat()
                }
            ],
            "terms": "Payment released upon milestone completion and buyer approval within 7 days",
            "dispute_resolution": "platform_mediation",
            "auto_release_days": 7
        }
        
        success, response = self.make_request("POST", "/escrow/transactions", escrow_data, "Escrow - Create Transaction")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Escrow CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["escrow_id"] = response["id"]
        
        # READ - Get escrow transactions list
        print("\n📋 Testing Escrow Transactions List (READ)...")
        success, response = self.make_request("GET", "/escrow/transactions", test_name="Escrow - Get Transactions")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Escrow READ")
        
        # UPDATE - Update escrow transaction
        print("\n✏️ Testing Escrow Transaction Update (UPDATE)...")
        if "escrow_id" in self.created_resources:
            update_data = {
                "status": "milestone_1_completed",
                "notes": "First milestone completed successfully, awaiting buyer approval"
            }
            success, response = self.make_request("PUT", f"/escrow/transactions/{self.created_resources['escrow_id']}", 
                                                update_data, "Escrow - Update Transaction")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Escrow UPDATE")
        
        # DELETE - Remove escrow transaction (usually not allowed, but testing endpoint)
        print("\n🗑️ Testing Escrow Transaction Deletion (DELETE)...")
        if "escrow_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/escrow/transactions/{self.created_resources['escrow_id']}", 
                                                test_name="Escrow - Delete Transaction")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def test_mobile_pwa_service(self):
        """Test mobile_pwa_service (devices)"""
        print("\n📱 TESTING MOBILE PWA SERVICE")
        print("=" * 60)
        
        service_results = {"create": False, "read": False, "update": False, "delete": False}
        
        # CREATE - Register new device
        print("\n📲 Testing Device Registration (CREATE)...")
        device_data = {
            "device_id": f"device_{uuid.uuid4().hex[:12]}",
            "device_type": "mobile",
            "platform": "android",
            "app_version": "2.1.0",
            "os_version": "Android 12",
            "device_info": {
                "manufacturer": "Samsung",
                "model": "Galaxy S21",
                "screen_resolution": "1080x2400",
                "memory_gb": 8,
                "storage_gb": 128
            },
            "push_token": f"push_token_{uuid.uuid4().hex[:16]}",
            "capabilities": ["push_notifications", "offline_storage", "camera", "location"],
            "settings": {
                "notifications_enabled": True,
                "offline_sync": True,
                "data_saver": False
            }
        }
        
        success, response = self.make_request("POST", "/mobile-pwa/devices", device_data, "Mobile PWA - Register Device")
        if success:
            service_results["create"] = True
            self.check_for_mock_data(response, "Mobile PWA CREATE")
            if isinstance(response, dict) and "id" in response:
                self.created_resources["device_id"] = response["id"]
        
        # READ - Get devices list
        print("\n📋 Testing Devices List (READ)...")
        success, response = self.make_request("GET", "/mobile-pwa/devices", test_name="Mobile PWA - Get Devices")
        if success:
            service_results["read"] = True
            self.check_for_mock_data(response, "Mobile PWA READ")
        
        # UPDATE - Update device
        print("\n✏️ Testing Device Update (UPDATE)...")
        if "device_id" in self.created_resources:
            update_data = {
                "app_version": "2.1.1",
                "settings": {
                    "notifications_enabled": True,
                    "offline_sync": True,
                    "data_saver": True
                }
            }
            success, response = self.make_request("PUT", f"/mobile-pwa/devices/{self.created_resources['device_id']}", 
                                                update_data, "Mobile PWA - Update Device")
            if success:
                service_results["update"] = True
                self.check_for_mock_data(response, "Mobile PWA UPDATE")
        
        # DELETE - Remove device
        print("\n🗑️ Testing Device Deletion (DELETE)...")
        if "device_id" in self.created_resources:
            success, response = self.make_request("DELETE", f"/mobile-pwa/devices/{self.created_resources['device_id']}", 
                                                test_name="Mobile PWA - Delete Device")
            if success:
                service_results["delete"] = True
        
        return service_results
    
    def run_comprehensive_crud_test(self):
        """Run comprehensive CRUD test for all 10 critical services"""
        print("🎯 COMPREHENSIVE CRUD VERIFICATION FOR MEWAYZ V2 PLATFORM - JANUARY 2025")
        print("=" * 80)
        print("Testing all 10 critical services mentioned in the review request")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Stopping tests.")
            return False
        
        print(f"\n✅ Authentication successful. Token: {self.access_token[:20]}...")
        
        # Test all 10 critical services
        all_results = {}
        
        print("\n🎯 TESTING 10 CRITICAL SERVICES WITH FULL CRUD OPERATIONS")
        print("=" * 80)
        
        # 1. E-commerce Service
        all_results["ecommerce"] = self.test_ecommerce_service()
        
        # 2. Social Media Leads Service
        all_results["social_media_leads"] = self.test_social_media_leads_service()
        
        # 3. Template Marketplace Service
        all_results["template_marketplace"] = self.test_template_marketplace_service()
        
        # 4. Financial Service
        all_results["financial"] = self.test_financial_service()
        
        # 5. Course Community Service
        all_results["course_community"] = self.test_course_community_service()
        
        # 6. Multi-Workspace Service
        all_results["multi_workspace"] = self.test_multi_workspace_service()
        
        # 7. Email Marketing Service
        all_results["email_marketing"] = self.test_email_marketing_service()
        
        # 8. Booking Service
        all_results["booking"] = self.test_booking_service()
        
        # 9. Escrow Service
        all_results["escrow"] = self.test_escrow_service()
        
        # 10. Mobile PWA Service
        all_results["mobile_pwa"] = self.test_mobile_pwa_service()
        
        # Print comprehensive summary
        self.print_comprehensive_summary(all_results)
        
        return True
    
    def print_comprehensive_summary(self, all_results):
        """Print comprehensive summary of all CRUD tests"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE CRUD VERIFICATION SUMMARY - MEWAYZ V2 PLATFORM")
        print("=" * 80)
        
        total_services = len(all_results)
        total_operations = total_services * 4  # 4 CRUD operations per service
        successful_operations = 0
        
        service_names = {
            "ecommerce": "Complete E-commerce Service (Products)",
            "social_media_leads": "Social Media Leads Service (Leads)",
            "template_marketplace": "Template Marketplace Service (Templates)",
            "financial": "Complete Financial Service (Transactions)",
            "course_community": "Course Community Service (Courses)",
            "multi_workspace": "Multi-Workspace Service (Workspaces)",
            "email_marketing": "Email Marketing Service (Campaigns)",
            "booking": "Complete Booking Service (Appointments)",
            "escrow": "Complete Escrow Service (Escrow Transactions)",
            "mobile_pwa": "Mobile PWA Service (Devices)"
        }
        
        print(f"📊 CRUD OPERATIONS RESULTS BY SERVICE:")
        print("-" * 80)
        
        for service_key, results in all_results.items():
            service_name = service_names.get(service_key, service_key.title())
            operations_passed = sum(1 for success in results.values() if success)
            operations_total = len(results)
            success_rate = (operations_passed / operations_total * 100) if operations_total > 0 else 0
            
            successful_operations += operations_passed
            
            status_icon = "✅" if success_rate == 100 else "⚠️" if success_rate >= 75 else "❌"
            print(f"{status_icon} {service_name}")
            print(f"   CRUD Operations: {operations_passed}/{operations_total} ({success_rate:.1f}%)")
            
            # Show individual CRUD operation results
            crud_icons = {"create": "➕", "read": "📖", "update": "✏️", "delete": "🗑️"}
            for operation, success in results.items():
                op_icon = "✅" if success else "❌"
                print(f"   {crud_icons.get(operation, '•')} {operation.upper()}: {op_icon}")
            print()
        
        overall_success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
        
        print(f"📈 OVERALL CRUD VERIFICATION RESULTS:")
        print(f"   Total Services Tested: {total_services}")
        print(f"   Total CRUD Operations: {total_operations}")
        print(f"   Successful Operations: {successful_operations}")
        print(f"   Failed Operations: {total_operations - successful_operations}")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Production readiness assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        if overall_success_rate >= 90:
            print("   🟢 EXCELLENT - All critical services have comprehensive CRUD functionality")
            print("   ✅ Platform is production-ready with full database operations")
        elif overall_success_rate >= 75:
            print("   🟡 VERY GOOD - Most critical services have working CRUD operations")
            print("   ⚠️ Platform is nearly production-ready with minor fixes needed")
        elif overall_success_rate >= 50:
            print("   🟠 PARTIAL - Some critical services have working CRUD operations")
            print("   🔧 Platform needs significant improvements before production")
        else:
            print("   🔴 CRITICAL - Most CRUD operations are not working")
            print("   ❌ Platform requires major development work before production")
        
        # Data quality assessment
        mock_data_count = len([r for r in self.test_results if "Mock Data Check" in r["test"] and not r["success"]])
        real_data_count = len([r for r in self.test_results if "Mock Data Check" in r["test"] and r["success"]])
        
        if mock_data_count == 0 and real_data_count > 0:
            print(f"\n✅ DATA QUALITY VERIFICATION: EXCELLENT")
            print(f"   🎯 NO MOCK/HARDCODED DATA DETECTED in any responses")
            print(f"   📊 All {real_data_count} services using real database operations")
        elif mock_data_count < real_data_count:
            print(f"\n⚠️ DATA QUALITY VERIFICATION: MOSTLY GOOD")
            print(f"   ✅ {real_data_count} services using real data")
            print(f"   ❌ {mock_data_count} services still using mock/hardcoded data")
        else:
            print(f"\n❌ DATA QUALITY VERIFICATION: NEEDS IMPROVEMENT")
            print(f"   ❌ {mock_data_count} services using mock/hardcoded data")
            print(f"   ✅ {real_data_count} services using real data")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = CRUDTester()
    tester.run_comprehensive_crud_test()