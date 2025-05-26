from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
    TokenVerifyView,
)
from TempiApp.views import CustomTokenObtainPairView


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("/", include("TempiApp.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/jwt/create/", CustomTokenObtainPairView.as_view(), name="jwt_create"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("auth/jwt/verify/", TokenVerifyView.as_view(), name="jwt_verify"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="jwt_blacklist"),
]
