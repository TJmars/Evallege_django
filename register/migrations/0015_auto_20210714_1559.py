# Generated by Django 3.1 on 2021-07-14 06:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0014_auto_20210703_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='input_invi_code',
            field=models.CharField(blank=True, max_length=200, verbose_name='招待コード'),
        ),
        migrations.CreateModel(
            name='Text_product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200, verbose_name='教科書名')),
                ('price', models.IntegerField(verbose_name='価格')),
                ('description', models.TextField(verbose_name='商品の詳細説明')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='出品日')),
                ('on_sale', models.BooleanField(default=True, verbose_name='販売中かチェック')),
                ('lecture', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='register.lecture', verbose_name='講義')),
                ('sale_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='出品者')),
            ],
        ),
    ]
