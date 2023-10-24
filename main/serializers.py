from django.contrib.auth.models import Group

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from main.models import CompanyDoc, Company, CustomUser, Plan, Feature
from djoser.serializers import UserCreateSerializer


class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ('first_name', 'last_name', 'email', 'password')


class CustomUserUpdateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('address_line1', 'city', 'zip_code', 'country', 'current_plan')


class AllUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'last_login', 'email', 'is_superuser', 'is_staff', 'is_active', 'first_name', 'last_name',
                  'address_line1', 'city', 'zip_code', 'country', 'current_plan')


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', "first_name", "last_name")


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)


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
        fields = '__all__'
