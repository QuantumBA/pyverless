from datetime import datetime
from calendar import timegm
import time
import pytest

from pyverless.crypto import PBKDF2PasswordHasher, get_json_web_token, decode_json_web_token, is_expired
from pyverless.exceptions import Unauthorized


class TestCrypto():

    def setup_class(self):
        self.hasher = PBKDF2PasswordHasher()
        self.password = '$Sup3r-s3cr3t-p4ssw0rd!'
        self.token_payload = {
            "uid": "e845205a36ed42efa0dcc5d35d343722",
            "email": "user@users.com",
        }

    def test_encode_and_verify_password(self):
        encoded_password = self.hasher.encode(self.password)

        assert self.hasher.verify(self.password, encoded_password)

    def test_json_web_tokens(self):

        # Create a new json web token
        token = get_json_web_token(self.token_payload)

        # Check that decode works
        assert self.token_payload == decode_json_web_token(token)

        # An EXPIRED token CAN'T be decoded
        token = get_json_web_token(self.token_payload, expiry=1)
        time.sleep(2)

        with pytest.raises(Unauthorized):
            decode_json_web_token(token, leeway=0)

        # A BOGUS token CAN'T be decoded
        with pytest.raises(Unauthorized):
            decode_json_web_token('this-is-a-fake-token')

    def test_is_expired(self):
        now = timegm(datetime.utcnow().utctimetuple())
        expiry = now + 100  # Expiry is 100 seconds away from now

        assert not is_expired(expiry)
