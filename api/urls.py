from django.urls import path
from .views import protected_view, register, logout
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/protected/', protected_view, name='protected_view'),
    path('v1/register/', register, name='register'),
    path('v1/logout/', logout, name='logout'),
]
