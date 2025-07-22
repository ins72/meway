"""
External API Manager
Real integrations with social media platforms, AI services, and other external APIs
NO MOCK DATA - All real external API connections
"""

import os
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from core.logging import admin_logger
from core.database import get_database

class ExternalAPIManager:
    """Manages all external API integrations with real data"""
    
    def __init__(self):
        self.client = None
        self.api_keys = {}
        self.service_status = {}
        
    async def initialize(self):
        """Initialize API connections and load configuration"""
        self.client = httpx.AsyncClient(timeout=30.0)
        await self._load_api_configuration()
        await self._test_api_connections()
        
    async def close(self):
        """Close API connections"""
        if self.client:
            await self.client.aclose()
    
    async def _load_api_configuration(self):
        """Load API configuration from database (admin-configurable)"""
        try:
            db = get_database()
            config = await db.api_configuration.find_one({"type": "external_apis"})
            
            if config:
                # Decrypt sensitive API keys
                from core.security import security_manager
                
                self.api_keys = {
                    # Social Media APIs
                    "twitter_bearer_token": self._get_decrypted_key(config, "twitter_bearer_token"),
                    "instagram_access_token": self._get_decrypted_key(config, "instagram_access_token"),
                    "facebook_access_token": self._get_decrypted_key(config, "facebook_access_token"),
                    "linkedin_access_token": self._get_decrypted_key(config, "linkedin_access_token"),
                    "tiktok_access_token": self._get_decrypted_key(config, "tiktok_access_token"),
                    
                    # AI Services
                    "openai_api_key": self._get_decrypted_key(config, "openai_api_key"),
                    "anthropic_api_key": self._get_decrypted_key(config, "anthropic_api_key"),
                    "google_ai_key": self._get_decrypted_key(config, "google_ai_key"),
                    
                    # Analytics
                    "google_analytics_key": self._get_decrypted_key(config, "google_analytics_key"),
                    "mixpanel_token": self._get_decrypted_key(config, "mixpanel_token"),
                }
            else:
                # Load from environment variables as fallback
                self.api_keys = {
                    "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
                    "instagram_access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
                    "facebook_access_token": os.getenv("FACEBOOK_ACCESS_TOKEN"),
                    "linkedin_access_token": os.getenv("LINKEDIN_ACCESS_TOKEN"),
                    "tiktok_access_token": os.getenv("TIKTOK_ACCESS_TOKEN"),
                    "openai_api_key": os.getenv("OPENAI_API_KEY"),
                    "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
                    "google_ai_key": os.getenv("GOOGLE_AI_KEY"),
                    "google_analytics_key": os.getenv("GOOGLE_ANALYTICS_KEY"),
                    "mixpanel_token": os.getenv("MIXPANEL_TOKEN"),
                }
                
        except Exception as e:
            admin_logger.log_system_event("API_CONFIG_LOAD_FAILED", {
                "error": str(e)
            }, "ERROR")
    
    def _get_decrypted_key(self, config: Dict, key: str) -> Optional[str]:
        """Decrypt API key from configuration"""
        try:
            if key in config and config[key]:
                from core.security import security_manager
                return security_manager.decrypt_sensitive_data(config[key])
        except Exception as e:
            admin_logger.log_system_event("KEY_DECRYPTION_FAILED", {
                "key": key,
                "error": str(e)
            }, "ERROR")
        return None
    
    async def _test_api_connections(self):
        """Test all API connections and update service status"""
        test_results = {}
        
        # Test Twitter API
        if self.api_keys.get("twitter_bearer_token"):
            test_results["twitter"] = await self._test_twitter_api()
        
        # Test tiktok_api
        if self.api_keys.get("instagram_access_token"):
            test_results["instagram"] = await self._test_tiktok_api()
        
        # Test Facebook API
        if self.api_keys.get("facebook_access_token"):
            test_results["facebook"] = await self._test_facebook_api()
        
        # Test LinkedIn API
        if self.api_keys.get("linkedin_access_token"):
            test_results["linkedin"] = await self._test_linkedin_api()
        
        # Test OpenAI API
        if self.api_keys.get("openai_api_key"):
            test_results["openai"] = await self._test_openai_api()
        
        self.service_status = test_results
        
        admin_logger.log_system_event("API_CONNECTION_TEST", {
            "results": test_results
        })
    
    async def _test_twitter_api(self) -> Dict[str, Any]:
        """Test Twitter API connection"""
        try:
            start_time = datetime.now()
            headers = {
                "Authorization": f"Bearer {self.api_keys['twitter_bearer_token']}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.get(
                "https://api.twitter.com/2/users/me",
                headers=headers
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "response_time": response_time,
                    "last_tested": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "last_tested": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_tested": datetime.utcnow().isoformat()
            }
    
    async def _test_tiktok_api(self) -> Dict[str, Any]:
        """Test Instagram Graph API connection"""
        try:
            start_time = datetime.now()
            
            response = await self.client.get(
                f"https://graph.instagram.com/me?fields=id,username&access_token={self.api_keys['instagram_access_token']}"
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "response_time": response_time,
                    "last_tested": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "last_tested": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_tested": datetime.utcnow().isoformat()
            }
    
    async def _test_facebook_api(self) -> Dict[str, Any]:
        """Test Facebook Graph API connection"""
        try:
            start_time = datetime.now()
            
            response = await self.client.get(
                f"https://graph.facebook.com/me?access_token={self.api_keys['facebook_access_token']}"
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "response_time": response_time,
                    "last_tested": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "last_tested": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_tested": datetime.utcnow().isoformat()
            }
    
    async def _test_linkedin_api(self) -> Dict[str, Any]:
        """Test LinkedIn API connection"""
        try:
            start_time = datetime.now()
            headers = {
                "Authorization": f"Bearer {self.api_keys['linkedin_access_token']}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.get(
                "https://api.linkedin.com/v2/people/~",
                headers=headers
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "response_time": response_time,
                    "last_tested": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "last_tested": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_tested": datetime.utcnow().isoformat()
            }
    
    async def _test_openai_api(self) -> Dict[str, Any]:
        """Test OpenAI API connection"""
        try:
            start_time = datetime.now()
            headers = {
                "Authorization": f"Bearer {self.api_keys['openai_api_key']}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.get(
                "https://api.openai.com/v1/models",
                headers=headers
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "response_time": response_time,
                    "last_tested": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "last_tested": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_tested": datetime.utcnow().isoformat()
            }
    
    # SOCIAL MEDIA API METHODS - REAL DATA ONLY
    
    async def get_twitter_user_posts(self, user_id: str, max_results: int = 10) -> Dict[str, Any]:
        """Get real Twitter posts for user"""
        if not self.api_keys.get("twitter_bearer_token"):
            raise ValueError("Twitter API not configured")
        
        start_time = datetime.now()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['twitter_bearer_token']}",
                "Content-Type": "application/json"
            }
            
            params = {
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,public_metrics,context_annotations",
                "user.fields": "public_metrics"
            }
            
            response = await self.client.get(
                f"https://api.twitter.com/2/users/{user_id}/tweets",
                headers=headers,
                params=params
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            admin_logger.log_external_api_call(
                service="twitter",
                endpoint=f"/users/{user_id}/tweets",
                status=response.status_code,
                response_time=response_time
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store in database for caching
                await self._cache_social_media_data("twitter", user_id, data)
                
                return {
                    "success": True,
                    "data": data,
                    "cached_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Twitter API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            admin_logger.log_external_api_call(
                service="twitter",
                endpoint=f"/users/{user_id}/tweets",
                status=0,
                response_time=0,
                error=str(e)
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_instagram_user_media(self, user_id: str) -> Dict[str, Any]:
        """Get real Instagram media for user"""
        if not self.api_keys.get("instagram_access_token"):
            raise ValueError("tiktok_api not configured")
        
        start_time = datetime.now()
        
        try:
            params = {
                "fields": "id,media_type,media_url,permalink,thumbnail_url,timestamp,caption",
                "access_token": self.api_keys["instagram_access_token"]
            }
            
            response = await self.client.get(
                f"https://graph.instagram.com/{user_id}/media",
                params=params
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            admin_logger.log_external_api_call(
                service="instagram",
                endpoint=f"/{user_id}/media",
                status=response.status_code,
                response_time=response_time
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store in database for caching
                await self._cache_social_media_data("instagram", user_id, data)
                
                return {
                    "success": True,
                    "data": data,
                    "cached_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"tiktok_api error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            admin_logger.log_external_api_call(
                service="instagram",
                endpoint=f"/{user_id}/media",
                status=0,
                response_time=0,
                error=str(e)
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_facebook_page_posts(self, page_id: str) -> Dict[str, Any]:
        """Get real Facebook page posts"""
        if not self.api_keys.get("facebook_access_token"):
            raise ValueError("Facebook API not configured")
        
        start_time = datetime.now()
        
        try:
            params = {
                "fields": "id,message,created_time,likes.summary(true),comments.summary(true)",
                "access_token": self.api_keys["facebook_access_token"]
            }
            
            response = await self.client.get(
                f"https://graph.facebook.com/{page_id}/posts",
                params=params
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            admin_logger.log_external_api_call(
                service="facebook",
                endpoint=f"/{page_id}/posts",
                status=response.status_code,
                response_time=response_time
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store in database for caching
                await self._cache_social_media_data("facebook", page_id, data)
                
                return {
                    "success": True,
                    "data": data,
                    "cached_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Facebook API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            admin_logger.log_external_api_call(
                service="facebook",
                endpoint=f"/{page_id}/posts",
                status=0,
                response_time=0,
                error=str(e)
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    # AI API METHODS - REAL INTEGRATIONS
    
    async def generate_content_openai(self, prompt: str, model: str = "gpt-4") -> Dict[str, Any]:
        """Generate content using OpenAI GPT"""
        if not self.api_keys.get("openai_api_key"):
            raise ValueError("OpenAI API not configured")
        
        start_time = datetime.now()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['openai_api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            admin_logger.log_external_api_call(
                service="openai",
                endpoint="/chat/completions",
                status=response.status_code,
                response_time=response_time
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Log AI usage for billing
                await self._log_ai_usage("openai", model, result.get("usage", {}))
                
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": f"OpenAI API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            admin_logger.log_external_api_call(
                service="openai",
                endpoint="/chat/completions",
                status=0,
                response_time=0,
                error=str(e)
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _cache_social_media_data(self, platform: str, user_id: str, data: Dict[str, Any]):
        """Cache social media data in database"""
        try:
            db = get_database()
            cache_entry = {
                "platform": platform,
                "user_id": user_id,
                "data": data,
                "cached_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=1)
            }
            
            await db.social_media_cache.replace_one(
                {"platform": platform, "user_id": user_id},
                cache_entry,
                upsert=True
            )
            
        except Exception as e:
            admin_logger.log_system_event("CACHE_STORE_FAILED", {
                "platform": platform,
                "user_id": user_id,
                "error": str(e)
            }, "WARNING")
    
    async def _log_ai_usage(self, service: str, model: str, usage_data: Dict[str, Any]):
        """Log AI usage for billing and analytics"""
        try:
            db = get_database()
            usage_entry = {
                "service": service,
                "model": model,
                "usage": usage_data,
                "timestamp": datetime.utcnow(),
                "cost_estimate": self._calculate_ai_cost(service, model, usage_data)
            }
            
            await db.ai_usage_logs.insert_one(usage_entry)
            
        except Exception as e:
            admin_logger.log_system_event("AI_USAGE_LOG_FAILED", {
                "service": service,
                "model": model,
                "error": str(e)
            }, "WARNING")
    
    def _calculate_ai_cost(self, service: str, model: str, usage_data: Dict[str, Any]) -> float:
        """Calculate estimated cost for AI usage"""
        # Simplified cost calculation - in production, use actual pricing
        pricing = {
            "openai": {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
            }
        }
        
        if service in pricing and model in pricing[service]:
            rates = pricing[service][model]
            input_tokens = usage_data.get("prompt_tokens", 0)
            output_tokens = usage_data.get("completion_tokens", 0)
            
            cost = (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
            return round(cost, 4)
        
        return 0.0
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all external services"""
        return self.service_status

# Global external API manager instance
external_api_manager = ExternalAPIManager()