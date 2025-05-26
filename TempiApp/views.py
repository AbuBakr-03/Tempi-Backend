# TempiApp/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    CustomUserSerializer,
)
from .models import UserProfile


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()

    def get_object(self):
        return self.request.user.profile


class DetailedCurrentUserProfileView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class DetailedOtherUserProfileView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
