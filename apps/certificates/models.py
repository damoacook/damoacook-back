from django.db import models

class Certificate(models.Model):
    name           = models.CharField(max_length=255)
    description    = models.TextField()
    exam_schedule  = models.TextField(help_text='시험 일정 또는 안내')
    image          = models.ImageField(
        upload_to='certificates/%Y/%m/%d/',
        blank=True, null=True,
        help_text='자격증 상세 이미지 (선택)'
    )

    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = '자격증 안내'
        verbose_name_plural = '자격증 안내'

    def __str__(self):
        return self.name