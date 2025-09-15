from car.models import Car, Brand
from rest_framework import viewsets
from car.serializers import BrandSerializer, CarSerializer


class BrandModelViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class CarModelViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def get_queryset(self):
        return Car.objects.filter(user=self.request.user)