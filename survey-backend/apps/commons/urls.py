from django.urls import path
from .views import HealthCheckView
from .token_views import obtain_auth_token, logout, token_status

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('auth/login/', obtain_auth_token, name='auth-login'),
    path('auth/logout/', logout, name='auth-logout'),
    path('auth/token-status/', token_status, name='token-status'),
]
