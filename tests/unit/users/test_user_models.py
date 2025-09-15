from django.contrib.auth import get_user_model
import pytest
from django.db import IntegrityError

User = get_user_model()
pytestmark = pytest.mark.django_db

def test_user(user):
    assert user.email == "test@example.com"
    assert str(user) == "testuser lastname"

def test_user_email_unique_constraint():
    User.objects.create_user(email="a@example.com", username="a")
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="a@example.com", username="b")