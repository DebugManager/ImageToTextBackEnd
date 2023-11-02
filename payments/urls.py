from django.urls import path
from .views import *
import stripe

urlpatterns = [
    path('v1/payment/product/<int:pk>',  ProductPreview.as_view(), name="product"),
    path('v1/create-checkout-session/<pk>', csrf_exempt(CreateCheckOutSession.as_view()), name='checkout_session')

]