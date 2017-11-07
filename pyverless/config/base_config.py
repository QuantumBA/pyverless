from os import getenv


USER_MODEL = getenv('USER_MODEL', None)
SECRET_KEY = getenv('SECRET_KEY', None)

CORS_ORIGIN = getenv('CORS_ORIGIN', "*")
CORS_HEADERS = getenv('CORS_HEADERS', "*")

JWT_EXPIRY = getenv('JWT_EXPIRY', 300)
JWT_LEEWAY = getenv('JWT_LEEWAY', 60)
JWT_ALGORITHM = getenv('JWT_ALGORITHM', 'HS256')

WARMUP_LOG = getenv('WARMUP_LOG', True)
