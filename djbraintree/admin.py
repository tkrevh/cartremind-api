# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import BTPlan, BTCurrentSubscription


@admin.register(BTPlan)
class BTPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_id', 'name', 'price')


@admin.register(BTCurrentSubscription)
class BTCurrentSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'customer_id', 'subscription_id',
        'plan_name', 'status', 'date_modified', 'date_created'
    )

    def get_queryset(self, request):
        return BTCurrentSubscription.objects.select_related('user', 'plan')

    def user_email(self, instance):
        return instance.user.email

    def plan_name(self, instance):
        return instance.plan.name
