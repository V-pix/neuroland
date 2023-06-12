# Generated by Django 3.2.18 on 2023-03-31 08:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0003_coupon_partner_usercoupon"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="partner",
            options={
                "verbose_name": "Партнер",
                "verbose_name_plural": "Партнеры"
            },
        ),
        migrations.RemoveField(
            model_name="partner",
            name="discount_coupon",
        ),
        migrations.AlterField(
            model_name="partner",
            name="name",
            field=models.CharField(
                max_length=255,
                verbose_name="Именование партнера"
            ),
        ),
        migrations.AlterField(
            model_name="partner",
            name="promo_video",
            field=models.URLField(
                blank=True, null=True, verbose_name="Промо видео партнера"
            ),
        ),
        migrations.CreateModel(
            name="PartnerVideo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "promo_video",
                    models.URLField(
                        blank=True,
                        null=True,
                        verbose_name="Промо видео партнера"
                    ),
                ),
                (
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="courses.partner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Промо-видео партнера",
                "verbose_name_plural": "Промо-видео партнеров",
            },
        ),
    ]
