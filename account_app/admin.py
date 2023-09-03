from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Otp
from django.db import models
from django import forms


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', "first_name", 'last_name', 'email', "is_staff", "is_active", "is_superuser")
    list_filter = ("is_staff", "is_active", "is_superuser", "date_joined", "last_login")
    readonly_fields = ('date_joined', 'last_login')
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    formfield_overrides = {
        models.PositiveIntegerField: {'widget': forms.NumberInput(attrs={'size': '15'})},
    }

    fieldsets = (
        (None, {"fields": ("password",)}),
        ('personal info', {"fields": (
            'username',
            'first_name',
            'last_name',
            'email',
            'last_login', 'date_joined',
        )}),
        ("permissions", {"fields": ("is_superuser", "is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "first_name",
                "last_name",
                "password1", "password2", "is_superuser", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
         ),
    )


admin.site.register(User, CustomUserAdmin)
