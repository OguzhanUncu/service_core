import pytest
from user.service import GeoCoder

@pytest.fixture
def address_data():
    return {
        "house_number": "221B",
        "road": "Baker Street",
        "suburb": "",
        "district": "Greater London",
        "city": "London",
        "postcode": "NW1 6XE",
        "country": "United Kingdom"
    }

def test_geocoder_returns_coordinates(mocker, address_data):
    mock_location = mocker.Mock()
    mock_location.latitude = 51.5
    mock_location.longitude = -0.1

    mocker.patch("user.service.Nominatim.geocode", return_value=mock_location)

    geocoder = GeoCoder(address_data)
    lat, lon = geocoder.get_coordinates()

    assert lat == 51.5
    assert lon == -0.1

