import json
import operator
import os
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import stripe

from user.models import CustomUser

stripe.api_key = settings.STRIPE_SECRET_KEY


class GetConfigView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            # Retrieves prices based on the interval query parameter
            interval = request.GET.get('interval', None)

            stripe.api_key = settings.STRIPE_SECRET_KEY

            params = {}
            if interval:
                params['recurring[interval]'] = interval

            prices = stripe.Price.list(**params)

            # Serialize the prices data
            serialized_prices = []
            for price in prices:
                product_name = stripe.Product.retrieve(id=price.product)
                serialized_prices.append({
                    'id': price.id,
                    'object': price.object,
                    'active': price.active,
                    'billing_scheme': price.billing_scheme,
                    'created': price.created,
                    'custom_unit_amount': price.custom_unit_amount,
                    'livemode': price.livemode,
                    'lookup_key': price.lookup_key,
                    'metadata': price.metadata,
                    'nickname': price.nickname,
                    'product': price.product,
                    'currency': price.currency,
                    'recurring': price.recurring,
                    'tax_behavior': price.tax_behavior,
                    'tiers_mode': price.tiers_mode,
                    'transform_quantity': price.transform_quantity,
                    'type': price.type,
                    'unit_amount': price.unit_amount,
                    'unit_amount_decimal': price.unit_amount_decimal,
                    'product_name': product_name.name,
                    'options': product_name.features,
                    # Add other fields you need here
                })

            return Response({
                'publishableKey': settings.STRIPE_PUBLISHABLE_KEY,
                'prices': serialized_prices,
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class GetAllSubscriptions(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        subscriptions = stripe.Subscription.list()

        return Response({
            'publishableKey': settings.STRIPE_PUBLISHABLE_KEY,
            'subscriptions': subscriptions,

        })


class GetPlanByIdView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, price_id):
        try:

            stripe.api_key = settings.STRIPE_SECRET_KEY
            price = stripe.Price.retrieve(price_id)
            product = stripe.Product.retrieve(price.product)

            return Response({
                'publishableKey': settings.STRIPE_PUBLISHABLE_KEY,
                'price': price,
                'product': product,
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class GetUserWithProduct(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        try:
            client = stripe.Customer.retrieve(data['customer_id'], expand=["subscriptions"])
            product_id = client['subscriptions']['data'][0]['items']['data'][0]['plan']['product']
            price_id = client['subscriptions']['data'][0]['items']['data'][0]['plan']['id']
            product_name = stripe.Product.retrieve(id=product_id)
            return Response({'client': client, 'product_id': product_name.id, 'price_id': price_id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class CreateCustomerView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        data = request.data

        try:
            customer = stripe.Customer.create(email=data['email'])
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
            customer_id = data['customer_id']
            customer = CustomUser.objects.get(customer_id=customer_id)
            # Cancel the subscription by deleting it
            deleted_subscription = stripe.Subscription.delete(data['subscription_id'])
            customer.subscription_id = None
            customer.payment_method_id = None
            customer.current_plan = None
            customer.save()

            return Response({'success': True, 'subscription': deleted_subscription}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class ListSubscriptionsView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
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
        try:
            data = json.loads(request.body.decode("utf-8"))
            token = data.get('token')
            price_id = data.get('price_id')
            customer_id = data.get('customer_id')
            payment_method_id = data.get('payment_method_id')
            price = stripe.Price.retrieve(price_id)
            old_subscription_id = data.get('old_subscription_id')
            try:
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={
                        "default_payment_method": payment_method_id
                    }
                )
            except stripe.error.StripeError as e:
                # Handle any errors
                return JsonResponse({"Error:": str(e)})

            customer = CustomUser.objects.get(customer_id=customer_id)
            if payment_method_id != customer.payment_method_id and payment_method_id:
                self.update_payment_method_id_in_db(customer=customer, new_payment_method_id=payment_method_id)

            # Create a payment intent using the card token
            payment_intent = stripe.PaymentIntent.create(
                amount=price.unit_amount,
                currency="usd",
                description="Payment for order",
                payment_method_types=["card"],
                payment_method_data={
                    "type": "card",
                    "card": {
                        "token": token
                    }
                },
                confirm=True
            )

            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {"price": price_id},
                ],
            )

            self.update_current_plan_id_in_db(customer=customer, price_id=price_id)

            if old_subscription_id:
                stripe.Subscription.cancel(old_subscription_id)
                self.update_subscription_id_in_db(customer=customer, new_subscription_id=subscription.id)
            else:
                self.update_subscription_id_in_db(customer=customer, new_subscription_id=subscription.id)

            # Payment processed successfully
            return JsonResponse({'success': True, 'intent': payment_intent, 'subscription': subscription})
        except stripe.error.CardError as e:
            return JsonResponse({'error': str(e)})

    def update_subscription_id_in_db(self, customer, new_subscription_id):
        customer.subscription_id = new_subscription_id
        customer.save()

    def update_payment_method_id_in_db(self, customer, new_payment_method_id):
        customer.payment_method_id = new_payment_method_id
        customer.save()

    def update_current_plan_id_in_db(self, customer, price_id):
        customer.current_plan = price_id
        customer.save()


@method_decorator(csrf_exempt, name='dispatch')
class ProcessOnHoldView(View):
    @method_decorator(require_POST)
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            price_id = data.get('price_id')
            customer_id = data.get('customer_id')
            payment_method_id = data.get('payment_method_id')
            price = stripe.Price.retrieve(price_id)
            old_subscription_id = data.get('old_subscription_id')

            customer = CustomUser.objects.get(customer_id=customer_id)
            if payment_method_id != customer.payment_method_id and payment_method_id:
                self.update_payment_method_id_in_db(customer=customer, new_payment_method_id=payment_method_id)

            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {"price": price_id},
                ],
            )

            self.update_current_plan_id_in_db(customer=customer, price_id=price_id)

            if old_subscription_id:
                stripe.Subscription.cancel(old_subscription_id)
                self.update_subscription_id_in_db(customer=customer, new_subscription_id=subscription.id)
            else:
                self.update_subscription_id_in_db(customer=customer, new_subscription_id=subscription.id)

            # Payment processed successfully
            return JsonResponse({'success': True, 'subscription': subscription})
        except stripe.error.CardError as e:
            return JsonResponse({'error': str(e)})

    def update_subscription_id_in_db(self, customer, new_subscription_id):
        customer.subscription_id = new_subscription_id
        customer.save()

    def update_payment_method_id_in_db(self, customer, new_payment_method_id):
        customer.payment_method_id = new_payment_method_id
        customer.save()

    def update_current_plan_id_in_db(self, customer, price_id):
        customer.current_plan = price_id
        customer.save()


class InvoiceTable(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        client_id = request.data.get('customer_id')
        try:
            invoice = stripe.Invoice.list(customer=client_id)
            invoices = []
            for inv in invoice['data']:
                invoices.append({
                    'id': inv['id'],
                    'amount': inv['amount_paid'],
                    'crated_date': datetime.fromtimestamp(inv['lines']['data'][0]['period']['start']),
                    'paid_date': datetime.fromtimestamp(inv['lines']['data'][0]['period']['end']),
                    'name': stripe.Product.retrieve(inv['lines']['data'][0]['plan']['product'])['name'],
                    'method': stripe.PaymentMethod.retrieve(
                        stripe.Customer.retrieve(client_id)['invoice_settings']['default_payment_method'])['card'][
                        'brand'],
                    'status': inv['status'],
                    'invoice_pdf': inv['invoice_pdf']
                })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        sort_field = request.GET.get('sort')
        if sort_field in ['id', 'amount', 'created_date', 'paid_date', 'name', 'method', 'status']:
            invoices.sort(key=lambda x: x[sort_field])
        return JsonResponse({'data': invoices})


class OrderView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        charges = stripe.Charge.list()
        orders = []

        for charge in charges['data']:
            if charge['customer']:
                customer = CustomUser.objects.get(customer_id=charge['customer'])
                # id name email package affiliate_code address price status country date
                orders.append({
                    "id": charge['id'],
                    "name": f"{customer.first_name} {customer.last_name}",
                    "email": customer.email,
                    "package": stripe.Product.retrieve(
                        stripe.Invoice.retrieve(charge['invoice'])['lines']['data'][0]['price']['product'])['name'],
                    'affiliate_code': customer.affiliate_id,
                    'address': customer.address_line1,
                    'price': charge['payment_method_details']['card']['amount_authorized'],
                    'status': charge['status'],
                    'country': charge['payment_method_details']['card']['country'],
                    'date': datetime.fromtimestamp(charge['created']),
                })

        search_query = request.GET.get('search')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if search_query:
            filtered_orders = [
                order for order in orders
                if (
                        search_query in order['name'] or
                        search_query in order['email'] or
                        search_query in order['package'] or
                        search_query in order['status']
                )
            ]
        else:
            if start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                filtered_orders = [
                    order for order in orders
                    if start_date <= order['date'] <= end_date
                ]
            else:
                filtered_orders = orders

        sort_field = request.GET.get('sort')
        if sort_field in ['id', 'name', 'email', 'package', 'affiliate_code', 'address', 'price', 'status', 'country',
                          'date']:
            filtered_orders.sort(key=lambda x: x[sort_field])
        return JsonResponse({'data': orders})


class InvoiceDetail(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        invoice_id = request.GET.get('invoice_id')
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            customer = CustomUser.objects.get(customer_id=invoice['customer'])
            data = {
                "id": invoice['id'],
                "account_country": invoice['account_country'],
                "account_name": invoice['account_name'],
                "amount": invoice['amount_due'],
                "created": datetime.fromtimestamp(invoice['created']),
                "currency": invoice['currency'],
                "name": f'{customer.first_name} {customer.last_name}',
                "address": customer.address_line1,
                "email": customer.email,
                "brand": stripe.Charge.retrieve(invoice['charge'])['payment_method_details']['card']['brand'],
                "last4": stripe.Charge.retrieve(invoice['charge'])['payment_method_details']['card']['last4'],
                "product_name": stripe.Product.retrieve(invoice['lines']['data'][0]['price']['product'])['name'],
                "interval": invoice['lines']['data'][0]['price']['recurring']['interval'],
                "description": invoice['lines']['data'][0]['description'],
                "invoice_pdf": invoice['invoice_pdf']

            }
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        return JsonResponse({'data': data})


# @method_decorator(csrf_exempt, name='dispatch')
# class UserInfoUpdate(APIView):
