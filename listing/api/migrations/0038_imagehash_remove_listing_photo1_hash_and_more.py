# Generated by Django 5.1.2 on 2024-12-28 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_alter_listing_buyer_commission'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageHash',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_value', models.CharField(max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo1_hash',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo2_hash',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo3_hash',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo4_hash',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo5_hash',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo6_hash',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo7_hash',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo8_hash',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='photo9_hash',
        ),
    ]
