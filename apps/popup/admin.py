from django.contrib import admin
from .models import PopupBanner

@admin.register(PopupBanner)
class PopupBannerAdmin(admin.ModelAdmin):
    list_display    = ('title', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter     = ('is_active',)
    search_fields   = ('title',)