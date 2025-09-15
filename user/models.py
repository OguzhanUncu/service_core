from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from django.conf import settings
from django.contrib.gis.db import models as gis_models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} {self.last_name}"


class Address(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")

    # Location related
    house_number = models.CharField(_("House Number / Name"), max_length=50, blank=True, null=True)
    road = models.CharField(_("Street / Road"), max_length=255, blank=True, null=True)
    suburb = models.CharField(_("Suburb / Neighbourhood"), max_length=100, blank=True, null=True)
    district = models.CharField(_("District / County"), max_length=100, blank=True, null=True)
    city = models.CharField(_("City / Town"), max_length=100, blank=True, null=True)
    postcode = models.CharField(_("Postcode / ZIP"), max_length=20, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=100)
    label = models.CharField(_("Address Label"), max_length=50, blank=True, null=True)

    # Coordination
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    #Location
    location = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return f"{self.label or 'Address'} - {self.user}"
