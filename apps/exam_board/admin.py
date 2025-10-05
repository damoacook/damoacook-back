from django.contrib import admin
from .models import ExamPost, Attachment


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


@admin.register(ExamPost)
class ExamPostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "is_pinned", "view_count", "created_at")
    list_filter = ("is_pinned", "created_at")
    search_fields = ("title", "content", "author__username")
    inlines = [AttachmentInline]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "original_name", "kind", "size", "uploaded_at")
    search_fields = ("original_name", "post__title")
