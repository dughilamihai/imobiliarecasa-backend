# Generated by Django 5.1.2 on 2025-02-27 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0064_alter_listing_number_of_floors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='compartimentare',
            field=models.SmallIntegerField(choices=[(0, 'Decomandat'), (1, 'Semidecomandat'), (2, 'Nedecomandat'), (3, 'Circular')], db_index=True, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='floor',
            field=models.SmallIntegerField(choices=[(0, 'Demisol'), (1, 'Parter'), (2, 'Etaj 1'), (3, 'Etaj 2'), (4, 'Etaj 3'), (5, 'Etaj 4'), (6, 'Etaj 5'), (7, 'Etaj 6'), (8, 'Etaj 7'), (9, 'Etaj 8'), (10, 'Etaj 9'), (11, 'Etaj 10'), (12, 'Etaj 11'), (13, 'Etaj 12'), (14, 'Etaj 13'), (15, 'Etaj 14'), (16, 'Etaj 15'), (17, 'Etaj 16'), (18, 'Etaj 17'), (19, 'Etaj 18'), (20, 'Etaj 19'), (21, 'Etaj 20'), (22, 'Ultimul etaj'), (23, 'Mansardă')], db_index=True, default=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='foundation_type',
            field=models.IntegerField(choices=[(0, 'Parter'), (1, 'Subsol + Parter'), (2, 'Demisol + Parter')], db_index=True, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='numar_camere',
            field=models.IntegerField(choices=[(1, '1 cameră'), (2, '2 camere'), (3, '3 camere'), (4, '4 camere'), (5, '5+ camere')], db_index=True, default=1, help_text='Se aplica doar pentru apartamente, case, vile, spatii comerciale.'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='number_of_bathrooms',
            field=models.SmallIntegerField(choices=[(0, 'Fără baie'), (1, '1 baie'), (2, '2 băi'), (3, '3 sau mai multe băi')], db_index=True, default=1, help_text='Se aplica doar pentru apartamente, case, vile, spatii comerciale, pensiuni și hoteluri.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='number_of_floors',
            field=models.PositiveIntegerField(default=11),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='year_of_construction',
            field=models.IntegerField(default=1988, help_text='Year of construction'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='listing',
            name='zonare',
            field=models.SmallIntegerField(choices=[(0, 'Intravilan'), (1, 'Extravilan')], db_index=True, default=0, help_text='Zonarea poate fi intravilan, extravilan.'),
            preserve_default=False,
        ),
    ]
