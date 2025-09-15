from rest_framework import serializers
from service.models import Service
from core.serializers import BaseModelSerializer
from user.serializers import AddressSerializer


class ServiceSerializer(BaseModelSerializer):
    hr_brands = serializers.SerializerMethodField()
    hr_address = serializers.SerializerMethodField()
    # can add more validation for polygons
    quick_polygon = serializers.ListField(
        child=serializers.ListField(
            child=serializers.ListField(
                child=serializers.FloatField(),
                min_length=2,
                max_length=2
            ),
            allow_empty=False
        ),
        required=False,
        allow_null=True,
        allow_empty=True
    )
    scheduled_polygon = serializers.ListField(
        child=serializers.ListField(
            child=serializers.ListField(
                child=serializers.FloatField(),
                min_length=2,
                max_length=2
            ),
            allow_empty=False
        ),
        required=False,
        allow_null=True,
        allow_empty=True
    )
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = '__all__'

    def get_hr_brands(self, obj):
        return [
            {
                "id": brand.id,
                "name": brand.name
            }
            for brand in obj.brands.all()
        ]

    def get_hr_address(self, obj):
        if obj.address:
            return AddressSerializer(obj.address).data
        return None

    def get_distance(self, obj):
        if hasattr(obj, "distance") and obj.distance:
            return f"{round(obj.distance.km, 2)}km"
        return None


class PointSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()