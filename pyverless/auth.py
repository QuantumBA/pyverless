from pyverless.crypto import PBKDF2PasswordHasher
from pyverless.models import get_user_by_email


def authenticate(email, password):
    """
    Returns the user_id in case the user exists, None otherwise
    """
    hasher = PBKDF2PasswordHasher()

    # Get user by email
    user = get_user_by_email(email=email)

    if user and user.password:
        # Verify the password. Return User if it's valid
        valid_password = hasher.verify(password, user.password)

        if valid_password:
            return user

    return None
