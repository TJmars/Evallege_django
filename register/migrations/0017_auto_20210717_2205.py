# Generated by Django 3.1 on 2021-07-17 13:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0016_auto_20210717_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='text_product',
            name='buy_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='buy_user', to=settings.AUTH_USER_MODEL, verbose_name='購入者'),
        ),
    ]
