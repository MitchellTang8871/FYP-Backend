# Generated by Django 4.2.6 on 2024-03-04 07:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Staff', '0003_alter_otp_validuntil_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='myr',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='otp',
            name='validUntil',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 4, 7, 37, 4, 390418, tzinfo=datetime.timezone.utc)),
        ),
    ]
