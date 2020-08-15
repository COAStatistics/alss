# Generated by Django 2.2.14 on 2020-08-15 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys20', '0003_auto_20200527_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='new_type',
            field=models.IntegerField(blank=True, choices=[(1, 'Crop'), (2, 'Animal')], null=True, verbose_name='Product Type'),
        ),
        migrations.AddField(
            model_name='loss',
            name='new_type',
            field=models.IntegerField(blank=True, choices=[(1, 'Crop'), (2, 'Animal')], null=True, verbose_name='Product Type'),
        ),
        migrations.AddField(
            model_name='unit',
            name='new_type',
            field=models.IntegerField(blank=True, choices=[(1, 'Crop'), (2, 'Animal')], null=True, verbose_name='Product Type'),
        ),
    ]
