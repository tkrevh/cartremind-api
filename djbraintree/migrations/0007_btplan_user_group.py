# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-23 21:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('djbraintree', '0006_auto_20171123_2225'),
    ]

    operations = [
        migrations.AddField(
            model_name='btplan',
            name='user_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group'),
        ),
    ]
