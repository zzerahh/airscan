from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
import datetime

class SessionTimeoutMiddleware(MiddlewareMixin):
    """Enforce session timeout - OWASP ASVS V2"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Check if session has expired
            if request.session.get_expiry_age() <= 0:
                from django.contrib.auth import logout
                logout(request)
                messages.warning(request, 'Your session has expired. Please login again.')
                return redirect('login')
        return None

class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """Add Content Security Policy header - OWASP ASVS V3"""
    
    def process_response(self, request, response):
        # Set a basic CSP header to prevent XSS attacks
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        return response

class HideServerInfoMiddleware(MiddlewareMixin):
    """Hide server version information - OWASP"""
    
    def process_response(self, request, response):
        # Remove or mask the Server header to prevent information disclosure
        if 'Server' in response:
            response['Server'] = 'WebServer'  # Generic name instead of version info
        return response