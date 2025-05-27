# TempiApp/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    CustomUserSerializer,
    CategorySerializer,
    CompanySerializer,
    JobSerializer,
    JobTypeSerializer,
    WishlistSerializer,
)
from .models import UserProfile, Category, Company, Job, JobType, Wishlist

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


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


class isRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff
            or request.user.groups.filter(name="Recruiter").exists()
        )


class CompanyView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class SingleCompanyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class JobTypeView(generics.ListCreateAPIView):
    queryset = JobType.objects.all()
    serializer_class = JobTypeSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class SingleJobTypeView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobType.objects.all()
    serializer_class = JobTypeSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class JobView(generics.ListCreateAPIView):
    queryset = Job.objects.select_related("category", "company", "job_type").all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category__name", "company__name", "job_type__name", "location"]
    search_fields = ["title"]
    ordering_fields = ["start_date", "pay"]

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class SingleJobView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.select_related("category", "company", "job_type").all()
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.select_related("job", "user").filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SingleWishlistView(generics.RetrieveDestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.select_related("job", "user").filter(
            user=self.request.user
        )
