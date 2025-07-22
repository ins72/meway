"""
Advanced Business Intelligence Service
Predictive analytics, ML models, cohort analysis, and competitive intelligence
"""
import asyncio
import uuid
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from core.database import get_database
from core.professional_logger import professional_logger, LogLevel, LogCategory

class PredictionModel(Enum):
    REVENUE_FORECASTING = "revenue_forecasting"
    CUSTOMER_CHURN = "customer_churn"
    LIFETIME_VALUE = "lifetime_value"
    DEMAND_FORECASTING = "demand_forecasting"
    PRICE_OPTIMIZATION = "price_optimization"

class AdvancedBIService:
    """Comprehensive business intelligence with predictive capabilities"""
    
    def __init__(self):
        self.ml_models = {}
        self.prediction_cache = {}
    
    async def generate_predictive_insights(self, user_id: str, model_type: PredictionModel, 
                                         historical_days: int = 90) -> Dict[str, Any]:
        """Generate ML-powered predictive insights"""
        try:
            db = get_database()
            
            # Get historical data for predictions
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=historical_days)
            
            if model_type == PredictionModel.REVENUE_FORECASTING:
                return await self._predict_revenue(user_id, start_date, end_date)
            elif model_type == PredictionModel.CUSTOMER_CHURN:
                return await self._predict_churn(user_id, start_date, end_date)
            elif model_type == PredictionModel.LIFETIME_VALUE:
                return await self._predict_clv(user_id, start_date, end_date)
            elif model_type == PredictionModel.DEMAND_FORECASTING:
                return await self._forecast_demand(user_id, start_date, end_date)
            else:
                return {"error": "Model type not supported"}
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.ANALYTICS,
                f"Predictive insights failed: {str(e)}",
                error=e, user_id=user_id
            )
            return {"error": str(e)}
    
    async def _predict_revenue(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Revenue forecasting using time series analysis"""
        try:
            db = get_database()
            
            # Get historical revenue data
            revenue_pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "created_at": {"$gte": start_date, "$lte": end_date},
                        "status": "completed"
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"},
                            "day": {"$dayOfMonth": "$created_at"}
                        },
                        "daily_revenue": {"$sum": "$amount"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            historical_data = await db.orders.aggregate(revenue_pipeline).to_list(length=None)
            
            if len(historical_data) < 7:
                return {
                    "prediction": "insufficient_data",
                    "message": "Need at least 7 days of data for revenue prediction"
                }
            
            # Simple trend analysis (in production, use more sophisticated ML models)
            revenues = [day["daily_revenue"] for day in historical_data]
            
            # Calculate trend
            x = list(range(len(revenues)))
            if len(x) > 1:
                # Simple linear regression
                n = len(x)
                sum_x = sum(x)
                sum_y = sum(revenues)
                sum_xy = sum(x[i] * revenues[i] for i in range(n))
                sum_x2 = sum(xi * xi for xi in x)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                intercept = (sum_y - slope * sum_x) / n
                
                # Predict next 30 days
                future_predictions = []
                for day in range(1, 31):
                    future_day = len(revenues) + day
                    predicted_revenue = slope * future_day + intercept
                    future_predictions.append(max(0, predicted_revenue))  # Non-negative revenue
                
                return {
                    "model": "linear_trend",
                    "historical_average": sum(revenues) / len(revenues),
                    "trend_slope": slope,
                    "prediction_period": "30_days",
                    "predicted_total": sum(future_predictions),
                    "predicted_daily_average": sum(future_predictions) / len(future_predictions),
                    "confidence_interval": {
                        "lower": sum(future_predictions) * 0.8,
                        "upper": sum(future_predictions) * 1.2
                    },
                    "recommendations": self._generate_revenue_recommendations(slope, revenues)
                }
            
            return {"prediction": "insufficient_variation", "message": "Revenue data lacks variation for prediction"}
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.ANALYTICS,
                f"Revenue prediction failed: {str(e)}",
                error=e
            )
            return {"error": str(e)}
    
    async def _predict_churn(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Customer churn prediction"""
        try:
            db = get_database()
            
            # Get customer activity data
            customers = await db.customers.find({"user_id": user_id}).to_list(length=None)
            
            if len(customers) < 10:
                return {"prediction": "insufficient_customers", "message": "Need at least 10 customers for churn analysis"}
            
            churn_predictions = []
            
            for customer in customers:
                customer_id = customer["_id"]
                
                # Get customer activity metrics
                last_30_days = datetime.utcnow() - timedelta(days=30)
                
                # Recent orders
                recent_orders = await db.orders.count_documents({
                    "customer_id": customer_id,
                    "created_at": {"$gte": last_30_days}
                })
                
                # Recent interactions
                recent_interactions = await db.customer_interactions.count_documents({
                    "customer_id": customer_id,
                    "created_at": {"$gte": last_30_days}
                })
                
                # Calculate churn risk score (simplified)
                risk_score = 0
                
                if recent_orders == 0:
                    risk_score += 40
                elif recent_orders < 2:
                    risk_score += 20
                
                if recent_interactions == 0:
                    risk_score += 30
                
                # Customer lifetime
                customer_age_days = (datetime.utcnow() - customer.get("created_at", datetime.utcnow())).days
                if customer_age_days > 180:  # Older customers
                    risk_score += 10
                
                churn_risk = "high" if risk_score > 60 else "medium" if risk_score > 30 else "low"
                
                churn_predictions.append({
                    "customer_id": customer_id,
                    "customer_email": customer.get("email", "unknown"),
                    "churn_risk": churn_risk,
                    "risk_score": risk_score,
                    "factors": {
                        "recent_orders": recent_orders,
                        "recent_interactions": recent_interactions,
                        "customer_age_days": customer_age_days
                    }
                })
            
            # Summary statistics
            high_risk = len([c for c in churn_predictions if c["churn_risk"] == "high"])
            medium_risk = len([c for c in churn_predictions if c["churn_risk"] == "medium"])
            low_risk = len([c for c in churn_predictions if c["churn_risk"] == "low"])
            
            return {
                "model": "risk_scoring",
                "total_customers": len(customers),
                "churn_summary": {
                    "high_risk": high_risk,
                    "medium_risk": medium_risk,
                    "low_risk": low_risk,
                    "churn_rate_estimate": (high_risk / len(customers)) * 100
                },
                "customer_predictions": churn_predictions[:20],  # Top 20 for API response
                "recommendations": self._generate_churn_recommendations(high_risk, len(customers))
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.ANALYTICS,
                f"Churn prediction failed: {str(e)}",
                error=e
            )
            return {"error": str(e)}
    
    async def _predict_clv(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Customer Lifetime Value prediction"""
        try:
            db = get_database()
            
            # Get customer transaction data
            clv_pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "status": "completed"
                    }
                },
                {
                    "$group": {
                        "_id": "$customer_id",
                        "total_spent": {"$sum": "$amount"},
                        "order_count": {"$sum": 1},
                        "first_order": {"$min": "$created_at"},
                        "last_order": {"$max": "$created_at"},
                        "avg_order_value": {"$avg": "$amount"}
                    }
                }
            ]
            
            customer_data = await db.orders.aggregate(clv_pipeline).to_list(length=None)
            
            if len(customer_data) < 5:
                return {"prediction": "insufficient_data", "message": "Need at least 5 customers with orders"}
            
            clv_predictions = []
            
            for customer in customer_data:
                customer_id = customer["_id"]
                
                # Calculate customer lifetime in days
                lifetime_days = (customer["last_order"] - customer["first_order"]).days + 1
                
                # Calculate metrics
                avg_order_value = customer["avg_order_value"]
                purchase_frequency = customer["order_count"] / max(lifetime_days / 30, 1)  # Orders per month
                
                # Simple CLV calculation: AOV * Purchase Frequency * Predicted Lifetime (months)
                predicted_lifetime_months = min(lifetime_days / 30 * 2, 24)  # Assume double current lifetime, max 24 months
                predicted_clv = avg_order_value * purchase_frequency * predicted_lifetime_months
                
                clv_predictions.append({
                    "customer_id": customer_id,
                    "current_value": customer["total_spent"],
                    "predicted_clv": round(predicted_clv, 2),
                    "avg_order_value": round(avg_order_value, 2),
                    "purchase_frequency": round(purchase_frequency, 2),
                    "lifetime_days": lifetime_days,
                    "value_segment": self._classify_customer_value(predicted_clv)
                })
            
            # Sort by predicted CLV
            clv_predictions.sort(key=lambda x: x["predicted_clv"], reverse=True)
            
            # Calculate summary
            total_predicted_clv = sum(c["predicted_clv"] for c in clv_predictions)
            avg_predicted_clv = total_predicted_clv / len(clv_predictions)
            
            return {
                "model": "basic_clv",
                "total_customers": len(clv_predictions),
                "clv_summary": {
                    "total_predicted_clv": round(total_predicted_clv, 2),
                    "average_predicted_clv": round(avg_predicted_clv, 2),
                    "high_value_customers": len([c for c in clv_predictions if c["value_segment"] == "high"]),
                    "medium_value_customers": len([c for c in clv_predictions if c["value_segment"] == "medium"]),
                    "low_value_customers": len([c for c in clv_predictions if c["value_segment"] == "low"])
                },
                "top_customers": clv_predictions[:10],
                "recommendations": self._generate_clv_recommendations(clv_predictions)
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.ANALYTICS,
                f"CLV prediction failed: {str(e)}",
                error=e
            )
            return {"error": str(e)}
    
    async def generate_cohort_analysis(self, user_id: str, cohort_type: str = "monthly") -> Dict[str, Any]:
        """Generate cohort analysis for customer behavior"""
        try:
            db = get_database()
            
            # Get customer first order dates
            first_orders_pipeline = [
                {
                    "$match": {"user_id": user_id, "status": "completed"}
                },
                {
                    "$sort": {"customer_id": 1, "created_at": 1}
                },
                {
                    "$group": {
                        "_id": "$customer_id",
                        "first_order_date": {"$first": "$created_at"},
                        "total_orders": {"$sum": 1},
                        "total_spent": {"$sum": "$amount"}
                    }
                }
            ]
            
            first_orders = await db.orders.aggregate(first_orders_pipeline).to_list(length=None)
            
            if len(first_orders) < 10:
                return {"error": "Insufficient data for cohort analysis"}
            
            # Group customers by cohort (month of first order)
            cohorts = {}
            
            for customer in first_orders:
                first_order_date = customer["first_order_date"]
                cohort_key = f"{first_order_date.year}-{first_order_date.month:02d}"
                
                if cohort_key not in cohorts:
                    cohorts[cohort_key] = []
                
                cohorts[cohort_key].append({
                    "customer_id": customer["_id"],
                    "first_order_date": first_order_date,
                    "total_orders": customer["total_orders"],
                    "total_spent": customer["total_spent"]
                })
            
            # Calculate cohort metrics
            cohort_analysis = []
            
            for cohort_key, customers in cohorts.items():
                if len(customers) < 3:  # Skip small cohorts
                    continue
                
                cohort_size = len(customers)
                
                # Calculate retention and revenue metrics
                avg_orders = sum(c["total_orders"] for c in customers) / cohort_size
                avg_revenue = sum(c["total_spent"] for c in customers) / cohort_size
                
                cohort_analysis.append({
                    "cohort": cohort_key,
                    "cohort_size": cohort_size,
                    "avg_orders_per_customer": round(avg_orders, 2),
                    "avg_revenue_per_customer": round(avg_revenue, 2),
                    "total_cohort_revenue": sum(c["total_spent"] for c in customers),
                    "repeat_customers": len([c for c in customers if c["total_orders"] > 1]),
                    "repeat_rate": len([c for c in customers if c["total_orders"] > 1]) / cohort_size * 100
                })
            
            # Sort by cohort date
            cohort_analysis.sort(key=lambda x: x["cohort"])
            
            return {
                "cohort_type": cohort_type,
                "total_cohorts": len(cohort_analysis),
                "cohorts": cohort_analysis,
                "insights": self._generate_cohort_insights(cohort_analysis),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.ANALYTICS,
                f"Cohort analysis failed: {str(e)}",
                error=e
            )
            return {"error": str(e)}
    
    def _generate_revenue_recommendations(self, slope: float, revenues: List[float]) -> List[str]:
        """Generate recommendations based on revenue trends"""
        recommendations = []
        
        if slope > 0:
            recommendations.append("Revenue is trending upward - consider scaling marketing efforts")
            recommendations.append("Invest in customer acquisition to maintain growth")
        elif slope < 0:
            recommendations.append("Revenue is declining - review customer retention strategies")
            recommendations.append("Analyze customer feedback for improvement opportunities")
        else:
            recommendations.append("Revenue is stable - explore new revenue streams")
        
        avg_revenue = sum(revenues) / len(revenues)
        if avg_revenue < 1000:  # Threshold for low revenue
            recommendations.append("Consider premium pricing or additional services")
        
        return recommendations
    
    def _generate_churn_recommendations(self, high_risk_count: int, total_customers: int) -> List[str]:
        """Generate churn prevention recommendations"""
        churn_rate = (high_risk_count / total_customers) * 100
        
        recommendations = []
        
        if churn_rate > 20:
            recommendations.append("HIGH PRIORITY: Implement immediate retention campaigns")
            recommendations.append("Survey at-risk customers to identify pain points")
        elif churn_rate > 10:
            recommendations.append("Create targeted re-engagement campaigns")
            recommendations.append("Offer loyalty incentives to at-risk customers")
        
        recommendations.append("Monitor customer health scores regularly")
        recommendations.append("Implement proactive customer success outreach")
        
        return recommendations
    
    def _classify_customer_value(self, clv: float) -> str:
        """Classify customer value segment"""
        if clv > 5000:
            return "high"
        elif clv > 1000:
            return "medium"
        else:
            return "low"
    
    def _generate_clv_recommendations(self, clv_predictions: List[Dict[str, Any]]) -> List[str]:
        """Generate CLV-based recommendations"""
        high_value = len([c for c in clv_predictions if c["value_segment"] == "high"])
        total = len(clv_predictions)
        
        recommendations = []
        
        if high_value / total < 0.2:  # Less than 20% high-value customers
            recommendations.append("Focus on increasing average order value")
            recommendations.append("Develop premium service tiers")
        
        recommendations.append("Create VIP program for high-value customers")
        recommendations.append("Implement personalized marketing for different value segments")
        
        return recommendations
    
    def _generate_cohort_insights(self, cohort_analysis: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from cohort analysis"""
        insights = []
        
        if len(cohort_analysis) >= 3:
            # Compare first and last cohort
            first_cohort = cohort_analysis[0]
            last_cohort = cohort_analysis[-1]
            
            repeat_rate_change = last_cohort["repeat_rate"] - first_cohort["repeat_rate"]
            
            if repeat_rate_change > 5:
                insights.append("Customer retention is improving over time")
            elif repeat_rate_change < -5:
                insights.append("Customer retention is declining - investigate causes")
            
            revenue_change = last_cohort["avg_revenue_per_customer"] - first_cohort["avg_revenue_per_customer"]
            
            if revenue_change > 0:
                insights.append("Average customer value is increasing")
            else:
                insights.append("Average customer value needs improvement")
        
        return insights

# Global instance
advanced_bi_service = AdvancedBIService()
