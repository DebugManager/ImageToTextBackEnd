from django.urls import path

from rest_framework.routers import SimpleRouter

from main import views
from main.views import MainList, MainDetail

router = SimpleRouter()

# router.register(r'mainlist', MainList)
# router.register(r'maindetail', MainDetail)

urlpatterns = [
    path('main/', views.MainList.as_view()),
    path('main/<int:pk>/', views.MainDetail.as_view()),
]

urlpatterns += router.urls
