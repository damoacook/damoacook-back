from rest_framework import serializers
from .models import Certificate, CertificateExamPlan

class CertificateExamPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateExamPlan
        fields = '__all__'