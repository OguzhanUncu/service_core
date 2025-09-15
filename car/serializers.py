from rest_framework import serializers
from core.serializers import BaseModelSerializer
from car.models import Brand, Car


class BrandSerializer(BaseModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CarSerializer(BaseModelSerializer):
    hr_brand = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = ["id", "brand", "hr_brand", "model_name", "registration_number", "year",
                  "color", "vin_number"]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def get_hr_brand(self, obj):
        return str(obj.brand)
