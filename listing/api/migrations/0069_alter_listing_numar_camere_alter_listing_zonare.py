# Generated by Django 5.1.2 on 2025-02-27 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0068_alter_listing_numar_camere'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='numar_camere',
            field=models.IntegerField(blank=True, choices=[(1, '1 cameră'), (2, '2 camere'), (3, '3 camere'), (4, '4 camere'), (5, '5+ camere')], db_index=True, help_text='Se aplica doar pentru apartamente, case, vile, spatii comerciale.', null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='zonare',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Intravilan'), (1, 'Extravilan')], db_index=True, help_text='Zonarea poate fi intravilan, extravilan.', null=True),
        ),
    ]
