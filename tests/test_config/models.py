# from neomodel import StructuredNode, StringProperty, UniqueIdProperty, EmailProperty

from pyverless.crypto import PBKDF2PasswordHasher
from unittest.mock import MagicMock


hasher = PBKDF2PasswordHasher()

mock_user = MagicMock()
mock_user.email = 'user@users.com'
mock_user.password = hasher.encode('test-password')


class User(object):

    def __init__(self, email, password):
        self.email = email
        self.password = password

    @classmethod
    def create_user(cls, **kwargs):
        # Given a password, encode it before storing it
        mock_user.email = kwargs['email']
        mock_user.password = hasher.encode(kwargs['password'])

        return mock_user

    nodes = MagicMock()


# class User(StructuredNode):

#     # Properties
#     uid = UniqueIdProperty()
#     email = EmailProperty(unique_index=True, required=True)
#     password = StringProperty(required=True)
#     name = StringProperty(required=False)
#     phone = StringProperty(required=False)

#     @classmethod
#     def create_user(cls, **kwargs):
#         # Given a password, encode it before storing it
#         kwargs['password'] = hasher.encode(kwargs['password'])

#         return super(User, cls).create(kwargs).pop()
