from django.db import models
from core.models import BaseModel
from django.conf import settings


class Brand(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Car(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cars")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="cars")
    model_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    vin_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.registration_number} - {self.brand.name} {self.model_name}"
