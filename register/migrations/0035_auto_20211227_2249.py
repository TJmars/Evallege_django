# Generated by Django 3.1 on 2021-12-27 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0034_circle_user_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='administrator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='administrator', to=settings.AUTH_USER_MODEL, verbose_name='管理者'),
        ),
    ]