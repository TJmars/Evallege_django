# Generated by Django 3.1 on 2021-11-06 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0024_auto_20211106_2104'),
    ]

    operations = [
        migrations.AddField(
            model_name='text_product',
            name='url',
            field=models.URLField(default='', verbose_name='商品URL'),
        ),
    ]
