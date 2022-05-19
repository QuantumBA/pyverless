from logging import config, getLogger, INFO, ERROR
from os import environ
from pyverless.config import settings


test_env = "TEST_ENV" in environ
logger_level = environ.get("LOGGER_LEVEL", "DEBUG")

formatter_config = {
    "format": "%(asctime)s : %(levelname)s : %(name)s : %(funcName)s : %(message)s",
    "datefmt": "%d-%m-%Y %I:%M:%S",
}


if not test_env:

    from pythonjsonlogger.jsonlogger import JsonFormatter

    class CustomJsonFormatter(JsonFormatter):
        aws_request_id = None

        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(
                log_record, record, message_dict
            )
            if self.aws_request_id is None and "AWS_REQUEST_ID" in environ:
                self.aws_request_id = environ["AWS_REQUEST_ID"]
            log_record["aws_request_id"] = (
                self.aws_request_id if self.aws_request_id else "default_aws_request_id"
            )

    formatter_config["()"] = CustomJsonFormatter

    if settings.USE_SENTRY:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_logging = LoggingIntegration(level=INFO, event_level=ERROR)
        sentry_sdk.init(
            dsn=settings.SENTRY_DNS,
            integrations=[sentry_logging],
            environment=settings.STAGE,
        )

config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "pyverless": {
                "handlers": ["handler_for_pyverless"],
                "level": logger_level,
                "propagate": False,
            }
        },
        "handlers": {
            "handler_for_pyverless": {
                "formatter": "formatter_for_pyverless",
                "class": "logging.StreamHandler",
                "level": logger_level,
            }
        },
        "formatters": {"formatter_for_pyverless": formatter_config},
    }
)

logger = getLogger("pyverless")
