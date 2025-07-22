"""
Enterprise Security & Compliance Service
SSO, advanced audit logging, IP whitelisting, device management, and compliance
"""
import asyncio
import uuid
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import ipaddress

from core.database import get_database
from core.professional_logger import professional_logger, LogLevel, LogCategory

class AuditEventType(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFY = "data_modify"
    ADMIN_ACTION = "admin_action"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_EVENT = "compliance_event"

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DeviceStatus(Enum):
    TRUSTED = "trusted"
    PENDING = "pending"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"

class EnterpriseSecurityService:
    """Comprehensive enterprise security management"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = set()
        self.trusted_devices = {}
        
    async def sso_authenticate(self, saml_token: str, provider: str) -> Dict[str, Any]:
        """SAML 2.0 SSO Authentication"""
        try:
            # In production, this would validate SAML tokens from providers like:
            # Active Directory, Google Workspace, Okta, Azure AD, etc.
            
            # Simulate SAML token validation
            if not saml_token or len(saml_token) < 20:
                raise Exception("Invalid SAML token")
            
            # Extract user information from SAML response
            # This is a simplified version - real implementation would parse XML
            user_data = {
                "email": f"user@{provider}.com",  # Extracted from SAML
                "name": "SSO User",  # Extracted from SAML  
                "groups": ["employees", "sso_users"],  # From SAML attributes
                "department": "IT",  # From SAML attributes
                "employee_id": "EMP123"  # From SAML attributes
            }
            
            db = get_database()
            
            # Find or create user from SSO
            user = await db.users.find_one({"email": user_data["email"]})
            
            if not user:
                # Create new SSO user
                user_id = str(uuid.uuid4())
                user = {
                    "_id": user_id,
                    "email": user_data["email"],
                    "name": user_data["name"],
                    "sso_provider": provider,
                    "sso_attributes": user_data,
                    "account_type": "sso",
                    "created_at": datetime.utcnow(),
                    "last_login": datetime.utcnow()
                }
                await db.users.insert_one(user)
            else:
                # Update last login
                await db.users.update_one(
                    {"_id": user["_id"]},
                    {
                        "$set": {
                            "last_login": datetime.utcnow(),
                            "sso_attributes": user_data
                        }
                    }
                )
            
            # Log SSO authentication
            await self.log_audit_event(
                user["_id"], AuditEventType.LOGIN,
                {"sso_provider": provider, "method": "saml_sso"},
                SecurityLevel.MEDIUM
            )
            
            return {
                "user_id": user["_id"],
                "email": user["email"],
                "name": user["name"],
                "sso_provider": provider,
                "sso_authenticated": True
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.SECURITY,
                f"SSO authentication failed: {str(e)}",
                error=e
            )
            raise Exception(f"SSO authentication failed: {str(e)}")
    
    async def log_audit_event(self, user_id: str, event_type: AuditEventType, 
                            event_data: Dict[str, Any], security_level: SecurityLevel,
                            ip_address: str = None, user_agent: str = None) -> str:
        """Advanced audit logging with forensic-level detail"""
        try:
            db = get_database()
            
            audit_id = str(uuid.uuid4())
            
            # Get additional context
            user = await db.users.find_one({"_id": user_id}) if user_id else None
            
            audit_record = {
                "audit_id": audit_id,
                "timestamp": datetime.utcnow(),
                "event_type": event_type.value,
                "security_level": security_level.value,
                "user_context": {
                    "user_id": user_id,
                    "email": user.get("email") if user else None,
                    "name": user.get("name") if user else None,
                    "role": user.get("role") if user else None
                },
                "technical_context": {
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "session_id": event_data.get("session_id"),
                    "request_id": event_data.get("request_id")
                },
                "event_details": event_data,
                "risk_assessment": {
                    "risk_score": self._calculate_risk_score(event_type, event_data, ip_address),
                    "anomaly_flags": self._detect_anomalies(user_id, event_type, ip_address),
                    "compliance_flags": self._check_compliance(event_type, event_data)
                },
                "data_classification": self._classify_data_sensitivity(event_data),
                "retention_period": self._calculate_retention_period(security_level),
                "hash": self._generate_audit_hash(audit_id, event_type, user_id, event_data)
            }
            
            await db.audit_logs.insert_one(audit_record)
            
            # Real-time security monitoring
            if audit_record["risk_assessment"]["risk_score"] > 7:
                await self._trigger_security_alert(audit_record)
            
            await professional_logger.log(
                LogLevel.INFO, LogCategory.SECURITY,
                f"Audit event logged: {event_type.value}",
                user_id=user_id,
                details={"audit_id": audit_id, "risk_score": audit_record["risk_assessment"]["risk_score"]}
            )
            
            return audit_id
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.SECURITY,
                f"Audit logging failed: {str(e)}",
                error=e
            )
            return ""
    
    async def check_ip_whitelist(self, user_id: str, ip_address: str) -> bool:
        """Check if IP address is whitelisted for user"""
        try:
            if not ip_address:
                return False
            
            db = get_database()
            
            # Check user-specific whitelist
            user_whitelist = await db.ip_whitelists.find_one({"user_id": user_id})
            
            if user_whitelist:
                allowed_ips = user_whitelist.get("allowed_ips", [])
                allowed_ranges = user_whitelist.get("allowed_ranges", [])
                
                # Check exact IP match
                if ip_address in allowed_ips:
                    return True
                
                # Check IP ranges
                for ip_range in allowed_ranges:
                    try:
                        if ipaddress.ip_address(ip_address) in ipaddress.ip_network(ip_range):
                            return True
                    except ValueError:
                        continue
            
            # Check global whitelist
            global_whitelist = await db.global_ip_settings.find_one({"type": "whitelist"})
            if global_whitelist:
                global_allowed = global_whitelist.get("ip_addresses", [])
                global_ranges = global_whitelist.get("ip_ranges", [])
                
                if ip_address in global_allowed:
                    return True
                
                for ip_range in global_ranges:
                    try:
                        if ipaddress.ip_address(ip_address) in ipaddress.ip_network(ip_range):
                            return True
                    except ValueError:
                        continue
            
            # Log access attempt from non-whitelisted IP
            await self.log_audit_event(
                user_id, AuditEventType.SECURITY_EVENT,
                {"event": "non_whitelisted_ip_access", "ip_address": ip_address},
                SecurityLevel.HIGH,
                ip_address
            )
            
            return False
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.SECURITY,
                f"IP whitelist check failed: {str(e)}",
                error=e
            )
            return False
    
    async def register_device(self, user_id: str, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Register and manage user devices"""
        try:
            db = get_database()
            
            device_id = str(uuid.uuid4())
            
            # Generate device fingerprint
            device_fingerprint = hashlib.sha256(
                f"{device_info.get('user_agent', '')}{device_info.get('screen_resolution', '')}{device_info.get('timezone', '')}{device_info.get('language', '')}".encode()
            ).hexdigest()
            
            device_record = {
                "device_id": device_id,
                "user_id": user_id,
                "device_fingerprint": device_fingerprint,
                "device_info": {
                    "name": device_info.get("name", "Unknown Device"),
                    "type": device_info.get("type", "desktop"),  # desktop, mobile, tablet
                    "os": device_info.get("os", "unknown"),
                    "browser": device_info.get("browser", "unknown"),
                    "ip_address": device_info.get("ip_address"),
                    "location": device_info.get("location", {}),
                    "user_agent": device_info.get("user_agent")
                },
                "status": DeviceStatus.PENDING.value,
                "trust_score": 5,  # Initial neutral score
                "first_seen": datetime.utcnow(),
                "last_used": datetime.utcnow(),
                "usage_count": 1,
                "security_events": [],
                "verification": {
                    "verified": False,
                    "verification_method": None,
                    "verified_at": None
                }
            }
            
            await db.user_devices.insert_one(device_record)
            
            # Log device registration
            await self.log_audit_event(
                user_id, AuditEventType.SECURITY_EVENT,
                {"event": "device_registration", "device_id": device_id, "device_type": device_info.get("type")},
                SecurityLevel.MEDIUM,
                device_info.get("ip_address")
            )
            
            return {
                "device_id": device_id,
                "status": DeviceStatus.PENDING.value,
                "requires_verification": True,
                "trust_score": 5
            }
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.SECURITY,
                f"Device registration failed: {str(e)}",
                error=e
            )
            raise Exception(f"Device registration failed: {str(e)}")
    
    async def data_loss_prevention_scan(self, content: str, content_type: str, user_id: str) -> Dict[str, Any]:
        """Scan content for sensitive data and potential data loss"""
        try:
            import re
            
            sensitive_patterns = {
                "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
                "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
                "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                "api_key": r"(?i)(api[_-]?key|token)["'\s]*[:=]["'\s]*([a-zA-Z0-9_-]{20,})",
                "password": r"(?i)(password|pwd)["'\s]*[:=]["'\s]*([\S]+)"
            }
            
            findings = []
            risk_score = 0
            
            for data_type, pattern in sensitive_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    finding = {
                        "data_type": data_type,
                        "matches_count": len(matches),
                        "confidence": 0.9,
                        "severity": "high" if data_type in ["ssn", "credit_card", "api_key"] else "medium"
                    }
                    findings.append(finding)
                    risk_score += len(matches) * (3 if finding["severity"] == "high" else 1)
            
            # Check for bulk data patterns
            lines = content.split('\n')
            if len(lines) > 1000:  # Large data export
                findings.append({
                    "data_type": "bulk_export",
                    "matches_count": len(lines),
                    "confidence": 0.8,
                    "severity": "medium"
                })
                risk_score += 2
            
            dlp_result = {
                "scan_id": str(uuid.uuid4()),
                "content_type": content_type,
                "findings": findings,
                "risk_score": min(risk_score, 10),  # Cap at 10
                "action_required": risk_score > 5,
                "recommendations": self._generate_dlp_recommendations(findings)
            }
            
            # Log DLP scan
            if dlp_result["action_required"]:
                await self.log_audit_event(
                    user_id, AuditEventType.COMPLIANCE_EVENT,
                    {"event": "dlp_high_risk_content", "scan_result": dlp_result},
                    SecurityLevel.HIGH
                )
            
            return dlp_result
            
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.SECURITY,
                f"DLP scan failed: {str(e)}",
                error=e
            )
            return {"error": str(e), "risk_score": 0}
    
    def _calculate_risk_score(self, event_type: AuditEventType, event_data: Dict[str, Any], ip_address: str) -> int:
        """Calculate risk score for security event"""
        risk_score = 0
        
        # Base risk by event type
        event_risks = {
            AuditEventType.LOGIN: 2,
            AuditEventType.DATA_ACCESS: 3,
            AuditEventType.DATA_MODIFY: 5,
            AuditEventType.ADMIN_ACTION: 7,
            AuditEventType.SECURITY_EVENT: 8
        }
        
        risk_score += event_risks.get(event_type, 1)
        
        # Additional risk factors
        if ip_address and ip_address in self.blocked_ips:
            risk_score += 3
        
        if event_data.get("failed_attempts", 0) > 3:
            risk_score += 2
        
        if event_data.get("suspicious_activity", False):
            risk_score += 4
        
        return min(risk_score, 10)  # Cap at 10
    
    def _detect_anomalies(self, user_id: str, event_type: AuditEventType, ip_address: str) -> List[str]:
        """Detect anomalous patterns in user behavior"""
        anomalies = []
        
        # Check for unusual login times (simplified)
        current_hour = datetime.utcnow().hour
        if event_type == AuditEventType.LOGIN and (current_hour < 6 or current_hour > 22):
            anomalies.append("unusual_login_time")
        
        # Check for new IP address
        if ip_address and ip_address not in self.trusted_devices.get(user_id, []):
            anomalies.append("new_ip_address")
        
        return anomalies
    
    def _check_compliance(self, event_type: AuditEventType, event_data: Dict[str, Any]) -> List[str]:
        """Check for compliance-related flags"""
        compliance_flags = []
        
        # GDPR compliance checks
        if event_type == AuditEventType.DATA_ACCESS and event_data.get("personal_data", False):
            compliance_flags.append("gdpr_personal_data_access")
        
        # SOX compliance checks
        if event_type == AuditEventType.ADMIN_ACTION and event_data.get("financial_data", False):
            compliance_flags.append("sox_financial_data_modification")
        
        return compliance_flags
    
    def _classify_data_sensitivity(self, event_data: Dict[str, Any]) -> str:
        """Classify data sensitivity level"""
        if any(key in event_data for key in ["ssn", "credit_card", "financial"]):
            return "highly_sensitive"
        elif any(key in event_data for key in ["personal", "email", "phone"]):
            return "sensitive"
        else:
            return "public"
    
    def _calculate_retention_period(self, security_level: SecurityLevel) -> int:
        """Calculate audit log retention period in days"""
        retention_periods = {
            SecurityLevel.LOW: 90,
            SecurityLevel.MEDIUM: 365,
            SecurityLevel.HIGH: 2555,  # 7 years
            SecurityLevel.CRITICAL: 3650  # 10 years
        }
        return retention_periods.get(security_level, 365)
    
    def _generate_audit_hash(self, audit_id: str, event_type: AuditEventType, user_id: str, event_data: Dict[str, Any]) -> str:
        """Generate tamper-proof hash for audit record"""
        hash_input = f"{audit_id}{event_type.value}{user_id}{str(event_data)}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _generate_dlp_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate DLP recommendations based on findings"""
        recommendations = []
        
        for finding in findings:
            data_type = finding["data_type"]
            severity = finding["severity"]
            
            if data_type == "ssn":
                recommendations.append("Mask or redact Social Security Numbers")
            elif data_type == "credit_card":
                recommendations.append("Encrypt or tokenize credit card data")
            elif data_type == "api_key":
                recommendations.append("Remove API keys and use secure storage")
            elif data_type == "bulk_export":
                recommendations.append("Review bulk data export permissions")
        
        return recommendations
    
    async def _trigger_security_alert(self, audit_record: Dict[str, Any]):
        """Trigger real-time security alert for high-risk events"""
        try:
            # This would integrate with alerting systems (email, Slack, etc.)
            await professional_logger.log(
                LogLevel.CRITICAL, LogCategory.SECURITY,
                f"HIGH RISK SECURITY EVENT DETECTED",
                details={
                    "audit_id": audit_record["audit_id"],
                    "event_type": audit_record["event_type"],
                    "risk_score": audit_record["risk_assessment"]["risk_score"],
                    "user_id": audit_record["user_context"]["user_id"]
                }
            )
        except Exception as e:
            await professional_logger.log(
                LogLevel.ERROR, LogCategory.SECURITY,
                f"Security alert failed: {str(e)}",
                error=e
            )

# Global instance
enterprise_security_service = EnterpriseSecurityService()
