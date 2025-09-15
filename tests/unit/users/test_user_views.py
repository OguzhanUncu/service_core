import pytest
from rest_framework.test import APIRequestFactory
from user.views import RegisterView
from django.contrib.auth import get_user_model

User = get_user_model()
pytestmark = pytest.mark.django_db

def test_register_view_creates_user():
    factory = APIRequestFactory()
    payload = {
        "email": "oguzhan@example.com",
        "username": "oguzhan",
        "password": "S3curePass!232",
        "password2": "S3curePass!232",
        "first_name": "Demo2",
        "last_name": "Uncu",
        "phone": "5551234565"
    }

    request = factory.post("/users/register/", payload, format="json")

    view = RegisterView.as_view()
    response = view(request)

    assert response.status_code == 201
    assert User.objects.filter(email="oguzhan@example.com").exists()


def test_register_view_rejects_short_password():
    factory = APIRequestFactory()
    payload = {
        "email": "shortpass@example.com",
        "username": "shorty",
        "password": "123",
        "password2": "123",
        "first_name": "Short",
        "last_name": "Pass",
        "phone": "5551234567"
    }

    request = factory.post("/auth/register/", payload, format="json")
    view = RegisterView.as_view()
    response = view(request)

    assert response.status_code == 400
    assert "password" in response.data
    assert any("at least 8 char" in msg.lower() for msg in response.data["password"])