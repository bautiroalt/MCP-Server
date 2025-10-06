# NEW MCP Server - Security Manager
# Centralized security management
# ----------------------------------------------------

import hashlib
import hmac
import secrets
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class SecurityManager:
    """Centralized security management for the MCP server"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.failed_attempts: Dict[str, List[float]] = {}
        self.blocked_ips: set = set()
        self.suspicious_activities: List[Dict[str, Any]] = []
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        timestamp = int(time.time())
        message = f"{timestamp}:{self.secret_key}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{timestamp}:{signature}"
    
    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token"""
        try:
            timestamp, signature = token.split(":")
            timestamp = int(timestamp)
            current_time = int(time.time())
            
            # Check if token is not too old (5 minutes)
            if current_time - timestamp > 300:
                return False
            
            # Verify signature
            message = f"{timestamp}:{self.secret_key}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, IndexError):
            return False
    
    def record_failed_attempt(self, identifier: str, max_attempts: int = 5, lockout_duration: int = 900) -> bool:
        """Record failed login attempt and check if account should be locked"""
        current_time = time.time()
        
        # Clean old attempts
        if identifier in self.failed_attempts:
            self.failed_attempts[identifier] = [
                attempt_time for attempt_time in self.failed_attempts[identifier]
                if current_time - attempt_time < lockout_duration
            ]
        else:
            self.failed_attempts[identifier] = []
        
        # Add current attempt
        self.failed_attempts[identifier].append(current_time)
        
        # Check if account should be locked
        if len(self.failed_attempts[identifier]) >= max_attempts:
            self._log_suspicious_activity(
                "account_locked",
                {"identifier": identifier, "attempts": len(self.failed_attempts[identifier])}
            )
            return True
        
        return False
    
    def is_account_locked(self, identifier: str, lockout_duration: int = 900) -> bool:
        """Check if account is locked due to failed attempts"""
        if identifier not in self.failed_attempts:
            return False
        
        current_time = time.time()
        recent_attempts = [
            attempt_time for attempt_time in self.failed_attempts[identifier]
            if current_time - attempt_time < lockout_duration
        ]
        
        return len(recent_attempts) >= 5
    
    def clear_failed_attempts(self, identifier: str):
        """Clear failed attempts for successful login"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    def block_ip(self, ip_address: str, reason: str = "suspicious_activity"):
        """Block IP address"""
        self.blocked_ips.add(ip_address)
        self._log_suspicious_activity("ip_blocked", {"ip": ip_address, "reason": reason})
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        self.blocked_ips.discard(ip_address)
    
    def _log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activity for monitoring"""
        activity = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": activity_type,
            "details": details
        }
        self.suspicious_activities.append(activity)
        
        # Keep only last 1000 activities
        if len(self.suspicious_activities) > 1000:
            self.suspicious_activities = self.suspicious_activities[-1000:]
        
        logger.warning(f"Suspicious activity: {activity_type} - {details}")
    
    def get_suspicious_activities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent suspicious activities"""
        return self.suspicious_activities[-limit:]
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent XSS"""
        import html
        import re
        
        # HTML escape
        sanitized = html.escape(input_data)
        
        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove javascript: URLs
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remove on* event handlers
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def validate_file_upload(self, filename: str, content_type: str, file_size: int) -> bool:
        """Validate file upload for security"""
        # Check file extension
        allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                            '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif'}
        
        import os
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            return False
        
        # Check file size (100MB limit)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            return False
        
        # Check content type
        allowed_types = {
            'text/plain', 'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'image/jpeg', 'image/png', 'image/gif'
        }
        
        if content_type not in allowed_types:
            return False
        
        return True
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """Generate secure filename to prevent path traversal"""
        import os
        import uuid
        
        # Get file extension
        _, ext = os.path.splitext(original_filename)
        
        # Generate secure filename
        secure_name = f"{uuid.uuid4()}{ext}"
        
        return secure_name
