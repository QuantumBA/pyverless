from logging import config, INFO, ERROR
from os import environ

from pythonjsonlogger.jsonlogger import JsonFormatter


def initialize_logger(
    logger_level: str = "DEBUG",
    environment: str = "dev",
    sentry_dns: str = None,
    aws_request_id: str = "default_aws_request_id",
):

    sentry_dns = environ.get("SENTRY_DNS", None) or sentry_dns

    formatter_config = {
        "format": "%(asctime)s : %(levelname)s : %(name)s : %(funcName)s : %(message)s",
        "datefmt": "%d-%m-%Y %I:%M:%S",
    }

    environ["AWS_REQUEST_ID"] = aws_request_id

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

    if sentry_dns:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_logging = LoggingIntegration(level=INFO, event_level=ERROR)
        sentry_sdk.init(
            dsn=sentry_dns,
            integrations=[sentry_logging],
            environment=environment,
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
