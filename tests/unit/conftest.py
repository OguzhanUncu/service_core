import factory
from django.contrib.auth import get_user_model
import pytest
from rest_framework.test import APIRequestFactory

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = "test@example.com"
    username = "testuser"
    last_name = "lastname"
    password = factory.PostGenerationMethodCall("set_password", "password123")

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def api_request(user):
    request_factory = APIRequestFactory()
    request = request_factory.post("/fake-url/")
    request.user = user
    return request
