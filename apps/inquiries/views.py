from typing import cast
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status

# from twilio.rest import Client

from .models import Inquiry
from .serializers import InquirySerializer


class InquiryCreateView(APIView):
    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inquiry = cast(Inquiry, serializer.save())  # ✅ 타입 명시

        subject = f"[수강문의] {inquiry.name} 님으로부터"
        body = (
            "새 수강 문의가 접수되었습니다.\n\n"
            f"• 이름: {inquiry.name}\n"
            f"• 전화: {inquiry.phone}\n"
            f"• 접수시간: {inquiry.created_at:%Y-%m-%d %H:%M}\n\n"
            f"문의 내용:\n{inquiry.message}"
        )

        recipients = getattr(settings, "INQUIRY_TO_EMAILS", None) or [
            settings.ADMIN_EMAIL
        ]

        reply_to = None
        if hasattr(request.data, "get"):
            sender_email = request.data.get("email")
            if sender_email:
                reply_to = [sender_email]

        EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            reply_to=reply_to,
        ).send(fail_silently=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
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


class AdminInquiryListView(generics.ListAPIView):
    """
    GET /api/inquiries/admin/
    관리자 전용: 수강 문의 전체 조회
    """

    queryset = Inquiry.objects.order_by("-created_at")
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAdminUser]
