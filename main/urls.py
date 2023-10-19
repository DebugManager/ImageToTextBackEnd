from django.urls import path, include, re_path

from main import views
from main.views import MainList, MainDetail, UserList



urlpatterns = [
    path('v1/main/', views.MainList.as_view()),
    path('v1/main/<int:pk>/', views.MainDetail.as_view()),
    path('v1/users/', UserList.as_view()),
    path('v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]

