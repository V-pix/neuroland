# Generated by Django 3.2.18 on 2023-04-04 06:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0006_auto_20230404_0446"),
    ]

    operations = [
        migrations.AddField(
            model_name="partnervideo",
            name="partner_preview",
            field=models.ImageField(default=1, upload_to="partners_previews/"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="partnervideo",
            name="points",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Укажите количество баллов, "
                          "которое будет начисляться",
                verbose_name="Количество баллов",
            ),
        ),
        migrations.AlterField(
            model_name="partnervideo",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="uservideo",
            name="partner_video",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_videos",
                to="courses.partnervideo",
            ),
        ),
        migrations.AlterField(
            model_name="uservideo",
            name="video",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_videos",
                to="courses.video",
            ),
        ),
    ]
