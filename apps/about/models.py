from django.db import models

class About(models.Model):
    # 대표 인사말
    greeting        = models.TextField('대표 인사말')
    # 학원 비전
    vision          = models.TextField('학원 비전')
    # 학원 찾아오는 길 (도로명 주소)
    address         = models.CharField('학원 찾아오는 길', max_length=255)
    # 대표 번호
    phone           = models.CharField('대표 번호', max_length=50)
    # 운영 시간
    opening_hours   = models.CharField('운영 시간', max_length=100)
    # 지도용 좌표 (선택)
    latitude        = models.DecimalField('위도', max_digits=9, decimal_places=6, blank=True, null=True)
    longitude       = models.DecimalField('경도', max_digits=9, decimal_places=6, blank=True, null=True)
    # 대표 이미지 (선택)
    image           = models.ImageField(
                        '대표 이미지',
                        upload_to='about/%Y/%m/%d/',
                        blank=True, null=True
                      )
    # 최종 수정일시
    updated_at      = models.DateTimeField('최종 수정일시', auto_now=True)

    class Meta:
        verbose_name = '학원 소개'
        verbose_name_plural = '학원 소개'

    def __str__(self):
        return "학원 소개 정보"