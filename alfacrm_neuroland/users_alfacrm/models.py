import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Coordinaties(models.Model):
    lat = models.CharField(max_length=255)
    lon = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Latitude: {self.lat}, Longitude: {self.lon}"


class City(models.Model):
    coordinaties = models.OneToOneField(
        Coordinaties, on_delete=models.CASCADE
    )
    district = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    population = models.IntegerField()
    subject = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class AlfaCRMUser(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone"]
    name = models.CharField(
        max_length=150,
        verbose_name="Имя пользователя",
        help_text="Укажите имя",
        unique=False,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        max_length=254,
        verbose_name="Адрес электронной почты",
        help_text="Укажите Email",
        unique=True,
        blank=False,
        null=False,
    )
    phone = PhoneNumberField(
        verbose_name="Номер телефона пользователя",
        help_text="Укажите номер телефона пользователя",
    )
    branch_ids = models.CharField(max_length=255)
    password = models.CharField(
        max_length=150,
        verbose_name="Пароль пользователя",
        help_text="Придумайте пароль",
        blank=False,
        null=False,
    )
    avatar = models.ImageField(
        verbose_name="Аватарка",
        upload_to="avatars/",
        null=True,
        blank=True,
    )
    balance = models.IntegerField(
        default=0,
        verbose_name="Баланс пользователя",
    )
    referral_code = models.CharField(
        max_length=10,
        blank=True,
        unique=True,
        verbose_name="Реферальный код пользователя",
        help_text="Реферальный код сгенерируется автоматически "
                  "после сохранения пользователя",
    )
    referrer = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals",
        verbose_name="Пригласивший пользователь",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Город пользователя",
    )

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.name


class Notification(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок",
        help_text="Укажите заголовок уведомления",
    )
    message = models.TextField(
        verbose_name="Сообщение",
        help_text="Укажите сообщение уведомления",
    )

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self) -> str:
        return self.title


class UserToken(models.Model):
    user = models.ForeignKey(
        AlfaCRMUser,
        on_delete=models.CASCADE,
        related_name="tokens"
    )
    fcm_token = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.fcm_token}'
