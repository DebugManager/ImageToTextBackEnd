from django.contrib.auth.models import User, Group
from django.shortcuts import render
from requests import Response
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from main.models import CompanyDoc, Company, CustomUser
from main.serializers import CompanyDocSerializer, CompanySerializer, UserSerializer, GroupSerializer
from rest_framework.permissions import IsAuthenticated



class MainList(generics.ListCreateAPIView):
    queryset = CompanyDoc.objects.all()
    serializer_class = CompanyDocSerializer
    permission_classes = (IsAuthenticated,)


class MainDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyDoc.objects.all()
    serializer_class = CompanyDocSerializer


class CompanyList(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class UserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
