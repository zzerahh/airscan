from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from .models import InventoryItem

# Whitelist validation for username
username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]+$',
    message='Username can only contain letters, numbers, and underscores.'
)

class CustomUserCreationForm(UserCreationForm):
    """Secure registration form with input validation"""
    
    username = forms.CharField(
        max_length=30,
        validators=[username_validator, MinLengthValidator(3), MaxLengthValidator(30)],
        help_text='Letters, numbers, and underscores only. 3-30 characters.'
    )
    
    email = forms.EmailField(
        required=True,
        help_text='Valid email address required.'
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text='At least 12 characters, not common, not entirely numeric.',
        validators=[MinLengthValidator(12)]
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        """Server-side validation - prevent injection"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email


class InventoryItemForm(forms.ModelForm):
    """Secure CRUD form with whitelist validation"""
    
    name = forms.CharField(
        max_length=200,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-_]+$',
                message='Item name can only contain letters, numbers, spaces, hyphens, and underscores.'
            ),
            MinLengthValidator(2)
        ]
    )
    
    quantity = forms.IntegerField(
        min_value=0,
        max_value=999999,
        help_text='Must be 0 or positive number.'
    )
    
    price = forms.DecimalField(
        min_value=0,
        max_value=999999.99,
        decimal_places=2,
        help_text='Positive number only.'
    )
    
    class Meta:
        model = InventoryItem
        fields = ['name', 'category', 'quantity', 'price', 'reorder_level', 'description']
    
    def clean_name(self):
        """Server-side whitelist validation - prevent injection"""
        name = self.cleaned_data.get('name')
        # Extra check: strip any suspicious characters
        import re
        if re.search(r'[<>\"\'%;()&+]', name):
            raise forms.ValidationError('Item name contains invalid characters.')
        return name.strip()