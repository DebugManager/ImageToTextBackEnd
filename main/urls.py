from django.urls import path

from main import views
from main.views import CompanyList, CompanyDetail

urlpatterns = [
    path('v1/main/', views.MainList.as_view()),
    path('v1/main/<int:pk>/', views.MainDetail.as_view()),
    path('v1/company/', CompanyList.as_view()),
    path('v1/company/<int:pk>/', CompanyDetail.as_view()),
    path('v1/plan/', views.PlanList.as_view()),
    path('v1/plan/<int:pk>/', views.PlanDetail.as_view()),
    path('v1/features/vote/', views.FeatureVoteView.as_view()),
    path('v1/features/unvote/', views.FeatureUnvoteView.as_view()),
    path('v1/features/', views.FeatureView.as_view()),
    path('v1/support-posts/', views.SupportPostGetAllView.as_view()),
    path('v1/support-posts/create/', views.SupportPostCreateView.as_view()),
    path('v1/support-posts/edit/<int:pk>/', views.SupportPostEditView.as_view()),
    path('v1/support/tickets/', views.TicketList.as_view()),
    path('v1/support/tickets/<int:pk>', views.TicketDetail.as_view())
]

