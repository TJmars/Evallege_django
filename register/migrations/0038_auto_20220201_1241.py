# Generated by Django 3.1 on 2022-02-01 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0037_auto_20220201_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lectureeva',
            name='everyweek_time',
            field=models.IntegerField(verbose_name='課題/テスト勉強時間(毎週)'),
        ),
        migrations.AlterField(
            model_name='lectureeva',
            name='last_time',
            field=models.IntegerField(verbose_name='課題/テスト勉強時間(毎週)'),
        ),
    ]