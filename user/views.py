import base64
import os
from datetime import datetime

import stripe
from django.contrib.auth.models import Permission
from django.core.mail import send_mail
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django_filters import DateFromToRangeFilter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser import utils
from djoser.views import TokenCreateView
from djoser.views import UserViewSet
from dotenv import load_dotenv

from rest_framework import generics, status, filters
from rest_framework.generics import get_object_or_404, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from user.models import CustomUser, Ticket, ChatRoom, ChatMessage, Affiliate, AffiliateLink, AffiliatedUser
from user.serializers import CustomUserUpdateSerializer, AllUserSerializer, GrantPermissionSerializer, \
    AllUserForAdminSerializer, UserForAdminUpdateSerializer, TicketForAdminSerializer, ChatRoomSerializer, \
    ChatMessageSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny

from user.utils import encode_unique_link, decode_unique_link

load_dotenv()

class DateRangeFilter(FilterSet):
    created = DateFromToRangeFilter(field_name="created")


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


class CustomUserCreateView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AllUserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        # Extract the fields from the request data
        email = request.data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            response_data = {"error": "Email already exists in the database"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        affiliate_link = request.data.get('unique_link')
        if affiliate_link:
            try:
                # affiliate_id = decode_unique_link(affiliate_link)
                encoded_id, _ = affiliate_link.split('-')
                decoded_id = base64.urlsafe_b64decode(encoded_id).decode()

                affiliate = Affiliate.objects.get(id=decoded_id)

                customer = stripe.Customer.create(email=email, name=f'{first_name} {last_name}')

                # Update the user to become an affiliate
                user = CustomUser.objects.create(
                    email=email,
                    first_name=request.data.get('first_name'),
                    last_name=request.data.get('last_name'),
                    customer_id=stripe.Customer.create(email=email,
                                                       name=f'{request.data.get("first_name")} {request.data.get("last_name")}').id,
                )
                user.set_password(request.data.get('password'))

                # Create an affiliated user for the affiliate
                AffiliatedUser.objects.create(user=user, affiliate=affiliate)

                response_data = {
                    "user_id": user.id,
                    "email": user.email,
                    "customer_id": user.customer_id,
                    "message": "User registered successfully as an affiliated user",
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            except AffiliateLink.DoesNotExist:
                # Handle the case when the affiliate link is not valid
                response_data = {"error": "Invalid affiliate link"}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Create a Stripe customer and obtain the customer ID
            customer = stripe.Customer.create(email=email, name=f'{first_name} {last_name}')

            # Create a user model instance with the provided fields
            user = CustomUser(
                email=email,
                first_name=first_name,
                last_name=last_name,
                customer_id=customer.id,  # Store the customer ID from Stripe
                # You can add other fields here if needed
            )
            user.set_password(request.data.get('password'))

            # Save the user to the database
            user.save()

            # Customize the response data if needed
            response_data = {
                "user_id": user.id,
                "email": user.email,
                "customer_id": customer.id,  # Include the customer ID from Stripe
                "message": "User registered successfully",
            }
            return Response(response_data, status=status.HTTP_201_CREATED)


#
# class CustomUserCreateView(UserViewSet):
#     permission_classes = (AllowAny,)
#
#     def create(self, request, *args, **kwargs):
#         user_serializer = self.get_serializer(data=request.data)
#         customer = stripe.Customer.create(email=request.data['email'])
#
#         user_serializer.is_valid(raise_exception=True)
#         user_serializer.save()
#         # You can add custom logic here, e.g., sending a welcome email
#         user = user_serializer.instance
#         # Customize the response data if needed
#         response_data = {
#             "user_id": user.id,
#             "email": user.email,
#             "customer": customer,
#             "message": "User registered successfully",
#         }
#         return Response(response_data, status=status.HTTP_201_CREATED)


class CustomUserViewSet(UserViewSet):

    @action(detail=False, methods=['post'])
    def create_user_and_grant_permission(self, request):
        # Extract user info and permissions data from the request
        user_data = request.data.get('user_info', {})
        permissions_to_grant = request.data.get('permissions_to_grant', [])

        # Create a user using Djoser's serializer
        user_serializer = self.get_serializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        # Get the created user instance
        user = user_serializer.instance

        # Grant permissions
        for permission_codename in permissions_to_grant:
            try:
                permission = Permission.objects.get(codename=permission_codename)
                user.user_permissions.add(permission)
            except Permission.DoesNotExist:
                return Response({'error': f'Permission "{permission_codename}" not found.'},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'User created and permissions granted.'}, status=status.HTTP_201_CREATED)


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
        user = serializer.save()
        # Set the user's password and hash it
        user.set_password(self.request.data.get('password'))
        # Save any additional user data
        user.joined = timezone.now()
        is_superuser = self.request.data.get('is_superuser', False)
        is_staff = self.request.data.get('is_staff', False)
        user.type = 'admin' if is_superuser else ('staff' if is_staff else 'customer')
        user.save()

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


class UpdateUserAndPermissionsView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AllUserSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'pk'  # The primary key lookup field

    def partial_update(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')  # Extract user ID from URL parameter
        user = get_object_or_404(CustomUser, id=user_id)

        # Extract user data and permissions from the request
        user_data = request.data
        permissions_to_grant = user_data.pop('user_permissions', [])  # Remove permissions from user_data

        # Update user info
        user_serializer = self.serializer_class(user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Grant or revoke permissions
        user.user_permissions.clear()  # Remove all existing permissions
        for permission_id in permissions_to_grant:
            permission = get_object_or_404(Permission, pk=permission_id)
            user.user_permissions.add(permission)

        return Response({'message': 'User info and permissions updated.'}, status=status.HTTP_200_OK)


class AllUsersForAdminView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AllUserForAdminSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['role', 'company', 'joined', 'last_login', 'first_name', 'last_name', 'type']


class DetailUserForAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserForAdminUpdateSerializer
    permission_classes = (AllowAny,)


class AllTicketForAdminView(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketForAdminSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'website', 'description']
    ordering_fields = ['website', 'site_code', 'id', 'user__first_name', 'user__last_name', 'user__email', 'status',
                       'user_id']
    filterset_class = DateRangeFilter  # Apply the custom filter

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply additional filtering based on your needs
        # For example, you can filter the queryset using request data

        date_range = self.request.query_params.get("date_range")
        if date_range:
            # date_range format should be like "2023-10-01|2023-10-31"
            start_date, end_date = date_range.split("|")
            queryset = queryset.filter(created__range=[start_date, end_date])

        return queryset


class ChatRoomListCreateView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = (AllowAny,)


class ChatRoomDetailView(generics.RetrieveAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    lookup_field = 'name'
    permission_classes = (AllowAny,)


class ChatMessagesView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        # Get the room name from the URL parameter
        room_name = self.kwargs['room_name']

        # Retrieve the room_id associated with the room_name
        try:
            room_id = ChatRoom.objects.get(name=room_name).id
        except ChatRoom.DoesNotExist:
            room_id = None

        # Filter messages based on the room_id
        queryset = ChatMessage.objects.filter(room_id=room_id)
        return queryset


class AffiliateEdit(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            user = CustomUser.objects.get(id=user_id)

            affiliate_data = {
                'promotion_plan': request.data.get('promotion_plan'),
                'twitter': request.data.get('twitter'),
                'instagram': request.data.get('instagram'),
                'tiktok': request.data.get('tiktok'),
                'linkedin': request.data.get('linkedin'),
                'facebook': request.data.get('facebook'),
                'paypal_email': request.data.get('paypal_email'),
                'btc_adress': request.data.get('btc_adress'),
                'user': user
            }

            affiliate = Affiliate.objects.create(**affiliate_data)

            for field in ['first_name', 'last_name', 'email']:
                if field in request.data:
                    setattr(user, field, request.data[field])
            print(user.affiliate_id_id)
            user.affiliate_id_id = affiliate
            print(user.affiliate_id_id.id)
            # user.affiliate_id = affiliate
            # user.save()

            return Response({'success': AllUserSerializer(user).data})  # affiliate.id})
        # except ObjectDoesNotExist as e:
        #     return Response({'error': f'Object not found: {str(e)}'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class AffiliateListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        affiliates = Affiliate.objects.all()
        affiliate_data = []

        for affiliate in affiliates:
            affiliated_users = affiliate.affiliateduser_set.all()
            sales = 0
            if affiliated_users:
                for affiliated_user in affiliated_users:
                    try:
                        sales += stripe.Price.retrieve(affiliated_user.user.current_plan)['unit_amount']
                    except Exception: print("Hello")

            data = {
                "id": affiliate.id,
                "first_name": affiliate.user.first_name,
                "last_name": affiliate.user.last_name,
                "email": affiliate.user.email,
                "users_signed_up": affiliated_users.count(),
                "sales": sales,
                "commission": sales // 10,  # Set default commission to 10%
                "status": affiliate.approved,
                "country": affiliate.user.country,
                "created": affiliate.created
            }
            affiliate_data.append(data)

        search_query = request.GET.get('search')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if search_query:
            filtered_affiliate_user = [
                affiliate_user for affiliate_user in affiliate_data
                if (
                        search_query in affiliate_user['first_name'] or
                        search_query in affiliate_user['last_name'] or
                        search_query in affiliate_user['email'] or
                        search_query in affiliate_user['country']
                )
            ]
        else:
            if start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                filtered_affiliate_user = [
                    affiliate_user for affiliate_user in affiliate_data
                    if start_date <= affiliate_user['date'] <= end_date
                ]

            else:
                filtered_affiliate_user = affiliate_data
        sort_field = request.GET.get('sort')
        if sort_field in ['first_name', 'last_name', 'email', 'users_signed_up', 'sales', 'commission', 'status',
                          'country']:
            filtered_affiliate_user.sort(key=lambda x: x[sort_field])

        return JsonResponse({'affiliates': filtered_affiliate_user})


class ApproveAffiliateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            affiliate_id = request.data.get('affiliate_id'),
            affiliate = Affiliate.objects.get(id=affiliate_id)
        except Affiliate.DoesNotExist:
            return JsonResponse({'error': 'Affiliate not found'}, status=404)

        affiliate.approved = True
        affiliate.save()

        return JsonResponse({'message': 'Affiliate approved successfully'})

    # def delete(self, request):
    #     try:
    #         affiliate_id = request.data.get('affiliate_id'),
    #         affiliate = Affiliate.objects.get(id=affiliate_id)


class AffiliateEditOrApprove(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            affiliate_id = request.data.get('affiliate_id')
            affiliate = Affiliate.objects.get(id=affiliate_id)

            if 'first_name' in request.data:
                affiliate.user.first_name = request.data.get('first_name')
            if 'last_name' in request.data:
                affiliate.user.last_name = request.data.get('last_name')
            if 'email' in request.data:
                affiliate.user.email = request.data.get('email')
            if 'country' in request.data:
                affiliate.user.country = request.data.get('country')
            if 'approved' in request.data:
                affiliate.approved = request.data.get('approved')

            # Save the changes
            affiliate.user.save()
            affiliate.save()
            if affiliate.approved:
                affiliate_link = AffiliateLink.objects.create(affiliate=affiliate)
                hostname = request.get_host()
                generated_link = f'{hostname}/auth/{affiliate_link.unique_link}'
                print(generated_link)

                send_mail(
                    subject='Affiliate Approval',
                    message=f'Congratulations! Your affiliate account has been approved. Follow this link to sign up: {generated_link}',
                    from_email=os.environ.get('DEFAULT_FROM_EMAIL'),
                    recipient_list=[affiliate.user.email],  # List of recipient emails
                    fail_silently=False,
                )
            return Response({'success': 200})
        # except ObjectDoesNotExist as e:
        #     return Response({'error': f'Object not found: {str(e)}'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class GetAffiliateById(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        affiliate_id = request.data.get('affiliate_id')
        affiliate = Affiliate.objects.get(id=affiliate_id)
        sales = 0
        affiliated_users = affiliate.affiliateduser_set.all()
        if affiliated_users:
            for affiliated_user in affiliated_users:
                sales += stripe.Price.retrieve(affiliated_user.user.current_plan)['unit_amount']

        data = {
            "id": affiliate.id,
            "first_name": affiliate.user.first_name,
            "last_name": affiliate.user.last_name,
            "email": affiliate.user.email,
            "users_signed_up": affiliated_users.count(),
            "sales": sales,  # todo
            "commission": sales // 10,
            "status": affiliate.approved,
            "country": affiliate.user.country,
            "created": affiliate.created
        }

        return Response(data)
