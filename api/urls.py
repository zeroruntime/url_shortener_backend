from django.urls import path
from .views import (
    ProtectedView,
    RegisterView,
    LogoutView,
    ShortenURLView,
    LinkListView,
    LinkDetailView,
    DeleteLinkView,
    RedirectView,
    LinkAnalyticsView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/protected/', ProtectedView.as_view(), name='protected'),

    path('links/shorten/', ShortenURLView.as_view(), name='shorten-url'),

    path('links/', LinkListView.as_view(), name='list-links'),
    path('links/<int:pk>/', LinkDetailView.as_view(), name='get-link'),
    path('links/<int:pk>/delete/', DeleteLinkView.as_view(), name='delete-link'),


    path('links/<int:pk>/analytics/', LinkAnalyticsView.as_view(), name='link-analytics'),

    # path('<str:short_code>/', RedirectView.as_view(), name='redirect'),
]