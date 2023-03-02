import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from djoser.serializers import UserSerializer

from users.models import CustomUser


class CustomUserSerializer(UserSerializer):

    def create(self, validated_data):
        user = CustomUser(
            phone_number=validated_data["phone_number"],
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "phone_number",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)
