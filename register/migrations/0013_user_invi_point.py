# Generated by Django 3.1 on 2021-07-03 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0012_user_invi_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='invi_point',
            field=models.IntegerField(default=0, verbose_name='被招待ポイント'),
        ),
    ]