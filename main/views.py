from djoser.views import TokenCreateView
from rest_framework import generics

from main.models import CompanyDoc, Company, CustomUser, Plan
from main.serializers import CompanyDocSerializer, CompanySerializer, UserSerializer, GroupSerializer, PlanSerializer, \
    CustomUserUpdateSerializer, CustomTokenCreateSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


class CustomTokenCreateView(TokenCreateView):
    serializer_class = CustomTokenCreateSerializer


class MainList(generics.ListCreateAPIView):
    queryset = CompanyDoc.objects.all()
    serializer_class = CompanyDocSerializer
    permission_classes = (AllowAny,)


class MainDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyDoc.objects.all()
    serializer_class = CompanyDocSerializer
    permission_classes = (AllowAny,)


class PlanList(generics.ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (AllowAny,)
    filterset_fields = ['type']


class PlanDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (AllowAny,)


class CompanyList(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (AllowAny,)


class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (AllowAny,)


class UserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class PersonalInfoUpdade(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserUpdateSerializer
    permission_classes = (AllowAny,)


class MounthPlanList(generics.ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (AllowAny,)
