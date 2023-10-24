from django.urls import path, include, re_path

from main import views
from main.views import UserList, CustomTokenCreateView

urlpatterns = [
    path('v1/main/', views.MainList.as_view()),
    path('v1/main/<int:pk>/', views.MainDetail.as_view()),
    path('v1/', UserList.as_view()),
    path('v1/<int:pk>/', views.UserDetail.as_view()),
    path('v1/plan/', views.PlanList.as_view()),
    path('v1/plan/<int:pk>/', views.PlanDetail.as_view()),
    path('v1/features/vote', views.FeatureVoteView.as_view()),
    path('v1/features/', views.FeatureView.as_view()),
    path('v1/choose-plan/<int:pk>/', views.PersonalInfoUpdade.as_view()),
    path('v1/auth/token/create/', CustomTokenCreateView.as_view()),
    path('v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
