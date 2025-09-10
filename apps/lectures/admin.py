from django.contrib import admin
from .models import Lecture


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "title",
        "start_date",
        "end_date",
        "capacity",
        "applied",
        "institution_name",
    )
    list_display_links = ("id", "title")
    search_fields = ("title", "tags", "institution_name", "description")
    list_filter = ("type", "start_date", "end_date")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
