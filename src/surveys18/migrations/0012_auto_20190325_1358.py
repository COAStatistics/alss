# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2019-03-25 05:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys18', '0011_auto_20180622_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='investigator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='surveys18', to=settings.AUTH_USER_MODEL, verbose_name='Investigator'),
        ),
    ]
