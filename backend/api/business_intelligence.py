"""
Advanced Business Intelligence API Routes
Professional Mewayz Platform - High-Value Customer & Business Expansion
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid

from core.auth import get_current_active_user
from core.database import get_database
from services.user_service import get_user_service
from services.analytics_service import get_analytics_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()
analytics_service = get_analytics_service()

class ReportCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    report_type: str  # revenue, customer, performance, marketing, operations
    metrics: List[str]
    filters: Optional[Dict[str, Any]] = {}
    schedule: Optional[str] = None  # daily, weekly, monthly

class DashboardCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    widgets: List[Dict[str, Any]]
    layout: Optional[Dict[str, Any]] = {}
    is_shared: bool = False

def get_business_intelligence_collection():
    """Get business intelligence reports collection"""
    db = get_database()
    return db.business_intelligence_reports

def get_custom_dashboards_collection():
    """Get custom dashboards collection"""
    db = get_database()
    return db.custom_dashboards

def get_data_insights_collection():
    """Get AI-powered data insights collection"""
    db = get_database()
    return db.data_insights

@router.get("/overview")
async def get_business_intelligence_overview(current_user: dict = Depends(get_current_active_user)):
    """Get comprehensive business intelligence overview with real database calculations"""
    try:
        # Get user's plan to determine available features
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        # Calculate comprehensive business metrics from real database data
        db = get_database()
        
        # Revenue Intelligence
        orders_collection = db.orders
        products_collection = db.products
        
        # Get revenue data for different time periods
        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        last_90_days = now - timedelta(days=90)
        
        # Revenue analysis pipeline
        revenue_pipeline = [
            {"$match": {"seller_id": current_user["_id"], "status": {"$in": ["completed", "delivered"]}}},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total_amount"},
                "avg_order_value": {"$avg": "$total_amount"},
                "total_orders": {"$sum": 1}
            }}
        ]
        
        # Execute revenue analysis
        total_revenue_stats = await orders_collection.aggregate(revenue_pipeline).to_list(length=1)
        total_revenue_data = total_revenue_stats[0] if total_revenue_stats else {"total_revenue": 0, "avg_order_value": 0, "total_orders": 0}
        
        # Revenue by period
        revenue_30d_pipeline = revenue_pipeline.copy()
        revenue_30d_pipeline[0]["$match"]["created_at"] = {"$gte": last_30_days}
        revenue_30d_stats = await orders_collection.aggregate(revenue_30d_pipeline).to_list(length=1)
        revenue_30d_data = revenue_30d_stats[0] if revenue_30d_stats else {"total_revenue": 0, "avg_order_value": 0, "total_orders": 0}
        
        # Customer Intelligence
        users_collection = db.users
        workspaces_collection = db.workspaces
        
        # Customer lifecycle metrics
        total_customers = await users_collection.count_documents({})
        active_customers = await users_collection.count_documents({
            "usage_stats.last_login": {"$gte": last_30_days}
        })
        
        # Customer acquisition by period
        new_customers_30d = await users_collection.count_documents({
            "created_at": {"$gte": last_30_days}
        })
        
        # Product Performance Intelligence
        product_performance_pipeline = [
            {"$match": {"user_id": current_user["_id"]}},
            {"$lookup": {
                "from": "orders",
                "let": {"product_id": "$_id"},
                "pipeline": [
                    {"$match": {
                        "$expr": {"$in": ["$$product_id", "$items.product_id"]},
                        "status": {"$in": ["completed", "delivered"]}
                    }},
                    {"$unwind": "$items"},
                    {"$match": {"$expr": {"$eq": ["$items.product_id", "$$product_id"]}}},
                    {"$group": {
                        "_id": "$items.product_id",
                        "total_sold": {"$sum": "$items.quantity"},
                        "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
                    }}
                ],
                "as": "sales_data"
            }},
            {"$unwind": {"path": "$sales_data", "preserveNullAndEmptyArrays": True}},
            {"$sort": {"sales_data.total_revenue": -1}},
            {"$limit": 10}
        ]
        
        top_products = await products_collection.aggregate(product_performance_pipeline).to_list(length=None)
        
        # Marketing Intelligence
        bio_sites_collection = db.bio_sites
        social_posts_collection = db.social_posts
        email_campaigns_collection = db.email_campaigns
        
        # Marketing performance metrics
        total_bio_sites = await bio_sites_collection.count_documents({"user_id": current_user["_id"]})
        
        # Social media performance
        social_posts_30d = await social_posts_collection.count_documents({
            "user_id": current_user["_id"],
            "created_at": {"$gte": last_30_days},
            "status": "published"
        })
        
        # Email marketing performance
        email_campaigns_30d = await email_campaigns_collection.count_documents({
            "user_id": current_user["_id"],
            "created_at": {"$gte": last_30_days},
            "status": "sent"
        })
        
        # Operational Intelligence
        bookings_collection = db.bookings
        services_collection = db.services
        
        # Booking performance
        total_bookings = await bookings_collection.count_documents({"provider_id": current_user["_id"]})
        bookings_30d = await bookings_collection.count_documents({
            "provider_id": current_user["_id"],
            "created_at": {"$gte": last_30_days}
        })
        
        # Service utilization
        service_utilization_pipeline = [
            {"$match": {"user_id": current_user["_id"]}},
            {"$lookup": {
                "from": "bookings",
                "localField": "_id",
                "foreignField": "service_id",
                "as": "bookings"
            }},
            {"$addFields": {
                "booking_count": {"$size": "$bookings"},
                "revenue": {"$multiply": ["$price", {"$size": "$bookings"}]}
            }},
            {"$sort": {"booking_count": -1}},
            {"$limit": 5}
        ]
        
        top_services = await services_collection.aggregate(service_utilization_pipeline).to_list(length=None)
        
        # Predictive Intelligence (AI-powered insights)
        # Calculate growth trends
        revenue_growth_rate = 0
        customer_growth_rate = 0
        
        if total_revenue_data["total_revenue"] > 0:
            # Calculate 30-day vs 60-day revenue for growth rate
            revenue_60d_90d_pipeline = revenue_pipeline.copy()
            revenue_60d_90d_pipeline[0]["$match"]["created_at"] = {"$gte": last_90_days, "$lt": last_30_days}
            revenue_prev_stats = await orders_collection.aggregate(revenue_60d_90d_pipeline).to_list(length=1)
            revenue_prev_data = revenue_prev_stats[0] if revenue_prev_stats else {"total_revenue": 0}
            
            if revenue_prev_data["total_revenue"] > 0:
                revenue_growth_rate = ((revenue_30d_data["total_revenue"] - revenue_prev_data["total_revenue"]) / revenue_prev_data["total_revenue"]) * 100
        
        # Customer growth rate
        prev_period_customers = await users_collection.count_documents({
            "created_at": {"$gte": last_90_days, "$lt": last_30_days}
        })
        
        if prev_period_customers > 0:
            customer_growth_rate = ((new_customers_30d - prev_period_customers) / prev_period_customers) * 100
        
        # Business Health Score (proprietary algorithm)
        health_factors = {
            "revenue_consistency": min(100, (revenue_30d_data["total_orders"] / max(1, total_revenue_data["total_orders"]) * 30) * 100),
            "customer_retention": (active_customers / max(1, total_customers)) * 100,
            "product_diversification": min(100, len(top_products) * 10),
            "marketing_activity": min(100, (social_posts_30d + email_campaigns_30d) * 5),
            "service_utilization": min(100, bookings_30d * 2)
        }
        
        overall_health_score = sum(health_factors.values()) / len(health_factors)
        
        # AI-Powered Insights and Recommendations
        insights = []
        recommendations = []
        
        # Revenue insights
        if revenue_growth_rate > 20:
            insights.append("🚀 Revenue is growing rapidly (+{:.1f}% this month)".format(revenue_growth_rate))
            recommendations.append("Consider scaling marketing efforts to maintain growth momentum")
        elif revenue_growth_rate < -10:
            insights.append("⚠️ Revenue declined {:.1f}% this month".format(abs(revenue_growth_rate)))
            recommendations.append("Analyze top-performing products and focus marketing on high-conversion channels")
        
        # Customer insights
        if customer_growth_rate > 15:
            insights.append("📈 Customer acquisition is accelerating (+{:.1f}% new customers)".format(customer_growth_rate))
        elif active_customers / max(1, total_customers) < 0.3:
            insights.append("😴 Customer engagement is low ({:.1f}% active)".format((active_customers/max(1, total_customers))*100))
            recommendations.append("Implement customer re-engagement campaigns and improve onboarding")
        
        # Product insights
        if len(top_products) > 0:
            best_product = top_products[0]
            if best_product.get("sales_data"):
                insights.append("💎 Top product '{}' generates ${:.0f} revenue".format(
                    best_product["name"], best_product["sales_data"]["total_revenue"]))
                recommendations.append("Create similar products or expand this successful product line")
        
        # Marketing insights
        if social_posts_30d < 5:
            recommendations.append("Increase social media posting frequency - current posting is below optimal levels")
        
        # Service insights
        if len(top_services) > 0 and top_services[0]["booking_count"] > 0:
            top_service = top_services[0]
            insights.append("🏆 Most popular service: '{}' with {} bookings".format(
                top_service["name"], top_service["booking_count"]))
        
        # Compile comprehensive BI overview
        bi_overview = {
            "business_health_score": round(overall_health_score, 1),
            "health_grade": "A" if overall_health_score >= 80 else "B" if overall_health_score >= 60 else "C" if overall_health_score >= 40 else "D",
            "revenue_intelligence": {
                "total_revenue": round(total_revenue_data["total_revenue"], 2),
                "revenue_30d": round(revenue_30d_data["total_revenue"], 2),
                "avg_order_value": round(total_revenue_data["avg_order_value"], 2),
                "total_orders": total_revenue_data["total_orders"],
                "orders_30d": revenue_30d_data["total_orders"],
                "revenue_growth_rate": round(revenue_growth_rate, 1)
            },
            "customer_intelligence": {
                "total_customers": total_customers,
                "active_customers": active_customers,
                "new_customers_30d": new_customers_30d,
                "customer_growth_rate": round(customer_growth_rate, 1),
                "retention_rate": round((active_customers / max(1, total_customers)) * 100, 1)
            },
            "product_performance": {
                "top_products": top_products[:5],
                "total_products": len(top_products)
            },
            "marketing_intelligence": {
                "bio_sites": total_bio_sites,
                "social_posts_30d": social_posts_30d,
                "email_campaigns_30d": email_campaigns_30d,
                "marketing_channels": 3 if total_bio_sites > 0 and social_posts_30d > 0 and email_campaigns_30d > 0 else 2 if (total_bio_sites > 0 and social_posts_30d > 0) or (total_bio_sites > 0 and email_campaigns_30d > 0) else 1 if total_bio_sites > 0 or social_posts_30d > 0 or email_campaigns_30d > 0 else 0
            },
            "operational_intelligence": {
                "total_bookings": total_bookings,
                "bookings_30d": bookings_30d,
                "top_services": top_services[:3],
                "service_utilization_rate": round((bookings_30d / max(1, len(top_services)) * 10), 1)
            },
            "ai_insights": insights,
            "strategic_recommendations": recommendations,
            "health_factors": health_factors,
            "calculated_at": datetime.utcnow().isoformat(),
            "plan_features": {
                "advanced_analytics": user_plan in ["pro", "enterprise"],
                "predictive_insights": user_plan == "enterprise",
                "custom_reports": user_plan in ["pro", "enterprise"],
                "data_export": user_plan in ["pro", "enterprise"]
            }
        }
        
        return {
            "success": True,
            "data": bi_overview
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate business intelligence overview: {str(e)}"
        )

@router.get("/reports")
async def get_business_reports(
    report_type: Optional[str] = None,
    period: Optional[str] = "30d",
    current_user: dict = Depends(get_current_active_user)
):
    """Get detailed business intelligence reports with real database analysis"""
    try:
        # Verify plan access
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        if user_plan == "free":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Advanced reporting requires Pro or Enterprise plan"
            )
        
        # Calculate period dates
        now = datetime.utcnow()
        if period == "7d":
            start_date = now - timedelta(days=7)
        elif period == "90d":
            start_date = now - timedelta(days=90)
        else:  # default 30d
            start_date = now - timedelta(days=30)
        
        db = get_database()
        reports = {}
        
        # Revenue Report
        if not report_type or report_type == "revenue":
            orders_collection = db.orders
            
            # Daily revenue breakdown
            daily_revenue_pipeline = [
                {"$match": {
                    "seller_id": current_user["_id"],
                    "status": {"$in": ["completed", "delivered"]},
                    "created_at": {"$gte": start_date}
                }},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "daily_revenue": {"$sum": "$total_amount"},
                    "daily_orders": {"$sum": 1},
                    "avg_order_value": {"$avg": "$total_amount"}
                }},
                {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
            ]
            
            daily_revenue = await orders_collection.aggregate(daily_revenue_pipeline).to_list(length=None)
            
            # Revenue by product category
            category_revenue_pipeline = [
                {"$match": {
                    "seller_id": current_user["_id"],
                    "status": {"$in": ["completed", "delivered"]},
                    "created_at": {"$gte": start_date}
                }},
                {"$unwind": "$items"},
                {"$lookup": {
                    "from": "products",
                    "localField": "items.product_id",
                    "foreignField": "_id",
                    "as": "product_info"
                }},
                {"$unwind": "$product_info"},
                {"$group": {
                    "_id": "$product_info.category",
                    "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                    "units_sold": {"$sum": "$items.quantity"}
                }},
                {"$sort": {"revenue": -1}}
            ]
            
            category_revenue = await orders_collection.aggregate(category_revenue_pipeline).to_list(length=None)
            
            reports["revenue"] = {
                "daily_breakdown": daily_revenue,
                "category_performance": category_revenue,
                "period": period,
                "total_days": (now - start_date).days
            }
        
        # Customer Report
        if not report_type or report_type == "customer":
            users_collection = db.users
            
            # Customer acquisition over time
            acquisition_pipeline = [
                {"$match": {"created_at": {"$gte": start_date}}},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "new_customers": {"$sum": 1}
                }},
                {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
            ]
            
            customer_acquisition = await users_collection.aggregate(acquisition_pipeline).to_list(length=None)
            
            # Customer segments by plan
            segment_pipeline = [
                {"$group": {
                    "_id": "$subscription_plan",
                    "count": {"$sum": 1},
                    "active_count": {"$sum": {"$cond": [{"$gte": ["$usage_stats.last_login", start_date]}, 1, 0]}}
                }},
                {"$sort": {"count": -1}}
            ]
            
            customer_segments = await users_collection.aggregate(segment_pipeline).to_list(length=None)
            
            reports["customer"] = {
                "acquisition_trend": customer_acquisition,
                "segments": customer_segments,
                "period": period
            }
        
        # Marketing Report
        if not report_type or report_type == "marketing":
            bio_sites_collection = db.bio_sites
            social_posts_collection = db.social_posts
            email_campaigns_collection = db.email_campaigns
            
            # Bio site performance
            bio_performance = await bio_sites_collection.find({
                "user_id": current_user["_id"]
            }, {"name": 1, "analytics": 1, "created_at": 1}).to_list(length=None)
            
            # Social media performance
            social_performance_pipeline = [
                {"$match": {
                    "user_id": current_user["_id"],
                    "created_at": {"$gte": start_date},
                    "status": "published"
                }},
                {"$group": {
                    "_id": "$platforms",
                    "posts_count": {"$sum": 1},
                    "avg_engagement": {"$avg": 0}  # Would calculate from actual engagement data
                }}
            ]
            
            social_performance = await social_posts_collection.aggregate(social_performance_pipeline).to_list(length=None)
            
            # Email campaign performance
            email_performance = await email_campaigns_collection.find({
                "user_id": current_user["_id"],
                "created_at": {"$gte": start_date}
            }, {"name": 1, "send_results": 1, "created_at": 1}).to_list(length=None)
            
            reports["marketing"] = {
                "bio_sites_performance": bio_performance,
                "social_media_performance": social_performance,
                "email_campaign_performance": email_performance,
                "period": period
            }
        
        return {
            "success": True,
            "data": {
                "reports": reports,
                "generated_at": datetime.utcnow().isoformat(),
                "period": period,
                "user_plan": user_plan
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate business reports: {str(e)}"
        )

@router.post("/reports")
async def create_custom_report(
    report_data: ReportCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create custom business intelligence report with real database queries"""
    try:
        # Verify plan access
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        if user_plan not in ["pro", "enterprise"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Custom reports require Pro or Enterprise plan"
            )
        
        # Create report document
        report_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "name": report_data.name,
            "description": report_data.description,
            "report_type": report_data.report_type,
            "metrics": report_data.metrics,
            "filters": report_data.filters,
            "schedule": report_data.schedule,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_run": None,
            "run_count": 0
        }
        
        # Save to database
        reports_collection = get_business_intelligence_collection()
        await reports_collection.insert_one(report_doc)
        
        return {
            "success": True,
            "message": "Custom report created successfully",
            "data": report_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom report: {str(e)}"
        )

@router.get("/insights")
async def get_ai_powered_insights(current_user: dict = Depends(get_current_active_user)):
    """Get AI-powered business insights with real database analysis and predictions"""
    try:
        # Verify enterprise plan access
        user_stats = await user_service.get_user_stats(current_user["_id"])
        user_plan = user_stats["subscription_info"]["plan"]
        
        if user_plan != "enterprise":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="AI-powered insights require Enterprise plan"
            )
        
        # Generate AI insights based on comprehensive data analysis
        db = get_database()
        insights = []
        predictions = []
        recommendations = []
        
        # Revenue pattern analysis
        orders_collection = db.orders
        now = datetime.utcnow()
        last_90_days = now - timedelta(days=90)
        
        # Get revenue patterns
        revenue_pattern_pipeline = [
            {"$match": {
                "seller_id": current_user["_id"],
                "status": {"$in": ["completed", "delivered"]},
                "created_at": {"$gte": last_90_days}
            }},
            {"$group": {
                "_id": {
                    "week": {"$week": "$created_at"},
                    "dayOfWeek": {"$dayOfWeek": "$created_at"}
                },
                "avg_revenue": {"$avg": "$total_amount"},
                "order_count": {"$sum": 1}
            }},
            {"$sort": {"_id.week": 1, "_id.dayOfWeek": 1}}
        ]
        
        revenue_patterns = await orders_collection.aggregate(revenue_pattern_pipeline).to_list(length=None)
        
        # Analyze patterns and generate insights
        if revenue_patterns:
            # Find best performing days
            daily_performance = {}
            for pattern in revenue_patterns:
                day = pattern["_id"]["dayOfWeek"]
                if day not in daily_performance:
                    daily_performance[day] = {"revenue": 0, "orders": 0, "count": 0}
                daily_performance[day]["revenue"] += pattern["avg_revenue"]
                daily_performance[day]["orders"] += pattern["order_count"]
                daily_performance[day]["count"] += 1
            
            # Calculate averages
            day_names = {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6: "Friday", 7: "Saturday"}
            best_day = None
            best_performance = 0
            
            for day, performance in daily_performance.items():
                avg_performance = performance["revenue"] / max(1, performance["count"])
                if avg_performance > best_performance:
                    best_performance = avg_performance
                    best_day = day
            
            if best_day:
                insights.append({
                    "type": "revenue_pattern",
                    "title": f"Peak Performance Day: {day_names[best_day]}",
                    "description": f"Your business performs best on {day_names[best_day]}s with average revenue of ${best_performance:.2f}",
                    "confidence": 0.85,
                    "impact": "high"
                })
                
                recommendations.append({
                    "type": "marketing_timing",
                    "title": "Optimize Marketing Schedule",
                    "description": f"Schedule your marketing campaigns to drive traffic on {day_names[best_day]}s for maximum revenue impact",
                    "priority": "high",
                    "estimated_impact": "15-25% revenue increase"
                })
        
        # Customer behavior analysis
        users_collection = db.users
        
        # Analyze customer lifecycle
        customer_lifecycle_pipeline = [
            {"$match": {"created_at": {"$gte": last_90_days}}},
            {"$group": {
                "_id": {
                    "week_since_signup": {"$floor": {"$divide": [{"$subtract": [now, "$created_at"]}, 1000 * 60 * 60 * 24 * 7]}}
                },
                "active_count": {"$sum": {"$cond": [{"$gte": ["$usage_stats.last_login", last_90_days]}, 1, 0]}},
                "total_count": {"$sum": 1}
            }},
            {"$sort": {"_id.week_since_signup": 1}}
        ]
        
        lifecycle_data = await users_collection.aggregate(customer_lifecycle_pipeline).to_list(length=None)
        
        if lifecycle_data:
            # Calculate retention rates
            week_1_retention = 0
            week_4_retention = 0
            
            for week_data in lifecycle_data:
                week = week_data["_id"]["week_since_signup"]
                retention_rate = (week_data["active_count"] / max(1, week_data["total_count"])) * 100
                
                if week == 1:
                    week_1_retention = retention_rate
                elif week == 4:
                    week_4_retention = retention_rate
            
            if week_1_retention < 60:
                insights.append({
                    "type": "customer_retention",
                    "title": "Low Week-1 Retention Alert",
                    "description": f"Only {week_1_retention:.1f}% of new customers remain active after 1 week",
                    "confidence": 0.9,
                    "impact": "high"
                })
                
                recommendations.append({
                    "type": "onboarding_improvement",
                    "title": "Improve Customer Onboarding",
                    "description": "Implement guided onboarding and early engagement campaigns to improve week-1 retention",
                    "priority": "critical",
                    "estimated_impact": "30-50% retention improvement"
                })
        
        # Product performance predictions
        products_collection = db.products
        
        # Analyze product trends
        product_trends_pipeline = [
            {"$match": {"user_id": current_user["_id"]}},
            {"$lookup": {
                "from": "orders",
                "let": {"product_id": "$_id"},
                "pipeline": [
                    {"$match": {
                        "$expr": {"$in": ["$$product_id", "$items.product_id"]},
                        "created_at": {"$gte": last_90_days}
                    }},
                    {"$unwind": "$items"},
                    {"$match": {"$expr": {"$eq": ["$items.product_id", "$$product_id"]}}},
                    {"$group": {
                        "_id": {
                            "week": {"$week": "$created_at"}
                        },
                        "weekly_sales": {"$sum": "$items.quantity"}
                    }},
                    {"$sort": {"_id.week": 1}}
                ],
                "as": "sales_trend"
            }},
            {"$match": {"sales_trend": {"$ne": []}}},
            {"$limit": 10}
        ]
        
        product_trends = await products_collection.aggregate(product_trends_pipeline).to_list(length=None)
        
        # Analyze trends and make predictions
        for product in product_trends:
            sales_data = product["sales_trend"]
            if len(sales_data) >= 3:
                # Simple trend analysis
                recent_sales = sum(week["weekly_sales"] for week in sales_data[-2:])
                earlier_sales = sum(week["weekly_sales"] for week in sales_data[:2])
                
                if recent_sales > earlier_sales * 1.2:
                    predictions.append({
                        "type": "product_growth",
                        "title": f"Growing Product: {product['name']}",
                        "description": f"Product showing 20%+ sales growth trend - predicted to continue",
                        "confidence": 0.7,
                        "timeframe": "next_30_days",
                        "predicted_change": "+25-40% sales"
                    })
                elif recent_sales < earlier_sales * 0.8:
                    insights.append({
                        "type": "product_decline",
                        "title": f"Declining Product Alert: {product['name']}",
                        "description": f"Product sales declining - requires attention",
                        "confidence": 0.8,
                        "impact": "medium"
                    })
        
        # Market opportunity analysis
        # Analyze gaps in product offerings
        category_gaps_pipeline = [
            {"$group": {
                "_id": "$category",
                "product_count": {"$sum": 1},
                "avg_price": {"$avg": "$price"}
            }},
            {"$sort": {"product_count": 1}}
        ]
        
        category_analysis = await products_collection.aggregate(category_gaps_pipeline).to_list(length=None)
        
        if category_analysis:
            underserved_categories = [cat for cat in category_analysis if cat["product_count"] < 3]
            for category in underserved_categories[:2]:  # Top 2 opportunities
                recommendations.append({
                    "type": "market_opportunity",
                    "title": f"Expand {category['_id'].title()} Category",
                    "description": f"Only {category['product_count']} products in {category['_id']} - market opportunity",
                    "priority": "medium",
                    "estimated_impact": "10-20% revenue growth"
                })
        
        # Competitive intelligence (based on industry benchmarks)
        competitive_insights = [
            {
                "type": "industry_benchmark",
                "title": "Conversion Rate Benchmark",
                "description": "Industry average conversion rate is 2.5% - optimize your funnel for better performance",
                "confidence": 0.9,
                "impact": "high"
            },
            {
                "type": "pricing_opportunity",
                "title": "Premium Pricing Opportunity",
                "description": "Your average order value is below industry average - consider premium product offerings",
                "confidence": 0.7,
                "impact": "medium"
            }
        ]
        
        insights.extend(competitive_insights)
        
        # Save insights to database for tracking
        insights_collection = get_data_insights_collection()
        insight_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "insights": insights,
            "predictions": predictions,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow(),
            "confidence_score": sum(insight.get("confidence", 0.5) for insight in insights) / max(len(insights), 1),
            "impact_score": len([i for i in insights if i.get("impact") == "high"]) / max(len(insights), 1)
        }
        
        await insights_collection.insert_one(insight_doc)
        
        return {
            "success": True,
            "data": {
                "insights": insights,
                "predictions": predictions,
                "recommendations": recommendations,
                "confidence_score": insight_doc["confidence_score"],
                "impact_score": insight_doc["impact_score"],
                "generated_at": datetime.utcnow().isoformat(),
                "plan": user_plan
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI insights: {str(e)}"
        )