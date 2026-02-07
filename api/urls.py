from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/auth/protected/', protected_view, name='protected_view'),
    path('v1/auth/register/', register, name='register'),
    path('v1/auth/logout/', logout, name='logout'),

    path('v1/urls/shorten/', shorten_url, name='shorten_url')
    path('v1/urls/getall/', getlinks, name='getlinks')
]
