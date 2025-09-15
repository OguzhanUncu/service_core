from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderServiceError, GeocoderTimedOut


class GeoCoder:
    def __init__(self, validated_data: dict):
        self.validated_data = validated_data
        self.geolocator = Nominatim(user_agent="oguzhan-geocoder-demo/0.1")

        # Rate limit, retry mechanism
        self.geocode = RateLimiter(
            self.geolocator.geocode,
            min_delay_seconds=1,
            max_retries=3,
            error_wait_seconds=2.0,
            swallow_exceptions=False,
        )

    def _build_address_string(self):
        parts = [
            self.validated_data.get("house_number"),
            self.validated_data.get("road"),
            self.validated_data.get("suburb"),
            self.validated_data.get("district"),
            self.validated_data.get("city"),
            self.validated_data.get("postcode"),
            self.validated_data.get("country"),
        ]
        return ", ".join([part for part in parts if part])

    def get_coordinates(self):
        address = self._build_address_string()

        if not address or len(address.split(",")) < 2: # if not data
            return None, None

        try:
            location = self.geocode(address)
            if location:
                return location.latitude, location.longitude
        except (GeocoderServiceError, GeocoderTimedOut) as e:
            print(f"Geocoding error: {e}")
        return None, None
