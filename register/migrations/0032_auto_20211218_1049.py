# Generated by Django 3.1 on 2021-12-18 01:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0031_auto_20211217_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='user',
        ),
        migrations.AddField(
            model_name='board',
            name='good_user',
            field=models.ManyToManyField(blank=True, null=True, related_name='good_user', to=settings.AUTH_USER_MODEL, verbose_name='いいねしたユーザー'),
        ),
        migrations.AddField(
            model_name='board',
            name='post_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='post_user', to=settings.AUTH_USER_MODEL, verbose_name='投稿者'),
        ),
    ]
