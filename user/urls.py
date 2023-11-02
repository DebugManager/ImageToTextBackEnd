from django.urls import path, include, re_path


from user.views import CustomTokenCreateView, GrantPermissionView, UserRoleList, \
    CreateUserAndGrantPermissionView, UpdateUserAndPermissionsView, UserDetail, AllUsersForAdminView, \
    DetailUserForAdminView, AllTicketForAdminView

urlpatterns = [
    path('v1/user-create-with-permissions/', CreateUserAndGrantPermissionView.as_view()),
    path('v1/user-create-with-permissions/<int:pk>/', UpdateUserAndPermissionsView.as_view()),
    path('v1/users/', UserRoleList.as_view()),
    path('v1/users/<int:pk>/', UserDetail.as_view()),
    path('v1/users/grant-permission/', GrantPermissionView.as_view()),
    path('v1/auth/token/create/', CustomTokenCreateView.as_view()),
    path('v1/admin/users/', AllUsersForAdminView.as_view()),
    path('v1/admin/users/<int:pk>/', DetailUserForAdminView.as_view()),
    path('v1/admin/ticket/', AllTicketForAdminView.as_view()),
    path('v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]

