# Generated by Django 3.1 on 2021-05-29 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0007_lecturechat'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecturechat',
            name='chat_text',
            field=models.TextField(default=1, max_length=1000, verbose_name='コメント(空欄可)'),
            preserve_default=False,
        ),
    ]
