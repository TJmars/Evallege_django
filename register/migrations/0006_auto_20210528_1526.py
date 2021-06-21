# Generated by Django 3.1 on 2021-05-28 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0005_auto_20210528_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='college_name',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='register.college', verbose_name='大学名'),
            preserve_default=False,
        ),
    ]
