# TempiApp/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    CompanyProfileSerializer,
    CustomUserSerializer,
    CategorySerializer,
    JobSerializer,
    JobTypeSerializer,
    WishlistSerializer,
    ApplicationSerializer,
    StatusSerializer,
    JobAssignmentSerializer,
    JobAssignmentStatusSerializer,
    JobAssignmentUpdateSerializer,
    RatingSerializer,
)
from .models import (
    UserProfile,
    CompanyProfile,
    Category,
    Job,
    JobType,
    Wishlist,
    Application,
    Status,
    JobAssignmentStatus,
    JobAssignment,
    Rating,
)

from . import models

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.groups.filter(name="Company").exists():
            return CompanyProfileSerializer
        return UserProfileSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name="Company").exists():
            return CompanyProfile.objects.all()
        return UserProfile.objects.all()

    def get_object(self):
        if self.request.user.groups.filter(name="Company").exists():
            return self.request.user.company_profile
        return self.request.user.profile


class DetailedCurrentUserProfileView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class DetailedOtherUserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()


class IsCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or request.user.groups.filter(name="Company").exists()
        )


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


class JobView(generics.ListAPIView):
    queryset = Job.objects.select_related("category", "company", "job_type").all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "category__name",
        "company__company_profile__name",
        "job_type__name",
        "location",
    ]
    search_fields = ["title"]
    ordering_fields = ["start_date", "pay"]

    def get_permissions(self):
        return []


class SingleJobView(generics.RetrieveAPIView):
    queryset = Job.objects.select_related("category", "company", "job_type").all()
    serializer_class = JobSerializer

    def get_permissions(self):
        return []


class DashboardJobView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsCompany]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "category__name",
        "company__company_profile__name",
        "job_type__name",
        "location",
    ]
    search_fields = ["title"]
    ordering_fields = ["start_date", "pay"]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Job.objects.select_related(
                "category", "company", "job_type"
            ).all()
            return queryset
        elif self.request.user.groups.filter(name="Company").exists():
            queryset = Job.objects.select_related(
                "category", "company", "job_type"
            ).filter(company=self.request.user)
            return queryset


class SingleDashboardJobView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsCompany]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Job.objects.select_related(
                "category", "company", "job_type"
            ).all()
            return queryset
        elif self.request.user.groups.filter(name="Company").exists():
            queryset = Job.objects.select_related(
                "category", "company", "job_type"
            ).filter(company=self.request.user)
            return queryset


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


class StatusView(generics.ListCreateAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class SingleStatusView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class ApplicationView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Application.objects.select_related("user", "job", "status").all()
            return queryset
        elif self.request.user.groups.filter(name="Company").exists():
            queryset = Application.objects.select_related(
                "user", "job", "status"
            ).filter(job__company=self.request.user)
            return queryset
        else:
            queryset = Application.objects.select_related(
                "user", "job", "status"
            ).filter(user=self.request.user)
            return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status=Status.objects.get(pk=1))


class SingleApplicationView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return [IsCompany]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = Application.objects.select_related("user", "job", "status").all()
            return queryset
        elif user.groups.filter(name="Company").exists():
            queryset = Application.objects.select_related(
                "user", "job", "status"
            ).filter(job__company=user)
            return queryset
        else:
            queryset = Application.objects.select_related(
                "user", "job", "status"
            ).filter(user=user)
            return queryset

    def perform_update(self, serializer):
        user = self.request.user
        application = self.get_object()
        if user.is_staff or application.job.company == user:
            updated_application = serializer.save()
            current_application_id = updated_application.id
            if updated_application.status.id == 2:
                JobAssignment.objects.get_or_create(
                    user=updated_application.user,
                    job=updated_application.job,
                    application=updated_application,
                    status=JobAssignmentStatus.objects.get(pk=1),
                )
                other_applications = Application.objects.filter(
                    job=updated_application.job
                ).exclude(id=current_application_id)
                other_applications.update(status_id=3)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff or instance.job.company == user:
            if hasattr(instance, "assignment"):
                instance.assignment.delete()
            instance.delete()


class JobAssignmentStatusView(generics.ListCreateAPIView):
    queryset = JobAssignmentStatus.objects.all()
    serializer_class = JobAssignmentStatusSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class SingleJobAssignmentStatusView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobAssignmentStatus.objects.all()
    serializer_class = JobAssignmentStatusSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permissions.IsAdminUser()]


class JobAssignmentView(generics.ListAPIView):
    serializer_class = JobAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Admin can see all assignments
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).all()
        elif user.groups.filter(name="Company").exists():
            # Companies can see assignments for jobs they created
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).filter(job__company=user)
        else:
            # Regular users can only see their own assignments
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).filter(user=user)


class SingleJobAssignmentView(generics.RetrieveUpdateAPIView):
    serializer_class = JobAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return JobAssignmentUpdateSerializer
        return JobAssignmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).all()
        elif user.groups.filter(name="Company").exists():
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).filter(job__company=user)
        else:
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).filter(user=user)


# Company endpoints for public listing
class CompanyView(generics.ListAPIView):
    """Public view to list all companies"""

    queryset = User.objects.filter(groups__name="Company").select_related(
        "company_profile"
    )
    serializer_class = CustomUserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["company_profile__name", "company_profile__industry"]
    ordering_fields = ["company_profile__name", "company_profile__established_date"]

    def get_permissions(self):
        return []


class SingleCompanyView(generics.RetrieveAPIView):
    """Public view to get a single company's details"""

    queryset = User.objects.filter(groups__name="Company").select_related(
        "company_profile"
    )
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        return []


# Add these simple views to TempiApp/views.py


class RatingView(generics.ListCreateAPIView):
    """List and create ratings"""

    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Show ratings user has given or received
        return Rating.objects.filter(
            models.Q(rater=self.request.user) | models.Q(rated_user=self.request.user)
        ).select_related("rater", "rated_user")


class SingleRatingView(generics.RetrieveUpdateDestroyAPIView):
    """View, update, or delete a rating (only your own)"""

    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow editing your own ratings
        return Rating.objects.filter(rater=self.request.user)


class UserRatingsView(generics.ListAPIView):
    """Public view of ratings for any user/company"""

    serializer_class = RatingSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return (
            Rating.objects.filter(rated_user_id=user_id)
            .select_related("rater", "rated_user")
            .order_by("-created_at")
        )

    def get_permissions(self):
        return []  # Public endpoint
