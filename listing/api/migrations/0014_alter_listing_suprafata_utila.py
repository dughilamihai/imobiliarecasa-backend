# Generated by Django 5.1.2 on 2024-12-16 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_listing_suprafata_utila'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='suprafata_utila',
            field=models.FloatField(blank=True, null=True, verbose_name='Suprafață utilă'),
        ),
    ]
