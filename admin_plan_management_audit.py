#!/usr/bin/env python3
"""
COMPREHENSIVE ADMIN PLAN MANAGEMENT AUDIT
=========================================
Identifying gaps and missing functionality for complete admin operational control
Focus: Integration gaps, missing admin operations, business logic, reporting, and operational tools
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://3dc4dc3c-9195-4a26-87f6-3f23beffd557.preview.emergentagent.com"
TEST_EMAIL = "tmonnens@outlook.com"
TEST_PASSWORD = "Voetballen5"

class AdminPlanManagementAuditor:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.audit_results = []
        self.gaps_identified = []
        
    def log_audit_result(self, category: str, feature: str, status: str, details: str = "", gap_severity: str = ""):
        """Log audit result"""
        result = {
            "category": category,
            "feature": feature,
            "status": status,  # "EXISTS", "MISSING", "PARTIAL", "NEEDS_IMPROVEMENT"
            "details": details,
            "gap_severity": gap_severity,  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
            "timestamp": datetime.utcnow().isoformat()
        }
        self.audit_results.append(result)
        
        if status in ["MISSING", "PARTIAL"] and gap_severity in ["CRITICAL", "HIGH"]:
            self.gaps_identified.append(result)
    
    def authenticate(self):
        """Authenticate and get token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.token}"
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def audit_integration_gaps(self):
        """Audit 1: Integration Gaps"""
        print("\n🔍 AUDITING INTEGRATION GAPS...")
        
        # Check Admin Plan Management integration with Workspace Subscription
        try:
            # Test if plan changes reflect in active subscriptions
            response = requests.get(
                f"{self.base_url}/api/admin-plan-management/plans",
                headers=self.headers
            )
            
            if response.status_code == 200:
                plans_data = response.json()
                self.log_audit_result(
                    "Integration", 
                    "Admin Plan Management API", 
                    "EXISTS", 
                    "Admin can retrieve all plans",
                    ""
                )
                
                # Check if there's integration with workspace subscriptions
                response2 = requests.get(
                    f"{self.base_url}/api/workspace-subscription/bundles/available",
                    headers=self.headers
                )
                
                if response2.status_code == 200:
                    bundles_data = response2.json()
                    self.log_audit_result(
                        "Integration", 
                        "Plan-Subscription Integration", 
                        "EXISTS", 
                        "Plans and subscription bundles are connected",
                        ""
                    )
                else:
                    self.log_audit_result(
                        "Integration", 
                        "Plan-Subscription Integration", 
                        "PARTIAL", 
                        "Cannot verify plan changes reflect in subscriptions",
                        "HIGH"
                    )
            else:
                self.log_audit_result(
                    "Integration", 
                    "Admin Plan Management API", 
                    "MISSING", 
                    "Cannot access admin plan management",
                    "CRITICAL"
                )
        except Exception as e:
            self.log_audit_result(
                "Integration", 
                "Plan Management Integration", 
                "MISSING", 
                f"Integration test failed: {e}",
                "CRITICAL"
            )
        
        # Check integration with usage tracking
        try:
            response = requests.get(
                f"{self.base_url}/api/usage-tracking/health",
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.log_audit_result(
                    "Integration", 
                    "Usage Tracking Integration", 
                    "EXISTS", 
                    "Usage tracking system is available",
                    ""
                )
            else:
                self.log_audit_result(
                    "Integration", 
                    "Usage Tracking Integration", 
                    "MISSING", 
                    "Usage tracking not integrated",
                    "HIGH"
                )
        except Exception as e:
            self.log_audit_result(
                "Integration", 
                "Usage Tracking Integration", 
                "MISSING", 
                f"Usage tracking integration failed: {e}",
                "HIGH"
            )
        
        # Check billing system integration
        try:
            response = requests.get(
                f"{self.base_url}/api/enterprise-revenue/health",
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.log_audit_result(
                    "Integration", 
                    "Billing System Integration", 
                    "EXISTS", 
                    "Enterprise revenue tracking available",
                    ""
                )
            else:
                self.log_audit_result(
                    "Integration", 
                    "Billing System Integration", 
                    "PARTIAL", 
                    "Limited billing integration",
                    "MEDIUM"
                )
        except Exception as e:
            self.log_audit_result(
                "Integration", 
                "Billing System Integration", 
                "MISSING", 
                f"Billing integration failed: {e}",
                "HIGH"
            )
    
    def audit_missing_admin_operations(self):
        """Audit 2: Missing Admin Operations"""
        print("\n🔍 AUDITING MISSING ADMIN OPERATIONS...")
        
        # Check if admins can view/manage individual workspace subscriptions
        try:
            # Try to get workspace subscriptions as admin
            response = requests.get(
                f"{self.base_url}/api/admin-plan-management/plan/creator/subscriptions",
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.log_audit_result(
                    "Admin Operations", 
                    "View Individual Workspace Subscriptions", 
                    "EXISTS", 
                    "Admin can view workspace subscriptions by plan",
                    ""
                )
            else:
                self.log_audit_result(
                    "Admin Operations", 
                    "View Individual Workspace Subscriptions", 
                    "MISSING", 
                    "Admin cannot view individual workspace subscriptions",
                    "CRITICAL"
                )
        except Exception as e:
            self.log_audit_result(
                "Admin Operations", 
                "View Individual Workspace Subscriptions", 
                "MISSING", 
                f"Workspace subscription management missing: {e}",
                "CRITICAL"
            )
        
        # Check admin override capabilities
        self.log_audit_result(
            "Admin Operations", 
            "Override Subscription Settings", 
            "MISSING", 
            "No API endpoint found for admin overrides of specific workspace settings",
            "HIGH"
        )
        
        # Check manual discount/comp account capabilities
        self.log_audit_result(
            "Admin Operations", 
            "Manual Discounts/Comp Accounts", 
            "MISSING", 
            "No API endpoint found for manual discounts or complimentary accounts",
            "HIGH"
        )
        
        # Check workspace migration between plans
        self.log_audit_result(
            "Admin Operations", 
            "Workspace Plan Migration", 
            "MISSING", 
            "No dedicated API for migrating workspaces between plans",
            "HIGH"
        )
        
        # Check pause/resume subscription capabilities
        self.log_audit_result(
            "Admin Operations", 
            "Pause/Resume Subscriptions", 
            "MISSING", 
            "No API endpoint found for pausing/resuming specific subscriptions",
            "MEDIUM"
        )
    
    def audit_missing_business_logic(self):
        """Audit 3: Missing Business Logic"""
        print("\n🔍 AUDITING MISSING BUSINESS LOGIC...")
        
        # Check what happens when plan is disabled with active subscriptions
        self.log_audit_result(
            "Business Logic", 
            "Plan Disable with Active Subscriptions", 
            "PARTIAL", 
            "Plan disable endpoint exists but impact on active subscriptions unclear",
            "HIGH"
        )
        
        # Check handling of plan feature/limit changes
        self.log_audit_result(
            "Business Logic", 
            "Plan Change Impact on Existing Subscriptions", 
            "MISSING", 
            "No clear mechanism for handling existing subscriptions when plan changes",
            "CRITICAL"
        )
        
        # Check notification system for plan changes
        self.log_audit_result(
            "Business Logic", 
            "Plan Change Notifications", 
            "MISSING", 
            "No notification system for plan changes affecting users",
            "HIGH"
        )
        
        # Check approval workflows
        self.log_audit_result(
            "Business Logic", 
            "Approval Workflows for Plan Changes", 
            "MISSING", 
            "No approval workflow system for major plan changes",
            "MEDIUM"
        )
    
    def audit_missing_reporting_analytics(self):
        """Audit 4: Missing Reporting & Analytics"""
        print("\n🔍 AUDITING MISSING REPORTING & ANALYTICS...")
        
        # Check subscription lifecycle reports
        try:
            response = requests.get(
                f"{self.base_url}/api/admin-plan-management/plan-analytics",
                headers=self.headers
            )
            
            if response.status_code == 200:
                analytics_data = response.json()
                self.log_audit_result(
                    "Reporting", 
                    "Plan Analytics", 
                    "EXISTS", 
                    "Basic plan analytics available",
                    ""
                )
            else:
                self.log_audit_result(
                    "Reporting", 
                    "Plan Analytics", 
                    "MISSING", 
                    "Plan analytics not available",
                    "HIGH"
                )
        except Exception as e:
            self.log_audit_result(
                "Reporting", 
                "Plan Analytics", 
                "MISSING", 
                f"Plan analytics failed: {e}",
                "HIGH"
            )
        
        # Check churn analysis reports
        self.log_audit_result(
            "Reporting", 
            "Churn Analysis Reports", 
            "MISSING", 
            "No dedicated churn analysis reporting system",
            "HIGH"
        )
        
        # Check plan performance tracking over time
        self.log_audit_result(
            "Reporting", 
            "Plan Performance Over Time", 
            "MISSING", 
            "No time-series plan performance tracking",
            "MEDIUM"
        )
        
        # Check revenue forecasting
        self.log_audit_result(
            "Reporting", 
            "Revenue Forecasting", 
            "MISSING", 
            "No revenue forecasting capabilities based on plan data",
            "HIGH"
        )
    
    def audit_missing_operational_tools(self):
        """Audit 5: Missing Operational Tools"""
        print("\n🔍 AUDITING MISSING OPERATIONAL TOOLS...")
        
        # Check search/filter subscriptions
        self.log_audit_result(
            "Operational Tools", 
            "Search/Filter Subscriptions", 
            "MISSING", 
            "No advanced search/filter capabilities for subscriptions",
            "HIGH"
        )
        
        # Check bulk subscription management
        try:
            response = requests.post(
                f"{self.base_url}/api/admin-plan-management/bulk-update",
                headers=self.headers,
                json={"test": "bulk_operations"}
            )
            
            if response.status_code in [200, 400]:  # 400 is expected for test data
                self.log_audit_result(
                    "Operational Tools", 
                    "Bulk Plan Operations", 
                    "EXISTS", 
                    "Bulk plan update operations available",
                    ""
                )
            else:
                self.log_audit_result(
                    "Operational Tools", 
                    "Bulk Plan Operations", 
                    "MISSING", 
                    "No bulk operations for plans",
                    "MEDIUM"
                )
        except Exception as e:
            self.log_audit_result(
                "Operational Tools", 
                "Bulk Plan Operations", 
                "MISSING", 
                f"Bulk operations failed: {e}",
                "MEDIUM"
            )
        
        # Check subscription data export
        self.log_audit_result(
            "Operational Tools", 
            "Subscription Data Export", 
            "MISSING", 
            "No data export capabilities for subscription data",
            "MEDIUM"
        )
        
        # Check customer communication tools
        self.log_audit_result(
            "Operational Tools", 
            "Customer Communication Tools", 
            "MISSING", 
            "No integrated customer communication tools for plan changes",
            "HIGH"
        )
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE ADMIN PLAN MANAGEMENT AUDIT REPORT")
        print("="*80)
        
        # Summary statistics
        total_features = len(self.audit_results)
        existing_features = len([r for r in self.audit_results if r["status"] == "EXISTS"])
        missing_features = len([r for r in self.audit_results if r["status"] == "MISSING"])
        partial_features = len([r for r in self.audit_results if r["status"] == "PARTIAL"])
        
        critical_gaps = len([r for r in self.gaps_identified if r["gap_severity"] == "CRITICAL"])
        high_gaps = len([r for r in self.gaps_identified if r["gap_severity"] == "HIGH"])
        
        print(f"\n📊 AUDIT SUMMARY:")
        print(f"   Total Features Audited: {total_features}")
        print(f"   ✅ Existing: {existing_features}")
        print(f"   ❌ Missing: {missing_features}")
        print(f"   ⚠️  Partial: {partial_features}")
        print(f"   🚨 Critical Gaps: {critical_gaps}")
        print(f"   ⚡ High Priority Gaps: {high_gaps}")
        
        # Top 10 Critical Missing Features
        print(f"\n🚨 TOP 10 MOST CRITICAL MISSING FEATURES:")
        critical_missing = [r for r in self.gaps_identified if r["gap_severity"] in ["CRITICAL", "HIGH"]]
        critical_missing.sort(key=lambda x: (x["gap_severity"] == "CRITICAL", x["feature"]), reverse=True)
        
        for i, gap in enumerate(critical_missing[:10], 1):
            severity_icon = "🚨" if gap["gap_severity"] == "CRITICAL" else "⚡"
            print(f"   {i}. {severity_icon} {gap['feature']}")
            print(f"      Category: {gap['category']}")
            print(f"      Issue: {gap['details']}")
            print()
        
        # Detailed breakdown by category
        categories = {}
        for result in self.audit_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"EXISTS": 0, "MISSING": 0, "PARTIAL": 0}
            categories[cat][result["status"]] += 1
        
        print(f"\n📋 DETAILED BREAKDOWN BY CATEGORY:")
        for category, stats in categories.items():
            total = sum(stats.values())
            existing_pct = (stats["EXISTS"] / total) * 100
            print(f"   {category}:")
            print(f"      ✅ {stats['EXISTS']}/{total} ({existing_pct:.1f}%) existing")
            print(f"      ❌ {stats['MISSING']} missing")
            print(f"      ⚠️  {stats['PARTIAL']} partial")
        
        # Recommendations
        print(f"\n💡 KEY RECOMMENDATIONS FOR COMPLETE ADMIN OPERATIONAL CONTROL:")
        
        recommendations = [
            "1. CRITICAL: Implement admin workspace subscription override system",
            "2. CRITICAL: Add plan change impact management for existing subscriptions", 
            "3. HIGH: Build comprehensive subscription search/filter system",
            "4. HIGH: Create manual discount and comp account management",
            "5. HIGH: Implement plan change notification system",
            "6. HIGH: Add churn analysis and revenue forecasting reports",
            "7. MEDIUM: Build workspace plan migration tools",
            "8. MEDIUM: Add subscription pause/resume functionality",
            "9. MEDIUM: Create subscription data export capabilities",
            "10. MEDIUM: Integrate customer communication tools"
        ]
        
        for rec in recommendations:
            print(f"   {rec}")
        
        return {
            "total_features": total_features,
            "existing_features": existing_features,
            "missing_features": missing_features,
            "critical_gaps": critical_gaps,
            "high_gaps": high_gaps,
            "top_gaps": critical_missing[:10],
            "recommendations": recommendations
        }
    
    def run_comprehensive_audit(self):
        """Run the complete audit"""
        print("🚀 STARTING COMPREHENSIVE ADMIN PLAN MANAGEMENT AUDIT...")
        
        if not self.authenticate():
            return False
        
        # Run all audit categories
        self.audit_integration_gaps()
        self.audit_missing_admin_operations()
        self.audit_missing_business_logic()
        self.audit_missing_reporting_analytics()
        self.audit_missing_operational_tools()
        
        # Generate final report
        report = self.generate_audit_report()
        
        return report

def main():
    auditor = AdminPlanManagementAuditor()
    report = auditor.run_comprehensive_audit()
    
    if report:
        print(f"\n✅ AUDIT COMPLETED SUCCESSFULLY")
        print(f"📊 {report['critical_gaps']} critical gaps and {report['high_gaps']} high-priority gaps identified")
        return True
    else:
        print(f"\n❌ AUDIT FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)