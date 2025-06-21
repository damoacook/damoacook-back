from django.db import models

class Lecture(models.Model):
    # 공통 필드
    LECTURE_TYPE_CHOICES = [
        ('academy', '학원 강의'),
        ('hrd', 'HRD-Net 강의'),
    ]
    type = models.CharField(max_length=10, choices=LECTURE_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='lectures/', null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 학원 강의 전용 필드
    day_of_week = models.CharField(max_length=50, blank=True, null=True)  # 예: 월/수/금
    time = models.CharField(max_length=50, blank=True, null=True)         # 예: 오후 2시~4시
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    applied = models.PositiveIntegerField(default=0)

    # HRD 강의 전용 필드
    process_id = models.CharField(max_length=100, null=True, blank=True)  # 과정 ID
    apply_url = models.URLField(max_length=500, null=True, blank=True)    # 수강신청 URL
    institution_name = models.CharField(max_length=255, null=True, blank=True)  # 교육기관명

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"
