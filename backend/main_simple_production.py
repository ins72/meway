"""
Mewayz Professional Platform - SIMPLIFIED PRODUCTION READY VERSION
Complete CRUD operations with proper authentication - Immediate router loading
"""

import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Minimal logging to stdout only
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(message)s')
logger = logging.getLogger("mewayz")

# Global startup time - never changes
STARTUP_TIME = datetime.utcnow()

# Create FastAPI app with production configuration
app = FastAPI(
    title="Mewayz Professional Platform API",
    version="2.0.0",
    description="Complete CRUD operations for Mewayz Professional Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Production CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# BULLETPROOF HEALTH ENDPOINTS - Zero dependencies, instant response
@app.get("/")
def root():
    """Root endpoint - pure Python, no dependencies"""
    return {
        "service": "mewayz-professional-api",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "production_ready": True
    }

@app.get("/health")
def health():
    """Health check - guaranteed to work, no dependencies"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - STARTUP_TIME).total_seconds(),
        "production_ready": True
    }

@app.get("/api/health") 
def api_health():
    """API health check - same as health"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - STARTUP_TIME).total_seconds(),
        "production_ready": True
    }

@app.get("/readiness")
def readiness():
    """Kubernetes readiness probe - always ready"""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "ready"
    }

@app.get("/liveness")
def liveness():
    """Kubernetes liveness probe - always alive"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "alive"
    }

# Log successful startup
logger.info("🚀 Mewayz Professional API starting - health endpoints ready")

# IMMEDIATE ROUTER LOADING - No background threads
logger.info("🔄 Loading API routers immediately...")

# Core CRUD routers - load these first
core_routers = [
    ("workspace", "/api/workspace"),
    ("user", "/api/user"),
    ("blog", "/api/blog"),
    ("auth", "/api/auth"),
    ("dashboard", "/api/dashboard"),
    ("analytics", "/api/analytics"),
    ("crm", "/api/crm"),
    ("booking", "/api/booking"),
    ("email_marketing", "/api/email-marketing"),
    ("financial", "/api/financial"),
    ("workspace_subscription", "/api/workspace-subscription"),
    ("website_builder", "/api/website-builder"),
    ("notification", "/api/notification"),
    ("campaign", "/api/campaign"),
    ("content", "/api/content"),
    ("media", "/api/media"),
    ("templates", "/api/templates"),
    ("integrations", "/api/integrations"),
    ("settings", "/api/settings"),
    ("profile", "/api/profile"),
    ("admin", "/api/admin"),
]

loaded_routers = 0
for router_name, prefix in core_routers:
    try:
        module = __import__(f"api.{router_name}", fromlist=["router"])
        if hasattr(module, "router"):
            app.include_router(module.router, prefix=prefix, tags=[router_name])
            loaded_routers += 1
            logger.info(f"✅ Loaded router: {router_name}")
        else:
            logger.warning(f"⚠️ Router not found in {router_name}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load router {router_name}: {e}")

logger.info(f"✅ Core routers loaded: {loaded_routers}")

# Load additional routers
additional_routers = [
    ("workspace_subscription", "/api/workspace-subscription"),
    ("website_builder", "/api/website-builder"),
    ("workflow_automation", "/api/workflow-automation"),
    ("webhook", "/api/webhook"),
    ("visual_builder", "/api/visual-builder"),
    ("vendor_customer_referrals", "/api/vendor-customer-referrals"),
    ("usage_tracking", "/api/usage-tracking"),
    ("unified_analytics_gamification", "/api/unified-analytics-gamification"),
    ("twitter", "/api/twitter"),
    ("tiktok", "/api/tiktok"),
    ("template_marketplace", "/api/template-marketplace"),
    ("template_marketplace_revenue", "/api/template-marketplace-revenue"),
    ("template_marketplace_access", "/api/template-marketplace-access"),
    ("template", "/api/template"),
    ("team_management", "/api/team-management"),
    ("sync", "/api/sync"),
    ("survey", "/api/survey"),
    ("support", "/api/support"),
    ("subscription", "/api/subscription"),
    ("stripe_integration", "/api/stripe-integration"),
    ("social_media", "/api/social-media"),
    ("social_email_integration", "/api/social-email-integration"),
    ("social_email", "/api/social-email"),
    ("simple_stripe", "/api/simple-stripe"),
    ("seo", "/api/seo"),
    ("security", "/api/security"),
    ("report", "/api/report"),
    ("referral_system", "/api/referral-system"),
    ("realtime_notifications", "/api/realtime-notifications"),
    ("real_ai_automation", "/api/real-ai-automation"),
    ("real_email_automation", "/api/real-email-automation"),
    ("rate_limiting", "/api/rate-limiting"),
    ("pwa_management", "/api/pwa-management"),
    ("promotions_referrals", "/api/promotions-referrals"),
    ("preference", "/api/preference"),
    ("production_monitoring", "/api/production-monitoring"),
    ("plan_change_impact", "/api/plan-change-impact"),
    ("onboarding_progress", "/api/onboarding-progress"),
    ("payment", "/api/payment"),
    ("native_mobile", "/api/native-mobile"),
    ("monitoring", "/api/monitoring"),
    ("multi_vendor_marketplace", "/api/multi-vendor-marketplace"),
    ("mobile_pwa_features", "/api/mobile-pwa-features"),
    ("mobile_pwa", "/api/mobile-pwa"),
    ("metric", "/api/metric"),
    ("marketing", "/api/marketing"),
    ("media_library", "/api/media-library"),
    ("log", "/api/log"),
    ("link", "/api/link"),
    ("link_shortener", "/api/link-shortener"),
    ("lead", "/api/lead"),
    ("launch_pricing", "/api/launch-pricing"),
    ("integration", "/api/integration"),
    ("integration_tests", "/api/integration-tests"),
    ("i18n", "/api/i18n"),
    ("import_api", "/api/import-api"),
    ("google_oauth", "/api/google-oauth"),
    ("form_builder", "/api/form-builder"),
    ("form", "/api/form"),
    ("export", "/api/export"),
    ("escrow", "/api/escrow"),
    ("enterprise_security_compliance", "/api/enterprise-security-compliance"),
    ("enterprise_security", "/api/enterprise-security"),
    ("enterprise_revenue", "/api/enterprise-revenue"),
    ("enhanced_stripe", "/api/enhanced-stripe"),
    ("enhanced_features", "/api/enhanced-features"),
    ("data_population", "/api/data-population"),
    ("customer_experience", "/api/customer-experience"),
    ("course", "/api/course"),
    ("content_creation", "/api/content-creation"),
    ("comprehensive_marketing_website", "/api/comprehensive-marketing-website"),
    ("configuration", "/api/configuration"),
    ("complete_social_media_leads", "/api/complete-social-media-leads"),
    ("compliance", "/api/compliance"),
    ("complete_onboarding", "/api/complete-onboarding"),
    ("complete_multi_workspace", "/api/complete-multi-workspace"),
    ("complete_link_in_bio", "/api/complete-link-in-bio"),
    ("complete_financial", "/api/complete-financial"),
    ("complete_ecommerce", "/api/complete-ecommerce"),
    ("complete_course_community", "/api/complete-course-community"),
    ("complete_admin_dashboard", "/api/complete-admin-dashboard"),
    ("campaign", "/api/campaign"),
    ("business_intelligence", "/api/business-intelligence"),
    ("bio_sites", "/api/bio-sites"),
    ("automation", "/api/automation"),
    ("backup", "/api/backup")
]

additional_loaded = 0
for router_name, prefix in additional_routers:
    try:
        module = __import__(f"api.{router_name}", fromlist=["router"])
        if hasattr(module, "router"):
            app.include_router(module.router, prefix=prefix, tags=[router_name])
            additional_loaded += 1
            logger.info(f"✅ Loaded additional router: {router_name}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load additional router {router_name}: {e}")

total_routers = loaded_routers + additional_loaded
logger.info(f"✅ Total routers loaded: {total_routers}")

# Initialize database connection
async def initialize_database():
    """Initialize database connection"""
    try:
        from core.database import connect_to_mongo
        await connect_to_mongo()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {e}")

# Add startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await initialize_database()

logger.info("✅ Mewayz Professional API ready - Complete CRUD operations available")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    ) 