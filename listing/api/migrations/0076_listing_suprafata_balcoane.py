# Generated by Django 5.1.2 on 2025-03-01 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0075_listing_number_of_balconies'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='suprafata_balcoane',
            field=models.FloatField(blank=True, null=True, verbose_name='Suprafață balcoane'),
        ),
    ]
