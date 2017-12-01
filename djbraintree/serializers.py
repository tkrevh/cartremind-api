from rest_framework import serializers

from djbraintree.models import BTPlan, BTCurrentSubscription


class BTPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = BTPlan


class BTCurrentSubscriptionSerializer(serializers.ModelSerializer):

    price = serializers.SerializerMethodField()
    plan_id = serializers.SerializerMethodField()
    plan_name = serializers.SerializerMethodField()
    plan_description = serializers.SerializerMethodField()
    plan_price = serializers.SerializerMethodField()
    plan_currency = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    def get_price(self, instance):
        return instance.plan.price

    def get_plan_id(self, instance):
        return instance.plan.plan_id

    def get_plan_name(self, instance):
        return instance.plan.name

    def get_plan_price(self, instance):
        return instance.plan.price

    def get_plan_currency(self, instance):
        return instance.plan.currency_iso_code

    def get_plan_description(self, instance):
        return instance.plan.description

    def get_is_active(self, instance):
        return instance.status == 'Active'

    class Meta:
        model = BTCurrentSubscription
        fields = (
            'id', 'plan_id', 'plan_name', 'price', 'status', 'subscription_id',
            'plan_description', 'is_active', 'date_created', 'date_modified',
            'billing_period_start_date', 'billing_period_end_date', 'expire_at_period_end',
            'plan_price', 'plan_currency'
        )
        read_only_fields = (
            'id', 'plan_id', 'plan_name', 'price', 'status', 'subscription_id',
            'plan_description', 'is_active', 'date_created', 'date_modified',
            'billing_period_start_date', 'billing_period_end_date', 'expire_at_period_end',
            'plan_price', 'plan_currency'
        )

