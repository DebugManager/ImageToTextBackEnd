from rest_framework.serializers import ModelSerializer

from main.models import CompanyDoc, Company, Plan, SupportPost
from user.models import Feature, Ticket


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
        fields = ("id", "name", "votes", "voted_users")


class SupportPostSerializer(ModelSerializer):
    class Meta:
        model = SupportPost
        fields = '__all__'


class TicketSerializer(ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class TitleCollumTitleSerializer(ModelSerializer):
    class Meta:
        model = SupportPost
        fields = ('id', 'collum_title', 'title')
