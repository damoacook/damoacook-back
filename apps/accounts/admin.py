from django.contrib import admin
from django.contrib.auth import get_user_model

AdminUser = get_user_model()


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_staff", "is_active", "last_login")
    list_display_links = ("id", "email")
    search_fields = ("email",)
    list_filter = ("is_staff", "is_active")
    ordering = ("-id",)
    readonly_fields = ("last_login",)
