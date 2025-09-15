import pytest
from car.models import Brand
from car.serializers import BrandSerializer

pytestmark = pytest.mark.django_db

def test_brand_serializer_create_sets_user(api_request):
    data = {"name": "Toyota"}
    serializer = BrandSerializer(data=data, context={"request": api_request})
    assert serializer.is_valid(), serializer.errors
    brand = serializer.save()
    assert brand.name == "Toyota"
    assert brand.created_by == api_request.user
    assert brand.updated_by == api_request.user


def test_brand_serializer_output_includes_hr_fields(api_request):
    brand = Brand.objects.create(name="Mazda", created_by=api_request.user, updated_by=api_request.user)
    serializer = BrandSerializer(brand, context={"request": api_request})
    data = serializer.data
    assert data["name"] == "Mazda"
    assert data["hr_created_by"] == str(api_request.user)
    assert data["hr_updated_by"] == str(api_request.user)

