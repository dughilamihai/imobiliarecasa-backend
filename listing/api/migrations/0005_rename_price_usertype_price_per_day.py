# Generated by Django 5.1.2 on 2024-12-02 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_usertype_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usertype',
            old_name='price',
            new_name='price_per_day',
        ),
    ]
