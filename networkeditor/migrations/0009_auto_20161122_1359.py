# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-22 20:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networkeditor', '0008_auto_20161122_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networkconn',
            name='LatLongx',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='networkconn',
            name='LatLongy',
            field=models.FloatField(null=True),
        ),
    ]
