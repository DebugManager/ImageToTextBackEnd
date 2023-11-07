import json
import os

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class GetConfigView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            # Retrieves two prices with the lookup_keys
            # `sample_basic` and `sample_premium`. To
            # create these prices, you can use the Stripe
            # CLI fixtures command with the supplied
            # `seed.json` fixture file like so:
            #
            #    stripe fixtures seed.json
            #

            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Define the lookup keys
            # lookup_keys = ['Montly subscribe']

            prices = []
            prices_1 = stripe.Price.list()

            for price in prices_1:
                prices.append(price)

            return Response({
                'publishableKey': settings.STRIPE_PUBLISHABLE_KEY,
                'prices': prices,
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class CreateCustomerView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        # Reads JSON data from the request
        data = request.data

        try:
            # Create a new customer object
            customer = stripe.Customer.create(email=data['email'])

            # At this point, you can associate the ID of the Customer object with
            # your own internal representation of a customer if needed.

            # Simulate authentication by storing the ID of the customer in a cookie.
            response = Response({'customer': customer}, status=status.HTTP_201_CREATED)
            response.set_cookie('customer', customer.id)

            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class CancelSubscriptionView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        data = request.data
        try:
            # Cancel the subscription by deleting it
            deleted_subscription = stripe.Subscription.delete(data['subscriptionId'])
            return Response({'subscription': deleted_subscription}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class ListSubscriptionsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        customer_id = request.data.get('customer_id')

        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='all',
                expand=['data.default_payment_method']
            )
            return Response({'subscriptions': subscriptions}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class PreviewInvoiceView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        customer_id = request.data.get('customer_id')
        subscription_id = request.GET.get('subscriptionId')
        new_price_lookup_key = request.GET.get('newPriceLookupKey')

        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            invoice = stripe.Invoice.upcoming(
                customer=customer_id,
                subscription=subscription_id,
                subscription_items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': os.getenv(new_price_lookup_key),
                }],
            )
            return Response({'invoice': invoice}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class UpdateSubscriptionView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        data = request.data
        try:
            subscription = stripe.Subscription.retrieve(data['subscriptionId'])
            update_subscription = stripe.Subscription.modify(
                data['subscriptionId'],
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': os.getenv(data['newPriceLookupKey'].upper()),
                }]
            )
            return Response({'update_subscription': update_subscription}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookReceivedView(View):
    permission_classes = (AllowAny,)

    def post(self, request):
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        request_data = json.loads(request.body.decode('utf-8'))

        if webhook_secret:
            signature = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body, sig_header=signature, secret=webhook_secret)
                data = event['data']
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']

        data_object = data['object']

        if event_type == 'invoice.payment_succeeded':
            if data_object['billing_reason'] == 'subscription_create':
                subscription_id = data_object['subscription']
                payment_intent_id = data_object['payment_intent']
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                stripe.Subscription.modify(
                    subscription_id,
                    default_payment_method=payment_intent.payment_method
                )

                print("Default payment method set for subscription: " + payment_intent.payment_method)
        elif event_type == 'invoice.payment_failed':
            print('Invoice payment failed: %s' % event['id'])
        elif event_type == 'invoice.finalized':
            print('Invoice finalized: %s' % event['id'])
        elif event_type == 'customer.subscription.deleted':
            print('Subscription canceled: %s' % event['id'])

        return JsonResponse({'status': 'success'})

@method_decorator(csrf_exempt, name='dispatch')
class ProcessPaymentView(View):
    @method_decorator(require_POST)
    def post(self, request):
        # Parse the JSON data from the request body
        try:
            data = json.loads(request.body.decode("utf-8"))
            token = data.get('token')

            # Create a payment intent using the card token
            payment_intent = stripe.PaymentIntent.create(
                amount=1000,  # Amount in cents
                currency="usd",
                description="Payment for order",
                payment_method_types=["card"],
                payment_method_data={
                    "type": "card",
                    "card": {
                        "token": token  # Use the card token here
                    }
                },
                confirm=True
            )

            # Payment processed successfully
            return JsonResponse({'success': True, 'intent': payment_intent})
        except stripe.error.CardError as e:
            # Payment error, return the error to the client
            return JsonResponse({'error': str(e)})

