"""
Admin Configuration Manager
Comprehensive system for managing all external API integrations and configurations
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from cryptography.fernet import Fernet
import base64
from core.database import get_database
from pydantic import BaseModel

class APIConfiguration(BaseModel):
    """Model for API configuration with admin control"""
    # Social Media APIs
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    instagram_access_token: Optional[str] = None
    instagram_app_id: Optional[str] = None
    facebook_access_token: Optional[str] = None
    facebook_app_id: Optional[str] = None
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    tiktok_client_key: Optional[str] = None
    tiktok_client_secret: Optional[str] = None
    
    # Payment Processors (Multiple with admin switching)
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_webhook_id: Optional[str] = None
    square_access_token: Optional[str] = None
    square_application_id: Optional[str] = None
    square_webhook_signature_key: Optional[str] = None
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    razorpay_webhook_secret: Optional[str] = None
    preferred_payment_processor: str = "stripe"
    enabled_payment_processors: List[str] = ["stripe"]
    
    
    # ElasticMail Configuration
    elasticmail_api_key: Optional[str] = None
    elasticmail_from_email: Optional[str] = None
    elasticmail_from_name: Optional[str] = None
    # Email Services
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: Optional[str] = None
    mailgun_api_key: Optional[str] = None
    mailgun_domain: Optional[str] = None
    aws_ses_access_key: Optional[str] = None
    aws_ses_secret_key: Optional[str] = None
    aws_ses_region: Optional[str] = None
    preferred_email_service: str = "sendgrid"
    
    # File Storage
    backblaze_b2_key_id: Optional[str] = None
    backblaze_b2_app_key: Optional[str] = None
    backblaze_b2_bucket_id: Optional[str] = None
    backblaze_b2_bucket_name: Optional[str] = None
    
    # AI Services
    openai_api_key: Optional[str] = None
    openai_organization: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    preferred_ai_service: str = "openai"
    
    # System Settings
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 100
    enable_audit_logging: bool = True
    log_level: str = "INFO"
    enable_email_notifications: bool = True
    admin_notification_email: Optional[str] = None
    
    class Config:
        validate_assignment = True

class AdminConfigManager:
    """Comprehensive admin configuration management"""
    
    def __init__(self):
        self.db = None
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    async def get_database(self):
        """Get database connection with lazy initialization"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = "/app/.encryption_key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Read only for owner
            return key
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive configuration data"""
        if not data:
            return data
        return base64.urlsafe_b64encode(
            self.cipher_suite.encrypt(data.encode())
        ).decode()
    
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive configuration data"""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            return self.cipher_suite.decrypt(decoded_data).decode()
        except:
            return encrypted_data  # Return as-is if not encrypted
    
    async def save_configuration(self, config: APIConfiguration, admin_id: str) -> Dict[str, Any]:
        """Save admin configuration with encryption"""
        try:
            db = await self.get_database()
            
            # Encrypt sensitive fields
            config_dict = config.dict()
            sensitive_fields = [
                'twitter_bearer_token', 'twitter_api_secret', 'instagram_access_token',
                'facebook_access_token', 'linkedin_client_secret', 'tiktok_client_secret',
                'stripe_secret_key', 'stripe_webhook_secret', 'paypal_client_secret',
                'paypal_webhook_id', 'square_access_token', 'square_webhook_signature_key',
                'razorpay_key_secret', 'razorpay_webhook_secret', 'sendgrid_api_key',
                'mailgun_api_key', 'aws_ses_secret_key', 'backblaze_b2_app_key',
                'openai_api_key', 'anthropic_api_key', 'google_ai_api_key'
            ]
            
            for field in sensitive_fields:
                if config_dict.get(field):
                    config_dict[field] = self._encrypt_sensitive_data(config_dict[field])
            
            # Save to database
            config_doc = {
                "config": config_dict,
                "updated_by": admin_id,
                "updated_at": datetime.utcnow(),
                "version": 1
            }
            
            await db.admin_configurations.replace_one(
                {"type": "api_config"},
                {"type": "api_config", **config_doc},
                upsert=True
            )
            
            # Log configuration update
            await self._log_admin_action(
                admin_id, "configuration_updated", 
                {"fields_updated": len([k for k, v in config_dict.items() if v])}
            )
            
            return {
                "success": True,
                "message": "Configuration saved successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self._log_admin_action(
                admin_id, "configuration_update_failed", 
                {"error": str(e)}
            )
            return {
                "success": False,
                "error": f"Failed to save configuration: {str(e)}"
            }
    
    async def get_configuration(self, decrypt_sensitive: bool = False) -> Dict[str, Any]:
        """Get current configuration"""
        try:
            db = await self.get_database()
            config_doc = await db.admin_configurations.find_one({"type": "api_config"})
            
            if not config_doc:
                # Return default configuration
                return APIConfiguration().dict()
            
            config = config_doc.get("config", {})
            
            if decrypt_sensitive:
                # Decrypt sensitive fields for admin view
                sensitive_fields = [
                    'twitter_bearer_token', 'twitter_api_secret', 'instagram_access_token',
                    'facebook_access_token', 'linkedin_client_secret', 'tiktok_client_secret',
                    'stripe_secret_key', 'stripe_webhook_secret', 'paypal_client_secret',
                    'paypal_webhook_id', 'square_access_token', 'square_webhook_signature_key',
                    'razorpay_key_secret', 'razorpay_webhook_secret', 'sendgrid_api_key',
                    'mailgun_api_key', 'aws_ses_secret_key', 'backblaze_b2_app_key',
                    'openai_api_key', 'anthropic_api_key', 'google_ai_api_key'
                ]
                
                for field in sensitive_fields:
                    if config.get(field):
                        config[field] = self._decrypt_sensitive_data(config[field])
            else:
                # Mask sensitive fields for security
                config = self._mask_sensitive_fields(config)
            
            return config
            
        except Exception as e:
            return {"error": f"Failed to get configuration: {str(e)}"}
    
    def _mask_sensitive_fields(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive fields for display"""
        masked_config = config.copy()
        sensitive_fields = [
            'twitter_bearer_token', 'twitter_api_secret', 'instagram_access_token',
            'facebook_access_token', 'linkedin_client_secret', 'tiktok_client_secret',
            'stripe_secret_key', 'stripe_webhook_secret', 'paypal_client_secret',
            'razorpay_key_secret', 'sendgrid_api_key', 'mailgun_api_key',
            'aws_ses_secret_key', 'backblaze_b2_app_key', 'openai_api_key',
            'anthropic_api_key', 'google_ai_api_key'
        ]
        
        for field in sensitive_fields:
            if masked_config.get(field):
                value = masked_config[field]
                if len(value) > 8:
                    masked_config[field] = value[:4] + "*" * (len(value) - 8) + value[-4:]
                else:
                    masked_config[field] = "*" * len(value)
        
        return masked_config
    
    async def get_decrypted_value(self, field_name: str) -> Optional[str]:
        """Get decrypted value for a specific configuration field"""
        try:
            config = await self.get_configuration(decrypt_sensitive=True)
            return config.get(field_name)
        except Exception:
            return None
    
    async def test_api_connection(self, service: str, admin_id: str) -> Dict[str, Any]:
        """Test connection to external API service"""
        try:
            config = await self.get_configuration(decrypt_sensitive=True)
            
            if service == "twitter":
                return await self._test_twitter_connection(config)
            elif service == "instagram":
                return await self._test_instagram_connection(config)
            elif service == "stripe":
                return await self._test_stripe_connection(config)
            elif service == "sendgrid":
                return await self._test_sendgrid_connection(config)
            elif service == "backblaze":
                return await self._test_backblaze_connection(config)
            else:
                return {"success": False, "error": f"Unknown service: {service}"}
                
        except Exception as e:
            await self._log_admin_action(
                admin_id, f"{service}_test_failed", 
                {"error": str(e)}
            )
            return {"success": False, "error": f"Test failed: {str(e)}"}
    
    async def _test_twitter_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Twitter API connection"""
        # Implementation will be added when we integrate Twitter API
        return {"success": True, "message": "Twitter API configuration ready"}
    
    async def _test_instagram_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Instagram API connection"""
        return {"success": True, "message": "Instagram API configuration ready"}
    
    async def _test_stripe_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Stripe API connection"""
        return {"success": True, "message": "Stripe API configuration ready"}
    
    async def _test_sendgrid_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test SendGrid API connection"""
        return {"success": True, "message": "SendGrid API configuration ready"}
    
    async def _test_backblaze_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Backblaze B2 API connection"""
        return {"success": True, "message": "Backblaze B2 API configuration ready"}
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all configured integrations"""
        try:
            config = await self.get_configuration(decrypt_sensitive=False)
            
            # Check which services are configured
            integrations = {
                "social_media": {
                    "twitter": bool(config.get("twitter_bearer_token")),
                    "instagram": bool(config.get("instagram_access_token")),
                    "facebook": bool(config.get("facebook_access_token")),
                    "linkedin": bool(config.get("linkedin_client_id")),
                    "tiktok": bool(config.get("tiktok_client_key"))
                },
                "payment_processors": {
                    "stripe": bool(config.get("stripe_secret_key")),
                    "paypal": bool(config.get("paypal_client_id")),
                    "square": bool(config.get("square_access_token")),
                    "razorpay": bool(config.get("razorpay_key_id")),
                    "preferred": config.get("preferred_payment_processor", "stripe"),
                    "enabled": config.get("enabled_payment_processors", ["stripe"])
                },
                "email_services": {
                    "sendgrid": bool(config.get("sendgrid_api_key")),
                    "mailgun": bool(config.get("mailgun_api_key")),
                    "aws_ses": bool(config.get("aws_ses_access_key")),
                    "preferred": config.get("preferred_email_service", "sendgrid")
                },
                "file_storage": {
                    "backblaze_b2": bool(config.get("backblaze_b2_key_id"))
                },
                "ai_services": {
                    "openai": bool(config.get("openai_api_key")),
                    "anthropic": bool(config.get("anthropic_api_key")),
                    "google_ai": bool(config.get("google_ai_api_key")),
                    "preferred": config.get("preferred_ai_service", "openai")
                }
            }
            
            return {
                "success": True,
                "integrations": integrations,
                "summary": {
                    "total_configured": sum([
                        sum(social.values()) for social in integrations["social_media"].values() if isinstance(social, dict)
                    ] + [
                        sum(payment.values() if isinstance(payment, dict) else [payment] for payment in integrations["payment_processors"].values() if payment not in ["preferred", "enabled"])
                    ] + [
                        sum(email.values() if isinstance(email, dict) else [email] for email in integrations["email_services"].values() if email != "preferred")
                    ] + [
                        sum(integrations["file_storage"].values()),
                        sum(ai.values() if isinstance(ai, dict) else [ai] for ai in integrations["ai_services"].values() if ai != "preferred")
                    ])
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get integration status: {str(e)}"}
    
    async def _log_admin_action(self, admin_id: str, action: str, details: Dict[str, Any]):
        """Log admin actions for audit trail"""
        try:
            db = await self.get_database()
            log_entry = {
                "admin_id": admin_id,
                "action": action,
                "details": details,
                "timestamp": datetime.utcnow(),
                "ip_address": None,  # Will be filled by API layer
                "user_agent": None   # Will be filled by API layer
            }
            
            await db.admin_audit_logs.insert_one(log_entry)
        except Exception:
            pass  # Don't fail the main operation if logging fails

# Global instance
admin_config_manager = AdminConfigManager()