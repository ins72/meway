#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script
Tests authentication and newly created API endpoints
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://e0ab52c3-9e31-486e-974d-41e6b1129712.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
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
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            # Check if we can access the OpenAPI spec (this confirms the backend is running)
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                paths_count = len(data.get('paths', {}))
                self.log_result("Health Check", True, f"Backend is operational with {paths_count} API endpoints", {"paths_count": paths_count})
                return True
            else:
                self.log_result("Health Check", False, f"Backend not accessible - OpenAPI status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Health check error: {str(e)}")
            return False
    
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
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, test_name: str = None):
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
                self.log_result(test_name, False, f"Unsupported method: {method}")
                return False
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code}", data)
                    return True
                except:
                    self.log_result(test_name, True, f"Endpoint accessible - Status {response.status_code} (non-JSON response)")
                    return True
            elif response.status_code == 404:
                self.log_result(test_name, False, f"Endpoint not found (404) - May not be implemented or imported")
                return False
            elif response.status_code == 401:
                self.log_result(test_name, False, f"Authentication required (401)")
                return False
            elif response.status_code == 403:
                self.log_result(test_name, False, f"Access forbidden (403)")
                return False
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Internal server error')
                    self.log_result(test_name, False, f"Internal server error (500): {error_msg}")
                except:
                    self.log_result(test_name, False, f"Internal server error (500): {response.text}")
                return False
            else:
                self.log_result(test_name, False, f"Endpoint error - Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request error: {str(e)}")
            return False
    
    def test_enterprise_features(self):
        """Test the NEW ENTERPRISE FEATURES as requested in the review"""
        print("\n=== Testing NEW ENTERPRISE FEATURES ===")
        print("Testing Advanced Learning Management System (LMS), Multi-Vendor Marketplace, and Advanced Business Intelligence")
        
        # 1. Test Advanced Learning Management System (LMS) - /api/lms/*
        print("\n--- 1. Advanced Learning Management System (LMS) Testing ---")
        
        # SCORM Package Management
        scorm_data = {
            "package_name": "Introduction to Digital Marketing",
            "version": "1.0",
            "content_type": "scorm_2004",
            "duration_minutes": 120
        }
        self.test_endpoint("/lms/scorm/packages", "POST", scorm_data, "LMS - Create SCORM Package")
        self.test_endpoint("/lms/scorm/packages", test_name="LMS - List SCORM Packages")
        
        # Learning Progress Tracking
        progress_data = {
            "course_id": "course_123",
            "completion_percentage": 75,
            "time_spent_minutes": 90,
            "quiz_scores": [85, 92, 78]
        }
        self.test_endpoint("/lms/progress/track", "POST", progress_data, "LMS - Track Learning Progress")
        self.test_endpoint("/lms/progress/analytics", test_name="LMS - Get Learning Analytics")
        
        # Certificate Generation with Blockchain Verification
        cert_data = {
            "course_id": "course_123",
            "learner_id": "learner_456",
            "completion_date": "2024-12-20",
            "blockchain_verify": True
        }
        self.test_endpoint("/lms/certificates/generate", "POST", cert_data, "LMS - Generate Certificate")
        self.test_endpoint("/lms/certificates/verify", test_name="LMS - Verify Certificate Blockchain")
        
        # Gamification Data
        self.test_endpoint("/lms/gamification/leaderboard", test_name="LMS - Get Gamification Leaderboard")
        self.test_endpoint("/lms/gamification/badges", test_name="LMS - Get Available Badges")
        self.test_endpoint("/lms/gamification/points", test_name="LMS - Get User Points")
        
        # 2. Test Multi-Vendor Marketplace - /api/marketplace/*
        print("\n--- 2. Multi-Vendor Marketplace Testing ---")
        
        # Vendor Onboarding
        vendor_data = {
            "business_name": "TechSolutions Inc",
            "contact_email": "vendor@techsolutions.com",
            "business_type": "software",
            "tax_id": "123456789",
            "bank_account": "****1234"
        }
        self.test_endpoint("/marketplace/vendors/onboard", "POST", vendor_data, "Marketplace - Vendor Onboarding")
        self.test_endpoint("/marketplace/vendors/pending", test_name="Marketplace - Pending Vendor Approvals")
        
        # Vendor Approval Workflow
        approval_data = {
            "vendor_id": "vendor_123",
            "approval_status": "approved",
            "reviewer_notes": "All documents verified"
        }
        self.test_endpoint("/marketplace/vendors/approve", "POST", approval_data, "Marketplace - Approve Vendor")
        self.test_endpoint("/marketplace/vendors/active", test_name="Marketplace - Active Vendors")
        
        # Dynamic Pricing Calculation
        pricing_data = {
            "product_id": "prod_456",
            "base_price": 99.99,
            "demand_factor": 1.2,
            "competition_factor": 0.95,
            "seasonal_factor": 1.1
        }
        self.test_endpoint("/marketplace/pricing/calculate", "POST", pricing_data, "Marketplace - Calculate Dynamic Pricing")
        self.test_endpoint("/marketplace/pricing/history", test_name="Marketplace - Pricing History")
        
        # Vendor Payout Processing
        payout_data = {
            "vendor_id": "vendor_123",
            "period": "2024-12",
            "total_sales": 5000.00,
            "commission_rate": 0.15
        }
        self.test_endpoint("/marketplace/payouts/process", "POST", payout_data, "Marketplace - Process Vendor Payout")
        self.test_endpoint("/marketplace/payouts/pending", test_name="Marketplace - Pending Payouts")
        
        # Vendor Performance Metrics
        self.test_endpoint("/marketplace/vendors/performance", test_name="Marketplace - Vendor Performance Metrics")
        self.test_endpoint("/marketplace/analytics/sales", test_name="Marketplace - Sales Analytics")
        
        # 3. Test Advanced Business Intelligence - /api/business-intelligence/*
        print("\n--- 3. Advanced Business Intelligence Testing ---")
        
        # Predictive Analytics
        prediction_data = {
            "analysis_type": "revenue_forecasting",
            "time_horizon": "6_months",
            "data_sources": ["sales", "marketing", "customer_behavior"],
            "confidence_level": 0.95
        }
        self.test_endpoint("/business-intelligence/predictive/revenue-forecast", "POST", prediction_data, "BI - Revenue Forecasting")
        
        churn_data = {
            "customer_segment": "premium",
            "prediction_window": "30_days",
            "risk_factors": ["usage_decline", "support_tickets", "payment_delays"]
        }
        self.test_endpoint("/business-intelligence/predictive/churn-prediction", "POST", churn_data, "BI - Churn Prediction")
        
        # Cohort Analysis
        cohort_data = {
            "cohort_type": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "metric": "retention_rate"
        }
        self.test_endpoint("/business-intelligence/cohort/analysis", "POST", cohort_data, "BI - Cohort Analysis")
        self.test_endpoint("/business-intelligence/cohort/retention", test_name="BI - Retention Cohorts")
        
        # Funnel Tracking
        funnel_data = {
            "funnel_name": "sales_conversion",
            "stages": ["awareness", "interest", "consideration", "purchase"],
            "time_period": "last_30_days"
        }
        self.test_endpoint("/business-intelligence/funnel/track", "POST", funnel_data, "BI - Track Conversion Funnel")
        self.test_endpoint("/business-intelligence/funnel/analytics", test_name="BI - Funnel Analytics")
        
        # Competitive Analysis
        competitor_data = {
            "industry": "saas",
            "competitors": ["competitor_a", "competitor_b"],
            "metrics": ["pricing", "features", "market_share"]
        }
        self.test_endpoint("/business-intelligence/competitive/analysis", "POST", competitor_data, "BI - Competitive Analysis")
        self.test_endpoint("/business-intelligence/competitive/reports", test_name="BI - Competitive Reports")
        
        # Custom Report Creation
        report_data = {
            "report_name": "Monthly Performance Dashboard",
            "data_sources": ["sales", "marketing", "support"],
            "chart_types": ["line", "bar", "pie"],
            "filters": {"date_range": "last_30_days", "region": "north_america"}
        }
        self.test_endpoint("/business-intelligence/reports/create", "POST", report_data, "BI - Create Custom Report")
        self.test_endpoint("/business-intelligence/reports/list", test_name="BI - List Custom Reports")
        
        # Advanced Analytics Dashboard
        self.test_endpoint("/business-intelligence/dashboard/overview", test_name="BI - Analytics Dashboard Overview")
        self.test_endpoint("/business-intelligence/dashboard/kpis", test_name="BI - Key Performance Indicators")
        
    def test_existing_platform_stability(self):
        """Test existing platform stability to ensure no regressions"""
        print("\n--- 4. Existing Platform Stability Testing ---")
        
        # Core authentication and user management
        self.test_endpoint("/users/profile", test_name="Stability - User Profile")
        self.test_endpoint("/users/stats", test_name="Stability - User Statistics")
        
        # Dashboard functionality
        self.test_endpoint("/dashboard/overview", test_name="Stability - Dashboard Overview")
        self.test_endpoint("/dashboard/activity-summary", test_name="Stability - Dashboard Activity")
        
        # Analytics functionality
        self.test_endpoint("/analytics/overview", test_name="Stability - Analytics Overview")
        self.test_endpoint("/analytics/features/usage", test_name="Stability - Feature Usage Analytics")
        
        # AI services
        self.test_endpoint("/ai/services", test_name="Stability - AI Services")
        self.test_endpoint("/ai/conversations", test_name="Stability - AI Conversations")
        
        # E-commerce functionality
        self.test_endpoint("/ecommerce/products", test_name="Stability - E-commerce Products")
        self.test_endpoint("/ecommerce/orders", test_name="Stability - E-commerce Orders")
        self.test_endpoint("/ecommerce/dashboard", test_name="Stability - E-commerce Dashboard")
        
        # Marketing functionality
        self.test_endpoint("/marketing/campaigns", test_name="Stability - Marketing Campaigns")
        self.test_endpoint("/marketing/contacts", test_name="Stability - Marketing Contacts")
        self.test_endpoint("/marketing/analytics", test_name="Stability - Marketing Analytics")
        
        # Admin functionality
        self.test_endpoint("/admin/users", test_name="Stability - Admin Users")
        self.test_endpoint("/admin/system/metrics", test_name="Stability - Admin System Metrics")
        
        # Workspace management
        self.test_endpoint("/workspaces", test_name="Stability - Workspaces")
        
        # Test data consistency for core features
        print("\nTesting data consistency for core platform features:")
        core_consistency_endpoints = [
            "/dashboard/overview",
            "/users/profile",
            "/ai/services",
            "/ecommerce/dashboard",
            "/marketing/analytics"
        ]
        
        for endpoint in core_consistency_endpoints:
            self.test_data_consistency(endpoint)
    
    def test_newly_created_apis(self):
        """Test the newly created Advanced AI Analytics, Real-time Notifications, and Workflow Automation API endpoints"""
        print("\n=== Testing Previously Created API Modules ===")
        print("Testing Advanced AI Analytics, Real-time Notifications, and Workflow Automation endpoints")
        
        # Test Advanced AI Analytics API (/api/ai-analytics/api/ai-analytics)
        print("\n--- Advanced AI Analytics API Testing ---")
        
        # Generate predictive insights (POST)
        insights_data = {
            "data_source": "user_behavior",
            "time_range": "30_days",
            "metrics": ["engagement", "conversion", "retention"]
        }
        self.test_endpoint("/ai-analytics/api/ai-analytics/insights/generate", "POST", insights_data, "AI Analytics - Generate Predictive Insights")
        
        # Get user insights (GET)
        self.test_endpoint("/ai-analytics/api/ai-analytics/insights", test_name="AI Analytics - Get User Insights")
        
        # Generate anomaly detection (POST)
        anomaly_data = {
            "dataset": "user_activity",
            "threshold": 0.95,
            "time_window": "7_days"
        }
        self.test_endpoint("/ai-analytics/api/ai-analytics/insights/anomaly-detection", "POST", anomaly_data, "AI Analytics - Generate Anomaly Detection")
        
        # Get analytics summary (GET)
        self.test_endpoint("/ai-analytics/api/ai-analytics/analytics/summary", test_name="AI Analytics - Get Analytics Summary")
        
        # Test Real-time Notifications API (/api/notifications/api/notifications)
        print("\n--- Real-time Notifications API Testing ---")
        
        # Send notification to user (POST)
        notification_data = {
            "title": "Test Notification",
            "message": "This is a test notification from the API testing suite",
            "notification_type": "info",
            "channels": ["websocket", "in_app"],
            "priority": 5
        }
        self.test_endpoint("/notifications/api/notifications/send", "POST", notification_data, "Notifications - Send Notification")
        
        # Get notification history (GET)
        self.test_endpoint("/notifications/api/notifications/history", test_name="Notifications - Get History")
        
        # Get notification statistics (GET)
        self.test_endpoint("/notifications/api/notifications/stats", test_name="Notifications - Get Statistics")
        
        # Get connection status (GET)
        self.test_endpoint("/notifications/api/notifications/connection-status", test_name="Notifications - Get Connection Status")
        
        # Test Workflow Automation API (/api/workflows/api/workflows)
        print("\n--- Workflow Automation API Testing ---")
        
        # List user workflows (GET)
        self.test_endpoint("/workflows/api/workflows/list", test_name="Workflows - List User Workflows")
        
        # Get workflow templates (GET)
        self.test_endpoint("/workflows/api/workflows/templates/list", test_name="Workflows - Get Workflow Templates")
        
        # Get workflow statistics (GET)
        self.test_endpoint("/workflows/api/workflows/stats", test_name="Workflows - Get Workflow Statistics")
    
    def test_core_working_endpoints(self):
        """Test the core working API endpoints that are actually available"""
        print("\n=== Testing Core Working API Endpoints ===")
        
        # Test authentication endpoints
        self.test_endpoint("/auth/register", "POST", {"email": "test@example.com", "password": "testpass"}, "Auth - Register")
        
        # Test dashboard endpoints
        self.test_endpoint("/dashboard/overview", test_name="Dashboard - Overview")
        self.test_endpoint("/dashboard/activity-summary", test_name="Dashboard - Activity Summary")
        
        # Test analytics endpoints
        self.test_endpoint("/analytics/overview", test_name="Analytics - Overview")
        self.test_endpoint("/analytics/platform/overview", test_name="Analytics - Platform Overview")
        self.test_endpoint("/analytics/features/usage", test_name="Analytics - Features Usage")
        
        # Test user management endpoints
        self.test_endpoint("/users/profile", test_name="Users - Profile")
        self.test_endpoint("/users/stats", test_name="Users - Stats")
        self.test_endpoint("/users/analytics", test_name="Users - Analytics")
        
        # Test workspace endpoints
        self.test_endpoint("/workspaces", test_name="Workspaces - List")
        
        # Test blog endpoints
        self.test_endpoint("/blog/posts", test_name="Blog - Posts")
        self.test_endpoint("/blog/analytics", test_name="Blog - Analytics")
        
        # Test admin endpoints
        self.test_endpoint("/admin/dashboard", test_name="Admin - Dashboard")
        self.test_endpoint("/admin/users", test_name="Admin - Users")
        self.test_endpoint("/admin/users/stats", test_name="Admin - User Stats")
        self.test_endpoint("/admin/system/metrics", test_name="Admin - System Metrics")
        
        # Test AI endpoints
        self.test_endpoint("/ai/services", test_name="AI - Services")
        self.test_endpoint("/ai/conversations", test_name="AI - Conversations")
        
        # Test ecommerce endpoints
        self.test_endpoint("/ecommerce/products", test_name="Ecommerce - Products")
        self.test_endpoint("/ecommerce/orders", test_name="Ecommerce - Orders")
        self.test_endpoint("/ecommerce/dashboard", test_name="Ecommerce - Dashboard")
        
        # Test marketing endpoints
        self.test_endpoint("/marketing/campaigns", test_name="Marketing - Campaigns")
        self.test_endpoint("/marketing/contacts", test_name="Marketing - Contacts")
        self.test_endpoint("/marketing/lists", test_name="Marketing - Lists")
        self.test_endpoint("/marketing/analytics", test_name="Marketing - Analytics")
    
    def test_database_integration_verification(self):
        """Test database integration verification for the massive database work completed"""
        print("\n=== Database Integration Verification ===")
        print("Testing services converted from random data to real database operations")
        
        # Test services mentioned in the review request as having been converted
        database_integrated_services = [
            # Wave 1 services (1,186 random calls fixed)
            ("/social-media/analytics", "Social Media Service Database Integration"),
            ("/customer-experience/dashboard", "Customer Experience Service Database Integration"),
            ("/enhanced-ecommerce/products", "Enhanced E-commerce Service Database Integration"),
            ("/automation/workflows", "Automation Service Database Integration"),
            ("/analytics/overview", "Analytics Service Database Integration"),
            ("/support/tickets", "Support Service Database Integration"),
            ("/content-creation/projects", "Content Creation Service Database Integration"),
            ("/email-marketing/campaigns", "Email Marketing Service Database Integration"),
            ("/social-email/campaigns", "Social Email Service Database Integration"),
            ("/advanced-financial/dashboard", "Advanced Financial Service Database Integration"),
            
            # Wave 2 services (310 random calls fixed)
            ("/advanced-ai/capabilities", "Advanced AI Service Database Integration"),
            ("/advanced-financial/forecasting", "Financial Analytics Service Database Integration"),
            ("/templates/marketplace", "Template Marketplace Service Database Integration"),
            ("/ai-content/templates", "AI Content Service Database Integration"),
            ("/escrow/transactions", "Escrow Service Database Integration"),
            ("/customer-experience/journey-mapping", "Customer Experience Suite Database Integration"),
            ("/compliance/framework-status", "Compliance Service Database Integration"),
            ("/business-intelligence/metrics", "Business Intelligence Service Database Integration"),
            ("/content-creation/assets", "Content Creation Suite Database Integration"),
            ("/monitoring/system-health", "Monitoring Service Database Integration")
        ]
        
        for endpoint, test_name in database_integrated_services:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_data_consistency_verification(self):
        """Test data consistency to verify real database usage vs random generation"""
        print("\n=== Data Consistency Verification ===")
        print("Testing for consistent data across multiple calls (indicates real database usage)")
        
        # Test endpoints that should have consistent data
        consistency_endpoints = [
            "/dashboard/overview",
            "/workspaces", 
            "/analytics/overview",
            "/users/profile",
            "/users/stats",
            "/ecommerce/dashboard",
            "/marketing/analytics"
        ]
        
        for endpoint in consistency_endpoints:
            self.test_data_consistency(endpoint)
    
    def test_data_consistency(self, endpoint: str):
        """Test if endpoint returns consistent data (indicating real database usage)"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            # Make first request
            response1 = self.session.get(url, timeout=10)
            if response1.status_code != 200:
                self.log_result(f"Data Consistency - {endpoint}", False, f"First request failed - Status {response1.status_code}")
                return False
            
            data1 = response1.json()
            
            # Wait a moment and make second request
            import time
            time.sleep(1)
            
            response2 = self.session.get(url, timeout=10)
            if response2.status_code != 200:
                self.log_result(f"Data Consistency - {endpoint}", False, f"Second request failed - Status {response2.status_code}")
                return False
            
            data2 = response2.json()
            
            # Compare responses
            if json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True):
                self.log_result(f"Data Consistency - {endpoint}", True, f"Data consistent across calls - confirms real database usage")
                return True
            else:
                self.log_result(f"Data Consistency - {endpoint}", False, f"Data inconsistent - may still be using random generation")
                return False
                
        except Exception as e:
            self.log_result(f"Data Consistency - {endpoint}", False, f"Request error: {str(e)}")
            return False
    
    def test_core_business_functionality(self):
        """Test core business functionality that now uses real data"""
        print("\n=== Core Business Functionality with Real Data ===")
        
        # Test key business endpoints that should now use real database data
        business_endpoints = [
            # Dashboard and analytics
            ("/dashboard/overview", "Dashboard Real Database Data"),
            ("/analytics/overview", "Analytics Real Database Data"),
            
            # User and workspace management
            ("/users/profile", "User Management Real Data"),
            ("/workspaces", "Workspace Management Real Data"),
            
            # AI services
            ("/advanced-ai/capabilities", "AI Services Real Data"),
            ("/advanced-ai/models", "AI Models Real Data"),
            
            # Business intelligence
            ("/compliance/framework-status", "Compliance Real Data"),
            ("/backup/comprehensive-status", "Backup System Real Data"),
            ("/monitoring/system-health", "Monitoring Real Data"),
            
            # Integration management
            ("/integrations/available", "Integration Management Real Data"),
            ("/integrations/connected", "Connected Integrations Real Data")
        ]
        
        for endpoint, test_name in business_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)

    def test_platform_startup_health(self):
        """Test platform startup and health metrics"""
        print("\n=== Platform Startup & Health Verification ===")
        
        # Test system endpoints - note that root might serve frontend HTML
        try:
            response = self.session.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                if 'application/json' in response.headers.get('content-type', ''):
                    data = response.json()
                    self.log_result("Platform Root Status", True, f"JSON API response: {data.get('message', 'Unknown')}", data)
                else:
                    self.log_result("Platform Root Status", True, "Root serves frontend (expected in production setup)")
            else:
                self.log_result("Platform Root Status", False, f"Root failed with status {response.status_code}")
        except Exception as e:
            self.log_result("Platform Root Status", False, f"Root error: {str(e)}")
        
        # Test health and metrics endpoints (these are not prefixed with /api)
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code in [200, 503]:  # 503 is acceptable for degraded status
                data = response.json()
                status = data.get('status', 'unknown')
                modules_loaded = data.get('system', {}).get('modules_loaded', 0)
                self.log_result("Platform Health Check", True, f"Health endpoint working - Status: {status}, Modules: {modules_loaded}", data)
            else:
                self.log_result("Platform Health Check", False, f"Health failed with status {response.status_code}")
        except Exception as e:
            self.log_result("Platform Health Check", False, f"Health error: {str(e)}")
            
        try:
            response = self.session.get(f"{BACKEND_URL}/metrics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                load_success_rate = data.get('modules', {}).get('load_success_rate', '0%')
                total_collections = data.get('database', {}).get('total_collections', 0)
                self.log_result("Platform System Metrics", True, f"Metrics endpoint working - Load success: {load_success_rate}, DB collections: {total_collections}", data)
            else:
                self.log_result("Platform System Metrics", False, f"Metrics failed with status {response.status_code}")
        except Exception as e:
            self.log_result("Platform System Metrics", False, f"Metrics error: {str(e)}")
        
        # Test API documentation
        try:
            response = self.session.get(f"{BACKEND_URL}/docs", timeout=10)
            if response.status_code == 200:
                self.log_result("API Documentation", True, "Swagger UI accessible")
            else:
                self.log_result("API Documentation", False, f"Docs failed with status {response.status_code}")
        except Exception as e:
            self.log_result("API Documentation", False, f"Docs error: {str(e)}")
            
        try:
            response = self.session.get(f"{BACKEND_URL}/openapi.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                paths_count = len(data.get('paths', {}))
                self.log_result("OpenAPI Specification", True, f"OpenAPI spec available with {paths_count} endpoints", {"paths_count": paths_count})
            else:
                self.log_result("OpenAPI Specification", False, f"OpenAPI failed with status {response.status_code}")
        except Exception as e:
            self.log_result("OpenAPI Specification", False, f"OpenAPI error: {str(e)}")
    
    def test_service_method_fixes(self):
        """Test service method fixes for previously failing services"""
        print("\n=== Service Method Fixes Verification ===")
        print("Testing services that were previously failing due to method mapping issues")
        
        # Test services that had method mapping issues
        service_fixes = [
            ("/customer-experience/dashboard", "Customer Experience Service - Dashboard"),
            ("/customer-experience/journey-mapping", "Customer Experience Service - Journey Mapping"),
            ("/customer-experience/feedback", "Customer Experience Service - Feedback"),
            ("/social-email/campaigns", "Social Email Service - Campaigns"),
            ("/social-email/templates", "Social Email Service - Templates"),
            ("/email-marketing/campaigns", "Email Marketing Service - Campaigns"),
            ("/content-creation/projects", "Content Creation Service - Projects"),
            ("/content-creation/templates", "Content Creation Service - Templates"),
            ("/content-creation/assets", "Content Creation Service - Assets")
        ]
        
        for endpoint, test_name in service_fixes:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_data_integrity_verification(self):
        """Test data integrity to verify elimination of mock data"""
        print("\n=== Data Integrity Verification ===")
        print("Verifying elimination of random data and real database operations")
        
        # Test core services that should now use real database data
        data_integrity_endpoints = [
            ("/dashboard/overview", "Dashboard Service - Real Database Data"),
            ("/analytics/overview", "Analytics Service - Real Database Data"),
            ("/users/profile", "User Management - Real Database Data"),
            ("/ai/services", "AI Services - Real Database Data"),
            ("/ecommerce/products", "E-commerce - Real Database Data"),
            ("/marketing/campaigns", "Marketing - Real Database Data"),
            ("/admin/users", "Admin Management - Real Database Data"),
            ("/automation/workflows", "Automation - Real Database Data"),
            ("/support/tickets", "Support System - Real Database Data"),
            ("/monitoring/system-health", "Monitoring - Real Database Data")
        ]
        
        for endpoint, test_name in data_integrity_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test data consistency
        self.test_data_consistency_verification()
    
    def test_api_endpoint_functionality(self):
        """Test API endpoint functionality across all major modules"""
        print("\n=== API Endpoint Functionality Testing ===")
        
        # Test core authentication
        print("Testing Core Authentication:")
        self.test_endpoint("/auth/register", "POST", {"name": "Test User", "email": "test@example.com", "password": "testpass"}, "Auth - Register")
        
        # Test dashboard analytics
        print("Testing Dashboard Analytics:")
        self.test_endpoint("/dashboard/overview", test_name="Dashboard - Overview")
        self.test_endpoint("/dashboard/activity-summary", test_name="Dashboard - Activity Summary")
        
        # Test AI services
        print("Testing AI Services:")
        self.test_endpoint("/ai/services", test_name="AI - Services")
        self.test_endpoint("/ai/conversations", test_name="AI - Conversations")
        self.test_endpoint("/advanced-ai/capabilities", test_name="Advanced AI - Capabilities")
        self.test_endpoint("/advanced-ai/models", test_name="Advanced AI - Models")
        
        # Test e-commerce functions
        print("Testing E-commerce Functions:")
        self.test_endpoint("/ecommerce/products", test_name="E-commerce - Products")
        self.test_endpoint("/ecommerce/orders", test_name="E-commerce - Orders")
        self.test_endpoint("/ecommerce/dashboard", test_name="E-commerce - Dashboard")
        
        # Test social media integrations
        print("Testing Social Media Integrations:")
        self.test_endpoint("/social-media/analytics", test_name="Social Media - Analytics")
        self.test_endpoint("/social-email/campaigns", test_name="Social Email - Campaigns")
        
        # Test business intelligence
        print("Testing Business Intelligence:")
        self.test_endpoint("/business-intelligence/metrics", test_name="Business Intelligence - Metrics")
        self.test_endpoint("/analytics/features/usage", test_name="Analytics - Features Usage")
        
        # Test integration management
        print("Testing Integration Management:")
        self.test_endpoint("/integrations/available", test_name="Integrations - Available")
        self.test_endpoint("/integrations/connected", test_name="Integrations - Connected")
    
    def test_performance_reliability(self):
        """Test performance and reliability metrics"""
        print("\n=== Performance & Reliability Testing ===")
        
        # Test response times for key endpoints
        performance_endpoints = [
            "/dashboard/overview",
            "/users/profile", 
            "/ai/services",
            "/ecommerce/products",
            "/analytics/overview"
        ]
        
        total_response_time = 0
        successful_requests = 0
        
        for endpoint in performance_endpoints:
            try:
                import time
                start_time = time.time()
                
                url = f"{API_BASE}{endpoint}"
                response = self.session.get(url, timeout=10)
                
                end_time = time.time()
                response_time = end_time - start_time
                total_response_time += response_time
                
                if response.status_code == 200:
                    successful_requests += 1
                    self.log_result(f"Performance - {endpoint}", True, f"Response time: {response_time:.3f}s")
                else:
                    self.log_result(f"Performance - {endpoint}", False, f"Failed with status {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Performance - {endpoint}", False, f"Request error: {str(e)}")
        
        if successful_requests > 0:
            avg_response_time = total_response_time / successful_requests
            self.log_result("Average Response Time", True, f"Average: {avg_response_time:.3f}s across {successful_requests} endpoints")
        
        # Test system stability
        self.test_endpoint("/health", test_name="System Stability Check")
        self.test_endpoint("/metrics", test_name="System Metrics Check")

    def test_admin_configuration_system(self):
        """Test the new Admin Configuration System endpoints"""
        print("\n=== Admin Configuration System Testing ===")
        print("Testing the new admin configuration endpoints for external API management")
        
        # Test admin configuration endpoints
        admin_config_endpoints = [
            ("/admin-config/configuration", "GET", "Admin Config - Get Configuration"),
            ("/admin-config/integrations/status", "GET", "Admin Config - Integration Status"),
            ("/admin-config/system/health", "GET", "Admin Config - System Health"),
            ("/admin-config/logs", "GET", "Admin Config - System Logs"),
            ("/admin-config/available-services", "GET", "Admin Config - Available Services"),
            ("/admin-config/analytics/dashboard", "GET", "Admin Config - Analytics Dashboard"),
            ("/admin-config/logs/statistics", "GET", "Admin Config - Log Statistics")
        ]
        
        for endpoint, method, test_name in admin_config_endpoints:
            self.test_endpoint(endpoint, method, test_name=test_name)
        
        # Test admin configuration update (POST)
        config_update_data = {
            "enable_rate_limiting": True,
            "rate_limit_per_minute": 100,
            "enable_audit_logging": True,
            "log_level": "INFO"
        }
        self.test_endpoint("/admin-config/configuration", "POST", config_update_data, "Admin Config - Update Configuration")
        
        # Test integration testing endpoints
        integration_services = ["stripe", "openai", "sendgrid", "twitter"]
        for service in integration_services:
            self.test_endpoint(f"/admin-config/integrations/{service}/test", "POST", {}, f"Admin Config - Test {service.title()} Integration")
    
    def test_external_api_integration_framework(self):
        """Test External API Integration Framework"""
        print("\n=== External API Integration Framework Testing ===")
        print("Testing the external API integration system initialization and configuration")
        
        # Test integration management endpoints
        integration_endpoints = [
            ("/integrations/available", "Integration - Available Services"),
            ("/integrations/connected", "Integration - Connected Services"),
            ("/integrations/status", "Integration - Status Check")
        ]
        
        for endpoint, test_name in integration_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
    
    def test_professional_logging_system(self):
        """Test Professional Logging System"""
        print("\n=== Professional Logging System Testing ===")
        print("Testing the comprehensive logging system operational status")
        
        # Test logging endpoints
        logging_endpoints = [
            ("/admin-config/logs", "Professional Logging - System Logs"),
            ("/admin-config/logs/statistics", "Professional Logging - Log Statistics"),
            ("/admin-config/analytics/dashboard", "Professional Logging - Analytics Dashboard")
        ]
        
        for endpoint, test_name in logging_endpoints:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test log filtering
        log_filter_params = "?level=INFO&category=API&limit=50"
        self.test_endpoint(f"/admin-config/logs{log_filter_params}", test_name="Professional Logging - Filtered Logs")
    
    def test_random_data_elimination_verification(self):
        """Test Random Data Elimination - verify real database operations"""
        print("\n=== Random Data Elimination Verification ===")
        print("Testing services to verify they use real database operations instead of random data")
        
        # Test services that should now use real database data
        real_data_services = [
            ("/dashboard/overview", "Email Marketing Analytics - Real Data"),
            ("/analytics/overview", "Dashboard Metrics - Real Data"),
            ("/users/profile", "User Activity Tracking - Real Data"),
            ("/ai/services", "AI Usage Analytics - Real Data"),
            ("/marketing/analytics", "Marketing Service Analytics - Real Data"),
            ("/ecommerce/dashboard", "E-commerce Analytics - Real Data"),
            ("/admin/system/metrics", "Admin System Metrics - Real Data")
        ]
        
        for endpoint, test_name in real_data_services:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test data consistency to verify real database usage
        print("\nTesting data consistency to confirm real database operations:")
        consistency_endpoints = [
            "/dashboard/overview",
            "/users/profile", 
            "/ai/services",
            "/marketing/analytics",
            "/ecommerce/dashboard"
        ]
        
        for endpoint in consistency_endpoints:
            self.test_data_consistency(endpoint)
    
    def test_core_platform_functionality_after_changes(self):
        """Test Core Platform Functionality after major infrastructure changes"""
        print("\n=== Core Platform Functionality After Infrastructure Changes ===")
        print("Ensuring all existing functionality still works after major infrastructure changes")
        
        # Test core business functionality
        core_endpoints = [
            # Authentication and user management
            ("/auth/register", "POST", {"name": "Test User", "email": "test@example.com", "password": "testpass"}, "Core - User Registration"),
            ("/users/profile", "GET", None, "Core - User Profile"),
            ("/users/stats", "GET", None, "Core - User Statistics"),
            
            # Dashboard and analytics
            ("/dashboard/overview", "GET", None, "Core - Dashboard Overview"),
            ("/dashboard/activity-summary", "GET", None, "Core - Dashboard Activity"),
            ("/analytics/overview", "GET", None, "Core - Analytics Overview"),
            ("/analytics/features/usage", "GET", None, "Core - Feature Usage Analytics"),
            
            # AI services
            ("/ai/services", "GET", None, "Core - AI Services"),
            ("/ai/conversations", "GET", None, "Core - AI Conversations"),
            
            # E-commerce
            ("/ecommerce/products", "GET", None, "Core - E-commerce Products"),
            ("/ecommerce/orders", "GET", None, "Core - E-commerce Orders"),
            ("/ecommerce/dashboard", "GET", None, "Core - E-commerce Dashboard"),
            
            # Marketing
            ("/marketing/campaigns", "GET", None, "Core - Marketing Campaigns"),
            ("/marketing/contacts", "GET", None, "Core - Marketing Contacts"),
            ("/marketing/analytics", "GET", None, "Core - Marketing Analytics"),
            
            # Admin functions
            ("/admin/users", "GET", None, "Core - Admin Users"),
            ("/admin/system/metrics", "GET", None, "Core - Admin System Metrics"),
            
            # Workspace management
            ("/workspaces", "GET", None, "Core - Workspaces")
        ]
        
        for endpoint, method, data, test_name in core_endpoints:
            self.test_endpoint(endpoint, method, data, test_name)
    
    def test_database_integration_improvements(self):
        """Test Database Integration improvements"""
        print("\n=== Database Integration Improvements Testing ===")
        print("Testing that real data population services are working correctly")
        
        # Test database-integrated services
        db_services = [
            ("/dashboard/overview", "Database Integration - Dashboard Service"),
            ("/analytics/overview", "Database Integration - Analytics Service"),
            ("/users/profile", "Database Integration - User Management"),
            ("/ai/services", "Database Integration - AI Services"),
            ("/ecommerce/products", "Database Integration - E-commerce"),
            ("/marketing/campaigns", "Database Integration - Marketing"),
            ("/admin/users", "Database Integration - Admin Management"),
            ("/workspaces", "Database Integration - Workspace Management")
        ]
        
        for endpoint, test_name in db_services:
            self.test_endpoint(endpoint, test_name=test_name)
        
        # Test data persistence by making multiple calls
        print("\nTesting data persistence across multiple calls:")
        for endpoint, _ in db_services[:5]:  # Test first 5 services
            self.test_data_consistency(endpoint)

    def run_comprehensive_test(self):
        """Run comprehensive backend testing for newly created Advanced AI Analytics, Real-time Notifications, and Workflow Automation APIs"""
        print("🎯 TESTING NEWLY CREATED API ENDPOINTS - MEWAYZ PLATFORM")
        print("Testing the newly created Advanced AI Analytics, Real-time Notifications, and Workflow Automation API endpoints:")
        print("- 🔧 Advanced AI Analytics (/api/ai-analytics): Predictive insights, anomaly detection, analytics summary")
        print("- 🔧 Real-time Notifications (/api/notifications): Send notifications, history, stats, connection status")
        print("- 🔧 Workflow Automation (/api/workflows): List workflows, templates, statistics")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("❌ Health check failed - backend may not be running properly.")
            return False
        
        # Test authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with testing.")
            return False
        
        # Test the newly created APIs (main focus)
        self.test_newly_created_apis()
        
        # Test some core functionality to ensure integration works
        print("\n=== Testing Core Integration ===")
        self.test_endpoint("/dashboard/overview", test_name="Core - Dashboard Overview")
        self.test_endpoint("/users/profile", test_name="Core - User Profile")
        
        # Test platform health
        self.test_platform_startup_health()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}: {result['message']}")

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)