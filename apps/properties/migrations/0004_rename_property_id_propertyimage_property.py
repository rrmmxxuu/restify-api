# Generated by Django 4.1.7 on 2023-03-15 02:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_property_thumbnail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='propertyimage',
            old_name='property_id',
            new_name='property',
        ),
    ]
