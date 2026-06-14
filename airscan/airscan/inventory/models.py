from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class InventoryItem(models.Model):
    """Secure CRUD model - uses Django ORM (SQLi protected)"""
    CATEGORY_CHOICES = [
        ('raw', 'Raw Material'),
        ('finished', 'Finished Good'),
        ('packaging', 'Packaging'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)  # PositiveInteger = validation
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.PositiveIntegerField(default=10)
    description = models.TextField(blank=True)
    
    # Audit fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class AuditLog(models.Model):
    """For Member 3 - logging system"""
    ACTION_CHOICES = [
        ('login_success', 'Login Success'),
        ('login_failed', 'Login Failed'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('access_denied', 'Access Denied'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
    
    class Meta:
        ordering = ['-timestamp']