# Generated by Django 5.1.2 on 2024-12-08 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='valability_end_date',
            field=models.DateField(blank=True, help_text='Data până la care anunțul este valid.', null=True),
        ),
    ]
