from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User, MerchantProfile, EmailVerificationToken, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ['email', 'is_staff', 'is_mail_verified', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_mail_verified', 'date_joined']
    search_fields = ['email']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_mail_verified', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'is_mail_verified'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']


@admin.register(MerchantProfile)
class MerchantProfileAdmin(ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']
    ordering = ['-created_at']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']
    ordering = ['-created_at']
