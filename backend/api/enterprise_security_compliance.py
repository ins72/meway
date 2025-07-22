"""
Enterprise Security & Compliance API Endpoints
Security frameworks, compliance management, and threat detection
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
from core.auth import get_current_user
from core.database import get_database
from services.enterprise_security_compliance_service import EnterpriseSecurityComplianceService

router = APIRouter(prefix="/api/enterprise-security", tags=["Enterprise Security"])

class ComplianceFrameworkCreate(BaseModel):
    framework_type: str  # SOC2, ISO27001, GDPR, HIPAA
    organization_id: str
    next_audit_date: Optional[datetime] = None

class ThreatDetectionSetup(BaseModel):
    organization_id: str
    monitoring_scope: List[str] = []
    alert_channels: List[str] = []

class AuditLogCreate(BaseModel):
    event_type: str
    severity: str = "info"
    username: str
    email: str
    user_role: str
    ip_address: str
    user_agent: str
    session_id: str
    hostname: Optional[str] = None
    service: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None

class VulnerabilityAssessment(BaseModel):
    scan_type: str = "comprehensive"
    target_systems: List[str] = []

class ComplianceReportRequest(BaseModel):
    framework_type: str
    organization_id: str
    reporting_period: str = "annual"
    auditor_id: str

@router.post("/compliance/frameworks")
async def implement_compliance_framework(
    framework_data: ComplianceFrameworkCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Implement comprehensive compliance framework"""
    service = EnterpriseSecurityComplianceService(db)
    result = await service.implement_compliance_framework(framework_data.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Compliance framework implemented successfully", "data": result}

@router.get("/compliance/frameworks")
async def list_compliance_frameworks(
    framework_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List all compliance frameworks"""
    filter_query = {}
    if framework_type:
        filter_query["framework_type"] = framework_type
    
    frameworks = await db["compliance_frameworks"].find(filter_query).to_list(length=50)
    
    return {
        "message": "Compliance frameworks retrieved successfully",
        "data": frameworks,
        "count": len(frameworks)
    }

@router.post("/threat-detection/setup")
async def setup_threat_detection(
    detection_data: ThreatDetectionSetup,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Set up advanced threat detection and response system"""
    service = EnterpriseSecurityComplianceService(db)
    result = await service.setup_threat_detection(detection_data.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Threat detection setup successfully", "data": result}

@router.get("/threat-detection/alerts")
async def get_threat_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get threat detection alerts"""
    # Mock threat alerts
    alerts = [
        {
            "id": "alert_1",
            "severity": "high",
            "threat_type": "brute_force_attack",
            "source_ip": "192.168.1.100",
            "target_system": "web-server",
            "description": "Multiple failed login attempts detected",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "investigating"
        },
        {
            "id": "alert_2",
            "severity": "medium",
            "threat_type": "unusual_access_pattern",
            "source_ip": "10.0.0.50",
            "target_system": "database",
            "description": "Access from unusual geographic location",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "resolved"
        }
    ]
    
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    
    return {
        "message": "Threat alerts retrieved successfully",
        "data": alerts,
        "count": len(alerts)
    }

@router.post("/audit/log")
async def create_audit_log(
    audit_data: AuditLogCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create comprehensive audit log with forensic-level detail"""
    service = EnterpriseSecurityComplianceService(db)
    
    audit_dict = audit_data.dict()
    audit_dict["user_id"] = current_user["user_id"]
    
    result = await service.create_advanced_audit_log(audit_dict)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Audit log created successfully", "data": result}

@router.get("/audit/logs")
async def get_audit_logs(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get audit logs with filtering"""
    filter_query = {}
    
    if event_type:
        filter_query["event_type"] = event_type
    if severity:
        filter_query["severity"] = severity
    if user_id:
        filter_query["user_info.user_id"] = user_id
    
    logs = await db["audit_logs"].find(filter_query).sort("timestamp", -1).to_list(length=limit)
    
    return {
        "message": "Audit logs retrieved successfully",
        "data": logs,
        "count": len(logs)
    }

@router.post("/vulnerability-assessment")
async def perform_vulnerability_assessment(
    assessment_data: VulnerabilityAssessment,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Perform comprehensive vulnerability assessment"""
    service = EnterpriseSecurityComplianceService(db)
    result = await service.perform_vulnerability_assessment(assessment_data.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Vulnerability assessment completed successfully", "data": result}

@router.get("/vulnerability-assessments")
async def list_vulnerability_assessments(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List vulnerability assessments"""
    assessments = await db["vulnerability_scans"].find({}).sort("scan_started_at", -1).to_list(length=20)
    
    return {
        "message": "Vulnerability assessments retrieved successfully",
        "data": assessments,
        "count": len(assessments)
    }

@router.post("/compliance/report")
async def generate_compliance_report(
    report_data: ComplianceReportRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Generate comprehensive compliance report"""
    service = EnterpriseSecurityComplianceService(db)
    result = await service.generate_compliance_report(report_data.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Compliance report generated successfully", "data": result}

@router.get("/compliance/reports")
async def list_compliance_reports(
    framework_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """List compliance reports"""
    filter_query = {}
    if framework_type:
        filter_query["framework_type"] = framework_type
    
    reports = await db["compliance_reports"].find(filter_query).sort("report_date", -1).to_list(length=20)
    
    return {
        "message": "Compliance reports retrieved successfully",
        "data": reports,
        "count": len(reports)
    }

@router.get("/security/dashboard")
async def get_security_dashboard(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get security dashboard overview"""
    dashboard_data = {
        "security_score": 87.5,
        "threat_level": "low",
        "active_incidents": 2,
        "compliance_status": {
            "SOC2": "compliant",
            "ISO27001": "in_progress",
            "GDPR": "compliant",
            "HIPAA": "not_applicable"
        },
        "recent_activities": [
            {
                "type": "vulnerability_scan",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "findings": {"critical": 0, "high": 1, "medium": 3}
            },
            {
                "type": "compliance_audit", 
                "status": "in_progress",
                "timestamp": datetime.utcnow().isoformat(),
                "framework": "SOC2"
            }
        ],
        "security_metrics": {
            "failed_login_attempts": 15,
            "blocked_threats": 234,
            "security_incidents": 8,
            "audit_events": 15420
        }
    }
    
    return {
        "message": "Security dashboard retrieved successfully",
        "data": dashboard_data
    }