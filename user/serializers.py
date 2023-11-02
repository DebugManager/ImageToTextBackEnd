from django.contrib.auth.models import Group

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from user.models import CustomUser
from djoser.serializers import UserCreateSerializer


class GrantPermissionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    permission_codenames = serializers.ListField(child=serializers.CharField())
    action = serializers.ChoiceField(choices=['grant', 'revoke'])


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
        fields = ('__all__')
        # fields = ('id', 'last_login', 'email', 'is_superuser', 'is_staff', 'is_active', 'first_name', 'last_name',
        #           'address_line1', 'city', 'zip_code', 'country', 'current_plan')


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', "first_name", "last_name", 'current_plan', 'id')


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)


class AllUserForAdminSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'affiliate', 'affiliate_code', 'address_line1', 'status',
                  'country', 'joined')


class UserForAdminUpdateSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'address_line1', 'country', 'affiliate')
