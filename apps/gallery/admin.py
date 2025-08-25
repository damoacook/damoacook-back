from django.contrib import admin
from .models import GalleryImage

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display    = ('title', 'views', 'uploaded_at')
    readonly_fields = ('views', 'uploaded_at')
    search_fields   = ('title', 'description')