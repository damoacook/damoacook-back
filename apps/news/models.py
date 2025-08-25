from django.db import models

class News(models.Model):
    title       = models.CharField(max_length=255)
    content     = models.TextField()
    views       = models.PositiveIntegerField(default=0)
    image       = models.ImageField(
        upload_to='news/',
        blank=True,
        null=True,
        help_text='뉴스 대표 이미지 (선택)'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = '공지·소식'
        verbose_name_plural = '공지·소식'

    def __str__(self):
        return self.title