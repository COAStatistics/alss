# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-05-24 08:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys18', '0005_auto_20180524_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='longtermhire',
            name='month',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='surveys18.Month', verbose_name='Month'),
        ),
        migrations.AlterField(
            model_name='numberworkers',
            name='count',
            field=models.IntegerField(blank=True, null=True, verbose_name='C'),
        ),
    ]