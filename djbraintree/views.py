# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import braintree
from django.conf import settings
from django.shortcuts import render
import logging
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, generics, mixins, views, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import serializers
from django.core.mail import EmailMessage

from djbraintree.models import BTPlan, BTCurrentSubscription
from djbraintree.serializers import BTPlanSerializer


logger = logging.getLogger(__name__)


# Create your views here.
class BTClientTokenView(views.APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        payload = {
            'customer_id': user.id
        }
        # data = {'client_token': braintree.ClientToken.generate(payload)}
        data = {'client_token': braintree.ClientToken.generate()}
        return Response(data)


class BTPlansListView(views.APIView):

    def get(self, request):
        qs = BTPlan.objects.all()
        return Response(
            data={
                'plans': BTPlanSerializer(qs, many=True).data
            }
        )

def send_error_email(subject, body):
    for admin in settings.ADMINS:
        email = EmailMessage(subject,
                             body,
                             settings.ADMINS[0][1],
                             [admin[1]])
        email.send()


class BTSubscribeView(views.APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        logger.debug(
            'Received activate subscription request. '
            'User: {}. Request data: {}'.format(user, request.data)
        )

        if not 'payment_method_nonce' in request.data:
            logger.warning('Received checkout request without '
                           'payment_method_nonce. User: {}. '
                           'Request data: {}'.format(
                user, request.data))
            return Response(
                data={
                    'error': 'Payment nonce not specified'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not 'plan' in request.data:
            logger.warning(
                'Received checkout request without subscription plan. '
                'User: {}. Request data: {}'.format(user, request.data))
            return Response(
                data={
                    'error': 'Subscription plan not specified'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        payment_nonce = request.data['payment_method_nonce']
        subscription_plan = request.data['plan']

        plan = BTPlan.objects.get(name=subscription_plan)

        user_has_subscription = user.btsubscription.exists()
        if user_has_subscription:
            btsubscription = user.btsubscription.first()
        else:
            btsubscription = None

        if user_has_subscription and btsubscription.is_active:
            # we already have a customer in BT for this user
            try:
                customer = braintree.Customer.find(btsubscription.customer_id)
            except braintree.exceptions.not_found_error.NotFoundError:
                error_msg = u'Customer for user {} {} ({}) could not be found on Braintree' \
                    .format(user.first_name, user.last_name, user.email)
                logger.error('[BTSubscribeView] {}'.format(error_msg))
                send_error_email('Failed to find Braintree customer', error_msg)
                return Response(
                    data={
                        'error': 'Failed to find customer on Braintree'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = braintree.PaymentMethod.create({
                'customer_id': btsubscription.customer_id,
                'payment_method_nonce': payment_nonce,
                'options': {
                    'make_default': True,
                    'verify_card': True,
                }
            })

            if result.is_success:
                # TODO - check this
                payment_method_token = result.customer.payment_methods[0].token
            else:
                payment_method_token = customer.payment_methods[0].token

            result = braintree.Subscription.update(
                btsubscription.subscription_id,
                {
                    'payment_method_token': payment_method_token,
                    'plan_id': subscription_plan
                }
            )
            if not result.is_success:
                error_msg = u'Subscription for user {} {} ({}) ' \
                            u'could not be updated'.format(
                    user.first_name, user.last_name, user.email
                )
                logger.error('[BTSubscribeView] {}'.format(error_msg))
                send_error_email('Failed to update Braintree subscription', error_msg)
                return Response(
                    data={
                        'error': 'Failed to update existing subscription on Braintree'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                logger.info('[BTSubscribeView] successfully updated subscription for '
                            'user {} to plan {} '.format(user.email, subscription_plan))
                # remove user from old group
                btsubscription.plan.user_group.user_set.remove(user)
                # add user to new one
                plan.user_group.user_set.remove(user)
                btsubscription.update_from_subscription(
                    plan=plan,
                    subscription=result.subscription,
                    save=True
                )

        else:
            # here we have inactive btsubscription
            if btsubscription:
                # Fetch existing Braintree customer
                try:
                    customer = braintree.Customer.find(btsubscription.customer_id)
                except braintree.exceptions.not_found_error.NotFoundError:
                    error_msg = u'Customer for user {} {} ({}) could not be found on Braintree'\
                        .format(user.first_name, user.last_name, user.email)
                    logger.error('[BTSubscribeView] {}'.format(error_msg))
                    send_error_email('Failed to find Braintree customer', error_msg)
                    return Response(
                        data={
                            'error': 'Failed to find customer on Braintree'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                result = braintree.Subscription.create({
                    "payment_method_token": customer.payment_methods[0].token,
                    "plan_id": plan.plan_id,
                })

                if result.is_success:
                    logger.info('[BTSubscribeView] successfully created subscription for '
                                'user {} to plan {} for amount of ${}'.format(
                        user.email, subscription_plan, plan.price
                    ))

                    # remove user from old group
                    btsubscription.plan.user_group.user_set.remove(user)
                    # add user to new one
                    plan.user_group.user_set.remove(user)

                    # user.activate
                    btsubscription.update_from_subscription(
                        plan=plan,
                        subscription=result.subscription,
                        save=True
                    )

                    # Return success
                    content = {
                        'result': "Successfuly activated subscription"
                    }
                    return Response(content, status=status.HTTP_200_OK)
                else:
                    error_msg = u'Subscription for user {} {} ({}) ' \
                                u'could not be created'.format(
                        user.first_name, user.last_name, user.email
                    )
                    logger.error('[BTSubscribeView] {}'.format(error_msg))
                    send_error_email('Failed to create Braintree subscription', error_msg)
                    return Response(
                        data={
                            'error': 'Failed to create subscription'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            else:
                # new braintree user
                customer_kwargs = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'payment_method_nonce': payment_nonce
                }
                # Create a new Braintree customer
                result = braintree.Customer.create(customer_kwargs)
                if not result.is_success:
                    error_msg = u'Customer for user {} {} ({}) could not ' \
                                u'be created on Braintree'.format(
                        user.first_name, user.last_name, user.email
                    )
                    logger.error('[BTSubscribeView] {}'.format(error_msg))
                    send_error_email('Failed to create Braintree customer',error_msg)
                    return Response(
                        data={
                            'error': 'Failed to create customer on Braintree'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                customer = result.customer

                result = braintree.Subscription.create({
                    "payment_method_token": result.customer.payment_methods[0].token,
                    "plan_id": plan.plan_id,
                })

                if result.is_success:
                    logger.info('[BTSubscribeView] successfully created subscription for '
                                'user {} to plan {} for amount of ${}'.format(
                        user.email, subscription_plan, plan.price
                    ))

                    # user.activate
                    BTCurrentSubscription.objects.create(
                        user=user,
                        customer_id=customer.id,
                        subscription_id=result.subscription.id,
                        plan=plan,
                        status=result.subscription.status,
                        billing_period_start_date=result.subscription.billing_period_start_date,
                        billing_period_end_date=result.subscription.billing_period_end_date
                    )

                    plan.user_group.user_set.add(user)

                    # Return success
                    content = {
                        'result': "Successfuly activated subscription"
                    }
                    return Response(content, status=status.HTTP_200_OK)
                else:
                    error_msg = u'Subscription for user {} {} ({}) ' \
                                u'could not be created'.format(
                        user.first_name, user.last_name, user.email
                    )
                    logger.error('[BTSubscribeView] {}'.format(error_msg))
                    send_error_email('Failed to create Braintree subscription', error_msg)
                    return Response(
                        data={
                            'error': 'Failed to create subscription'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )


class BTReactivateSubscriptionView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        btsubscription = user.btsubscription.first()
        if not btsubscription.expire_at_period_end:
            return Response(
                data={
                    'error': 'Subscription is active and can not be reactivated'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # set number_of_billing_cycles to current_billing_cycle
        result = braintree.Subscription.update(
            btsubscription.subscription_id,
            {
                'never_expires': True
            }
        )
        if not result.is_success:
            error_msg = u'Subscription for user {} {} ({}) ' \
                        u'could not be reactivated'.format(
                user.first_name, user.last_name, user.email
            )
            logger.error('[BTReactivateSubscriptionView] {}'.format(error_msg))
            send_error_email('Failed to reactivate Braintree subscription', error_msg)
            return Response(
                data={
                    'error': 'Failed to reactivate subscription'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            btsubscription.update_from_subscription(
                subscription=result.subscription,
                plan=btsubscription.plan,
                expire_at_period_end=False
            )

        return Response(status=status.HTTP_202_ACCEPTED)


class BTCancelSubscriptionView(views.APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        if hasattr(user, 'btsubscription'):
            btsubscription = user.btsubscription.first()
            if not btsubscription.is_active or btsubscription.expire_at_period_end:
                return Response(
                    data={
                        'error': 'Subscription is already cancelled'
                    },
                    status=status.HTTP_304_NOT_MODIFIED
                )

            # set number_of_billing_cycles to current_billing_cycle
            subscription = braintree.Subscription.find(btsubscription.subscription_id)
            result = braintree.Subscription.update(
                btsubscription.subscription_id,
                {
                    'number_of_billing_cycles': subscription.current_billing_cycle
                }
            )

            # we don't want to cancel, we must only set billing cycle to current number of billing cycles
            # so that it will expire on its own at billing end date
            # result = braintree.Subscription.cancel(btsubscription.subscription_id)
            if not result.is_success:
                error_msg = u'Subscription for user {} {} ({}) ' \
                            u'could not be cancelled'.format(
                    user.first_name, user.last_name, user.email
                )
                logger.error('[BTCancelSubscriptionView] {}'.format(error_msg))
                send_error_email('Failed to cancel Braintree subscription', error_msg)
                return Response(
                    data={
                        'error': 'Failed to cancel subscription'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ok, successfully cancelled
            btsubscription.update_from_subscription(
                plan=btsubscription.plan,
                subscription=result.subscription,
                expire_at_period_end=True
            )

        else:
            return Response(
                data={
                    'error': 'User has no subscription'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_202_ACCEPTED)


class BTWebhook(views.APIView):

    permission_classes = (AllowAny, )

    def handle_subscription_event(self, subscription, event_name):
        try:
            btsubscription = BTCurrentSubscription.objects.get(
                subscription_id=subscription.id
            )
            logger.info(
                '[BTWebhook] received {} for user={} subscription_id={}, '
                'amount={}{}'.format(
                    event_name,
                    btsubscription.user.email,
                    subscription.id,
                    btsubscription.plan.price,
                    btsubscription.plan.currency_iso_code
                )
            )
            btsubscription.update_from_subscription(
                subscription=subscription,
                plan=btsubscription.plan
            )
        except BTCurrentSubscription.DoesNotExist:
            logger.error(
                '[BTWebhook] received {} for subscription_id={}, '
                'but no such subscription exists in the system'.format(
                    event_name, subscription.id
                )
            )

    def post(self, request):
        data = request.data
        try:
            webhook_notification = braintree.WebhookNotification.parse(
                str(data.get('bt_signature')), data.get('bt_payload')
            )
        except braintree.exceptions.invalid_signature_error.InvalidSignatureError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        print(webhook_notification.kind)
        print(webhook_notification.timestamp)

        kind = webhook_notification.kind
        if kind in [
            braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully,
            braintree.WebhookNotification.Kind.SubscriptionCanceled,
            braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully,
            braintree.WebhookNotification.Kind.SubscriptionExpired,
            braintree.WebhookNotification.Kind.SubscriptionTrialEnded,
            braintree.WebhookNotification.Kind.SubscriptionWentActive,
            braintree.WebhookNotification.Kind.SubscriptionWentPastDue,
        ]:
            subscription = webhook_notification.subscription
            self.handle_subscription_event(subscription, kind)

        return Response(status=status.HTTP_200_OK)