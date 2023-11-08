from django.urls import path

from payments.views import GetConfigView, CreateCustomerView, CancelSubscriptionView, ListSubscriptionsView, \
    PreviewInvoiceView, UpdateSubscriptionView, ProcessPaymentView, GetUserWithProduct

urlpatterns = [
    path('get_config/', GetConfigView.as_view()),
    path('create-user/', CreateCustomerView.as_view()),
    # path('create-user/<str:customer_id>/', CreateCustomerView.as_view()),#todo
    path('get-user/', GetUserWithProduct.as_view()),
    path('cancel-subscription/', CancelSubscriptionView.as_view()),
    path('subscriptions/', ListSubscriptionsView.as_view()),
    path('invoice-preview/', PreviewInvoiceView.as_view()),
    path('update-subscription/', UpdateSubscriptionView.as_view()),
    path('process-payment/', ProcessPaymentView.as_view()),

]
