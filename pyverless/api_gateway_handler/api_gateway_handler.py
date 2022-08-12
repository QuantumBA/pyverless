import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Type

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

from pyverless.events_handler.events_handler import EventsHandler

logger = logging.getLogger("pyverless")


@dataclass
class ApiGatewayResponse:
    body: Dict
    status_code: int
    headers: Dict = None


@dataclass
class ErrorHandler:
    exception: Type[Exception]
    status_code: int
    msg: str = None
    error_code: int = None

    def is_my_exception(self, ex) -> bool:
        return type(ex) == self.exception

    def generate_error_message(self, ex) -> Dict:
        message = self.msg if self.msg else str(ex)
        error_dict = {"message": message}
        if self.error_code:
            error_dict["error_code"] = self.error_code
        return error_dict


class ApiGatewayHandler(EventsHandler, ABC):
    success_code = 200

    event_parsed: APIGatewayProxyEvent = None
    event_parser = APIGatewayProxyEvent

    error_handlers: List[ErrorHandler] = []

    def execute_lambda_code(self):
        logger.info(
            {
                "type": "REQUEST_STARTED",
                "path": self.event_parsed.path,
                "headers": self.event_parsed.headers,
                "method": self.event_parsed.http_method,
                "message": "request started",
            }
        )

        try:

            response_body = self.perform_action()

            response = ApiGatewayResponse(
                status_code=self.success_code, body=response_body
            )

        except Exception as ex:
            response = self.process_error(exception=ex)

        logger.info(
            {
                "type": "REQUEST_FINISHED",
                "message": "request finished",
                "status_code": response.status_code,
            }
        )

        return response

    def process_error(self, exception):
        for handler in self.error_handlers:
            if handler.is_my_exception(exception):
                return ApiGatewayResponse(
                    status_code=handler.status_code,
                    body=handler.generate_error_message(exception),
                )

        self.process_unhandled_error(error=exception)

    def process_unhandled_error(self, error):
        logger.exception(error)
        self.response = ApiGatewayResponse(
            status_code=500, body={"message": "Internal Server Error"}
        )

    @abstractmethod
    def perform_action(self):
        raise NotImplementedError()

    @abstractmethod
    def render_response(self):
        raise NotImplementedError()
