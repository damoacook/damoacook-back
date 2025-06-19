from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
# from twilio.rest import Client

from .models import Inquiry
from .serializers import InquirySerializer


class InquiryCreateView(APIView):
    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        inquiry = serializer.save()

        # ─── 이메일 발송 ───
        subject = f"[수강문의] {inquiry.name} 님으로부터"
        message = (
            f"새 수강 문의가 들어왔습니다.\n\n"
            f"• 이름: {inquiry.name}\n"
            f"• 전화: {inquiry.phone}\n"
            f"• 시간: {inquiry.created_at:%Y-%m-%d %H:%M}\n\n"
            f"문의 내용:\n{inquiry.message}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        # ──────────────────────

        # ─── SMS 발송 ───
        # client = Client(
        #     settings.TWILIO_ACCOUNT_SID,
        #     settings.TWILIO_AUTH_TOKEN
        # )
        # sms_body = (
        #     f"[수강문의]\n"
        #     f"이름: {inquiry.name}\n"
        #     f"전화: {inquiry.phone}\n"
        #     f"내용: {inquiry.message}"
        # )
        # client.messages.create(
        #     body=sms_body,
        #     from_=settings.TWILIO_FROM_NUMBER,
        #     to=settings.TWILIO_ADMIN_NUMBER
        # )
        # ──────────────

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AdminInquiryListView(generics.ListAPIView):
    """
    GET /api/inquiries/admin/
    관리자 전용: 수강 문의 전체 조회
    """
    queryset = Inquiry.objects.order_by('-created_at')
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAdminUser]