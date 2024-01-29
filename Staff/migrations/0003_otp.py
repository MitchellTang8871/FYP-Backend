# Generated by Django 4.2.6 on 2024-01-29 09:20

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Staff', '0002_log_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(max_length=6)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('validUntil', models.DateTimeField(default=datetime.datetime(2024, 1, 29, 9, 25, 44, 387060, tzinfo=datetime.timezone.utc))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
