# Generated by Django 4.2.6 on 2023-11-14 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_affiliate_created_alter_customuser_joined'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='joined',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
