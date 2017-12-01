# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-22 00:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BTCurrentSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=256)),
                ('subscription_id', models.CharField(max_length=256)),
                ('status', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='BTPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('plan_id', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('billing_frequency', models.PositiveIntegerField()),
                ('currency_iso_code', models.CharField(max_length=5)),
                ('description', models.CharField(max_length=256)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('trial_duration', models.PositiveIntegerField(blank=True, null=True)),
                ('trial_duration_unit', models.CharField(max_length=5)),
                ('trial_period', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Braintree Plan',
                'verbose_name_plural': 'Braintree Plans',
            },
        ),
        migrations.AddField(
            model_name='btcurrentsubscription',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='btsubscriptions', to='djbraintree.BTPlan'),
        ),
        migrations.AddField(
            model_name='btcurrentsubscription',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='btsubscription', to=settings.AUTH_USER_MODEL),
        ),
    ]
