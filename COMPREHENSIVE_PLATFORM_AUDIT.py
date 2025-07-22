#!/usr/bin/env python3
"""
COMPREHENSIVE MEWAYZ PLATFORM AUDIT
===================================
Complete audit of all features, APIs, services, and data integration
Mewayz v2 - July 22, 2025
"""

import os
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

class MewayzPlatformAuditor:
    def __init__(self):
        self.backend_path = Path("/app/backend")
        self.frontend_path = Path("/app/frontend")
        self.audit_results = {
            "audit_date": datetime.now().isoformat(),
            "platform_version": "v2",
            "api_endpoints": {},
            "services": {},
            "database_collections": {},
            "real_data_integrations": {},
            "mock_data_usage": {},
            "crud_operations": {},
            "authentication": {},
            "features_implemented": {},
            "issues_found": [],
            "recommendations": []
        }
    
    def run_full_audit(self):
        """Run complete platform audit"""
        print("🚀 STARTING COMPREHENSIVE MEWAYZ PLATFORM AUDIT")
        print("=" * 80)
        
        # 1. Audit API Endpoints
        print("\n📋 1. AUDITING API ENDPOINTS...")
        self.audit_api_endpoints()
        
        # 2. Audit Services
        print("\n📋 2. AUDITING SERVICES...")
        self.audit_services()
        
        # 3. Audit Database Collections
        print("\n📋 3. AUDITING DATABASE COLLECTIONS...")
        self.audit_database_collections()
        
        # 4. Audit Real Data Integrations
        print("\n📋 4. AUDITING REAL DATA INTEGRATIONS...")
        self.audit_real_data_integrations()
        
        # 5. Audit Mock Data Usage
        print("\n📋 5. AUDITING MOCK DATA USAGE...")
        self.audit_mock_data_usage()
        
        # 6. Audit CRUD Operations
        print("\n📋 6. AUDITING CRUD OPERATIONS...")
        self.audit_crud_operations()
        
        # 7. Audit Authentication System
        print("\n📋 7. AUDITING AUTHENTICATION SYSTEM...")
        self.audit_authentication()
        
        # 8. Audit Features Implementation
        print("\n📋 8. AUDITING FEATURES IMPLEMENTATION...")
        self.audit_features_implementation()
        
        # 9. Generate Report
        print("\n📋 9. GENERATING COMPREHENSIVE REPORT...")
        self.generate_audit_report()
        
        print("\n✅ AUDIT COMPLETED!")
        return self.audit_results
    
    def audit_api_endpoints(self):
        """Audit all API endpoints"""
        api_path = self.backend_path / "api"
        endpoints = {}
        
        for api_file in api_path.glob("*.py"):
            if api_file.name.startswith("__"):
                continue
                
            try:
                with open(api_file, 'r') as f:
                    content = f.read()
                
                # Extract router information
                router_match = re.search(r'router = APIRouter\(prefix="([^"]+)"', content)
                prefix = router_match.group(1) if router_match else "/api"
                
                # Extract endpoint methods
                endpoint_methods = re.findall(r'@router\.(get|post|put|delete|patch)\("([^"]+)"', content)
                
                file_endpoints = []
                for method, path in endpoint_methods:
                    full_path = f"{prefix}{path}"
                    file_endpoints.append({
                        "method": method.upper(),
                        "path": full_path,
                        "file": api_file.name
                    })
                
                endpoints[api_file.stem] = {
                    "file": api_file.name,
                    "prefix": prefix,
                    "endpoints": file_endpoints,
                    "endpoint_count": len(file_endpoints)
                }
                
            except Exception as e:
                endpoints[api_file.stem] = {
                    "file": api_file.name,
                    "error": str(e),
                    "status": "failed_to_parse"
                }
        
        self.audit_results["api_endpoints"] = endpoints
        print(f"   📊 Found {len(endpoints)} API modules")
        
        # Count total endpoints
        total_endpoints = sum(
            ep.get("endpoint_count", 0) for ep in endpoints.values() 
            if "endpoint_count" in ep
        )
        print(f"   📊 Total API endpoints: {total_endpoints}")
    
    def audit_services(self):
        """Audit all service files"""
        services_path = self.backend_path / "services"
        services = {}
        
        for service_file in services_path.glob("*.py"):
            if service_file.name.startswith("__"):
                continue
                
            try:
                with open(service_file, 'r') as f:
                    content = f.read()
                
                # Extract service classes
                class_matches = re.findall(r'class (\w+):', content)
                
                # Extract async methods
                async_methods = re.findall(r'async def (\w+)\(', content)
                
                # Extract regular methods
                regular_methods = re.findall(r'def (\w+)\(', content)
                
                # Check for real API integrations
                real_apis = []
                if "openai" in content.lower():
                    real_apis.append("OpenAI")
                if "twitter" in content.lower():
                    real_apis.append("Twitter")
                if "tiktok" in content.lower():
                    real_apis.append("TikTok")
                if "elasticmail" in content.lower():
                    real_apis.append("ElasticMail")
                if "stripe" in content.lower():
                    real_apis.append("Stripe")
                if "google" in content.lower():
                    real_apis.append("Google")
                
                # Check for mock data usage
                mock_indicators = []
                if "mock" in content.lower():
                    mock_indicators.append("mock")
                if "random" in content.lower():
                    mock_indicators.append("random")
                if "fake" in content.lower():
                    mock_indicators.append("fake")
                
                services[service_file.stem] = {
                    "file": service_file.name,
                    "classes": class_matches,
                    "async_methods": async_methods,
                    "regular_methods": regular_methods,
                    "total_methods": len(async_methods) + len(regular_methods),
                    "real_apis": real_apis,
                    "mock_indicators": mock_indicators,
                    "has_real_data": len(real_apis) > 0,
                    "has_mock_data": len(mock_indicators) > 0
                }
                
            except Exception as e:
                services[service_file.stem] = {
                    "file": service_file.name,
                    "error": str(e),
                    "status": "failed_to_parse"
                }
        
        self.audit_results["services"] = services
        print(f"   📊 Found {len(services)} service files")
        
        # Count real data services
        real_data_services = sum(1 for s in services.values() if s.get("has_real_data", False))
        print(f"   📊 Services with real data: {real_data_services}")
        
        # Count mock data services
        mock_data_services = sum(1 for s in services.values() if s.get("has_mock_data", False))
        print(f"   📊 Services with mock data: {mock_data_services}")
    
    def audit_database_collections(self):
        """Audit database collections by analyzing service files"""
        collections = {}
        
        for service_file in (self.backend_path / "services").glob("*.py"):
            try:
                with open(service_file, 'r') as f:
                    content = f.read()
                
                # Find database collection references
                collection_matches = re.findall(r'db\["([^"]+)"\]', content)
                collection_matches.extend(re.findall(r'\.([a-zA-Z_]+)\s*=\s*db\["([^"]+)"\]', content))
                
                for match in collection_matches:
                    if isinstance(match, tuple):
                        collection_name = match[1]
                    else:
                        collection_name = match
                    
                    if collection_name not in collections:
                        collections[collection_name] = {
                            "used_in_services": [],
                            "operations": set(),
                            "description": ""
                        }
                    
                    collections[collection_name]["used_in_services"].append(service_file.stem)
                    
                    # Check for CRUD operations
                    if "insert_one" in content or "insert_many" in content:
                        collections[collection_name]["operations"].add("CREATE")
                    if "find_one" in content or "find(" in content:
                        collections[collection_name]["operations"].add("READ")
                    if "update_one" in content or "update_many" in content:
                        collections[collection_name]["operations"].add("UPDATE")
                    if "delete_one" in content or "delete_many" in content:
                        collections[collection_name]["operations"].add("DELETE")
                    
            except Exception as e:
                continue
        
        # Convert sets to lists for JSON serialization
        for collection in collections.values():
            collection["operations"] = list(collection["operations"])
        
        self.audit_results["database_collections"] = collections
        print(f"   📊 Found {len(collections)} database collections")
        
        # Count collections with full CRUD
        full_crud = sum(1 for c in collections.values() if len(c["operations"]) == 4)
        print(f"   📊 Collections with full CRUD: {full_crud}")
    
    def audit_real_data_integrations(self):
        """Audit real data integrations"""
        integrations = {}
        
        # Check environment variables
        env_file = self.backend_path / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            # Check for API keys
            api_keys = {}
            if "OPENAI_API_KEY" in env_content:
                api_keys["openai"] = "configured"
            if "TWITTER_API_KEY" in env_content:
                api_keys["twitter"] = "configured"
            if "TIKTOK_CLIENT_KEY" in env_content:
                api_keys["tiktok"] = "configured"
            if "ELASTICMAIL_API_KEY" in env_content:
                api_keys["elasticmail"] = "configured"
            if "STRIPE_SECRET_KEY" in env_content:
                api_keys["stripe"] = "configured"
            if "GOOGLE_CLIENT_ID" in env_content:
                api_keys["google"] = "configured"
            
            integrations["environment_variables"] = api_keys
        
        # Check for real API service implementations
        real_services = {}
        services_path = self.backend_path / "services"
        
        for service_file in services_path.glob("real_*.py"):
            service_name = service_file.stem
            with open(service_file, 'r') as f:
                content = f.read()
            
            real_services[service_name] = {
                "file": service_file.name,
                "has_api_calls": "requests" in content or "aiohttp" in content,
                "has_authentication": "api_key" in content or "token" in content,
                "has_error_handling": "try:" in content and "except" in content,
                "external_apis": []
            }
            
            # Check for specific API usage
            if "openai" in content.lower():
                real_services[service_name]["external_apis"].append("OpenAI")
            if "twitter" in content.lower():
                real_services[service_name]["external_apis"].append("Twitter")
            if "tiktok" in content.lower():
                real_services[service_name]["external_apis"].append("TikTok")
            if "elasticmail" in content.lower():
                real_services[service_name]["external_apis"].append("ElasticMail")
        
        integrations["real_services"] = real_services
        
        self.audit_results["real_data_integrations"] = integrations
        print(f"   📊 Found {len(integrations.get('environment_variables', {}))} configured API keys")
        print(f"   📊 Found {len(integrations.get('real_services', {}))} real API services")
    
    def audit_mock_data_usage(self):
        """Audit mock data usage"""
        mock_usage = {}
        
        for service_file in (self.backend_path / "services").glob("*.py"):
            try:
                with open(service_file, 'r') as f:
                    content = f.read()
                
                mock_indicators = []
                
                # Check for mock data patterns
                if re.search(r'mock|fake|random|hardcoded|test_data', content, re.IGNORECASE):
                    mock_indicators.append("mock_keywords")
                
                if re.search(r'random\.', content):
                    mock_indicators.append("random_module")
                
                if re.search(r'uuid\.uuid4\(\)', content):
                    mock_indicators.append("uuid_generation")
                
                if re.search(r'f"test_|f"mock_|f"fake_', content):
                    mock_indicators.append("test_strings")
                
                if mock_indicators:
                    mock_usage[service_file.stem] = {
                        "file": service_file.name,
                        "mock_indicators": mock_indicators,
                        "severity": "high" if len(mock_indicators) > 2 else "medium"
                    }
                    
            except Exception as e:
                continue
        
        self.audit_results["mock_data_usage"] = mock_usage
        print(f"   📊 Found {len(mock_usage)} services with mock data indicators")
    
    def audit_crud_operations(self):
        """Audit CRUD operations across all services"""
        crud_operations = {}
        
        for service_file in (self.backend_path / "services").glob("*.py"):
            try:
                with open(service_file, 'r') as f:
                    content = f.read()
                
                operations = {
                    "CREATE": [],
                    "READ": [],
                    "UPDATE": [],
                    "DELETE": []
                }
                
                # Find CREATE operations
                create_matches = re.findall(r'async def (create_\w+|add_\w+|insert_\w+)', content)
                operations["CREATE"] = create_matches
                
                # Find READ operations
                read_matches = re.findall(r'async def (get_\w+|find_\w+|list_\w+|fetch_\w+)', content)
                operations["READ"] = read_matches
                
                # Find UPDATE operations
                update_matches = re.findall(r'async def (update_\w+|modify_\w+|edit_\w+)', content)
                operations["UPDATE"] = update_matches
                
                # Find DELETE operations
                delete_matches = re.findall(r'async def (delete_\w+|remove_\w+|destroy_\w+)', content)
                operations["DELETE"] = delete_matches
                
                if any(operations.values()):
                    crud_operations[service_file.stem] = {
                        "file": service_file.name,
                        "operations": operations,
                        "has_full_crud": all(operations.values()),
                        "total_operations": sum(len(ops) for ops in operations.values())
                    }
                    
            except Exception as e:
                continue
        
        self.audit_results["crud_operations"] = crud_operations
        print(f"   📊 Found {len(crud_operations)} services with CRUD operations")
        
        # Count services with full CRUD
        full_crud_services = sum(1 for c in crud_operations.values() if c["has_full_crud"])
        print(f"   📊 Services with full CRUD: {full_crud_services}")
    
    def audit_authentication(self):
        """Audit authentication system"""
        auth_info = {}
        
        # Check auth service
        auth_file = self.backend_path / "services" / "auth_service.py"
        if auth_file.exists():
            with open(auth_file, 'r') as f:
                content = f.read()
            
            auth_info["auth_service"] = {
                "exists": True,
                "has_jwt": "jwt" in content.lower(),
                "has_oauth": "oauth" in content.lower(),
                "has_google_auth": "google" in content.lower(),
                "has_apple_auth": "apple" in content.lower(),
                "has_email_auth": "email" in content.lower(),
                "has_password_hashing": "bcrypt" in content.lower() or "hash" in content.lower()
            }
        
        # Check auth API
        auth_api_file = self.backend_path / "api" / "auth.py"
        if auth_api_file.exists():
            with open(auth_api_file, 'r') as f:
                content = f.read()
            
            auth_info["auth_api"] = {
                "exists": True,
                "endpoints": re.findall(r'@router\.(get|post|put|delete)\("([^"]+)"', content),
                "has_login": "login" in content.lower(),
                "has_register": "register" in content.lower(),
                "has_logout": "logout" in content.lower(),
                "has_refresh": "refresh" in content.lower()
            }
        
        # Check Google OAuth
        google_oauth_file = self.backend_path / "api" / "google_oauth.py"
        if google_oauth_file.exists():
            auth_info["google_oauth"] = {"exists": True}
        
        self.audit_results["authentication"] = auth_info
        print(f"   📊 Authentication system components: {len(auth_info)}")
    
    def audit_features_implementation(self):
        """Audit implementation status of major features"""
        features = {
            "workspace_management": {
                "description": "Multi-workspace system with role-based access",
                "key_files": ["workspace_management_service.py", "workspaces.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["workspaces", "workspace_members"]
            },
            "social_media_leads": {
                "description": "Real social media lead generation",
                "key_files": ["real_twitter_lead_generation_service.py", "real_tiktok_lead_generation_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["twitter_leads", "tiktok_leads"]
            },
            "ai_automation": {
                "description": "AI-powered content generation and automation",
                "key_files": ["real_ai_automation_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["ai_generated_content", "automation_workflows"]
            },
            "email_automation": {
                "description": "Email marketing with real API integration",
                "key_files": ["real_email_automation_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["email_campaigns", "email_logs"]
            },
            "link_in_bio": {
                "description": "Link in bio builder with drag-and-drop",
                "key_files": ["bio_sites_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["bio_sites", "bio_links"]
            },
            "course_platform": {
                "description": "Course creation and community platform",
                "key_files": ["course_service.py", "advanced_lms_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["courses", "lessons", "communities"]
            },
            "ecommerce": {
                "description": "E-commerce marketplace and stores",
                "key_files": ["ecommerce_service.py", "enhanced_ecommerce_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["products", "orders", "stores"]
            },
            "website_builder": {
                "description": "No-code website builder",
                "key_files": ["website_builder_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["websites", "pages"]
            },
            "booking_system": {
                "description": "Appointment scheduling system",
                "key_files": ["booking_service.py", "bookings_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["bookings", "appointments"]
            },
            "template_marketplace": {
                "description": "Template creation and marketplace",
                "key_files": ["template_marketplace_service.py"],
                "implemented": False,
                "api_endpoints": [],
                "database_collections": ["templates", "template_categories"]
            }
        }
        
        # Check implementation status
        for feature_name, feature_info in features.items():
            # Check if key files exist
            key_files_exist = 0
            for key_file in feature_info["key_files"]:
                if (self.backend_path / "services" / key_file).exists():
                    key_files_exist += 1
            
            # Check if API endpoints exist
            api_files_exist = 0
            for api_file in (self.backend_path / "api").glob("*.py"):
                if any(keyword in api_file.name for keyword in feature_name.split("_")):
                    api_files_exist += 1
            
            # Determine implementation status
            if key_files_exist > 0 and api_files_exist > 0:
                feature_info["implemented"] = True
                feature_info["implementation_level"] = "full"
            elif key_files_exist > 0 or api_files_exist > 0:
                feature_info["implemented"] = True
                feature_info["implementation_level"] = "partial"
            else:
                feature_info["implemented"] = False
                feature_info["implementation_level"] = "none"
            
            feature_info["key_files_found"] = key_files_exist
            feature_info["api_files_found"] = api_files_exist
        
        self.audit_results["features_implemented"] = features
        
        # Count implementation status
        fully_implemented = sum(1 for f in features.values() if f.get("implementation_level") == "full")
        partially_implemented = sum(1 for f in features.values() if f.get("implementation_level") == "partial")
        not_implemented = sum(1 for f in features.values() if f.get("implementation_level") == "none")
        
        print(f"   📊 Fully implemented features: {fully_implemented}")
        print(f"   📊 Partially implemented features: {partially_implemented}")
        print(f"   📊 Not implemented features: {not_implemented}")
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        report_file = Path("/app/MEWAYZ_COMPREHENSIVE_AUDIT_REPORT.md")
        
        with open(report_file, 'w') as f:
            f.write("# 🔍 MEWAYZ PLATFORM COMPREHENSIVE AUDIT REPORT\n\n")
            f.write(f"**Audit Date:** {self.audit_results['audit_date']}\n")
            f.write(f"**Platform Version:** {self.audit_results['platform_version']}\n\n")
            
            # API Endpoints Summary
            f.write("## 📋 API ENDPOINTS SUMMARY\n\n")
            api_endpoints = self.audit_results["api_endpoints"]
            total_endpoints = sum(
                ep.get("endpoint_count", 0) for ep in api_endpoints.values() 
                if "endpoint_count" in ep
            )
            f.write(f"- **Total API Modules:** {len(api_endpoints)}\n")
            f.write(f"- **Total API Endpoints:** {total_endpoints}\n\n")
            
            # Services Summary
            f.write("## 🔧 SERVICES SUMMARY\n\n")
            services = self.audit_results["services"]
            real_data_services = sum(1 for s in services.values() if s.get("has_real_data", False))
            mock_data_services = sum(1 for s in services.values() if s.get("has_mock_data", False))
            f.write(f"- **Total Services:** {len(services)}\n")
            f.write(f"- **Services with Real Data:** {real_data_services}\n")
            f.write(f"- **Services with Mock Data:** {mock_data_services}\n\n")
            
            # Database Collections Summary
            f.write("## 🗄️ DATABASE COLLECTIONS SUMMARY\n\n")
            collections = self.audit_results["database_collections"]
            full_crud = sum(1 for c in collections.values() if len(c["operations"]) == 4)
            f.write(f"- **Total Collections:** {len(collections)}\n")
            f.write(f"- **Collections with Full CRUD:** {full_crud}\n\n")
            
            # Real Data Integrations Summary
            f.write("## 🔌 REAL DATA INTEGRATIONS SUMMARY\n\n")
            integrations = self.audit_results["real_data_integrations"]
            api_keys = len(integrations.get("environment_variables", {}))
            real_services = len(integrations.get("real_services", {}))
            f.write(f"- **Configured API Keys:** {api_keys}\n")
            f.write(f"- **Real API Services:** {real_services}\n\n")
            
            # Features Implementation Summary
            f.write("## 🎯 FEATURES IMPLEMENTATION SUMMARY\n\n")
            features = self.audit_results["features_implemented"]
            fully_implemented = sum(1 for f in features.values() if f.get("implementation_level") == "full")
            partially_implemented = sum(1 for f in features.values() if f.get("implementation_level") == "partial")
            not_implemented = sum(1 for f in features.values() if f.get("implementation_level") == "none")
            f.write(f"- **Fully Implemented:** {fully_implemented}\n")
            f.write(f"- **Partially Implemented:** {partially_implemented}\n")
            f.write(f"- **Not Implemented:** {not_implemented}\n\n")
            
            # Detailed Analysis
            f.write("## 📊 DETAILED ANALYSIS\n\n")
            
            # API Endpoints Details
            f.write("### API Endpoints by Module\n\n")
            for module, info in api_endpoints.items():
                if "endpoint_count" in info:
                    f.write(f"- **{module}**: {info['endpoint_count']} endpoints\n")
            f.write("\n")
            
            # Real Data Services Details
            f.write("### Real Data Services\n\n")
            for service, info in services.items():
                if info.get("has_real_data", False):
                    apis = ", ".join(info.get("real_apis", []))
                    f.write(f"- **{service}**: {apis}\n")
            f.write("\n")
            
            # Database Collections Details
            f.write("### Database Collections\n\n")
            for collection, info in collections.items():
                operations = ", ".join(info["operations"])
                f.write(f"- **{collection}**: {operations}\n")
            f.write("\n")
            
            # Features Implementation Details
            f.write("### Features Implementation Status\n\n")
            for feature, info in features.items():
                status = "✅" if info["implementation_level"] == "full" else "⚠️" if info["implementation_level"] == "partial" else "❌"
                f.write(f"- {status} **{feature}**: {info['implementation_level']}\n")
            f.write("\n")
        
        print(f"   📄 Report generated: {report_file}")
        
        # Also save as JSON
        json_file = Path("/app/mewayz_audit_results.json")
        with open(json_file, 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        print(f"   📄 JSON data saved: {json_file}")

def main():
    """Main execution function"""
    auditor = MewayzPlatformAuditor()
    results = auditor.run_full_audit()
    
    print("\n" + "=" * 80)
    print("🎉 AUDIT COMPLETED SUCCESSFULLY!")
    print("📄 Check MEWAYZ_COMPREHENSIVE_AUDIT_REPORT.md for detailed report")
    print("📄 Check mewayz_audit_results.json for raw data")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    main()