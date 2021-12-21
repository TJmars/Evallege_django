# Generated by Django 3.1 on 2021-12-15 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0028_auto_20211107_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='Attendance',
            field=models.TextField(blank=True, verbose_name='出席'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='contents',
            field=models.TextField(blank=True, verbose_name='講義内容・難易度'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='homework',
            field=models.TextField(blank=True, verbose_name='課題'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='others',
            field=models.TextField(blank=True, verbose_name='その他'),
        ),
    ]
