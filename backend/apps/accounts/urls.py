from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('join/', views.JoinView.as_view(), name='auth-join'),
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # Profile
    path('me/', views.MeView.as_view(), name='auth-me'),
    path('change-password/', views.ChangePasswordView.as_view(), name='auth-change-password'),
    # User management (Super Admin)
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<uuid:id>/', views.UserDetailView.as_view(), name='user-detail'),
]
