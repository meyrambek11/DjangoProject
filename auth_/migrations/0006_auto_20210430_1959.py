# Generated by Django 3.1 on 2021-04-30 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_', '0005_auto_20210430_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]