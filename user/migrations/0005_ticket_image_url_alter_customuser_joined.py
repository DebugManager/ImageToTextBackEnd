# Generated by Django 4.2.6 on 2023-10-31 14:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_customuser_joined_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 31, 14, 33, 7, 232711, tzinfo=datetime.timezone.utc)),
        ),
    ]
