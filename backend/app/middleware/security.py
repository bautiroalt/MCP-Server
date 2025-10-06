# NEW MCP Server - Enhanced Security Middleware
# Production-ready security features
# ----------------------------------------------------

import time
import hashlib
import hmac
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware for production deployment"""
    
    def __init__(self, app, max_requests_per_minute: int = 60, max_burst: int = 10):
        super().__init__(app)
        self.max_requests_per_minute = max_requests_per_minute
        self.max_burst = max_burst
        self.request_counts: Dict[str, list] = {}
        self.blocked_ips: set = set()
        
    async def dispatch(self, request: Request, call_next):
        """Process request through security checks"""
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "IP address is blocked"}
            )
        
        # Rate limiting
        if not self._check_rate_limit(client_ip):
            self.blocked_ips.add(client_ip)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Security headers
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits"""
        current_time = time.time()
        
        # Clean old requests
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.request_counts[client_ip] = []
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        return True

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Input validation and sanitization middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.suspicious_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"expression\s*\(",
            r"vbscript:",
            r"data:text/html",
            r"data:application/javascript"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Validate and sanitize input"""
        
        # Check for suspicious patterns in query parameters
        for key, value in request.query_params.items():
            if self._is_suspicious(str(value)):
                logger.warning(f"Suspicious query parameter detected: {key}={value}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid input detected"}
                )
        
        # Check for suspicious patterns in headers
        for key, value in request.headers.items():
            if self._is_suspicious(str(value)):
                logger.warning(f"Suspicious header detected: {key}={value}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid input detected"}
                )
        
        response = await call_next(request)
        return response
    
    def _is_suspicious(self, value: str) -> bool:
        """Check if input contains suspicious patterns"""
        import re
        value_lower = value.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        return False

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware for security monitoring"""
    
    def __init__(self, app):
        super().__init__(app)
        self.audit_logger = logging.getLogger("audit")
        
    async def dispatch(self, request: Request, call_next):
        """Log security-relevant events"""
        
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        # Log request
        self.audit_logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} with User-Agent: {user_agent}"
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            processing_time = time.time() - start_time
            self.audit_logger.info(
                f"Response: {response.status_code} "
                f"in {processing_time:.3f}s for {request.url.path}"
            )
            
            return response
            
        except Exception as e:
            # Log errors
            self.audit_logger.error(
                f"Error processing {request.method} {request.url.path}: {str(e)}"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware"""
    
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key
    
    async def dispatch(self, request: Request, call_next):
        """Check CSRF token for state-changing requests"""
        
        # Skip CSRF check for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)
        
        # Check CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token required"}
            )
        
        # Validate CSRF token
        if not self._validate_csrf_token(csrf_token, request):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid CSRF token"}
            )
        
        return await call_next(request)
    
    def _validate_csrf_token(self, token: str, request: Request) -> bool:
        """Validate CSRF token"""
        try:
            # Extract timestamp from token
            timestamp = int(token.split(":")[0])
            current_time = int(time.time())
            
            # Check if token is not too old (5 minutes)
            if current_time - timestamp > 300:
                return False
            
            # Verify token signature
            expected_token = self._generate_csrf_token(timestamp)
            return hmac.compare_digest(token, expected_token)
            
        except (ValueError, IndexError):
            return False
    
    def _generate_csrf_token(self, timestamp: int) -> str:
        """Generate CSRF token"""
        message = f"{timestamp}:{self.secret_key}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{timestamp}:{signature}"

class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    """Content Security Policy middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    async def dispatch(self, request: Request, call_next):
        """Add Content Security Policy header"""
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = self.csp_policy
        return response
