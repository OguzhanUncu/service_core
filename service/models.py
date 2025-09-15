from django.db import models
from car.models import Brand
from user.models import Address
from core.models import BaseModel


class Service(BaseModel):
    name = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)
    brands = models.ManyToManyField(Brand, related_name="services")
    scheduled_polygon = models.JSONField(default=dict, blank=True, null=True)
    quick_polygon = models.JSONField(default=dict, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
