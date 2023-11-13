from django.urls import path, include, re_path


from user.views import CustomTokenCreateView, GrantPermissionView, UserRoleList, \
    CreateUserAndGrantPermissionView, UpdateUserAndPermissionsView, UserDetail, AllUsersForAdminView, \
    DetailUserForAdminView, AllTicketForAdminView, PersonalInfoUpdade, ChatRoomListCreateView, ChatRoomDetailView, \
    ChatMessagesView, CustomUserCreateView, UserList, AffiliateEdit, AffiliateListView

urlpatterns = [
    path('v1/user-create-with-permissions/', CreateUserAndGrantPermissionView.as_view()),
    path('v1/user-create-with-permissions/<int:pk>/', UpdateUserAndPermissionsView.as_view()),
    path('v1/users/', UserRoleList.as_view()),
    path('v1/users/<int:pk>/', UserDetail.as_view()),
    path('v1/users/grant-permission/', GrantPermissionView.as_view()),
    path('v1/choose-plan/<int:pk>/', PersonalInfoUpdade.as_view()),
    path('v1/auth/token/create/', CustomTokenCreateView.as_view()),
    path('v1/admin/users/', AllUsersForAdminView.as_view()),
    path('v1/admin/users/<int:pk>/', DetailUserForAdminView.as_view()),
    path('v1/admin/ticket/', AllTicketForAdminView.as_view()),
    path('v1/admin/affiliates/', AffiliateListView.as_view()),
    path('v1/create-room/', ChatRoomListCreateView.as_view()),
    path('v1/room/<str:name>/', ChatRoomDetailView.as_view()),
    path('v1/messages/<str:room_name>/', ChatMessagesView.as_view()),
    path('v1/edit-affiliate/', AffiliateEdit.as_view()),
    path('v1/auth/register/', CustomUserCreateView.as_view()),
    path('v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]

