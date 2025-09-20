# TempiApp/serializers.py
from django.contrib.auth.models import Group, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from .models import (
    UserProfile,
    CompanyProfile,
    Category,
    JobType,
    Job,
    Wishlist,
    Application,
    Status,
    JobAssignmentStatus,
    JobAssignment,
    Rating,
)
from django.db import models


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
            "has_best_tempi_badge",
            "badge_earned_date",
        ]


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = [
            "name",
            "logo",
            "description",
            "website",
            "location",
            "phone_number",
            "email",
            "established_date",
            "employee_count",
            "industry",
            "has_best_employer_badge",
            "badge_earned_date",
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    company_profile = CompanyProfileSerializer(read_only=True)
    user_type = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile",
            "company_profile",
            "user_type",
            "average_rating",
            "total_ratings",
        ]

    def get_user_type(self, obj):
        return "company" if obj.groups.filter(name="Company").exists() else "user"

    def get_average_rating(self, obj):
        ratings = obj.received_ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / len(ratings), 1)
        return 0

    def get_total_ratings(self, obj):
        return obj.received_ratings.count()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        token["is_company"] = user.groups.filter(name="Company").exists()
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

            # Create appropriate profile after group assignment
            if group_name == "Company":
                CompanyProfile.objects.get_or_create(user=user)
            else:
                UserProfile.objects.get_or_create(user=user)
        else:
            # Create regular user profile for users without group
            UserProfile.objects.get_or_create(user=user)

        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = "__all__"


class CompanyBasicSerializer(serializers.ModelSerializer):
    """Basic company info for use in job listings"""

    name = serializers.CharField(source="company_profile.name", read_only=True)
    logo = serializers.ImageField(source="company_profile.logo", read_only=True)
    location = serializers.CharField(source="company_profile.location", read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "logo", "location"]


class JobSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    company = CompanyBasicSerializer(read_only=True)
    job_type = JobTypeSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False)
    job_type_id = serializers.IntegerField(write_only=True)

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
        ]

    def create(self, validated_data):
        # Set the company to the current user (who should be a company user)
        validated_data["company"] = self.context["request"].user
        return super().create(validated_data)


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
    status_id = serializers.IntegerField(write_only=True, required=False)

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
            "status_id",
        ]

    def validate(self, data):
        """
        Validate application status transitions
        """
        request = self.context.get("request")
        if not request:
            return data

        # If this is an update operation
        if self.instance:
            new_status_id = data.get('status_id')
            if new_status_id:
                current_status = self.instance.status.id
                
                # Validate status transitions
                if current_status == 2:  # Already approved
                    raise serializers.ValidationError(
                        "Cannot change status of an approved application"
                    )
                
                if current_status == 3:  # Already rejected
                    raise serializers.ValidationError(
                        "Cannot change status of a rejected application"
                    )
                
                # Only allow transitions from pending (1) or shortlisted (4)
                if current_status not in [1, 4]:
                    raise serializers.ValidationError(
                        "Invalid status transition"
                    )

        return data


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


class RatingSerializer(serializers.ModelSerializer):
    rater_name = serializers.CharField(source="rater.username", read_only=True)
    rated_user_name = serializers.CharField(
        source="rated_user.username", read_only=True
    )
    rater_type = serializers.SerializerMethodField()
    rated_user_type = serializers.SerializerMethodField()
    rated_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Rating
        fields = [
            "id",
            "rating",
            "comment",
            "rated_user_id",
            "rater_name",
            "rated_user_name",
            "rater_type",
            "rated_user_type",
            "created_at",
        ]

    def validate_rated_user_id(self, value):
        request = self.context.get("request")
        if request and request.user.id == value:
            raise serializers.ValidationError("You cannot rate yourself")
        return value

    def validate(self, data):
        """
        Validate that the rater and rated user have completed a task together
        """
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request context is required")
        
        rater = request.user
        rated_user_id = data.get('rated_user_id')
        
        # Get the rated user object
        from .models import User
        try:
            rated_user = User.objects.get(id=rated_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Rated user does not exist")
        
        # Check if they can rate each other based on completed job assignments
        from .models import Rating
        if not Rating.can_rate_each_other(rater, rated_user):
            raise serializers.ValidationError(
                "You can only rate users/companies with whom you have completed a task. "
                "Both parties must have worked together on a completed job assignment."
            )
        
        return data

    def create(self, validated_data):
        validated_data["rater"] = self.context["request"].user
        return super().create(validated_data)

    def get_rater_type(self, obj):
        return obj.get_rater_type()

    def get_rated_user_type(self, obj):
        return obj.get_rated_user_type()
