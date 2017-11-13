from pyverless.crypto import PBKDF2PasswordHasher
from pyverless.serializers import Serializer

hasher = PBKDF2PasswordHasher()


class User:

    class objects:

        def get_or_none(**kwargs):
            return User(email='one@users.com', password='test-password')

        def all():
            return [
                User(email='one@users.com', password='test-password'),
                User(email='two@users.com', password='test-password')
            ]

    def __init__(self, email, password, uid="b89ee4a1d9ac4dd5aeb242264968aa4e"):
        self.email = email
        self.password = hasher.encode(password)
        self.uid = uid

    def save(self):
        return self

    def delete(self):
        return None


class UserSerializer(Serializer):
    include = ['email']
