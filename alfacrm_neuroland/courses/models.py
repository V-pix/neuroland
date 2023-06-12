from django.core.exceptions import ValidationError
from django.db import models

from users_alfacrm.models import AlfaCRMUser


class Direction(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название направления",
        help_text="Укажите название направления",
    )
    about_direction = models.TextField(
        verbose_name="Описание направления",
        help_text="Укажите описание направления",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Направление курсов"
        verbose_name_plural = "Направления курсов"

    def __str__(self) -> str:
        return self.name


class Course(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    description = models.TextField(
        verbose_name="Описание курса",
        help_text="Укажите описание курса",
    )
    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE,
        verbose_name="Направление",
        help_text="Выберите направление",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def viewed_by_user(self, user):
        return self.courseviews.filter(user=user).exists()

    def __str__(self) -> str:
        return self.title


class Video(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="videos",
        null=True,
        blank=True,
        verbose_name="Курс",
        help_text="Если это видео урок, то укажите, к какому курсу "
        "относится видео",
    )
    preview = models.ImageField(
        verbose_name="Превью видео",
        help_text="Добавьте превью-картинку",
        upload_to="previews/",
    )
    duration = models.DurationField(
        verbose_name="Длительность видео",
        help_text="Укажите длительность видео",
    )
    video_url = models.URLField(
        verbose_name="Ссылка на видео",
        help_text="Укажите ссылку на видео",
    )
    points = models.PositiveIntegerField(
        verbose_name="Количество баллов",
        help_text="Укажите количество баллов, которое будет "
        "начисляться за просмотр видео",
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        max_length=100,
        verbose_name="Описание видео",
        help_text="Укажите описание видео",
    )

    class Meta:
        verbose_name = "Видео для курсов и купонов Нейроленда"
        verbose_name_plural = "Видео для курсов и купонов Нейроленда"

    def __str__(self) -> str:
        return self.description


class Partner(models.Model):
    name = models.CharField(
        verbose_name="Именование партнера", max_length=255
    )

    class Meta:
        verbose_name = "Партнер и промо-видео партнера"
        verbose_name_plural = "Партнеры и промо-видео партнеров"

    def __str__(self) -> str:
        return self.name


class PartnerVideo(models.Model):
    id = models.AutoField(primary_key=True)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name="Партнер",
    )
    promo_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Ссылка на промо-видео партнера",
        help_text="Укажите ссылку на промо-видео партнера",
    )
    points = models.PositiveIntegerField(
        verbose_name="Количество баллов",
        help_text="Укажите количество баллов, которое будет "
        "начисляться за просмотр",
        default=0,
    )
    description = models.TextField(
        verbose_name="Описание видео",
        help_text="Укажите описание видео",
    )
    partner_preview = models.ImageField(
        verbose_name="Превью видео",
        help_text="Добавьте превью-картинку",
        upload_to="partners_previews/",
    )

    class Meta:
        verbose_name = "Промо-видео партнера"
        verbose_name_plural = "Промо-видео партнеров"

    def __str__(self) -> str:
        return self.description


class UserVideo(models.Model):
    user = models.ForeignKey(AlfaCRMUser, on_delete=models.CASCADE)
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="user_videos",
        null=True,
        blank=True,
    )
    viewed = models.BooleanField(default=False)
    partner_video = models.ForeignKey(
        PartnerVideo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        to_field="id",
        related_name="user_videos",
    )

    class Meta:
        verbose_name = "Просмотренное видео"
        verbose_name_plural = "Просмотренные видео"


class Coupon(models.Model):
    COUPON_TYPES = [
        ("own", "Свой"),
        ("partner", "Партнерский"),
    ]
    coupon_type = models.CharField(
        max_length=255,
        choices=COUPON_TYPES,
        verbose_name="Тип купона",
        help_text="Выберите тип купона: Свой - Нейроленда или Партнерский",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название купона",
        help_text="Укажите название купона",
    )
    description = models.TextField(verbose_name="Описание купона")
    points_required = models.PositiveIntegerField(
        verbose_name="Стоимость купона в баллах"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество оставшихся купонов",
        default=0,
        null=True,
        blank=True,
    )
    image = models.ImageField(
        upload_to="coupons/", verbose_name="Изображение купона"
    )
    video_coupone = models.ForeignKey(
        Video,
        on_delete=models.SET_NULL,
        related_name="coupone_videos",
        null=True,
        blank=True,
        verbose_name="Видео для своего купона",
        help_text="Заполните это поле, если купон свой - Нейроленда",
    )
    video_coupone_partner = models.ForeignKey(
        PartnerVideo,
        on_delete=models.SET_NULL,
        related_name="coupone_videos",
        null=True,
        blank=True,
        verbose_name="Видео для партнерского купона",
        help_text="Заполните это поле, если купон партерский",
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name="coupons",
        null=True,
        blank=True,
        verbose_name="Партнер",
        help_text="Заполните это поле, если купон партерский",
    )
    partner_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Название компании партнера",
        help_text="Заполните это поле, если купон партерский",
    )

    class Meta:
        verbose_name = "Купон"
        verbose_name_plural = "Купоны"

    def clean(self):
        if self.coupon_type == "own" and (
            self.partner or self.partner_name or self.video_coupone_partner
        ):
            raise ValidationError(
                "Купоны своей компании не могут содержать поля партнер, "
                "название компании партнера и видео партнера"
            )
        super().clean()
        if self.coupon_type == "partner" and self.video_coupone:
            raise ValidationError(
                "Купоны партнеров не могут содержать поле видео своего купона"
            )
        super().clean()

    def __str__(self) -> str:
        return self.title


class UserCoupon(models.Model):
    user = models.ForeignKey(
        AlfaCRMUser,
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        help_text="Укажите клиента, которому хотите добавить купон",
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        verbose_name="Купон",
        help_text="Выберите купон",
    )
    redeemed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата и время получения купона"
    )

    class Meta:
        verbose_name = "Купон пользователя"
        verbose_name_plural = (
            "Купоны пользователей и списание баллов за " "купоны"
        )
