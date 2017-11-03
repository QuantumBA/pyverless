from os import getenv

CORS_ORIGIN = getenv('CORS_ORIGIN', "*")
CORS_HEADERS = getenv('CORS_HEADERS', "*")
USER_MODEL = None
JWT_EXPIRY = float(getenv('JWT_EXPIRY', 300))
JWT_LEEWAY = int(getenv('JWT_LEEWAY', 60))
SECRET_KEY = getenv('SECRET_KEY')
JWT_ALGORITHM = getenv('JWT_ALGORITHM', 'HS256')
