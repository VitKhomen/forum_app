from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.core.mail import send_mail
from django.conf import settings

from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Зберігаємо в БД
            Feedback.objects.create(**data)

            # Відправляємо email
            try:
                send_mail(
                    subject=f"Фідбек: {data['subject']} від {data['name']}",
                    message=f"""
                    Від: {data['name']} ({data['email']})
                    Тема: {data['subject']}

                    Повідомлення:
                    {data['message']}
                    """,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email send error: {e}")

            return Response({"message": "Дякуємо за фідбек!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
