from django.db import models

class PopupBanner(models.Model):
    title       = models.CharField('배너 제목', max_length=255)
    image       = models.ImageField(
        '팝업 이미지',
        upload_to='popup/%Y/%m/%d/',
        help_text='팝업에 표시될 이미지'
    )
    link_url    = models.URLField(
        '링크 URL',
        blank=True, null=True,
        help_text='배너 클릭 시 이동할 URL'
    )
    is_active   = models.BooleanField(
        '활성 여부',
        default=False,
        help_text='True인 배너만 화면에 표시 (단일 활성)'
    )
    created_at  = models.DateTimeField('생성일시', auto_now_add=True)
    updated_at  = models.DateTimeField('수정일시', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '팝업 배너'
        verbose_name_plural = '팝업 배너'

    def __str__(self):
        return self.title