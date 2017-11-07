import base64
from calendar import timegm
import hashlib
import hmac
import jwt
import random
import time
from datetime import datetime

from pyverless.exceptions import Unauthorized
from pyverless.config import settings


def get_json_web_token(payload, expires=True, expiry=settings.JWT_EXPIRY):
    """
    Returns a JWT given a payload.
    """
    if expires:
        # This is how PyJwt computes now, check:
        # https://github.com/jpadilla/pyjwt/blob/master/jwt/api_jwt.py#L153
        now = timegm(datetime.utcnow().utctimetuple())
        payload['exp'] = now + int(expiry)

    return jwt.encode(payload, settings.SECRET_KEY, settings.JWT_ALGORITHM).decode('utf-8')


def decode_json_web_token(token, leeway=settings.JWT_LEEWAY):
    """
    Decode a JWT. Leeway time may be provided.
    """
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, leeway=leeway, algorithms=[settings.JWT_ALGORITHM])
    except jwt.exceptions.DecodeError:
        raise Unauthorized()
    except jwt.exceptions.ExpiredSignatureError:
        raise Unauthorized()

    return decoded


def is_expired(expiry):
    """
    Check if the expiry seconds provided is before or after now. This code is
    based on how jwt checks for expiry:
    https://github.com/jpadilla/pyjwt/blob/master/jwt/api_jwt.py#L153
    """
    now = timegm(datetime.utcnow().utctimetuple())
    return expiry < now


# This code is a mashup of the code Django uses to encode and verify passwords,
# and it can be found here:
# https://github.com/django/django/blob/master/django/contrib/auth/hashers.py
# https://github.com/django/django/blob/master/django/utils/crypto.py
def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Return a securely generated random string.
    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    random.seed(
        hashlib.sha256(
            ('%s%s%s' % (random.getstate(), time.time(), settings.SECRET_KEY)).encode()
        ).digest()
    )
    return ''.join(random.choice(allowed_chars) for i in range(length))


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    val1 = val1.encode('utf-8', 'strict')
    val2 = val2.encode('utf-8', 'strict')
    return hmac.compare_digest(val1, val2)


def pbkdf2(password, salt, iterations, dklen=0, digest=None):
    """Return the hash of password using pbkdf2."""
    if digest is None:
        digest = hashlib.sha256
    if not dklen:
        dklen = None
    password = password.encode('utf-8', 'strict')
    salt = salt.encode('utf-8', 'strict')
    return hashlib.pbkdf2_hmac(digest().name, password, salt, iterations, dklen)


class PBKDF2PasswordHasher():
    """
    Secure password hashing using the PBKDF2 algorithm (recommended)
    Configured to use PBKDF2 + HMAC + SHA256.
    The result is a 64 byte binary string.  Iterations may be changed
    safely but you must rename the algorithm if you change SHA256.
    """
    algorithm = "pbkdf2_sha256"
    iterations = 100000
    digest = hashlib.sha256

    def encode(self, password, salt=None, iterations=None):
        assert password is not None
        if not salt:
            salt = get_random_string()
        if not iterations:
            iterations = self.iterations

        hash = pbkdf2(password, salt, iterations, digest=self.digest)
        hash = base64.b64encode(hash).decode('ascii').strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def verify(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt, int(iterations))
        return constant_time_compare(encoded, encoded_2)
