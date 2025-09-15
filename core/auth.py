from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

UserModel = get_user_model()


class ServiceAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            validate_email(username)
            user = UserModel.objects.get(email__iexact=username)
        except ValidationError:
            try: # try username
                user = UserModel.objects.get(username__iexact=username)
            except UserModel.DoesNotExist:
                return None
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None