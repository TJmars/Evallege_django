# Generated by Django 3.1 on 2021-07-22 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0017_auto_20210717_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='text_product',
            name='image',
            field=models.ImageField(default=1, upload_to='product_image/'),
            preserve_default=False,
        ),
    ]