# Generated by Django 3.2.18 on 2023-05-03 14:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_auto_20230501_1354'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partnervideo',
            old_name='promo_video',
            new_name='promo_url',
        ),
        migrations.AddField(
            model_name='coupon',
            name='video_coupone_partner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='coupone_videos',
                to='courses.partnervideo',
                verbose_name='Видео для партнерского купона'
            ),
        ),
        migrations.AddField(
            model_name='partnervideo',
            name='description',
            field=models.TextField(
                default=1,
                help_text='Укажите описание видео',
                verbose_name='Описание видео'
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coupon',
            name='video_coupone',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='coupone_videos',
                to='courses.video',
                verbose_name='Видео для своего купона'
            ),
        ),
        migrations.AlterField(
            model_name='video',
            name='description',
            field=models.TextField(
                help_text='Укажите описание видео',
                max_length=100,
                verbose_name='Описание видео'
            ),
        ),
    ]
