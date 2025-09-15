from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from user.models import Address
from user.service import GeoCoder
from core.serializers import BaseModelSerializer
from django.contrib.gis.geos import Point

User = get_user_model()


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "is_superuser", "is_staff", "groups", "user_permissions", "last_login",)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "phone",
                  "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "passwords do not match"})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2")
        return User.objects.create_user(password=password, **validated_data)


class AddressSerializer(BaseModelSerializer):
    hr_user = serializers.SerializerMethodField()

    class Meta:
        model = Address
        exclude = ("user",)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data = self.set_coordinates(validated_data)
        validated_data["location"] = Point(float(validated_data.get("longitude")), float(validated_data.get("latitude")))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.set_coordinates(validated_data)
        validated_data["location"] = Point(float(validated_data.get("longitude")), float(validated_data.get("latitude")))
        return super().update(instance, validated_data)

    def set_coordinates(self, validated_data):
        if not validated_data.get("latitude") or not validated_data.get("longitude"):
            lat, long = GeoCoder(validated_data=validated_data).get_coordinates()
            validated_data["latitude"] = lat
            validated_data["longitude"] = long
        return validated_data

    def get_hr_user(self, obj):
        return str(obj.user) if obj.user else None