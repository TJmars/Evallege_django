# Generated by Django 3.1 on 2021-11-07 11:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0027_circle'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='image',
            field=models.FileField(blank=True, upload_to='circle_image/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png', 'HEIC'])], verbose_name='画像'),
        ),
        migrations.AlterField(
            model_name='circle',
            name='circle_password',
            field=models.CharField(max_length=20, verbose_name='パスワード'),
        ),
    ]
