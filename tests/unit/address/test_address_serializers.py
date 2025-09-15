import pytest
from user.serializers import AddressSerializer
from django.contrib.gis.geos import Point

pytestmark = pytest.mark.django_db


def test_address_serializer_sets_coordinates(mocker, api_request, user):
    mocker.patch(
        "user.service.GeoCoder.get_coordinates",
        return_value=(41.123456, 29.987654)
    )

    payload = {
        "house_number": "221B",
        "road": "Baker Street",
        "district": "Greater London",
        "city": "London",
        "postcode": "NW1 6XE",
        "country": "United Kingdom",
        "label": "My Home"
        # not including latitude, longitude to fetch from geo class
    }

    serializer = AddressSerializer(data=payload, context={"request": api_request})
    assert serializer.is_valid(), serializer.errors
    address = serializer.save()

    assert address.latitude == 41.123456
    assert address.longitude == 29.987654
    assert isinstance(address.location, Point)
    assert address.user == user
