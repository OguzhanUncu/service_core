from service.models import Service
from service.serializers import ServiceSerializer
from user.serializers import AddressSerializer
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
import json
from service.utils import redis_client
from django.contrib.gis.geos import Point as GeoPoint
from shapely.geometry import Point, Polygon
from django.contrib.gis.db.models.functions import Distance


class ServiceService:
    """ Service class for service operations """

    def __init__(self, request):
        self.request = request
        self.service_data = self.request.data if self.request.data else {}
        self.address_data = self.service_data.pop("address", None)

    @transaction.atomic
    def create(self):
        """
        Creates a service and its associated address with transactional integrity. It
        validates and saves the address (if provided) and service data. Additionally,
        it updates cached polygons for the created service.
        """
        try:
            if self.address_data:
                address_serializer = AddressSerializer(data=self.address_data, context={"request": self.request})
                address_serializer.is_valid(raise_exception=True)
                address_serializer.save()
                self.service_data["address"] = address_serializer.data.get("id", None)

            service_serializer = ServiceSerializer(data=self.service_data, context={"request": self.request})
            service_serializer.is_valid(raise_exception=True)
            service_instance = service_serializer.save()

            self.update_cached_polygons(service_instance.id,
                                        service_instance.quick_polygon,
                                        service_instance.scheduled_polygon)
        except IntegrityError as e:
            raise ValidationError({"Integrity Error": str(e)})
        return service_serializer.data

    @transaction.atomic
    def update(self, service_id, partial=False):
        """
        Updates the details of a service instance with provided data
        updates cached polygons
        """
        service_instance = get_object_or_404(Service, pk=service_id)
        try:
            if self.address_data:
                address_serializer = AddressSerializer(instance=service_instance.address,
                                                       data=self.address_data,
                                                       partial=partial,
                                                       context={"request": self.request})
                address_serializer.is_valid(raise_exception=True)
                address_serializer.save()

            service_serializer = ServiceSerializer(instance=service_instance,
                                                   data=self.service_data,
                                                   context={"request": self.request},
                                                   partial=partial)
            service_serializer.is_valid(raise_exception=True)
            service_instance = service_serializer.save()

            self.update_cached_polygons(service_instance.id,
                                        service_instance.quick_polygon,
                                        service_instance.scheduled_polygon)

        except IntegrityError as e:
            raise ValidationError({"Integrity Error": str(e)})
        return service_serializer.data

    @transaction.atomic
    def delete(self, service_id):
        instance = self.get_object(service_id=service_id)
        instance.address.delete()
        ServiceCacheService.delete_polygons(instance.id)
        instance.delete()

    @staticmethod
    def get_object(service_id):
        return get_object_or_404(Service, pk=service_id)

    @staticmethod
    def update_cached_polygons(service_id, quick_polygon, scheduled_polygon):


        ServiceCacheService.cache_quick_polygon(service_id, quick_polygon)
        ServiceCacheService.cache_scheduled_polygon(service_id, scheduled_polygon)

    @staticmethod
    def find_service(longitude, latitude, car_brand, polygon_type="scheduled_polygons"):
        if not (latitude or latitude):
            return Service.objects.none()

        user_geo_point = GeoPoint(float(longitude), float(latitude), srid=4326)
        user_shape_point = Point(float(longitude), float(latitude))

        matching_service_ids = []

        for service_id, polygon_json in redis_client.hscan_iter(polygon_type):
            polygon_coords = json.loads(polygon_json)
            polygon = Polygon(polygon_coords[0])

            if polygon.contains(user_shape_point):
                matching_service_ids.append(int(service_id))

        if not matching_service_ids:
            return Service.objects.none()

        queryset = (
            Service.objects
            .filter(id__in=matching_service_ids,
                    brands=car_brand)
            .select_related(
                "address",
                "address__user",
                "address__created_by",
                "address__updated_by",
                "created_by",
                "updated_by",
            ).prefetch_related("brands")
            .filter(address__location__isnull=False)
            .annotate(distance=Distance("address__location", user_geo_point))  # db level order by
            .order_by("distance")
        )

        return queryset


class ServiceCacheService:

    @staticmethod
    def cache_quick_polygon(service_id, quick_polygon):
        if quick_polygon:
            geojson_str = json.dumps(quick_polygon)
            redis_client.hset("quick_polygons", service_id, geojson_str)
        else:
            redis_client.hdel("quick_polygons", service_id)

    @staticmethod
    def cache_scheduled_polygon(service_id, scheduled_polygon):
        if scheduled_polygon:
            geojson_str = json.dumps(scheduled_polygon)
            redis_client.hset("scheduled_polygons", service_id, geojson_str)
        else:
            redis_client.hdel("scheduled_polygons", service_id)

    @staticmethod
    def delete_polygons(service_id):
        redis_client.hdel("quick_polygons", service_id)
        redis_client.hdel("scheduled_polygons", service_id)