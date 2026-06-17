from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, InventoryItemForm
from .models import InventoryItem, AuditLog
from .decorators import role_required

import logging
import re

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Helper to get client IP for logging"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ========== REGISTRATION ==========
@csrf_protect
def register(request):
    """Secure user registration with input validation"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():  # Django handles whitelist validation automatically
            user = form.save(commit=False)
            user.is_superuser = False  # Default to Normal User
            user.is_staff = False
            user.save()
            
            # Log registration
            AuditLog.objects.create(
                user=user,
                action='create',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details=f"User registered: {user.username}"
            )
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})


# ========== LOGIN ==========
@csrf_protect
@ensure_csrf_cookie
def login_view(request):
    """Secure login with session management"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Input validation - whitelist check
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            messages.error(request, 'Invalid username format.')
            # Log failed attempt
            AuditLog.objects.create(
                user=None,
                action='login_failed',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details=f"Invalid username format: {username}"
            )
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry
            request.session.set_expiry(1800)  # 30 minutes
            
            # Log successful login
            AuditLog.objects.create(
                user=user,
                action='login_success',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details=f"User logged in from IP: {get_client_ip(request)}"
            )
            
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            # Log failed login
            AuditLog.objects.create(
                user=None,
                action='login_failed',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details=f"Failed login attempt for: {username}"
            )
    
    return render(request, 'login.html')


# ========== LOGOUT ==========
@login_required
def logout_view(request):
    """Secure logout with logging"""
    username = request.user.username
    AuditLog.objects.create(
        user=request.user,
        action='logout',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details=f"User logged out"
    )
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ========== DASHBOARD ==========
@login_required
def dashboard(request):
    """User dashboard - shows role-specific content"""
    context = {
        'is_admin': request.user.is_superuser,
        'username': request.user.username,
    }
    return render(request, 'dashboard.html', context)


# ========== USER PROFILE ==========
@login_required
def profile(request):
    """User profile page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Input validation for email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format.')
            return render(request, 'profile.html', {'user': request.user})
        
        # Update email only if changed and not taken
        if email != request.user.email:
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.error(request, 'Email already in use.')
            else:
                request.user.email = email
                request.user.save()
                messages.success(request, 'Profile updated successfully.')
        
        return redirect('profile')
    
    return render(request, 'profile.html', {'user': request.user})


# ========== SECURE CRUD - INVENTORY ==========
@login_required
def inventory_list(request):
    """List inventory items - with RBAC"""
    if request.user.is_superuser:
        # Admin sees all items
        items = InventoryItem.objects.all()
    else:
        # Normal users see only their own items
        items = InventoryItem.objects.filter(created_by=request.user)
    
    return render(request, 'inventory_list.html', {'items': items})


@login_required
@role_required(['admin', 'user'])  # Both roles can create
def inventory_create(request):
    """Create inventory item - with input validation"""
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():  # Django handles whitelist validation automatically
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='create',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details=f"Created inventory item: {item.name}"
            )
            
            messages.success(request, f'Item "{item.name}" created successfully.')
            return redirect('inventory_list')
    else:
        form = InventoryItemForm()
    
    return render(request, 'inventory_form.html', {'form': form, 'title': 'Create Item'})


@login_required
def inventory_update(request, pk):
    """Update inventory item - with IDOR protection"""
    # First check if item exists and user has permission
    try:
        if request.user.is_superuser:
            item = InventoryItem.objects.get(pk=pk)
        else:
            item = InventoryItem.objects.get(pk=pk, created_by=request.user)
    except InventoryItem.DoesNotExist:
        messages.error(request, 'Item not found or access denied.')
        return redirect('inventory_list')
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='update',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details=f"Updated inventory item: {item.name} (ID: {item.id})"
            )
            
            messages.success(request, f'Item "{item.name}" updated successfully.')
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    
    return render(request, 'inventory_form.html', {'form': form, 'title': 'Edit Item', 'item': item})


@login_required
def inventory_delete(request, pk):
    """Delete inventory item - with IDOR protection"""
    # First check if item exists and user has permission
    try:
        if request.user.is_superuser:
            item = InventoryItem.objects.get(pk=pk)
        else:
            item = InventoryItem.objects.get(pk=pk, created_by=request.user)
    except InventoryItem.DoesNotExist:
        messages.error(request, 'Item not found or access denied.')
        return redirect('inventory_list')
    
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details=f"Deleted inventory item: {item_name} (ID: {pk})"
        )
        
        messages.success(request, f'Item "{item_name}" deleted successfully.')
        return redirect('inventory_list')
    
    return render(request, 'inventory_confirm_delete.html', {'item': item})


# ========== AUDIT LOG VIEW (for Member 3) ==========
@login_required
@role_required(['admin'])  # Only admin can view audit logs
def audit_log_view(request):
    """Audit log page - shows login attempts and activities"""
    logs = AuditLog.objects.all()[:100]  # Last 100 logs
    return render(request, 'audit_log.html', {'logs': logs})


# ========== ERROR HANDLING ==========
def bad_request(request, exception=None):
    """Handle 400 errors"""
    return render(request, '400.html', status=400)

def permission_denied(request, exception=None):
    """Handle 403 errors"""
    return render(request, '403.html', status=403)

def page_not_found(request, exception=None):
    """Handle 404 errors"""
    return render(request, '404.html', status=404)

def server_error(request):
    """Handle 500 errors"""
    return render(request, '500.html', status=500)