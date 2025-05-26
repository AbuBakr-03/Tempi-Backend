from django.contrib.auth.models import Group, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer


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

        data.update(
            {
                "user": {
                    "id": self.user.id,
                    "username": self.user.username,
                    "email": self.user.email,
                    "is_staff": self.user.is_staff,
                    "is_superuser": self.user.is_superuser,
                    "is_recruiter": self.user.groups.filter(name="Recruiter").exists(),
                }
            }
        )

        return data


class CustomUserCreateSerializer(UserCreateSerializer):
    group = serializers.CharField(
        write_only=True, required=False, allow_null=True, allow_blank=True
    )

    class Meta(UserCreateSerializer.Meta):
        model = User
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
