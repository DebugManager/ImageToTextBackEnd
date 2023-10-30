# from django.contrib.auth.models import Permission
# from django.utils import timezone
# from django_filters.rest_framework import DjangoFilterBackend
# from djoser.compat import get_user_email
# from djoser.conf import settings
# from djoser import utils, signals
# from djoser.views import TokenCreateView
# from djoser.views import UserViewSet

from rest_framework import generics, status, filters
from rest_framework.generics import UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from main.models import CompanyDoc, Company, Plan, Feature
from main.serializers import CompanyDocSerializer, CompanySerializer, PlanSerializer, FeatureVoteSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny


class MainList(generics.ListCreateAPIView):
    queryset = CompanyDoc.objects.all()
    serializer_class = CompanyDocSerializer
    permission_classes = (IsAuthenticated,)


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


class MounthPlanList(generics.ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (AllowAny,)


class FeatureView(generics.ListCreateAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureVoteSerializer
    permission_classes = (AllowAny,)


class FeatureVoteView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        feature_id = request.data.get('id')

        try:
            feature = Feature.objects.get(id=feature_id)
            feature.votes += 1
            feature.save()
            return Response({'message': 'Vote successfully counted.', 'votes': feature.votes},
                            status=status.HTTP_200_OK)
        except Feature.DoesNotExist:
            return Response({'error': 'Feature not found.'}, status=status.HTTP_404_NOT_FOUND)
