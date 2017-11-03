import importlib
from pyverless.crypto import PBKDF2PasswordHasher
from pyverless.config import settings


def get_user_model():
    module, user_model = settings.USER_MODEL.rsplit('.', 1)
    return getattr(importlib.import_module(module), user_model)


def get_user_by_email(email):
    return get_user_model().nodes.get_or_none(email=email)


def authenticate(email, password):
    """
    Returns the user_id in case the user exists, None otherwise
    """
    hasher = PBKDF2PasswordHasher()

    # Get user by email
    user = get_user_by_email(email=email)

    if user:
        # Verify the password. Return User if it's valid
        valid_password = hasher.verify(password, user.password)

        if valid_password:
            return user

    return None
