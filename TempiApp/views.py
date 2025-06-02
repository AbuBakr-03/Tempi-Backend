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
    ApplicationSerializer,
    StatusSerializer,
    JobAssignmentSerializer,
    JobAssignmentStatusSerializer,
    JobAssignmentUpdateSerializer,
)
from .models import (
    UserProfile,
    Category,
    Company,
    Job,
    JobType,
    Wishlist,
    Application,
    Status,
    JobAssignmentStatus,
    JobAssignment,
)

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


class JobView(generics.ListAPIView):
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


class DashboardJobView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [isRecruiter()]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category__name", "company__name", "job_type__name", "location"]
    search_fields = ["title"]
    ordering_fields = ["start_date", "pay"]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Job.objects.select_related(
                "category", "company", "job_type"
            ).all()
            return queryset
        elif self.request.user.groups.filter(name="Recruiter").exists():
            queryset = Job.objects.select_related(
                "category", "company", "job_type"
            ).filter(recruiter=self.request.user)


class SingleDashboardJobView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [isRecruiter()]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Job.objects.select_related(
                "category", "company", "job_type"
            ).all()
            return queryset
        elif self.request.user.groups.filter(name="Recruiter").exists():
            queryset = Job.objects.select_related(
                "category", "company", "job_type"
            ).filter(recruiter=self.request.user)


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
        elif self.request.user.groups.filter(name="Recruiter").exists():
            queryset = Application.objects.select_related(
                "user", "job", "status"
            ).filter(job__recruiter=self.request.user)
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
        return [isRecruiter()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = Application.objects.select_related("user", "job", "status").all()
            return queryset
        elif user.groups.filter(name="Recruiter").exists():
            queryset = Application.objects.select_related(
                "user", "job", "status"
            ).filter(job__recruiter=user)
            return queryset
        else:
            queryset = Application.objects.select_related(
                "user", "job", "status"
            ).filter(user=user)
            return queryset

    def perform_update(self, serializer):
        user = self.request.user
        application = self.get_object()
        if user.is_staff or application.job.recruiter == user:
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
                other_applications.update(status_id=3)  # Moved inside the if block

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff or instance.job.recruiter == user:
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
        elif user.groups.filter(name="Recruiter").exists():
            # Recruiters can see assignments for jobs they created
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).filter(job__recruiter=user)
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
        elif user.groups.filter(name="Recruiter").exists():
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).filter(job__recruiter=user)
        else:
            return JobAssignment.objects.select_related(
                "user", "job", "application"
            ).filter(user=user)
