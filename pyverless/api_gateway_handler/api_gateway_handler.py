from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import environ
from typing import List, Dict, Type

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from pyverless.decorators import warmup

from pyverless.utils.logging import logger


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
        error_dict = {"msg": message}
        if self.error_code:
            error_dict["error_code"] = self.error_code
        return error_dict


class ApiGatewayHandler(ABC):
    success_code = 200

    event_parsed: APIGatewayProxyEvent = None
    event: dict = None
    context = None

    error_handlers: List[ErrorHandler] = []

    @abstractmethod
    def perform_action(self):
        raise NotImplementedError()

    def lambda_handler(self, event, context):
        self.event = event
        self.context = context

        environ["AWS_REQUEST_ID"] = (
            context.aws_request_id if context else "default_aws_request_id"
        )

        self.event_parsed = APIGatewayProxyEvent(event)

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
            response = self.process_errors(ex)

        logger.info(
            {
                "type": "REQUEST_FINISHED",
                "message": "request finished",
                "status_code": response.status_code,
            }
        )

        return self.render_response(response)

    def process_response(self, response_body: Dict) -> ApiGatewayResponse:
        return ApiGatewayResponse(status_code=self.success_code, body=response_body)

    def process_errors(self, exception):
        for handler in self.error_handlers:
            if handler.is_my_exception(exception):
                return ApiGatewayResponse(
                    status_code=handler.status_code,
                    body=handler.generate_error_message(exception),
                )

        logger.exception(exception)
        return ApiGatewayResponse(
            status_code=500, body={"msg": "Internal Server Error"}
        )

    @abstractmethod
    def render_response(self, response: ApiGatewayResponse):
        raise NotImplementedError()

    @classmethod
    def as_handler(cls):
        """
        Returns a lambda handler function.
        """

        @warmup
        def handler(event, context):
            self = cls()
            return self.lambda_handler(event, context)

        return handler
