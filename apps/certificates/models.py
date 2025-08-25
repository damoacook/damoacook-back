# certificates/models.py

from django.db import models

class Certificate(models.Model):
    jmcd = models.CharField(max_length=10, blank=True, null=True, help_text="Q-Net 종목코드")
    slug = models.SlugField(unique=True, help_text="URL 식별용 슬러그 (예: hansik)")

    def __str__(self):
        return self.slug


class CertificateExamPlan(models.Model):
    QUAL_GB_CHOICES = [
        ('T', '국가기술자격'),
        ('C', '과정평가형자격'),
        ('W', '일학습병행자격'),
        ('S', '국가전문자격'),
    ]

    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='exam_plans')
    impl_yy = models.IntegerField(help_text="시행년도")
    impl_seq = models.IntegerField(help_text="시행회차")
    qualgb_cd = models.CharField(max_length=2, choices=QUAL_GB_CHOICES)
    qualgb_nm = models.CharField(max_length=50)
    description = models.TextField()

    # 필기시험
    doc_reg_start_dt = models.DateField()
    doc_reg_end_dt = models.DateField()
    doc_exam_start_dt = models.DateField()
    doc_exam_end_dt = models.DateField()
    doc_pass_dt = models.DateField()

    # 실기시험
    prac_reg_start_dt = models.DateField()
    prac_reg_end_dt = models.DateField()
    prac_exam_start_dt = models.DateField()
    prac_exam_end_dt = models.DateField()
    prac_pass_dt = models.DateField()

    class Meta:
        ordering = ['impl_yy', 'impl_seq']

    def __str__(self):
        return f"{self.certificate.slug} - {self.impl_yy}년 {self.impl_seq}회"
