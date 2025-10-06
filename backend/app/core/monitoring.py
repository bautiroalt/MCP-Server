# NEW MCP Server - Advanced Monitoring System
# Health checks, metrics, and performance monitoring
# ----------------------------------------------------

import time
import psutil
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import asyncio
import aiofiles
import json

logger = logging.getLogger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter('mcp_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('mcp_active_connections', 'Active connections')
MEMORY_USAGE = Gauge('mcp_memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('mcp_cpu_usage_percent', 'CPU usage percentage')
DISK_USAGE = Gauge('mcp_disk_usage_bytes', 'Disk usage in bytes')
DATABASE_CONNECTIONS = Gauge('mcp_database_connections', 'Database connections')
CACHE_HITS = Counter('mcp_cache_hits_total', 'Cache hits')
CACHE_MISSES = Counter('mcp_cache_misses_total', 'Cache misses')
ERROR_COUNT = Counter('mcp_errors_total', 'Total errors', ['error_type', 'endpoint'])

@dataclass
class HealthStatus:
    """Health status data structure"""
    status: str
    timestamp: datetime
    uptime: float
    version: str
    environment: str
    checks: Dict[str, Any]

class SystemMonitor:
    """System monitoring and health checks"""
    
    def __init__(self):
        self.start_time = time.time()
        self.health_checks: Dict[str, callable] = {}
        self.metrics_history: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 5.0
        }
        
    def register_health_check(self, name: str, check_func: callable):
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            memory_total = memory.total
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used = disk.used
            disk_total = disk.total
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Process info
            process = psutil.Process()
            process_memory = process.memory_info().rss
            process_cpu = process.cpu_percent()
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'process_cpu_percent': process_cpu,
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'used_bytes': memory_used,
                    'total_bytes': memory_total,
                    'available_bytes': memory.available,
                    'process_memory_bytes': process_memory
                },
                'disk': {
                    'usage_percent': disk_percent,
                    'used_bytes': disk_used,
                    'total_bytes': disk_total,
                    'free_bytes': disk.free
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'uptime': time.time() - self.start_time
            }
            
            # Update Prometheus metrics
            CPU_USAGE.set(cpu_percent)
            MEMORY_USAGE.set(memory_used)
            DISK_USAGE.set(disk_used)
            
            # Store metrics history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:  # Keep last 1000 entries
                self.metrics_history = self.metrics_history[-1000:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            # This would be implemented based on your database
            # For now, return a mock response
            return {
                'status': 'healthy',
                'response_time': 0.001,
                'connections': 5,
                'last_check': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and health"""
        try:
            # This would be implemented based on your Redis setup
            # For now, return a mock response
            return {
                'status': 'healthy',
                'response_time': 0.001,
                'memory_usage': '10MB',
                'last_check': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    async def check_external_services(self) -> Dict[str, Any]:
        """Check external service dependencies"""
        services = {}
        
        # Check if required external services are accessible
        # This would be implemented based on your specific services
        
        return services
    
    async def get_health_status(self) -> HealthStatus:
        """Get comprehensive health status"""
        checks = {}
        
        # System metrics
        system_metrics = await self.get_system_metrics()
        checks['system'] = system_metrics
        
        # Database health
        db_health = await self.check_database_health()
        checks['database'] = db_health
        
        # Redis health
        redis_health = await self.check_redis_health()
        checks['redis'] = redis_health
        
        # External services
        external_services = await self.check_external_services()
        checks['external_services'] = external_services
        
        # Custom health checks
        for name, check_func in self.health_checks.items():
            try:
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                checks[name] = result
            except Exception as e:
                checks[name] = {'status': 'error', 'error': str(e)}
        
        # Determine overall status
        overall_status = 'healthy'
        for check_name, check_result in checks.items():
            if isinstance(check_result, dict):
                if check_result.get('status') == 'unhealthy':
                    overall_status = 'unhealthy'
                    break
                elif check_result.get('status') == 'error':
                    overall_status = 'degraded'
        
        return HealthStatus(
            status=overall_status,
            timestamp=datetime.utcnow(),
            uptime=time.time() - self.start_time,
            version="1.0.0",
            environment="production",
            checks=checks
        )
    
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        metrics = await self.get_system_metrics()
        
        if not metrics:
            return alerts
        
        # CPU usage alert
        if metrics.get('cpu', {}).get('usage_percent', 0) > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'cpu_usage',
                'severity': 'warning',
                'message': f"CPU usage is {metrics['cpu']['usage_percent']:.1f}%",
                'threshold': self.alert_thresholds['cpu_usage']
            })
        
        # Memory usage alert
        if metrics.get('memory', {}).get('usage_percent', 0) > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'memory_usage',
                'severity': 'warning',
                'message': f"Memory usage is {metrics['memory']['usage_percent']:.1f}%",
                'threshold': self.alert_thresholds['memory_usage']
            })
        
        # Disk usage alert
        if metrics.get('disk', {}).get('usage_percent', 0) > self.alert_thresholds['disk_usage']:
            alerts.append({
                'type': 'disk_usage',
                'severity': 'critical',
                'message': f"Disk usage is {metrics['disk']['usage_percent']:.1f}%",
                'threshold': self.alert_thresholds['disk_usage']
            })
        
        return alerts
    
    async def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cutoff_timestamp = cutoff_time.timestamp()
        
        return [
            metrics for metrics in self.metrics_history
            if datetime.fromisoformat(metrics['timestamp']).timestamp() > cutoff_timestamp
        ]
    
    async def export_prometheus_metrics(self) -> str:
        """Export Prometheus metrics"""
        return generate_latest()

class PerformanceMonitor:
    """Performance monitoring middleware"""
    
    def __init__(self):
        self.request_times: List[float] = []
        self.max_history = 1000
    
    async def track_request(self, request: Request, call_next):
        """Track request performance"""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Update metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        # Store request time
        self.request_times.append(duration)
        if len(self.request_times) > self.max_history:
            self.request_times = self.request_times[-self.max_history:]
        
        # Add performance headers
        response.headers["X-Response-Time"] = str(duration)
        response.headers["X-Request-ID"] = str(int(time.time() * 1000))
        
        return response
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.request_times:
            return {}
        
        sorted_times = sorted(self.request_times)
        count = len(sorted_times)
        
        return {
            'total_requests': count,
            'avg_response_time': sum(sorted_times) / count,
            'min_response_time': min(sorted_times),
            'max_response_time': max(sorted_times),
            'p50_response_time': sorted_times[int(count * 0.5)],
            'p95_response_time': sorted_times[int(count * 0.95)],
            'p99_response_time': sorted_times[int(count * 0.99)]
        }

# Global monitoring instances
system_monitor = SystemMonitor()
performance_monitor = PerformanceMonitor()
