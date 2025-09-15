from django.urls import path
from rest_framework.routers import DefaultRouter
from car.views import BrandModelViewSet, CarModelViewSet

router = DefaultRouter()
router.register('brand', BrandModelViewSet, basename='brand')
router.register('car', CarModelViewSet, basename='car')

urlpatterns = []

urlpatterns += router.urls