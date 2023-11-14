# Generated by Django 4.2.6 on 2023-11-14 09:29

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_affiliate_user_alter_customuser_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 14, 9, 29, 36, 281645, tzinfo=datetime.timezone.utc)),
        ),
    ]
