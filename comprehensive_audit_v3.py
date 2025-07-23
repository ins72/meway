#!/usr/bin/env python3
"""
COMPREHENSIVE AUDIT V3 - MEWAYZ PLATFORM AGAINST COMPLETE FEATURE DOCUMENTATION
June 2025 - Complete Platform Analysis
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any

class ComprehensiveAuditV3:
    def __init__(self):
        self.backend_path = "/app/backend"
        self.frontend_path = "/app/frontend"
        self.audit_results = {
            "audit_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "audit_version": "3.0",
            "platform_version": "v2",
            "total_features_required": 0,
            "features_implemented": 0,
            "features_missing": 0,
            "implementation_percentage": 0,
            "critical_gaps": [],
            "categories": {}
        }
        
    def audit_core_navigation_workspace(self):
        """Audit Core Navigation & Workspace Structure"""
        print("🔍 AUDITING: Core Navigation & Workspace Structure")
        
        required_features = [
            "Multi-Workspace System",
            "User Invitations", 
            "Role-Based Access (Owner, Admin, Editor, Viewer)",
            "Workspace Switching",
            "Workspace Settings",
            "Main Navigation (Dashboard, Socials, Link in Bio, Leads, etc.)"
        ]
        
        implemented_features = []
        missing_features = []
        
        # Check workspace service
        workspace_service = os.path.join(self.backend_path, "services", "complete_multi_workspace_service.py")
        if os.path.exists(workspace_service):
            with open(workspace_service, 'r') as f:
                content = f.read()
                if "create_workspace" in content:
                    implemented_features.append("Multi-Workspace System")
                if "invite_user" in content:
                    implemented_features.append("User Invitations")
                if "role" in content.lower() and "permission" in content.lower():
                    implemented_features.append("Role-Based Access")
        
        # Check API endpoints
        workspace_api = os.path.join(self.backend_path, "api", "complete_multi_workspace.py")
        if os.path.exists(workspace_api):
            with open(workspace_api, 'r') as f:
                content = f.read()
                if "/switch" in content:
                    implemented_features.append("Workspace Switching")
                if "/settings" in content:
                    implemented_features.append("Workspace Settings")
        
        # Check main navigation
        main_py = os.path.join(self.backend_path, "main.py")
        if os.path.exists(main_py):
            with open(main_py, 'r') as f:
                content = f.read()
                navigation_routes = [
                    "complete_onboarding",
                    "complete_link_in_bio", 
                    "complete_social_media_leads",
                    "complete_referral_system"
                ]
                if all(route in content for route in navigation_routes):
                    implemented_features.append("Main Navigation")
        
        for feature in required_features:
            if feature not in implemented_features:
                missing_features.append(feature)
        
        self.audit_results["categories"]["core_navigation_workspace"] = {
            "required": len(required_features),
            "implemented": len(implemented_features),
            "missing": len(missing_features),
            "percentage": (len(implemented_features) / len(required_features)) * 100,
            "implemented_features": implemented_features,
            "missing_features": missing_features
        }
        
        print(f"   ✅ Implemented: {len(implemented_features)}/{len(required_features)} features")
        print(f"   ❌ Missing: {missing_features}")
        
    def audit_social_media_management(self):
        """Audit Social Media Management System"""
        print("🔍 AUDITING: Social Media Management System")
        
        required_features = [
            "Instagram Database & Lead Generation",
            "Advanced Filtering System",
            "Data Export Features (CSV/Excel)",
            "Auto-Detection & Profile Building",
            "Social Media Posting & Scheduling",
            "Multi-Platform Support (Instagram, Facebook, Twitter, LinkedIn, TikTok, YouTube)",
            "Content Calendar",
            "Bulk Upload",
            "Auto-Posting",
            "Content Templates",
            "Hashtag Research"
        ]
        
        implemented_features = []
        missing_features = []
        
        # Check social media service
        social_service = os.path.join(self.backend_path, "services", "complete_social_media_leads_service.py")
        if os.path.exists(social_service):
            with open(social_service, 'r') as f:
                content = f.read()
                if "instagram" in content.lower():
                    implemented_features.append("Instagram Database & Lead Generation")
                if "filter" in content.lower():
                    implemented_features.append("Advanced Filtering System")
                if "export" in content.lower() or "csv" in content.lower():
                    implemented_features.append("Data Export Features (CSV/Excel)")
                if "detect" in content.lower() or "profile" in content.lower():
                    implemented_features.append("Auto-Detection & Profile Building")
                if "post" in content.lower() and "schedule" in content.lower():
                    implemented_features.append("Social Media Posting & Scheduling")
                if "facebook" in content.lower() and "twitter" in content.lower():
                    implemented_features.append("Multi-Platform Support")
                if "calendar" in content.lower():
                    implemented_features.append("Content Calendar")
                if "bulk" in content.lower():
                    implemented_features.append("Bulk Upload")
                if "auto" in content.lower() and "post" in content.lower():
                    implemented_features.append("Auto-Posting")
                if "template" in content.lower():
                    implemented_features.append("Content Templates")
                if "hashtag" in content.lower():
                    implemented_features.append("Hashtag Research")
        
        for feature in required_features:
            if feature not in implemented_features:
                missing_features.append(feature)
        
        self.audit_results["categories"]["social_media_management"] = {
            "required": len(required_features),
            "implemented": len(implemented_features),
            "missing": len(missing_features),
            "percentage": (len(implemented_features) / len(required_features)) * 100,
            "implemented_features": implemented_features,
            "missing_features": missing_features
        }
        
        print(f"   ✅ Implemented: {len(implemented_features)}/{len(required_features)} features")
        print(f"   ❌ Missing: {missing_features}")
        
    def audit_link_in_bio_system(self):
        """Audit Link in Bio System"""
        print("🔍 AUDITING: Link in Bio System")
        
        required_features = [
            "Drag & Drop Builder",
            "Pre-built Templates",
            "Responsive Design",
            "Custom Domains",
            "Analytics Integration",
            "Dynamic Content",
            "E-commerce Integration",
            "Contact Forms",
            "Event Integration",
            "QR Code Generation"
        ]
        
        implemented_features = []
        missing_features = []
        
        # Check link in bio service
        bio_service = os.path.join(self.backend_path, "services", "complete_link_in_bio_service.py")
        if os.path.exists(bio_service):
            with open(bio_service, 'r') as f:
                content = f.read()
                if "drag" in content.lower() or "builder" in content.lower():
                    implemented_features.append("Drag & Drop Builder")
                if "template" in content.lower():
                    implemented_features.append("Pre-built Templates")
                if "responsive" in content.lower():
                    implemented_features.append("Responsive Design")
                if "domain" in content.lower():
                    implemented_features.append("Custom Domains")
                if "analytics" in content.lower():
                    implemented_features.append("Analytics Integration")
                if "dynamic" in content.lower():
                    implemented_features.append("Dynamic Content")
                if "ecommerce" in content.lower() or "commerce" in content.lower():
                    implemented_features.append("E-commerce Integration")
                if "form" in content.lower():
                    implemented_features.append("Contact Forms")
                if "event" in content.lower():
                    implemented_features.append("Event Integration")
                if "qr" in content.lower():
                    implemented_features.append("QR Code Generation")
        
        for feature in required_features:
            if feature not in implemented_features:
                missing_features.append(feature)
        
        self.audit_results["categories"]["link_in_bio_system"] = {
            "required": len(required_features),
            "implemented": len(implemented_features),
            "missing": len(missing_features),
            "percentage": (len(implemented_features) / len(required_features)) * 100,
            "implemented_features": implemented_features,
            "missing_features": missing_features
        }
        
        print(f"   ✅ Implemented: {len(implemented_features)}/{len(required_features)} features")
        print(f"   ❌ Missing: {missing_features}")
        
    def audit_courses_community_system(self):
        """Audit Courses & Community System (Skool-like)"""
        print("🔍 AUDITING: Courses & Community System")
        
        required_features = [
            "Video Upload & Hosting",
            "Course Structure (Modules, lessons, quizzes)",
            "Progress Tracking",
            "Drip Content",
            "Interactive Elements",
            "Discussion Forums",
            "Group Creation",
            "Moderation Tools",
            "Gamification",
            "Live Streaming",
            "Direct Messaging",
            "Event Scheduling"
        ]
        
        implemented_features = []
        missing_features = []
        
        # Check course community service
        course_service = os.path.join(self.backend_path, "services", "complete_course_community_service.py")
        if os.path.exists(course_service):
            with open(course_service, 'r') as f:
                content = f.read()
                if "video" in content.lower() and "upload" in content.lower():
                    implemented_features.append("Video Upload & Hosting")
                if "module" in content.lower() and ("lesson" in content.lower() or "quiz" in content.lower()):
                    implemented_features.append("Course Structure (Modules, lessons, quizzes)")
                if "progress" in content.lower():
                    implemented_features.append("Progress Tracking")
                if "drip" in content.lower():
                    implemented_features.append("Drip Content")
                if "interactive" in content.lower():
                    implemented_features.append("Interactive Elements")
                if "forum" in content.lower() or "discussion" in content.lower():
                    implemented_features.append("Discussion Forums")
                if "group" in content.lower():
                    implemented_features.append("Group Creation")
                if "moderation" in content.lower():
                    implemented_features.append("Moderation Tools")
                if "gamification" in content.lower() or "points" in content.lower():
                    implemented_features.append("Gamification")
                if "live" in content.lower() and "stream" in content.lower():
                    implemented_features.append("Live Streaming")
                if "message" in content.lower():
                    implemented_features.append("Direct Messaging")
                if "event" in content.lower():
                    implemented_features.append("Event Scheduling")
        
        for feature in required_features:
            if feature not in implemented_features:
                missing_features.append(feature)
        
        self.audit_results["categories"]["courses_community_system"] = {
            "required": len(required_features),
            "implemented": len(implemented_features),
            "missing": len(missing_features),
            "percentage": (len(implemented_features) / len(required_features)) * 100,
            "implemented_features": implemented_features,
            "missing_features": missing_features
        }
        
        print(f"   ✅ Implemented: {len(implemented_features)}/{len(required_features)} features")
        print(f"   ❌ Missing: {missing_features}")
        
    def audit_marketplace_ecommerce(self):
        """Audit Marketplace & E-commerce"""
        print("🔍 AUDITING: Marketplace & E-commerce")
        
        required_features = [
            "Amazon-Style Marketplace",
            "Seller Onboarding",
            "Product Catalog",
            "Digital & Physical Products",
            "Inventory Management",
            "Order Management",
            "Payment Processing",
            "Review System",
            "Individual Store Creation",
            "Custom Storefronts",
            "Domain Integration",
            "Store Analytics",
            "Marketing Tools",
            "Mobile App"
        ]
        
        implemented_features = []
        missing_features = []
        
        # Check ecommerce service
        ecommerce_service = os.path.join(self.backend_path, "services", "complete_ecommerce_service.py")
        if os.path.exists(ecommerce_service):
            with open(ecommerce_service, 'r') as f:
                content = f.read()
                if "marketplace" in content.lower():
                    implemented_features.append("Amazon-Style Marketplace")
                if "seller" in content.lower() and "onboard" in content.lower():
                    implemented_features.append("Seller Onboarding")
                if "product" in content.lower() and "catalog" in content.lower():
                    implemented_features.append("Product Catalog")
                if "digital" in content.lower() and "physical" in content.lower():
                    implemented_features.append("Digital & Physical Products")
                if "inventory" in content.lower():
                    implemented_features.append("Inventory Management")
                if "order" in content.lower():
                    implemented_features.append("Order Management")
                if "payment" in content.lower():
                    implemented_features.append("Payment Processing")
                if "review" in content.lower():
                    implemented_features.append("Review System")
                if "store" in content.lower() and "create" in content.lower():
                    implemented_features.append("Individual Store Creation")
                if "storefront" in content.lower():
                    implemented_features.append("Custom Storefronts")
                if "domain" in content.lower():
                    implemented_features.append("Domain Integration")
                if "analytics" in content.lower():
                    implemented_features.append("Store Analytics")
                if "marketing" in content.lower():
                    implemented_features.append("Marketing Tools")
                if "mobile" in content.lower():
                    implemented_features.append("Mobile App")
        
        for feature in required_features:
            if feature not in implemented_features:
                missing_features.append(feature)
        
        self.audit_results["categories"]["marketplace_ecommerce"] = {
            "required": len(required_features),
            "implemented": len(implemented_features),
            "missing": len(missing_features),
            "percentage": (len(implemented_features) / len(required_features)) * 100,
            "implemented_features": implemented_features,
            "missing_features": missing_features
        }
        
        print(f"   ✅ Implemented: {len(implemented_features)}/{len(required_features)} features")
        print(f"   ❌ Missing: {missing_features}")
        
    def audit_all_categories(self):
        """Run audit on all major categories"""
        print("🚀 STARTING COMPREHENSIVE PLATFORM AUDIT")
        print("=" * 60)
        
        self.audit_core_navigation_workspace()
        self.audit_social_media_management()
        self.audit_link_in_bio_system()
        self.audit_courses_community_system()
        self.audit_marketplace_ecommerce()
        
        # Calculate overall statistics
        total_required = sum(cat["required"] for cat in self.audit_results["categories"].values())
        total_implemented = sum(cat["implemented"] for cat in self.audit_results["categories"].values())
        total_missing = sum(cat["missing"] for cat in self.audit_results["categories"].values())
        
        self.audit_results["total_features_required"] = total_required
        self.audit_results["features_implemented"] = total_implemented
        self.audit_results["features_missing"] = total_missing
        self.audit_results["implementation_percentage"] = (total_implemented / total_required) * 100 if total_required > 0 else 0
        
        # Identify critical gaps
        for category, data in self.audit_results["categories"].items():
            if data["percentage"] < 50:
                self.audit_results["critical_gaps"].append({
                    "category": category,
                    "percentage": data["percentage"],
                    "missing_count": data["missing"]
                })
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Features Required: {total_required}")
        print(f"Features Implemented: {total_implemented}")
        print(f"Features Missing: {total_missing}")
        print(f"Implementation Percentage: {self.audit_results['implementation_percentage']:.1f}%")
        
        if self.audit_results["critical_gaps"]:
            print(f"\n🚨 CRITICAL GAPS IDENTIFIED: {len(self.audit_results['critical_gaps'])}")
            for gap in self.audit_results["critical_gaps"]:
                print(f"   ❌ {gap['category']}: {gap['percentage']:.1f}% ({gap['missing_count']} missing)")
        
        return self.audit_results
    
    def save_audit_report(self):
        """Save comprehensive audit report"""
        report_path = "/app/comprehensive_audit_report_v3.json"
        with open(report_path, 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        print(f"\n📁 Audit report saved: {report_path}")
        return report_path

def main():
    auditor = ComprehensiveAuditV3()
    results = auditor.audit_all_categories()
    auditor.save_audit_report()
    
    return results

if __name__ == "__main__":
    main()