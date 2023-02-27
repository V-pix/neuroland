from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    USER = "user"
    ADMIN = "admin"

    USER_ROLES = (
        (USER, "Пользователь"),
        (ADMIN, "Администратор"),
    )

    role = models.CharField(
        verbose_name="Роль пользователя",
        help_text="Укажите роль пользователя",
        max_length=50,
        default=USER,
        choices=USER_ROLES,
    )
    phone_number = PhoneNumberField(
        verbose_name="Номер телефона пользователя",
        help_text="Укажите номер телефона пользователя",
        unique=True,
        null=False,
        blank=False,
    )
    email = models.EmailField(
        max_length=254,
        verbose_name="Адрес электронной почты",
        help_text="Укажите Email",
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        verbose_name="Логин пользователя",
        help_text="Укажите логин",
        unique=True,
    )
    first_name = models.TextField(
        max_length=150,
        verbose_name="Имя пользователя",
        help_text="Укажите имя",
    )
    last_name = models.TextField(
        max_length=150,
        verbose_name="Фамилия пользователя",
        help_text="Укажите фамилию",
    )
    password = models.CharField(
        max_length=150,
        verbose_name="Пароль пользователя",
        help_text="Придумайте пароль",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_user"
            )
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_superuser or self.role == "admin" or self.is_staff
