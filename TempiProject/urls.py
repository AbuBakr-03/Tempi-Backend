from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
    TokenVerifyView,
)
from TempiApp.views import CustomTokenObtainPairView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("TempiApp.urls")),  # Include app URLs
    path("auth/", include("djoser.urls")),
    path("auth/jwt/create/", CustomTokenObtainPairView.as_view(), name="jwt_create"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("auth/jwt/verify/", TokenVerifyView.as_view(), name="jwt_verify"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="jwt_blacklist"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
