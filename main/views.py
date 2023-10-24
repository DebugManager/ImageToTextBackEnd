from djoser.conf import settings
from djoser import utils
from djoser.views import TokenCreateView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import CompanyDoc, Company, CustomUser, Plan, Feature
from main.serializers import CompanyDocSerializer, CompanySerializer, UserSerializer, PlanSerializer, \
    CustomUserUpdateSerializer, FeatureVoteSerializer, AllUserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        data = {
            'token': token_serializer_class(token).data,
            'user': AllUserSerializer(serializer.user).data
        }
        return Response(
            data=data, status=status.HTTP_200_OK
        )


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


class FeatureView(generics.ListCreateAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureVoteSerializer
    permission_classes = (AllowAny,)


class FeatureVoteView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        serializer = FeatureVoteSerializer(data=request.data)
        if serializer.is_valid():
            features_votes = {feature.name: feature.votes for feature in Feature.objects.all()}
            return Response(features_votes)

    def post(self, request, format=None):
        serializer = FeatureVoteSerializer(data=request.data)

        if serializer.is_valid():
            feature_id = serializer.validated_data['id']

            try:
                feature = Feature.objects.get(id=feature_id)
                feature.votes += 1
                feature.save()
                return Response({'message': 'Vote added successfully.'}, status=status.HTTP_200_OK)
            except Feature.DoesNotExist:
                return Response({'message': 'Feature not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
