from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(User)

# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     """
#     Custom admin configuration for the User model.
#     Extends Django's UserAdmin to work with email-based authentication.
#     """
#     model = User

#     # Fields to display in the user list view
#     list_display = ['email', 'is_active', 'is_staff']

#     # Filters available in the right sidebar
#     list_filter = ['is_active', 'is_staff']

#     # Fields that can be searched
#     search_fields = ['email']

#     # Default ordering for the list view
#     ordering = ['email']

    # Fieldsets for the user change form
    # fieldsets = (
    #     (None, {'fields': ('email', 'password')}),
    #     ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    #     ('Important dates', {'fields': ('last_login',)}),
    # )

    # Fieldsets for the user creation form
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
    #     }),
    # )
