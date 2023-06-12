# Generated by Django 3.2.18 on 2023-04-10 17:24

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users_alfacrm", "0004_auto_20230404_0446"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alfacrmuser",
            name="phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Укажите номер телефона пользователя",
                max_length=128,
                region=None,
                verbose_name="Номер телефона пользователя",
            ),
        ),
    ]