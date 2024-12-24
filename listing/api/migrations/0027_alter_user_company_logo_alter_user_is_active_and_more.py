# Generated by Django 5.1.2 on 2024-12-24 20:29

import django_resized.forms
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_user_company_logo_user_company_logo_hash_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='company_logo',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='WEBP', keep_meta=True, null=True, quality=80, scale=None, size=[240, 60], upload_to='company_logos'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='WEBP', keep_meta=True, null=True, quality=80, scale=None, size=[200, 200], upload_to='profile_pictures'),
        ),
    ]