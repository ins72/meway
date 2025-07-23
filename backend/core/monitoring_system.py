"""
COMPREHENSIVE MONITORING AND ALERTING SYSTEM
Production-grade monitoring with intelligent alerting
"""

import asyncio
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os
from core.production_logging import production_logger

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types of alerts"""
    SYSTEM_RESOURCE = "system_resource"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    SECURITY_BREACH = "security_breach"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SERVICE_UNAVAILABLE = "service_unavailable"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    timestamp: str
    resolved: bool = False
    resolution_time: Optional[str] = None
    metadata: Dict[str, Any] = None

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.thresholds = {
            "cpu_percent": 85.0,
            "memory_percent": 80.0,
            "disk_percent": 85.0,
            "network_errors": 100,
            "response_time_ms": 5000
        }
        self.monitoring_active = True
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None,
                    "process_percent": process_cpu
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent,
                    "process_rss_mb": round(process_memory.rss / (1024**2), 2),
                    "process_vms_mb": round(process_memory.vms / (1024**2), 2)
                },
                "swap": {
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_gb": round(swap.used / (1024**3), 2),
                    "percent": swap.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": round((disk.used / disk.total) * 100, 2),
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                },
                "network": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv,
                    "errors_in": network_io.errin,
                    "errors_out": network_io.errout,
                    "connections": network_connections
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "status": "error"
            }
    
    def check_system_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check system metrics against thresholds and generate alerts"""
        alerts = []
        timestamp = datetime.utcnow().isoformat()
        
        if "error" in metrics:
            alerts.append(Alert(
                id=f"system_error_{timestamp}",
                type=AlertType.SYSTEM_RESOURCE,
                severity=AlertSeverity.CRITICAL,
                title="System Monitoring Error",
                description=f"Failed to collect system metrics: {metrics['error']}",
                timestamp=timestamp,
                metadata={"error": metrics["error"]}
            ))
            return alerts
        
        # CPU alert
        cpu_percent = metrics.get("cpu", {}).get("percent", 0)
        if cpu_percent > self.thresholds["cpu_percent"]:
            alerts.append(Alert(
                id=f"cpu_high_{timestamp}",
                type=AlertType.SYSTEM_RESOURCE,
                severity=AlertSeverity.CRITICAL if cpu_percent > 95 else AlertSeverity.WARNING,
                title="High CPU Usage",
                description=f"CPU usage is {cpu_percent}% (threshold: {self.thresholds['cpu_percent']}%)",
                timestamp=timestamp,
                metadata={"cpu_percent": cpu_percent, "threshold": self.thresholds["cpu_percent"]}
            ))
        
        # Memory alert
        memory_percent = metrics.get("memory", {}).get("percent", 0)
        if memory_percent > self.thresholds["memory_percent"]:
            alerts.append(Alert(
                id=f"memory_high_{timestamp}",
                type=AlertType.SYSTEM_RESOURCE,
                severity=AlertSeverity.CRITICAL if memory_percent > 90 else AlertSeverity.WARNING,
                title="High Memory Usage",
                description=f"Memory usage is {memory_percent}% (threshold: {self.thresholds['memory_percent']}%)",
                timestamp=timestamp,
                metadata={"memory_percent": memory_percent, "threshold": self.thresholds["memory_percent"]}
            ))
        
        # Disk alert
        disk_percent = metrics.get("disk", {}).get("percent", 0)
        if disk_percent > self.thresholds["disk_percent"]:
            alerts.append(Alert(
                id=f"disk_high_{timestamp}",
                type=AlertType.SYSTEM_RESOURCE,
                severity=AlertSeverity.CRITICAL if disk_percent > 95 else AlertSeverity.WARNING,
                title="High Disk Usage",
                description=f"Disk usage is {disk_percent}% (threshold: {self.thresholds['disk_percent']}%)",
                timestamp=timestamp,
                metadata={"disk_percent": disk_percent, "threshold": self.thresholds["disk_percent"]}
            ))
        
        # Network errors alert
        network_errors = metrics.get("network", {}).get("errors_in", 0) + metrics.get("network", {}).get("errors_out", 0)
        if network_errors > self.thresholds["network_errors"]:
            alerts.append(Alert(
                id=f"network_errors_{timestamp}",
                type=AlertType.SYSTEM_RESOURCE,
                severity=AlertSeverity.WARNING,
                title="Network Errors Detected",
                description=f"Network errors: {network_errors} (threshold: {self.thresholds['network_errors']})",
                timestamp=timestamp,
                metadata={"network_errors": network_errors, "threshold": self.thresholds["network_errors"]}
            ))
        
        return alerts

class ApplicationMonitor:
    """Application-specific monitoring"""
    
    def __init__(self):
        self.error_counts = {}
        self.response_times = []
        self.api_call_counts = {}
        self.last_reset = datetime.utcnow()
    
    def record_api_call(self, endpoint: str, status_code: int, response_time_ms: float):
        """Record API call metrics"""
        # Track API calls
        if endpoint not in self.api_call_counts:
            self.api_call_counts[endpoint] = {"total": 0, "errors": 0, "avg_response_time": 0}
        
        self.api_call_counts[endpoint]["total"] += 1
        
        # Track errors
        if status_code >= 400:
            self.api_call_counts[endpoint]["errors"] += 1
            
            error_key = f"{endpoint}_{status_code}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Track response times
        self.response_times.append({
            "endpoint": endpoint,
            "response_time_ms": response_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        # Update average response time
        endpoint_times = [rt["response_time_ms"] for rt in self.response_times if rt["endpoint"] == endpoint]
        if endpoint_times:
            self.api_call_counts[endpoint]["avg_response_time"] = sum(endpoint_times) / len(endpoint_times)
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application performance metrics"""
        current_time = datetime.utcnow()
        uptime_seconds = (current_time - self.last_reset).total_seconds()
        
        # Calculate overall metrics
        total_calls = sum(endpoint["total"] for endpoint in self.api_call_counts.values())
        total_errors = sum(endpoint["errors"] for endpoint in self.api_call_counts.values())
        error_rate = (total_errors / total_calls * 100) if total_calls > 0 else 0
        
        # Calculate average response time
        if self.response_times:
            avg_response_time = sum(rt["response_time_ms"] for rt in self.response_times) / len(self.response_times)
        else:
            avg_response_time = 0
        
        return {
            "timestamp": current_time.isoformat(),
            "uptime_seconds": uptime_seconds,
            "total_api_calls": total_calls,
            "total_errors": total_errors,
            "error_rate_percent": round(error_rate, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "endpoints": self.api_call_counts,
            "recent_errors": dict(sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def check_application_alerts(self) -> List[Alert]:
        """Check application metrics for alerts"""
        alerts = []
        timestamp = datetime.utcnow().isoformat()
        metrics = self.get_application_metrics()
        
        # High error rate alert
        error_rate = metrics.get("error_rate_percent", 0)
        if error_rate > 10:  # More than 10% error rate
            alerts.append(Alert(
                id=f"error_rate_high_{timestamp}",
                type=AlertType.API_ERROR,
                severity=AlertSeverity.CRITICAL if error_rate > 25 else AlertSeverity.WARNING,
                title="High API Error Rate",
                description=f"API error rate is {error_rate}% (threshold: 10%)",
                timestamp=timestamp,
                metadata={"error_rate": error_rate, "total_calls": metrics["total_api_calls"]}
            ))
        
        # Slow response time alert
        avg_response_time = metrics.get("average_response_time_ms", 0)
        if avg_response_time > 2000:  # Slower than 2 seconds
            alerts.append(Alert(
                id=f"response_time_slow_{timestamp}",
                type=AlertType.PERFORMANCE_DEGRADATION,
                severity=AlertSeverity.WARNING,
                title="Slow API Response Times",
                description=f"Average response time is {avg_response_time}ms (threshold: 2000ms)",
                timestamp=timestamp,
                metadata={"avg_response_time_ms": avg_response_time}
            ))
        
        return alerts

class AlertManager:
    """Centralized alert management"""
    
    def __init__(self):
        self.active_alerts = {}
        self.alert_history = []
        self.notification_channels = []
    
    def add_alert(self, alert: Alert):
        """Add new alert"""
        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts in history
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        # Log alert
        production_logger.log_business_event(
            "alert_triggered",
            metadata={
                "alert_id": alert.id,
                "type": alert.type.value,
                "severity": alert.severity.value,
                "title": alert.title
            }
        )
        
        # Send notifications (implement as needed)
        asyncio.create_task(self._send_alert_notifications(alert))
    
    def resolve_alert(self, alert_id: str):
        """Mark alert as resolved"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.utcnow().isoformat()
            
            del self.active_alerts[alert_id]
            
            production_logger.log_business_event(
                "alert_resolved",
                metadata={"alert_id": alert_id, "resolution_time": alert.resolution_time}
            )
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications (webhook, email, etc.)"""
        try:
            # Log alert notification
            logger.info(f"🚨 ALERT: {alert.severity.value.upper()} - {alert.title}")
            logger.info(f"   Description: {alert.description}")
            logger.info(f"   Timestamp: {alert.timestamp}")
            
            # Send to webhook if configured
            webhook_url = os.getenv("ALERT_WEBHOOK_URL")
            if webhook_url:
                # Implement webhook notification
                pass
            
        except Exception as e:
            logger.error(f"Failed to send alert notifications: {e}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Recent alerts (last 24 hours)
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00').replace('+00:00', '')) > last_24h
        ]
        
        return {
            "timestamp": now.isoformat(),
            "active_alerts_count": len(self.active_alerts),
            "recent_alerts_24h": len(recent_alerts),
            "active_alerts": [asdict(alert) for alert in self.active_alerts.values()],
            "alert_types_summary": self._get_alert_types_summary(recent_alerts),
            "severity_distribution": self._get_severity_distribution(recent_alerts)
        }
    
    def _get_alert_types_summary(self, alerts: List[Alert]) -> Dict[str, int]:
        """Get summary of alert types"""
        types_count = {}
        for alert in alerts:
            alert_type = alert.type.value
            types_count[alert_type] = types_count.get(alert_type, 0) + 1
        return types_count
    
    def _get_severity_distribution(self, alerts: List[Alert]) -> Dict[str, int]:
        """Get distribution of alert severities"""
        severity_count = {}
        for alert in alerts:
            severity = alert.severity.value
            severity_count[severity] = severity_count.get(severity, 0) + 1
        return severity_count

class ComprehensiveMonitor:
    """Main monitoring orchestrator"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.app_monitor = ApplicationMonitor()
        self.alert_manager = AlertManager()
        self.monitoring_active = True
        self.monitoring_interval = 60  # seconds
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("🎯 Starting comprehensive monitoring system...")
        
        while self.monitoring_active:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring cycle error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        try:
            # Get system metrics
            system_metrics = await self.system_monitor.get_system_metrics()
            
            # Check for system alerts
            system_alerts = self.system_monitor.check_system_alerts(system_metrics)
            for alert in system_alerts:
                self.alert_manager.add_alert(alert)
            
            # Check for application alerts
            app_alerts = self.app_monitor.check_application_alerts()
            for alert in app_alerts:
                self.alert_manager.add_alert(alert)
            
            # Log monitoring cycle
            production_logger.log_business_event(
                "monitoring_cycle_completed",
                metadata={
                    "system_alerts": len(system_alerts),
                    "app_alerts": len(app_alerts),
                    "active_alerts": len(self.alert_manager.active_alerts)
                }
            )
            
        except Exception as e:
            logger.error(f"Monitoring cycle error: {e}")
    
    def record_api_call(self, endpoint: str, status_code: int, response_time_ms: float):
        """Record API call for monitoring"""
        self.app_monitor.record_api_call(endpoint, status_code, response_time_ms)
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        system_metrics = await self.system_monitor.get_system_metrics()
        app_metrics = self.app_monitor.get_application_metrics()
        alert_summary = self.alert_manager.get_alert_summary()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "monitoring_active": self.monitoring_active,
            "system_metrics": system_metrics,
            "application_metrics": app_metrics,
            "alerts": alert_summary,
            "overall_health": self._calculate_overall_health(system_metrics, app_metrics, alert_summary)
        }
    
    def _calculate_overall_health(self, system_metrics: Dict, app_metrics: Dict, alert_summary: Dict) -> str:
        """Calculate overall system health"""
        if alert_summary["active_alerts_count"] > 0:
            # Check if there are critical alerts
            for alert in alert_summary["active_alerts"]:
                if alert["severity"] == "critical":
                    return "critical"
            return "warning"
        
        # Check system resource usage
        if "error" not in system_metrics:
            cpu_percent = system_metrics.get("cpu", {}).get("percent", 0)
            memory_percent = system_metrics.get("memory", {}).get("percent", 0)
            disk_percent = system_metrics.get("disk", {}).get("percent", 0)
            
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 95:
                return "warning"
        
        # Check application metrics
        error_rate = app_metrics.get("error_rate_percent", 0)
        if error_rate > 15:
            return "warning"
        
        return "healthy"
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Monitoring system stopped")

# Global monitoring instance
comprehensive_monitor = ComprehensiveMonitor()

async def initialize_monitoring_system():
    """Initialize the monitoring system"""
    logger.info("🎯 Initializing comprehensive monitoring system...")
    
    # Start monitoring in background
    asyncio.create_task(comprehensive_monitor.start_monitoring())
    
    logger.info("✅ Comprehensive monitoring system initialized")
    return comprehensive_monitor

if __name__ == "__main__":
    asyncio.run(initialize_monitoring_system())