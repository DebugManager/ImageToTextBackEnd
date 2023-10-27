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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['role', 'company', 'joined', 'last_login', 'first_name', 'last_name', 'type']

    def perform_create(self, serializer):
        serializer.save(joined=timezone.now())
        is_superuser = self.request.data.get('is_superuser', False)
        is_staff = self.request.data.get('is_staff', False)
        user_type = 'admin' if is_superuser else ('staff' if is_staff else 'customer')
        serializer.validated_data['type'] = user_type
        serializer.save()


class UserRoleList(generics.ListCreateAPIView):
    serializer_class = AllUserSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['role', 'company', 'joined', 'last_login', 'first_name', 'last_name']

    def list(self, request, *args, **kwargs):
        users = CustomUser.objects.all()
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
        serializer.save(joined=timezone.now())


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AllUserSerializer
    permission_classes = (AllowAny,)

    def perform_update(self, serializer):
        is_superuser = self.request.data.get('is_superuser', serializer.instance.is_superuser)
        is_staff = self.request.data.get('is_staff', serializer.instance.is_staff)
        user_type = 'admin' if is_superuser else ('staff' if is_staff else 'customer')
        serializer.validated_data['type'] = user_type
        serializer.save()


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
            permission_codenames = serializer.validated_data['permission_codenames']
            action = serializer.validated_data['action']

            try:
                user = CustomUser.objects.get(pk=user_id)

                for permission_codename in permission_codenames:
                    try:
                        permission = Permission.objects.get(codename=permission_codename)

                        if action == 'grant':
                            user.user_permissions.add(permission)
                        elif action == 'revoke':
                            user.user_permissions.remove(permission)

                    except Permission.DoesNotExist:
                        return Response({'error': f'Permission "{permission_codename}" not found.'},
                                        status=status.HTTP_400_BAD_REQUEST)

                user.save()
                return Response({'message': f'Permissions granted/revoked to/from user {user_id}.'},
                                status=status.HTTP_200_OK)

            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserAndGrantPermissionView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AllUserSerializer
    permission_classes = (AllowAny,)
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['email', 'first_name', 'last_name']
    # ordering_fields = ['role', 'company', 'joined', 'last_login', 'first_name', 'last_name', 'type']

    def perform_create(self, serializer):
        serializer.save(joined=timezone.now())
        is_superuser = self.request.data.get('is_superuser', False)
        is_staff = self.request.data.get('is_staff', False)
        user_type = 'admin' if is_superuser else ('staff' if is_staff else 'customer')
        serializer.validated_data['type'] = user_type
        serializer.save()

    def post(self, request, *args, **kwargs):
        # Create the user by calling the base class's create method
        response = super(CreateUserAndGrantPermissionView, self).post(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            # User was created successfully, now grant permissions
            user_id = response.data['id']
            permissions_to_grant = request.data.get('permissions_to_grant', [])

            try:
                user = CustomUser.objects.get(id=user_id)

                for permission_codename in permissions_to_grant:
                    try:
                        permission = Permission.objects.get(codename=permission_codename)
                        user.user_permissions.add(permission)

                    except Permission.DoesNotExist:
                        return Response({'error': f'Permission "{permission_codename}" not found.'},
                                        status=status.HTTP_400_BAD_REQUEST)

                user.save()
                response.data['message'] = f'User created and permissions granted.'
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)

        return response

#
# class UpdateUserAndPermissionsView(APIView):
#     permission_classes = (AllowAny,)
#     serializer_class = AllUserSerializer  # Use the serializer for user info
#
#     def patch(self, request, *args, **kwargs):
#         # Extract user info and permissions data from the request
#         user_data = request.data.get('user_info', {})
#         permission_data = request.data.get('permissions', [])
#
#         user_id = user_data.get('id')
#
#         try:
#             user = CustomUser.objects.get(id=user_id)
#
#             # Update user info
#             user_serializer = self.serializer_class(user, data=user_data, partial=True)
#             if user_serializer.is_valid():
#                 user_serializer.save()
#             else:
#                 return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#             # Grant or revoke permissions
#             for permission_codename in permission_data:
#                 try:
#                     permission = Permission.objects.get(codename=permission_codename)
#
#                     if 'grant' in permission_data:
#                         user.user_permissions.add(permission)
#                     elif 'revoke' in permission_data:
#                         user.user_permissions.remove(permission)
#
#                 except Permission.DoesNotExist:
#                     return Response({'error': f'Permission "{permission_codename}" not found.'},
#                                     status=status.HTTP_400_BAD_REQUEST)
#
#             user.save()
#             return Response({'message': 'User info and permissions updated.'}, status=status.HTTP_200_OK)
#
#         except CustomUser.DoesNotExist:
#             return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)