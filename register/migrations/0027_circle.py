# Generated by Django 3.1 on 2021-11-06 16:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0026_auto_20211106_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Circle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('circle_name', models.CharField(max_length=200, verbose_name='団体名')),
                ('genre', models.IntegerField(blank=True, choices=[(1, '球技'), (2, 'スポーツ'), (3, '学問'), (4, '音楽'), (5, 'その他')], verbose_name='ジャンル')),
                ('message', models.TextField(blank=True, verbose_name='活動紹介、メッセージ')),
                ('day_place', models.TextField(blank=True, verbose_name='活動日/場所')),
                ('member_num', models.TextField(blank=True, verbose_name='所属人数')),
                ('cost', models.TextField(blank=True, verbose_name='活動費用')),
                ('sns_mail', models.TextField(blank=True, verbose_name='SNS/連絡先')),
                ('circle_id', models.IntegerField(verbose_name='ID')),
                ('circle_password', models.CharField(max_length=20, verbose_name='教科書名')),
                ('administrator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='管理者')),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='register.college', verbose_name='大学名')),
            ],
        ),
    ]
