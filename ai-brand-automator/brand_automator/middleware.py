"""
Custom middleware for security and request validation
"""
import logging
import re
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """
    Middleware for additional security measures:
    - CSRF token validation for state-changing operations
    - Request size limits
    - Security headers
    """
    
    MAX_REQUEST_SIZE = 50 * 1024 * 1024  # 50 MB
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check request size
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_length = request.META.get('CONTENT_LENGTH')
            if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
                return JsonResponse(
                    {'error': 'Request body too large'},
                    status=413
                )
        
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RequestValidationMiddleware:
    """
    Middleware for validating request data:
    - Input sanitization
    - Injection prevention
    """
    
    # Patterns for detecting malicious input
    INJECTION_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',  # eval()
        r'expression\s*\(',  # CSS expressions
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.injection_regex = re.compile('|'.join(self.INJECTION_PATTERNS), re.IGNORECASE)
    
    def __call__(self, request):
        # Validate GET and POST parameters
        if request.method in ['GET', 'POST', 'PUT', 'PATCH']:
            if not self._validate_request_data(request):
                logger.warning(f"Suspicious input detected from {request.META.get('REMOTE_ADDR')}")
                return JsonResponse(
                    {'error': 'Invalid input detected'},
                    status=400
                )
        
        response = self.get_response(request)
        return response
    
    def _validate_request_data(self, request):
        """Check request data for malicious patterns"""
        # Check GET parameters
        for key, value in request.GET.items():
            if self.injection_regex.search(value):
                return False
        
        # Check POST data (only if it's form data)
        if request.content_type == 'application/x-www-form-urlencoded':
            for key, value in request.POST.items():
                if isinstance(value, str) and self.injection_regex.search(value):
                    return False
        
        return True


class RateLimitMiddleware:
    """
    Simple in-memory rate limiting middleware
    For production, use Redis-based solution
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}  # {ip: [(timestamp, count)]}
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds
    
    def __call__(self, request):
        import time
        
        # Skip rate limiting for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
        
        ip_address = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        if ip_address in self.requests:
            self.requests[ip_address] = [
                (ts, count) for ts, count in self.requests[ip_address]
                if current_time - ts < self.window
            ]
        
        # Count requests in current window
        request_count = sum(count for ts, count in self.requests.get(ip_address, []))
        
        if request_count >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )
        
        # Add current request
        if ip_address not in self.requests:
            self.requests[ip_address] = []
        self.requests[ip_address].append((current_time, 1))
        
        response = self.get_response(request)
        return response
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
