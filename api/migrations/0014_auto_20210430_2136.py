# Generated by Django 3.1 on 2021-04-30 15:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20210430_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 4, 30, 21, 36, 16, 40250)),
        ),
    ]
