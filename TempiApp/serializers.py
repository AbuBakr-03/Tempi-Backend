# TempiApp/serializers.py
from django.contrib.auth.models import Group, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from .models import (
    UserProfile,
    Category,
    Company,
    JobType,
    Job,
    Wishlist,
    Application,
    Status,
    JobAssignmentStatus,
    JobAssignment,
)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "name",
            "bio",
            "skill",
            "experience",
            "location",
            "phone_number",
            "profile_picture",
            "resume",
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        token["is_recruiter"] = user.groups.filter(name="Recruiter").exists()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({"user": CustomUserSerializer(self.user).data})
        return data


class CustomUserCreateSerializer(UserCreateSerializer):
    group = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ("group",)

    def validate(self, attrs):
        # Remove group from attrs before parent validation
        group_name = attrs.pop("group", None)
        # Call parent validation
        validated_data = super().validate(attrs)
        # Add group back to validated data for use in create method
        if group_name:
            validated_data["group"] = group_name
        return validated_data

    def create(self, validated_data):
        group_name = validated_data.get("group")
        validated_data.pop("group", None)
        user = super().create(validated_data)
        if group_name:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    job_type = JobTypeSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True)
    job_type_id = serializers.IntegerField(write_only=True)
    recruiter = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "location",
            "pay",
            "description",
            "qualifications",
            "responsibilities",
            "nice_to_haves",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "category_id",
            "category",
            "company_id",
            "company",
            "job_type_id",
            "job_type",
            "recruiter",
        ]


class WishlistSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "job_id", "job"]


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):
    status = StatusSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    job_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "location",
            "resume",
            "status",
            "job",
            "job_id",
        ]


class JobAssignmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAssignmentStatus
        fields = "__all__"


class JobAssignmentSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    user = CustomUserSerializer(read_only=True)
    application = ApplicationSerializer(read_only=True)

    class Meta:
        model = JobAssignment
        fields = [
            "id",
            "user",
            "job",
            "application",
            "status",
        ]


class JobAssignmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAssignment
        fields = ["status"]
