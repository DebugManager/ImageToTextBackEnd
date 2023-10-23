from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from main.models import CompanyDoc, Company, CustomUser, Plan
from djoser.serializers import UserCreateSerializer, TokenCreateSerializer


class CustomTokenCreateSerializer(TokenCreateSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        fields = ('auth_token', 'user')

    def get_user(self, obj):
        user = self.user  # Retrieve the user from the request context
        custom_user = CustomUser.objects.get(user=user)  # Assuming your user model has a ForeignKey to CustomUser
        user_data = {
            'id': custom_user.id,
            'email': user.email,
            'is_superuser': user.is_superuser,

            # Add more fields as needed
        }
        return user_data


class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ('first_name', 'last_name', 'email', 'password')


class CustomUserUpdateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('first_name', 'last_name', 'email', 'password', 'address_line1', 'city', 'zip_code', 'country')


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

# class UserSerializer(ModelSerializer):
#     class Meta:
#         model = MyUser
#         fields = ['username', 'password', 'package', 'amount', 'created_date', 'paid_date', 'method', 'status']
