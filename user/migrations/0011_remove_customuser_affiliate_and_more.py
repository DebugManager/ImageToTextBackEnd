# Generated by Django 4.2.6 on 2023-11-10 14:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_affiliate_customuser_payment_method_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='affiliate',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='affiliate_code',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 10, 14, 22, 14, 319942, tzinfo=datetime.timezone.utc)),
        ),
    ]
