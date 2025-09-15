from django.urls import path
from user.views import MeView, RegisterView, AddressModelViewSet

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'address', AddressModelViewSet, basename='address')

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
]

urlpatterns += router.urls