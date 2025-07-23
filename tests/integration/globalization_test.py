#!/usr/bin/env python3
"""
COMPREHENSIVE GLOBALIZATION AND LOCALIZATION SYSTEM TESTING - MEWAYZ PLATFORM
Phase 5 Globalization and Localization System Testing
Testing Agent - July 20, 2025
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

class GlobalizationTester:
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
        """Test a single endpoint"""
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

    def test_globalization_system(self):
        """Test Comprehensive Globalization and Localization System - Phase 5"""
        print(f"\n🌍 TESTING COMPREHENSIVE GLOBALIZATION AND LOCALIZATION SYSTEM")
        
        # 1. Language Support - Get supported languages
        print(f"\n🗣️ Testing Language Support...")
        self.test_endpoint("/globalization/languages/supported", "GET", 
                         description="Get comprehensive list of supported languages")
        
        # 2. Language Detection - Detect language from text
        print(f"\n🔍 Testing Language Detection...")
        detection_data = {
            "text": "Bonjour, comment allez-vous? Je suis très heureux de vous rencontrer.",
            "confidence_threshold": 0.8
        }
        self.test_endpoint("/globalization/language/detect", "POST", 
                         data=detection_data,
                         description="Detect language from French text sample")
        
        # 3. Translation System - Get translations for specific language
        print(f"\n🔄 Testing Translation System...")
        language_code = "es"  # Spanish
        self.test_endpoint(f"/globalization/translations/{language_code}", "GET",
                         description=f"Get translations for {language_code} language")
        
        # 4. Translation Contribution - Contribute new translation
        print(f"\n📝 Testing Translation Contribution...")
        contribution_data = {
            "key": "welcome_message",
            "language_code": "de",
            "translation": "Willkommen bei Mewayz Platform",
            "context": "Main dashboard welcome message",
            "contributor_notes": "Professional German translation for business context"
        }
        self.test_endpoint("/globalization/translations/contribute", "POST",
                         data=contribution_data,
                         description="Contribute German translation for welcome message")
        
        # 5. User Preferences - Update user globalization preferences
        print(f"\n⚙️ Testing User Preferences...")
        preferences_data = {
            "language": "fr",
            "region": "EU",
            "timezone": "Europe/Paris",
            "currency": "EUR",
            "date_format": "DD/MM/YYYY",
            "number_format": "european",
            "rtl_support": False
        }
        self.test_endpoint("/globalization/user-preferences/update", "POST",
                         data=preferences_data,
                         description="Update user globalization preferences to French/EU")
        
        # 6. Regional Content - Get content for specific region
        print(f"\n🌎 Testing Regional Content...")
        region = "EU"
        self.test_endpoint(f"/globalization/regional-content/{region}", "GET",
                         description=f"Get regional content customized for {region}")
        
        # 7. RTL Language Support - Get RTL support information
        print(f"\n📖 Testing RTL Language Support...")
        self.test_endpoint("/globalization/rtl/support", "GET",
                         description="Get RTL (Right-to-Left) language support information")
        
        # 8. Analytics & Insights - Get globalization usage analytics
        print(f"\n📊 Testing Globalization Analytics...")
        self.test_endpoint("/globalization/analytics/usage", "GET",
                         description="Get comprehensive globalization usage analytics and insights")

    def run_comprehensive_tests(self):
        """Run all comprehensive globalization tests"""
        print(f"\n{'='*80}")
        print(f"🌍 COMPREHENSIVE GLOBALIZATION AND LOCALIZATION SYSTEM TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Authenticate first
        if not self.authenticate():
            print(f"\n❌ AUTHENTICATION FAILED - Cannot proceed with testing")
            return
            
        # Test globalization system
        self.test_globalization_system()
        
        # Print comprehensive results
        self.print_results()

    def print_results(self):
        """Print comprehensive test results"""
        print(f"\n{'='*80}")
        print(f"🎯 COMPREHENSIVE GLOBALIZATION TESTING RESULTS")
        print(f"{'='*80}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Performance metrics
        response_times = [float(result['response_time'].replace('s', '')) for result in self.test_results if result['success']]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            total_data = sum(result['data_size'] for result in self.test_results)
            
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"📊 Average Response Time: {avg_time:.3f}s")
            print(f"🚀 Fastest Response: {min_time:.3f}s")
            print(f"🐌 Slowest Response: {max_time:.3f}s")
            print(f"📦 Total Data Processed: {total_data:,} bytes")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['method']} {result['endpoint']} - {result['status']} ({result['response_time']}) - {result['details']}")
        
        print(f"\n{'='*80}")
        if success_rate >= 80:
            print(f"🎉 GLOBALIZATION SYSTEM TESTING COMPLETED SUCCESSFULLY!")
            print(f"✅ Phase 5 globalization and localization system is working correctly")
        else:
            print(f"⚠️ GLOBALIZATION SYSTEM TESTING COMPLETED WITH ISSUES")
            print(f"❌ Some globalization endpoints need attention")
        print(f"{'='*80}")

if __name__ == "__main__":
    tester = GlobalizationTester()
    tester.run_comprehensive_tests()