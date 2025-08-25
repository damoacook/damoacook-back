from django.db import models

class GalleryImage(models.Model):
    title       = models.CharField('이미지 제목', max_length=255)
    image       = models.ImageField(
                    '갤러리 이미지 파일',
                    upload_to='gallery/%Y/%m/%d/',
                )
    description = models.CharField(
                    '간단 설명', max_length=255,
                    blank=True, null=True,
                )
    views       = models.PositiveIntegerField('조회수', default=0)
    uploaded_at = models.DateTimeField('업로드일시', auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = '갤러리 이미지'
        verbose_name_plural = '갤러리 이미지'

    def __str__(self):
        return self.title