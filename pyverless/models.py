import importlib
from pyverless.config import settings


def get_user_model():
    try:
        module, user_model = settings.USER_MODEL.rsplit('.', 1)
    except AttributeError:
        raise AttributeError('USER_MODEL configuration variable not set or invalid')
    return getattr(importlib.import_module(module), user_model)


def get_user_by_email(email):
    return getattr(get_user_model(), settings.MODEL_MANAGER).get_or_none(email=email)
