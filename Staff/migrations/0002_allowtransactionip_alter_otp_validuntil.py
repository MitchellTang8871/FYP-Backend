# Generated by Django 4.2.6 on 2024-03-05 08:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='allowTransactionIp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='otp',
            name='validUntil',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 5, 8, 45, 43, 96763, tzinfo=datetime.timezone.utc)),
        ),
    ]
