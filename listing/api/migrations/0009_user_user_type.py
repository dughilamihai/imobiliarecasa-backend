# Generated by Django 5.1.2 on 2024-12-04 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_user_first_name_alter_user_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('person', 'Persoană Fizică'), ('company', 'Companie')], default='person', max_length=10),
        ),
    ]
