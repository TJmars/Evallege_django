# Generated by Django 3.1 on 2021-12-17 02:46

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0029_auto_20211215_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(verbose_name='タイトル')),
                ('contents', models.TextField(verbose_name='コンテンツ')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='投稿日')),
                ('image', models.FileField(blank=True, upload_to='board_images/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png', 'HEIC'])], verbose_name='画像')),
                ('good', models.IntegerField(default=0, verbose_name='いいね')),
                ('circle', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='register.circle', verbose_name='サークル')),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='register.college', verbose_name='大学')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='投稿者')),
            ],
        ),
    ]