# Generated by Django 3.2.18 on 2023-05-17 16:06

import django.contrib.auth.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_alfacrm', '0011_auto_20230502_0645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alfacrmuser',
            name='balance',
            field=models.IntegerField(
                default=0,
                verbose_name='Баланс пользователя'
            ),
        ),
        migrations.AlterField(
            model_name='alfacrmuser',
            name='city',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='users_alfacrm.city',
                verbose_name='Город пользователя'
            ),
        ),
        migrations.AlterField(
            model_name='alfacrmuser',
            name='referral_code',
            field=models.CharField(
                blank=True,
                max_length=10,
                unique=True,
                verbose_name='Реферальный код пользователя'
            ),
        ),
        migrations.AlterField(
            model_name='alfacrmuser',
            name='referrer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referrals',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Пригласивший пользователь'
            ),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.TextField(
                help_text='Укажите сообщение уведомления',
                verbose_name='Сообщение'
            ),
        ),
        migrations.AlterField(
            model_name='notification',
            name='title',
            field=models.CharField(
                help_text='Укажите заголовок уведомления',
                max_length=255,
                verbose_name='Заголовок'
            ),
        ),
    ]
