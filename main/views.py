import cloudinary.uploader
from rest_framework import generics, status, filters
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import CompanyDoc, Company, Plan, SupportPost
from main.serializers import CompanyDocSerializer, CompanySerializer, PlanSerializer, FeatureVoteSerializer, \
    SupportPostSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny

from user.models import CustomUser, Feature, UserFeatureVote


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


class PlanDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (AllowAny,)


class CompanyList(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'votes']


class FeatureVoteView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        feature_id = request.data.get('feature_id')
        user_id = request.data.get('user_id')

        try:
            feature = Feature.objects.get(id=feature_id)
            user = CustomUser.objects.get(id=user_id)

            if feature.voted_users.filter(id=user_id).exists():
                return Response({'error': 'You have already voted for this feature.'},
                                status=status.HTTP_400_BAD_REQUEST)
            feature.votes += 1
            feature.save()

            user_vote = UserFeatureVote(user=user, feature=feature)
            user_vote.save()
            return Response({'message': 'Vote successfully counted.', 'votes': feature.votes},
                            status=status.HTTP_200_OK)
        except Feature.DoesNotExist:
            return Response({'error': 'Feature not found.'}, status=status.HTTP_404_NOT_FOUND)


class FeatureUnvoteView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        feature_id = request.data.get('feature_id')
        user_id = request.data.get('user_id')

        try:
            feature = Feature.objects.get(id=feature_id)
            user = CustomUser.objects.get(id=user_id)
            if not feature.voted_users.filter(id=user_id).exists():
                return Response({'error': 'You have already unvote for this feature.'},
                                status=status.HTTP_400_BAD_REQUEST)
            feature.votes -= 1
            feature.save()

            user_vote = UserFeatureVote.objects.filter(user=user, feature=feature)
            user_vote.delete()
            return Response({'message': 'Vote successfully counted.', 'votes': feature.votes},
                            status=status.HTTP_200_OK)
        except Feature.DoesNotExist:
            return Response({'error': 'Feature not found.'}, status=status.HTTP_404_NOT_FOUND)


class SupportPostGetAllView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = SupportPost.objects.all()
    serializer_class = SupportPostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['collum_title']


class SupportPostCreateView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser, JSONParser)

    def post(self, request):
        # Get data from the request
        collum_title = request.data.get('collum_title')
        title = request.data.get('title')
        description = request.data.get('description')
        file = request.data.get('picture')

        # Upload the image to Cloudinary
        upload_data = cloudinary.uploader.upload(file)

        # Create and save the record to the database
        uploaded_image = SupportPost(
            collum_title=collum_title,
            title=title,
            description=description,
            image_url=upload_data['url']
        )
        uploaded_image.save()

        # Serialize the data and return the response
        serializer = SupportPostSerializer(uploaded_image)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=201)
