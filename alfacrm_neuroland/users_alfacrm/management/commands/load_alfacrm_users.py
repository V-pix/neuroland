import requests
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from users_alfacrm.models import AlfaCRMUser
from users_alfacrm.views import get_token


class Command(BaseCommand):
    help = "Load users from Alfa CRM and register them in your application"

    def handle(self, *args, **options):
        token = get_token()
        url = "https://evropa.s20.online/v2api/7/customer/index"
        headers = {
            "X-ALFACRM-TOKEN": token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.request("POST", url, headers=headers)
        data = response.json()
        print(data)
        customers = data.get("items", [])
        print(customers)

        for customer in customers:
            print(customer)
            name = customer["name"]
            email = customer["email"][0] if customer["email"] else None
            phone = customer["phone"][0] if customer["phone"] else None
            balance = float(customer["balance_bonus"])
            try:
                user = AlfaCRMUser.objects.get(phone=phone)
            except AlfaCRMUser.DoesNotExist:
                try:
                    user = AlfaCRMUser.objects.get(email=email)
                except AlfaCRMUser.DoesNotExist:
                    user = None
            if user:
                user.balance += balance
                user.save()
            else:
                new_user = AlfaCRMUser.objects.create(
                    email=email,
                    username=get_random_string(length=15),
                    name=name,
                    phone=phone,
                    balance=balance
                )
                # Generate temporary password
                temp_password = get_random_string(length=10)
                new_user.set_password(temp_password)
                new_user.save()
                self.send_notification(new_user, temp_password)

    def send_notification(self, user, temp_password):
        subject = "Регистрация учетной записи"
        message = f"Добро пожаловать в наше приложение!\n\n" \
                  f"Ваша учетная запись была создана. " \
                  f"Временный пароль: {temp_password}\n" \
                  f"Пожалуйста, войдите в приложение с " \
                  f"использованием временного пароля " \
                  f"и измените его после входа.\n\n" \
                  f"С уважением,\n" \
                  f"Команда приложения"

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
