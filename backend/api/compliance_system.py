"""
Advanced Compliance & Audit API
Enterprise-grade compliance management and audit endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Form
from typing import Optional
import logging

from core.auth import get_current_user
from services.compliance_service import ComplianceService
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/framework-status")
async def get_compliance_framework_status(current_user: dict = Depends(get_current_user)):
    """Get comprehensive compliance framework status"""
    try:
        compliance_status = await ComplianceService.get_compliance_framework_status()
        return {"success": True, "data": compliance_status}
    except Exception as e:
        logger.error(f"Error getting compliance framework status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-logs")
async def get_audit_logs(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD format)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD format)"),
    event_type: Optional[str] = Query(None, description="Event type: security, access, data, system, compliance"),
    limit: Optional[int] = Query(100, description="Maximum number of logs to return (1-500)"),
    current_user: dict = Depends(get_current_user)
):
    """Get audit logs with filtering options"""
    try:
        if limit and (limit < 1 or limit > 500):
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 500")
        
        if event_type and event_type not in ["security", "access", "data", "system", "compliance"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid event type. Must be one of: security, access, data, system, compliance"
            )
        
        audit_logs = await ComplianceService.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            limit=limit or 100
        )
        return {"success": True, "data": audit_logs}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-report")
async def create_compliance_report(
    framework: str = Form(..., description="Framework: gdpr, soc2, iso27001, hipaa, pci_dss, all"),
    report_type: str = Form("summary", description="Report type: summary, detailed, executive"),
    current_user: dict = Depends(get_current_user)
):
    """Create a compliance report for specified framework"""
    try:
        valid_frameworks = ["gdpr", "soc2", "iso27001", "hipaa", "pci_dss", "all"]
        if framework not in valid_frameworks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework. Must be one of: {', '.join(valid_frameworks)}"
            )
        
        valid_types = ["summary", "detailed", "executive"]
        if report_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid report type. Must be one of: {', '.join(valid_types)}"
            )
        
        report = await ComplianceService.create_compliance_report(
            framework=framework,
            report_type=report_type
        )
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/policy-management")
async def get_policy_management(current_user: dict = Depends(get_current_user)):
    """Get policy management information"""
    try:
        policies = await ComplianceService.get_policy_management()
        return {"success": True, "data": policies}
    except Exception as e:
        logger.error(f"Error getting policy management: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-register")
async def get_risk_register(current_user: dict = Depends(get_current_user)):
    """Get comprehensive risk register"""
    try:
        risk_register = await ComplianceService.get_risk_register()
        return {"success": True, "data": risk_register}
    except Exception as e:
        logger.error(f"Error getting risk register: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance-dashboard")
async def get_compliance_dashboard(current_user: dict = Depends(get_current_user)):
    """Get comprehensive compliance dashboard data"""
    try:
        # Combine multiple compliance data sources for dashboard view
        framework_status = await ComplianceService.get_compliance_framework_status()
        policies = await ComplianceService.get_policy_management()
        risk_register = await ComplianceService.get_risk_register()
        
        dashboard = {
            "compliance_overview": {
                "total_frameworks": len(framework_status["frameworks"]),
                "compliant_frameworks": len([
                    f for f in framework_status["frameworks"].values() 
                    if f["status"] == "compliant"
                ]),
                "frameworks_in_progress": len([
                    f for f in framework_status["frameworks"].values() 
                    if f["status"] == "in_progress"
                ]),
                "average_compliance_score": round(sum([
                    f["compliance_score"] for f in framework_status["frameworks"].values()
                ]) / len(framework_status["frameworks"]), 1)
            },
            "risk_overview": {
                "total_risks": risk_register["total_risks"],
                "critical_risks": risk_register["risk_summary"]["critical_risks"],
                "high_risks": risk_register["risk_summary"]["high_risks"],
                "risk_trend": "stable"  # Could be calculated from historical data
            },
            "policy_overview": {
                "total_policies": len(policies["active_policies"]),
                "pending_reviews": len(policies["pending_reviews"]),
                "recent_violations": len(policies["policy_violations"]),
                "training_completion": policies["training_completion"]["overall_completion"]
            },
            "audit_overview": {
                "total_events_today": framework_status["audit_trail"]["total_events_today"],
                "security_events": framework_status["audit_trail"]["security_events"],
                "recent_audits": len(framework_status["audit_trail"]["recent_audits"]),
                "audit_findings": sum(audit["findings"] for audit in framework_status["audit_trail"]["recent_audits"])
            },
            "upcoming_activities": [
                {
                    "activity": "ISO 27001 Certification Assessment",
                    "due_date": "2025-04-30",
                    "type": "certification",
                    "priority": "high"
                },
                {
                    "activity": "GDPR Annual Review",
                    "due_date": "2025-06-01",
                    "type": "audit",
                    "priority": "medium"
                },
                {
                    "activity": "Staff Security Training",
                    "due_date": "2025-05-01",
                    "type": "training",
                    "priority": "medium"
                }
            ]
        }
        
        return {"success": True, "data": dashboard}
    except Exception as e:
        logger.error(f"Error getting compliance dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/framework/{framework_name}")
async def get_framework_details(
    framework_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information for a specific compliance framework"""
    try:
        valid_frameworks = ["gdpr", "soc2", "iso27001", "hipaa", "pci_dss"]
        if framework_name not in valid_frameworks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework. Must be one of: {', '.join(valid_frameworks)}"
            )
        
        compliance_status = await ComplianceService.get_compliance_framework_status()
        
        if framework_name not in compliance_status["frameworks"]:
            raise HTTPException(status_code=404, detail=f"Framework {framework_name} not found")
        
        framework_details = compliance_status["frameworks"][framework_name]
        
        return {"success": True, "data": framework_details}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting framework details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/certificates")
async def get_compliance_certificates(current_user: dict = Depends(get_current_user)):
    """Get all compliance certificates"""
    try:
        compliance_status = await ComplianceService.get_compliance_framework_status()
        
        certificates = []
        for framework_name, framework_data in compliance_status["frameworks"].items():
            if "certifications" in framework_data:
                for cert in framework_data["certifications"]:
                    cert_info = {
                        "framework": framework_name.upper(),
                        **cert
                    }
                    certificates.append(cert_info)
        
        certificate_summary = {
            "total_certificates": len(certificates),
            "active_certificates": len([c for c in certificates if "expiry_date" in c]),
            "certificates": certificates,
            "renewal_schedule": [
                {
                    "certificate": cert["name"],
                    "framework": cert["framework"],
                    "expiry_date": cert.get("expiry_date"),
                    "days_until_expiry": 200  # Would calculate from expiry_date
                }
                for cert in certificates if "expiry_date" in cert
            ]
        }
        
        return {"success": True, "data": certificate_summary}
    except Exception as e:
        logger.error(f"Error getting compliance certificates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training-status")
async def get_training_status(current_user: dict = Depends(get_current_user)):
    """Get compliance training status"""
    try:
        compliance_status = await ComplianceService.get_compliance_framework_status()
        training_data = compliance_status["staff_training"]
        
        # Enhanced training status with additional details
        enhanced_training = {
            **training_data,
            "training_analytics": {
                "total_employees": 125,
                "trained_employees": int(125 * (training_data["completion_rate"] / 100)),
                "pending_training": int(125 * (1 - training_data["completion_rate"] / 100)),
                "overdue_training": 2
            },
            "upcoming_sessions": [
                {
                    "module": "GDPR Updates 2025",
                    "scheduled_date": "2025-02-15",
                    "duration": "2 hours",
                    "mandatory": True
                },
                {
                    "module": "Incident Response Refresher",
                    "scheduled_date": "2025-03-01",
                    "duration": "1 hour",
                    "mandatory": False
                }
            ]
        }
        
        return {"success": True, "data": enhanced_training}
    except Exception as e:
        logger.error(f"Error getting training status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initiate-audit")
async def initiate_compliance_audit(
    framework: str = Form(..., description="Framework to audit"),
    audit_type: str = Form("internal", description="Audit type: internal, external, certification"),
    scope: str = Form("full", description="Audit scope: full, partial, focused"),
    current_user: dict = Depends(get_current_user)
):
    """Initiate a compliance audit"""
    try:
        valid_frameworks = ["gdpr", "soc2", "iso27001", "hipaa", "pci_dss"]
        if framework not in valid_frameworks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework. Must be one of: {', '.join(valid_frameworks)}"
            )
        
        valid_types = ["internal", "external", "certification"]
        if audit_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audit type. Must be one of: {', '.join(valid_types)}"
            )
        
        valid_scopes = ["full", "partial", "focused"]
        if scope not in valid_scopes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scope. Must be one of: {', '.join(valid_scopes)}"
            )
        
        import uuid
        from datetime import datetime, timedelta
        
        audit_job = {
            "audit_id": str(uuid.uuid4()),
            "framework": framework,
            "audit_type": audit_type,
            "scope": scope,
            "status": "initiated",
            "initiated_at": datetime.utcnow().isoformat(),
            "estimated_completion": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "audit_phases": [
                {"phase": "planning", "status": "pending", "estimated_duration": "5 days"},
                {"phase": "fieldwork", "status": "pending", "estimated_duration": "15 days"},
                {"phase": "testing", "status": "pending", "estimated_duration": "7 days"},
                {"phase": "reporting", "status": "pending", "estimated_duration": "3 days"}
            ],
            "auditor_assignment": {
                "lead_auditor": "Internal Compliance Team" if audit_type == "internal" else "External Audit Firm",
                "team_size": 3 if audit_type == "internal" else 5,
                "specialization": f"{framework.upper()} compliance"
            },
            "deliverables": [
                f"{framework.upper()} compliance assessment report",
                "Gap analysis and remediation plan",
                "Management letter with recommendations",
                "Evidence documentation package"
            ]
        }
        
        return {
            "success": True,
            "data": {
                "audit_id": audit_job["audit_id"],
                "framework": audit_job["framework"],
                "status": audit_job["status"],
                "estimated_completion": audit_job["estimated_completion"],
                "audit_phases": audit_job["audit_phases"],
                "status_url": f"/api/compliance/audits/{audit_job['audit_id']}/status",
                "initiated_at": audit_job["initiated_at"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating audit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))