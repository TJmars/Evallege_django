# Generated by Django 3.1 on 2021-12-19 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0032_auto_20211218_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='status_num',
            field=models.IntegerField(default=0, verbose_name='ステータス'),
        ),
    ]
