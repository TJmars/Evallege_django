# Generated by Django 3.1 on 2021-07-03 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0013_user_invi_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='input_invi_code',
            field=models.CharField(blank=True, max_length=200, verbose_name='入力した招待コード'),
        ),
        migrations.AlterField(
            model_name='user',
            name='invi_code',
            field=models.CharField(max_length=200, verbose_name='自分の招待コード'),
        ),
    ]