# NEW MCP Server - Monitoring API Routes
# Health checks, metrics, and monitoring endpoints
# ----------------------------------------------------

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import logging
from ..core.monitoring import system_monitor, performance_monitor, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        health_status = await system_monitor.get_health_status()
        return {
            "status": health_status.status,
            "timestamp": health_status.timestamp.isoformat(),
            "uptime": health_status.uptime,
            "version": health_status.version,
            "environment": health_status.environment,
            "checks": health_status.checks
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": system_monitor.start_time}

@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        health_status = await system_monitor.get_health_status()
        if health_status.status in ['healthy', 'degraded']:
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    try:
        metrics = await system_monitor.export_prometheus_metrics()
        return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Metrics export failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics export failed")

@router.get("/metrics/system")
async def get_system_metrics():
    """Get current system metrics"""
    try:
        metrics = await system_monitor.get_system_metrics()
        return metrics
    except Exception as e:
        logger.error(f"System metrics failed: {e}")
        raise HTTPException(status_code=500, detail="System metrics failed")

@router.get("/metrics/performance")
async def get_performance_metrics():
    """Get performance metrics"""
    try:
        stats = performance_monitor.get_performance_stats()
        return stats
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Performance metrics failed")

@router.get("/metrics/history")
async def get_metrics_history(hours: int = 24):
    """Get metrics history"""
    try:
        history = await system_monitor.get_metrics_history(hours)
        return {"history": history, "hours": hours}
    except Exception as e:
        logger.error(f"Metrics history failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics history failed")

@router.get("/alerts")
async def get_alerts():
    """Get current alerts"""
    try:
        alerts = await system_monitor.check_alerts()
        return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        logger.error(f"Alerts check failed: {e}")
        raise HTTPException(status_code=500, detail="Alerts check failed")

@router.get("/status")
async def get_status():
    """Get overall system status"""
    try:
        health_status = await system_monitor.get_health_status()
        alerts = await system_monitor.check_alerts()
        performance_stats = performance_monitor.get_performance_stats()
        
        return {
            "health": {
                "status": health_status.status,
                "uptime": health_status.uptime,
                "timestamp": health_status.timestamp.isoformat()
            },
            "alerts": {
                "count": len(alerts),
                "alerts": alerts
            },
            "performance": performance_stats,
            "version": health_status.version,
            "environment": health_status.environment
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

@router.post("/health/check/{check_name}")
async def run_health_check(check_name: str):
    """Run a specific health check"""
    try:
        if check_name not in system_monitor.health_checks:
            raise HTTPException(status_code=404, detail=f"Health check '{check_name}' not found")
        
        check_func = system_monitor.health_checks[check_name]
        result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
        
        return {
            "check_name": check_name,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check '{check_name}' failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/logs")
async def get_recent_logs(limit: int = 100):
    """Get recent log entries"""
    try:
        # This would be implemented based on your logging setup
        # For now, return a mock response
        return {
            "logs": [],
            "limit": limit,
            "message": "Log retrieval not implemented yet"
        }
    except Exception as e:
        logger.error(f"Log retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Log retrieval failed")

@router.get("/dashboard")
async def get_dashboard_data():
    """Get dashboard data for monitoring UI"""
    try:
        health_status = await system_monitor.get_health_status()
        system_metrics = await system_monitor.get_system_metrics()
        alerts = await system_monitor.check_alerts()
        performance_stats = performance_monitor.get_performance_stats()
        
        return {
            "overview": {
                "status": health_status.status,
                "uptime": health_status.uptime,
                "version": health_status.version,
                "environment": health_status.environment
            },
            "system": system_metrics,
            "alerts": alerts,
            "performance": performance_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Dashboard data failed: {e}")
        raise HTTPException(status_code=500, detail="Dashboard data failed")