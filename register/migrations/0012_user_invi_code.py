# Generated by Django 3.1 on 2021-06-29 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0011_auto_20210625_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='invi_code',
            field=models.CharField(default=1, max_length=200, verbose_name='招待コード'),
            preserve_default=False,
        ),
    ]
