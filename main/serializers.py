from rest_framework.serializers import ModelSerializer

from main.models import CompanyDoc, Company, Plan, Feature


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
