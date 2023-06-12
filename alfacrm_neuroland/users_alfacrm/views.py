import json
import os
import re
from datetime import timedelta

import requests
from django.conf import settings
from django.middleware.csrf import get_token
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import AlfaCRMUserSerializer, CitySerializer

from .models import AlfaCRMUser, City

load_dotenv()

api_key = os.getenv("API_KEY", default="api_key")
email_key = os.getenv("EMAIL", default="email")
TELEGRAM_BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN", default="telegram_bot_token"
)
TELEGRAM_BOT_USERNAME = os.environ.get(
    "TELEGRAM_BOT_USERNAME", default="telegram_bot_username"
)


def get_token():
    """Выполнение запроса для получения временного токена"""
    url = "https://evropa.s20.online/v2api/auth/login"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {"email": email_key, "api_key": api_key}

    response = requests.post(url, headers=headers, json=data)
    result = json.loads(response.text)

    if response.status_code != 200:
        raise Exception(result["name"] + " - " + result["message"])
    return result["token"]


@api_view(["POST"])
@permission_classes((AllowAny,))
def create_lead(request):
    token = get_token()
    name = request.data.get("name")
    phone = request.data.get("phone")
    email = request.data.get("email")
    city = request.data.get("city")
    password = request.data.get("password")
    referral_code = request.GET.get("referral_code")
    if not all([name, phone, email, password]):
        return Response(
            {"error": "Заполните все обязательные поля"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    email_regex = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    if not email_regex.match(email):
        return Response(
            {"error": "Некорректный формат email"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    phone_regex = re.compile(r"^\+7\d{10}$")
    if not phone_regex.match(phone):
        return Response(
            {"error": "Некорректный формат номера телефона"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    customer_data = {
        "name": name,
        "phone": [phone],
        "email": [email],
        "branch_ids": 7,
        "legal_type": 1,
        "is_study": 0,
    }
    customer_headers = {
        "Content-Type": "application/json",
        "X-ALFACRM-TOKEN": token,
    }
    customer_url = "https://evropa.s20.online/v2api/1/customer/create"
    response = requests.post(
        customer_url, headers=customer_headers, json=customer_data
    )
    if AlfaCRMUser.objects.filter(phone=phone).exists():
        return Response(
            {
                "error": "Пользователь с таким номером телефона "
                         "уже зарегистрирован"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if AlfaCRMUser.objects.filter(email=email).exists():
        return Response(
            {"error": "Пользователь с таким email уже зарегистрирован"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    city_id = request.data.get("city")
    city = None
    if city_id:
        try:
            city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            return Response(
                {"error": "Некорректный идентификатор города"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    if response.status_code == 200:
        user_data = {
            "name": name,
            "phone": phone,
            "email": email,
            "password": password,
        }
        if city:
            user_data["city"] = city
        if referral_code:
            try:
                referrer = AlfaCRMUser.objects.get(
                    referral_code=referral_code
                )
                user_data["referrer"] = referrer
                referrer.balance += settings.REFERRAL_BONUS_POINTS
                referrer.save()
            except AlfaCRMUser.DoesNotExist:
                return Response(
                    {"error": "Пользователь не сущетвует"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        user = AlfaCRMUser(**user_data)
        user.set_password(password)
        user.save()
        serializer = AlfaCRMUserSerializer(user)
        return Response(serializer.data, status=response.status_code)
    return Response(response.json(), status=response.status_code)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if email is not None and password is not None:
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                try:
                    user = AlfaCRMUser.objects.get(email=email)
                except AlfaCRMUser.DoesNotExist:
                    return Response(
                        {"error": "Пользователь не зарегистрирован"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"error": "Invalid email or phone format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)
                token.expires = timezone.now() + timedelta(seconds=600)
                token.save()
                return Response({"auth_token": token.key})
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RefreshTokenView(APIView):
    authentication_classes = (TokenAuthentication,)

    def post(self, request, format=None):
        token = request.auth
        if token is not None:
            try:
                Token.objects.get(key=token)
            except Token.DoesNotExist:
                return Response(
                    {"error": "Invalid token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = token.user
            if not user.is_active:
                return Response(
                    {"error": "User is inactive"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Token.objects.filter(key=token).delete()
            new_token = Token.objects.create(user=user)
            return Response({"auth_token": new_token.key})
        return Response(
            {"error": "Token is missing"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_user(request):
    referrer = request.user
    referral_code = referrer.referral_code
    invite_link = (
        f"{settings.BASE_URL}"
        f"{reverse('registration')}?referral_code={referral_code}"
    )
    return Response({"invite_link": invite_link})


@api_view(["GET"])
@csrf_exempt
def get_telegram_link(request):
    telegram_link = f"https://t.me/{TELEGRAM_BOT_USERNAME}"
    return Response({"telegram_link": telegram_link})
