from user.models import Address
from django.contrib.gis.geos import Point
import pytest

pytestmark = pytest.mark.django_db


def test_address_str_with_label(user):
    addr = Address.objects.create(
        user=user,
        label="Home",
        country="Turkey"
    )
    assert str(addr) == f"Home - {user}"

def test_address_str_without_label(user):
    addr = Address.objects.create(
        user=user,
        label=None,
        country="Turkey"
    )
    assert str(addr).startswith("Address - ")

def test_address_coordinates(user):
    addr = Address.objects.create(
        user=user,
        country="Turkey",
        latitude=41.123456,
        longitude=29.987654,
    )
    assert float(addr.latitude) == 41.123456
    assert float(addr.longitude) == 29.987654

def test_address_location_point(user):
    point = Point(29.9876, 41.1234)
    addr = Address.objects.create(
        user=user,
        country="Turkey",
        location=point
    )
    assert addr.location == point