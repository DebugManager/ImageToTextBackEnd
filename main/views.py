import django_filters
from django.contrib.auth.models import Permission
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser import utils
from djoser.views import TokenCreateView
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import CompanyDoc, Company, CustomUser, Plan, Feature
from main.serializers import CompanyDocSerializer, CompanySerializer, UserSerializer, PlanSerializer, \
    CustomUserUpdateSerializer, FeatureVoteSerializer, AllUserSerializer, GrantPermissionSerializer
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
    serializer_class = AllUserSerializer
    permission_classes = (AllowAny,)


class UserRoleList(generics.ListCreateAPIView):
    serializer_class = AllUserSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['role', 'company', 'joined', 'last_login', 'first_name', 'last_name']

    def list(self, request, *args, **kwargs):
        users = CustomUser.objects.all()  # Replace with your user model
        users = self.filter_queryset(users)

        user_data = []
        for user in users:
            role = "admin" if user.is_superuser else ("staff" if user.is_staff else "customer")
            user_data.append({
                "id": user.id,
                "email": user.email,
                "last_login": user.last_login,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "address_line1": user.address_line1,
                "city": user.city,
                "zip_code": user.zip_code,
                "country": user.country,
                "current_plan": user.current_plan,
                "joined": user.joined,
                "role": role,
            })

        return Response(user_data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(joined=timezone.now())  # todo


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AllUserSerializer
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


class GrantPermissionView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = GrantPermissionSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            permission_codename = serializer.validated_data['permission_codename']
            action = serializer.validated_data['action']

            try:
                user = CustomUser.objects.get(pk=user_id)
                permission = Permission.objects.get(codename=permission_codename)

                if action == 'grant':
                    user.user_permissions.add(permission)
                    user.save()
                    return Response({'message': f'Permission "{permission_codename}" granted to user {user_id}.'},
                                    status=status.HTTP_200_OK)
                elif action == 'revoke':
                    user.user_permissions.remove(permission)
                    user.save()
                    return Response({'message': f'Permission "{permission_codename}" revoked from user {user_id}.'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
            except Permission.DoesNotExist:
                return Response({'error': 'Permission not found.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
