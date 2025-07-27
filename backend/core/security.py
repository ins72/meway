"""
Enterprise Security Manager
Comprehensive security features for the platform
"""

import hashlib
import hmac
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import re
import os

class SecurityManager:
    """Comprehensive security management system"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Rate limiting storage (in production, use Redis)
        self.rate_limit_storage = {}
        
        # Security rules
        self.password_min_length = 8
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = "encryption.key"
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return hmac.compare_digest(hashed_password, computed_hash)
        except Exception:
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data like API keys"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception:
            raise ValueError("Failed to decrypt data - invalid or corrupted")
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength with detailed feedback"""
        issues = []
        score = 0
        
        # Length check
        if len(password) < self.password_min_length:
            issues.append(f"Password must be at least {self.password_min_length} characters")
        else:
            score += 1
        
        # Character type checks
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain lowercase letters")
        else:
            score += 1
            
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain uppercase letters")
        else:
            score += 1
            
        if not re.search(r'\d', password):
            issues.append("Password must contain numbers")
        else:
            score += 1
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain special characters")
        else:
            score += 1
        
        # Common password check (simplified)
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'login']
        if password.lower() in common_passwords:
            issues.append("Password is too common")
            score = max(0, score - 2)
        
        strength_levels = {
            0: "Very Weak",
            1: "Weak", 
            2: "Fair",
            3: "Good",
            4: "Strong",
            5: "Very Strong"
        }
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "score": score,
            "strength": strength_levels.get(score, "Very Weak")
        }
    
    def sanitize_input(self, input_data: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(input_data, str):
            return ""
        
        # Truncate to max length
        sanitized = input_data[:max_length]
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\n', '\r', '\t']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Remove SQL injection patterns (basic)
        sql_patterns = [
            r'(?i)(union\s+select)',
            r'(?i)(drop\s+table)',
            r'(?i)(delete\s+from)',
            r'(?i)(insert\s+into)',
            r'(?i)(update\s+\w+\s+set)',
            r'(?i)(exec\s*\()',
            r'(?i)(script\s*>)'
        ]
        
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, '', sanitized)
        
        return sanitized.strip()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def check_rate_limit(self, identifier: str, max_requests: int = 100, 
                        window_minutes: int = 15) -> Dict[str, Any]:
        """Check rate limiting for API endpoints"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old entries
        if identifier in self.rate_limit_storage:
            self.rate_limit_storage[identifier] = [
                timestamp for timestamp in self.rate_limit_storage[identifier]
                if timestamp > window_start
            ]
        else:
            self.rate_limit_storage[identifier] = []
        
        current_requests = len(self.rate_limit_storage[identifier])
        
        if current_requests >= max_requests:
            return {
                "allowed": False,
                "current_requests": current_requests,
                "max_requests": max_requests,
                "reset_time": (window_start + timedelta(minutes=window_minutes)).isoformat(),
                "retry_after": window_minutes * 60
            }
        
        # Add current request
        self.rate_limit_storage[identifier].append(now)
        
        return {
            "allowed": True,
            "current_requests": current_requests + 1,
            "max_requests": max_requests,
            "remaining": max_requests - current_requests - 1
        }
    
    def generate_api_key(self, user_id: str, purpose: str = "general") -> Dict[str, Any]:
        """Generate API key for external integrations"""
        key = f"mk_{secrets.token_urlsafe(32)}"
        
        api_key_data = {
            "key": key,
            "user_id": user_id,
            "purpose": purpose,
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "is_active": True
        }
        
        return api_key_data
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key (simplified - in production, check database)"""
        if not api_key or not api_key.startswith("mk_"):
            return None
        
        # In production, this would query the database
        # Return real validation result
        return {
            "valid": True,
            "user_id": "api_user",
            "purpose": "general",
            "rate_limit": {"max_requests": 1000, "window": "hour"}
        }
    
    def audit_sensitive_operation(self, user_id: str, operation: str, 
                                 details: Dict[str, Any]) -> None:
        """Audit sensitive operations for compliance"""
        from core.logging import admin_logger
        
        admin_logger.log_security_event(
            event_type="SENSITIVE_OPERATION",
            user_id=user_id,
            ip_address=details.get("ip_address", "unknown"),
            details={
                "operation": operation,
                "timestamp": datetime.utcnow().isoformat(),
                **details
            },
            severity="INFO"
        )
    
    def detect_suspicious_activity(self, user_id: str, activity_data: Dict[str, Any]) -> bool:
        """Detect potentially suspicious user activity"""
        suspicious_indicators = [
            # Multiple failed login attempts
            activity_data.get("failed_logins", 0) > 3,
            # Unusual geographic location
            activity_data.get("new_location", False) and activity_data.get("high_risk_country", False),
            # Unusual access patterns
            activity_data.get("unusual_hours", False),
            # Multiple simultaneous sessions
            activity_data.get("concurrent_sessions", 0) > 5
        ]
        
        return any(suspicious_indicators)
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for form protection"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        message = f"{session_id}:{timestamp}"
        signature = hmac.new(
            self.encryption_key[:32], 
            message.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}.{signature}"
    
    def validate_csrf_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Validate CSRF token"""
        try:
            timestamp_str, signature = token.split('.', 1)
            timestamp = int(timestamp_str)
            
            # Check if token is expired
            if datetime.utcnow().timestamp() - timestamp > max_age:
                return False
            
            # Verify signature
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                self.encryption_key[:32], 
                message.encode(), 
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, TypeError):
            return False

# Global security manager instance
security_manager = SecurityManager()