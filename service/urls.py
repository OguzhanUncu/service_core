from django.urls import path
from rest_framework.routers import DefaultRouter
from service.views import ServiceModelViewSet

router = DefaultRouter()
router.register('service', ServiceModelViewSet, basename='service')

urlpatterns = []
urlpatterns += router.urls