# Generated by Django 5.1.2 on 2024-12-12 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_tag_listing_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='categories',
            field=models.ManyToManyField(related_name='tags', to='api.category'),
        ),
    ]
