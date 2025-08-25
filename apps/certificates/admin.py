from django.contrib import admin
from .models import Certificate, CertificateExamPlan

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug', 'jmcd']
    search_fields = ['slug', 'jmcd']
    prepopulated_fields = {"slug": ("jmcd",)}  # 슬러그 자동 생성은 jmcd 기준으로 설정

@admin.register(CertificateExamPlan)
class CertificateExamPlanAdmin(admin.ModelAdmin):
    list_display = ['certificate', 'impl_yy', 'impl_seq', 'qualgb_nm']
    list_filter = ['impl_yy', 'qualgb_nm']
    search_fields = ['description']