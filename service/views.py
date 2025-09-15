from rest_framework import viewsets
from car.models import Brand
from service.models import Service
from service.serializers import ServiceSerializer, PointSerializer
from service.service import ServiceService
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from user.models import Address


class ServiceModelViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    accepted_http_methods = ("GET", "POST", "PUT", "DELETE", "OPTIONS")

    def get_queryset(self):
        return Service.objects.filter(created_by=self.request.user).select_related(
            "address",
            "address__user",
            "address__created_by",
            "address__updated_by",
            "created_by",
            "updated_by",
        ).prefetch_related("brands")

    def create(self, request, *args, **kwargs):
        data = ServiceService(request).create()
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        service_id = self.kwargs.get(self.lookup_field)
        data = ServiceService(request).update(service_id)
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            ServiceService(request=self.request).delete(self.kwargs.get("pk"))
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def get_scheduled_service(self, request):
        if not (request.query_params.get("address_id", None) and request.query_params.get("brand_id", None)):
            return Response({"error": "address_id and brand_id required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not Address.objects.filter(user=request.user, id=request.query_params.get("address_id")).exists():
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

        if not Brand.objects.filter(id=request.query_params.get("brand_id", None)).exists():
            return Response({"error": "Brand id is invalid"},
                            status=status.HTTP_400_BAD_REQUEST)

        address_instance = Address.objects.filter(user=request.user, id=request.query_params.get("address_id")).first()
        qs = ServiceService.find_service(address_instance.longitude,
                                         address_instance.latitude,
                                         request.query_params.get("brand_id", None),
                                         'scheduled_polygons')
        if not qs.exists():
            return self.return_none_qs()
        return self.paginate_return_data(qs)

    @action(detail=False, methods=["get"])
    def get_quick_service(self, request):
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        brand_id = request.query_params.get("brand_id")

        if not (latitude and longitude and brand_id):
            return Response({"error": "latitude,longitude and brand_id required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not Brand.objects.filter(id=brand_id).exists():
            return Response({"error": "brand id is invalid"},
                            status=status.HTTP_400_BAD_REQUEST)

        point_serializer = PointSerializer(data={"latitude": latitude, "longitude": longitude})
        point_serializer.is_valid(raise_exception=True)

        serialized_data = point_serializer.data
        qs = ServiceService.find_service(serialized_data.get('longitude'),
                                         serialized_data.get('latitude'),
                                         brand_id,
                                         'quick_polygons')
        if not qs:
            return self.return_none_qs()
        return self.paginate_return_data(qs)

    def paginate_return_data(self, qs):
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": self.request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True, context={"request": self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def return_none_qs(self):
            return Response(
                {"detail": "Could not find an available service."},
                status=status.HTTP_404_NOT_FOUND
            )
