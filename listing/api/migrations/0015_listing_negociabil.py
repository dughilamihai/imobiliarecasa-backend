# Generated by Django 5.1.2 on 2024-12-16 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_listing_suprafata_utila'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='negociabil',
            field=models.BooleanField(default=False),
        ),
    ]