from rest_framework import response
from django.http import HttpResponse
import stripe
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from rest_framework.generics import RetrieveAPIView
from rest_framework import permissions
from .serializers import ProductSerializer
from main.models import Plan
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class ProductPreview(RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Plan.objects.all()


class CreateCheckOutSession(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        permission_classes = [permissions.AllowAny]
        prod_id = self.kwargs["pk"]
        print('request:' , self.kwargs["pk"])
        prices = stripe.Price.list(
            lookup_keys=["price_1O7yPrDV4Z1ssWPD0lRvmoSA"],
            expand=['data.product']
        )
        print("PRICES ", prices)
        try:
            product = Plan.objects.get(pk=prod_id)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        # 'price_data': {
                        #     'currency': 'usd',
                        #     'unit_amount': int(product.price) * 100,
                        #     'product_data': {
                        #         'name': product.name,
                        #         # 'images': [f"{API_URL}/{product.product_image}"]
                        #
                        #     }
                        # },
                        "price": 'price_1O7yPrDV4Z1ssWPD0lRvmoSA',
                        'quantity': 1,
                    },
                ],
                metadata={
                    "product_id": product.id
                },
                mode='subscription',
                success_url=settings.SITE_URL + '?success=true',
                cancel_url=settings.SITE_URL + '?canceled=true',
            )
            return redirect(checkout_session.url)
        except Exception as e:
            return Response({'msg': 'something went wrong while creating stripe session', 'error': str(e)}, status=500)
