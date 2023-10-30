from django.contrib.auth.models import Group

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from main.models import CompanyDoc, Company, Plan, Feature
from djoser.serializers import UserCreateSerializer


class CompanyDocSerializer(ModelSerializer):
    class Meta:
        model = CompanyDoc
        fields = '__all__'


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class PlanSerializer(ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class FeatureVoteSerializer(ModelSerializer):
    class Meta:
        model = Feature
        fields = ("id", "name", "votes")
