#!/usr/bin/env python3
"""
TAB NAVIGATION SIMULATION TEST
=============================
Simulates the exact user scenario: "getting logged out when navigating between tabs"
This test simulates rapid tab switching and concurrent requests that might happen
when a user has multiple tabs open and switches between them quickly.
"""

import requests
import json
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
import concurrent.futures

# Configuration
BACKEND_URL = "https://eff6f53c-47df-43a1-9962-4d20b26f6dc5.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class TabNavigationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
    def authenticate(self) -> bool:
        """Get authentication token"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def make_auth_request(self, tab_id: int, request_id: int) -> Dict[str, Any]:
        """Make a single authenticated request (simulates a tab making a request)"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers=self.headers,
                timeout=30
            )
            end_time = time.time()
            
            result = {
                "tab_id": tab_id,
                "request_id": request_id,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": end_time - start_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if response.status_code == 200:
                result["user_data"] = response.json()
                self.successful_requests += 1
            else:
                result["error"] = response.text
                self.failed_requests += 1
                
            self.total_requests += 1
            return result
            
        except Exception as e:
            self.failed_requests += 1
            self.total_requests += 1
            return {
                "tab_id": tab_id,
                "request_id": request_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def simulate_single_tab_rapid_requests(self) -> List[Dict[str, Any]]:
        """Simulate rapid requests from a single tab (user refreshing or navigating quickly)"""
        print("\n🔄 SINGLE TAB RAPID REQUESTS TEST")
        results = []
        
        for i in range(10):  # 10 rapid requests
            result = self.make_auth_request(tab_id=1, request_id=i+1)
            results.append(result)
            
            if result["success"]:
                print(f"  ✅ Request {i+1}: Success ({result['response_time']:.3f}s)")
            else:
                print(f"  ❌ Request {i+1}: Failed - {result.get('error', 'Unknown error')}")
            
            # Very short delay to simulate rapid clicking/navigation
            time.sleep(0.1)
        
        return results
    
    def simulate_multiple_tabs_concurrent(self) -> List[Dict[str, Any]]:
        """Simulate multiple tabs making concurrent requests"""
        print("\n🔀 MULTIPLE TABS CONCURRENT REQUESTS TEST")
        results = []
        
        # Simulate 5 tabs each making 3 requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for tab_id in range(1, 6):  # 5 tabs
                for request_id in range(1, 4):  # 3 requests per tab
                    future = executor.submit(self.make_auth_request, tab_id, request_id)
                    futures.append(future)
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                
                if result["success"]:
                    print(f"  ✅ Tab {result['tab_id']} Request {result['request_id']}: Success")
                else:
                    print(f"  ❌ Tab {result['tab_id']} Request {result['request_id']}: Failed")
        
        return results
    
    def simulate_tab_switching_pattern(self) -> List[Dict[str, Any]]:
        """Simulate realistic tab switching pattern"""
        print("\n🔄 TAB SWITCHING PATTERN SIMULATION")
        results = []
        
        # Simulate user switching between 3 tabs with different timing patterns
        tab_patterns = [
            {"tab_id": 1, "requests": 5, "delay": 0.5},  # Slow tab
            {"tab_id": 2, "requests": 8, "delay": 0.2},  # Medium tab
            {"tab_id": 3, "requests": 6, "delay": 0.1},  # Fast tab
        ]
        
        def tab_worker(tab_id: int, num_requests: int, delay: float):
            tab_results = []
            for i in range(num_requests):
                result = self.make_auth_request(tab_id, i+1)
                tab_results.append(result)
                time.sleep(delay)
            return tab_results
        
        # Run tabs concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for pattern in tab_patterns:
                future = executor.submit(
                    tab_worker, 
                    pattern["tab_id"], 
                    pattern["requests"], 
                    pattern["delay"]
                )
                futures.append(future)
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                tab_results = future.result()
                results.extend(tab_results)
                
                for result in tab_results:
                    if result["success"]:
                        print(f"  ✅ Tab {result['tab_id']} Request {result['request_id']}: Success")
                    else:
                        print(f"  ❌ Tab {result['tab_id']} Request {result['request_id']}: Failed")
        
        return results
    
    def test_session_persistence_under_load(self) -> List[Dict[str, Any]]:
        """Test session persistence under various load conditions"""
        print("\n⚡ SESSION PERSISTENCE UNDER LOAD TEST")
        results = []
        
        # Test 1: Burst requests (simulates user clicking rapidly)
        print("  📊 Burst Test (20 requests in 2 seconds)")
        burst_results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self.make_auth_request, 1, i+1) 
                for i in range(20)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                burst_results.append(result)
        
        end_time = time.time()
        burst_duration = end_time - start_time
        
        successful_burst = sum(1 for r in burst_results if r["success"])
        print(f"    ✅ Burst completed in {burst_duration:.2f}s: {successful_burst}/20 successful")
        
        results.extend(burst_results)
        
        # Test 2: Sustained load (simulates multiple tabs over time)
        print("  📊 Sustained Load Test (30 requests over 10 seconds)")
        sustained_results = []
        
        def sustained_worker():
            worker_results = []
            for i in range(30):
                result = self.make_auth_request(2, i+1)
                worker_results.append(result)
                time.sleep(0.33)  # ~3 requests per second
            return worker_results
        
        sustained_results = sustained_worker()
        successful_sustained = sum(1 for r in sustained_results if r["success"])
        print(f"    ✅ Sustained load completed: {successful_sustained}/30 successful")
        
        results.extend(sustained_results)
        
        return results
    
    def run_comprehensive_tab_test(self):
        """Run comprehensive tab navigation tests"""
        print("=" * 80)
        print("🔄 TAB NAVIGATION SESSION PERSISTENCE TEST SUITE")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print(f"Test Time: {datetime.utcnow().isoformat()}")
        print("=" * 80)
        
        # Authenticate
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return
        
        all_results = []
        
        # Test 1: Single tab rapid requests
        single_tab_results = self.simulate_single_tab_rapid_requests()
        all_results.extend(single_tab_results)
        
        # Test 2: Multiple tabs concurrent
        concurrent_results = self.simulate_multiple_tabs_concurrent()
        all_results.extend(concurrent_results)
        
        # Test 3: Tab switching pattern
        switching_results = self.simulate_tab_switching_pattern()
        all_results.extend(switching_results)
        
        # Test 4: Session persistence under load
        load_results = self.test_session_persistence_under_load()
        all_results.extend(load_results)
        
        # Generate report
        self.generate_comprehensive_report(all_results)
    
    def generate_comprehensive_report(self, all_results: List[Dict[str, Any]]):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TAB NAVIGATION TEST REPORT")
        print("=" * 80)
        
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r["success"])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {successful_requests}")
        print(f"Failed: {failed_requests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Response time analysis
        successful_results = [r for r in all_results if r["success"] and "response_time" in r]
        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            print(f"\n📈 RESPONSE TIME ANALYSIS:")
            print(f"Average Response Time: {avg_response_time:.3f}s")
            print(f"Max Response Time: {max_response_time:.3f}s")
            print(f"Min Response Time: {min_response_time:.3f}s")
        
        # Error analysis
        failed_results = [r for r in all_results if not r["success"]]
        if failed_results:
            print(f"\n❌ ERROR ANALYSIS:")
            error_types = {}
            for result in failed_results:
                error = result.get("error", "Unknown error")
                if error in error_types:
                    error_types[error] += 1
                else:
                    error_types[error] = 1
            
            for error, count in error_types.items():
                print(f"  {error}: {count} occurrences")
        
        # Final assessment
        print(f"\n🔍 FINAL ASSESSMENT:")
        
        if success_rate >= 99:
            print("✅ EXCELLENT: Authentication system is highly reliable for tab navigation")
            print("   Users should not experience logout issues when switching tabs")
        elif success_rate >= 95:
            print("✅ GOOD: Authentication system is mostly reliable with minor issues")
            print("   Occasional authentication hiccups may occur but are rare")
        elif success_rate >= 90:
            print("⚠️  MODERATE: Authentication system has some reliability issues")
            print("   Users may occasionally experience authentication problems")
        else:
            print("❌ POOR: Authentication system has significant reliability issues")
            print("   Users will likely experience frequent logout problems during tab navigation")
            print("   IMMEDIATE ATTENTION REQUIRED")
        
        # Specific recommendations
        if failed_requests > 0:
            print(f"\n💡 RECOMMENDATIONS:")
            print("1. Review backend logs for authentication errors")
            print("2. Check database connection stability")
            print("3. Verify JWT token validation logic")
            print("4. Consider implementing token refresh mechanism")
            print("5. Add client-side retry logic for failed authentication requests")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = TabNavigationTester()
    tester.run_comprehensive_tab_test()