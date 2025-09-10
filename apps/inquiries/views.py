from typing import cast, Any, Dict, Mapping
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from datetime import timedelta

from .models import Inquiry
from .serializers import InquirySerializer

logger = logging.getLogger(__name__)


class InquiryCreateView(APIView):
    throttle_scope = "inquiries"  # ▼ 스로틀 적용

    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ▼ 최근 2분 내 동일 phone+message 중복 차단
        vd = cast(Mapping[str, Any], serializer.validated_data)
        phone = str(vd.get("phone", ""))
        message = str(vd.get("message", ""))
        two_min_ago = timezone.now() - timedelta(minutes=2)
        if Inquiry.objects.filter(
            phone=phone, message=message, created_at__gte=two_min_ago
        ).exists():
            return Response(
                {"detail": "잠시 후 다시 시도해주세요."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

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
        reply_to = (
            [request.data["email"]]
            if isinstance(request.data, dict) and request.data.get("email")
            else None
        )

        payload: Dict[str, Any] = dict(serializer.data)
        inq_id = payload.get("id")

        # ▼ 커밋 후 발송 + 로깅
        def _send():
            try:
                sent = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=recipients,
                    reply_to=reply_to,
                ).send(fail_silently=False)
                payload["email_sent"] = bool(sent)
                logger.info(
                    "inquiry_email_sent",
                    extra={
                        "inquiry_id": inq_id,
                        "phone": phone,
                        "email_sent": bool(sent),
                    },
                )
            except Exception as e:
                payload["email_sent"] = False
                logger.exception(
                    "inquiry_email_fail",
                    extra={"inquiry_id": inq_id, "phone": phone, "error": str(e)},
                )

        transaction.on_commit(_send)
        return Response(payload, status=status.HTTP_201_CREATED)


class AdminInquiryListView(generics.ListAPIView):
    queryset = Inquiry.objects.order_by("-created_at")
    serializer_class = InquirySerializer
    permission_classes = [permissions.IsAdminUser]
