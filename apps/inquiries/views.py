from typing import cast, Any
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status

from .models import Inquiry
from .serializers import InquirySerializer


class InquiryCreateView(APIView):
    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inquiry = cast(Inquiry, serializer.save())

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
        if isinstance(request.data, dict) and request.data.get("email"):
            reply_to = [request.data["email"]]

        email_sent = False
        try:
            EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients,
                reply_to=reply_to,
            ).send(fail_silently=False)
            email_sent = True
        except Exception:
            pass

        payload: dict[str, Any] = dict(serializer.data)
        payload["email_sent"] = email_sent
        return Response(payload, status=status.HTTP_201_CREATED)


class AdminInquiryListView(generics.ListAPIView):
    queryset = Inquiry.objects.order_by("-created_at")
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAdminUser]
