from rest_framework.serializers import ModelSerializer

from main.models import CompanyDoc, Company, MyUser


class CompanyDocSerializer(ModelSerializer):
    class Meta:
        model = CompanyDoc
        fields = '__all__'


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['username', 'password', 'package', 'amount', 'created_date', 'paid_date', 'method', 'status']

