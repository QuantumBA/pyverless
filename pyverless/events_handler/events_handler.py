import logging
from abc import abstractmethod, ABC

from pyverless.utils.logging import initialize_logger

logger = logging.getLogger("pyverless")


class EventsHandler(ABC):

    event_parser = None
    event = None
    context = None
    event_parsed = None
    response = None

    dependency_container = None

    def __init__(self, dependency_container=None):
        self.dependency_container = dependency_container

    def lambda_handler(self, event, context):
        try:
            self.event = event
            self.context = context

            logger.info({"event": self.event, "message": "lambda started"})

            self.event_parsed = (
                self.event_parser(self.event) if self.event_parser else None
            )

            self.response = self.execute_lambda_code()

        except Exception as ex:
            self.process_unhandled_error(error=ex)

        return self.render_response()

    def execute_lambda_code(self):
        return self.perform_action()

    @abstractmethod
    def perform_action(self):
        pass

    def process_unhandled_error(self, error):
        logger.exception(error)
        raise error

    def render_response(self):
        return self.response

    @classmethod
    def as_handler(
        cls,
        logger_level: str = "DEBUG",
        sentry_dns: str = None,
        environment: str = "test",
        dependency_container=None,
    ):
        """
        Returns a lambda handler function.
        """

        def handler(event, context):

            initialize_logger(
                logger_level=logger_level,
                sentry_dns=sentry_dns,
                environment=environment,
                aws_request_id=context.aws_request_id,
            )

            self = cls(dependency_container=dependency_container)
            return self.lambda_handler(event, context)

        return handler
