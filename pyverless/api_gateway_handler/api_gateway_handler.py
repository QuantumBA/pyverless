import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Type

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.data_classes.api_gateway_proxy_event import (
    APIGatewayEventRequestContext,
)

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

    logging_functions = [logger.info]
    error_handlers: List[ErrorHandler] = []

    def execute_lambda_code(self):
        request_id = self.context.aws_request_id
        for function in self.logging_functions:
            function(
                {
                    "type": "REQUEST_STARTED",
                    "request_id": request_id,
                    "path": self.event_parsed.path if self.event_parsed else None,
                    "headers": self.event_parsed.headers if self.event_parsed else None,
                    "method": self.event_parsed.http_method
                    if self.event_parsed
                    else None,
                    "message": "request started",
                }
            )

        try:
            self.preprocess_function()
            response_body = self.perform_action()
            self.postprocess_function()

            response = ApiGatewayResponse(
                status_code=self.success_code, body=response_body
            )

        except Exception as ex:
            response = self.process_error(exception=ex)

        for function in self.logging_functions:
            function(
                {
                    "type": "REQUEST_FINISHED",
                    "request_id": request_id,
                    "message": "request finished",
                    "status_code": response.status_code,
                }
            )

        return response

    def preprocess_function(self):
        pass

    def postprocess_function(self):
        pass

    def process_error(self, exception):
        for handler in self.error_handlers:
            if handler.is_my_exception(exception):
                return ApiGatewayResponse(
                    status_code=handler.status_code,
                    body=handler.generate_error_message(exception),
                )

        return self._process_500_errors(uncontrolled_error=exception)

    def process_unhandled_error(self, error):
        self.response = self._process_500_errors(uncontrolled_error=error)

    def _process_500_errors(self, uncontrolled_error) -> ApiGatewayResponse:
        logger.exception(uncontrolled_error)
        return ApiGatewayResponse(
            status_code=500, body={"message": "Internal Server Error"}
        )

    @abstractmethod
    def perform_action(self):
        raise NotImplementedError()

    @abstractmethod
    def render_response(self):
        raise NotImplementedError()


class APIGatewayWebsocketEvent(APIGatewayEventRequestContext):
    @property
    def body(self):
        return json.loads(self["body"])


class ApiGatewayWSHandler(EventsHandler, ABC):
    success_code = 200

    event_parsed: APIGatewayWebsocketEvent = None
    event_parser = APIGatewayWebsocketEvent

    logging_functions = [logger.info]
    error_handlers: List[ErrorHandler] = []

    def execute_lambda_code(self):
        request_id = self.context.aws_request_id
        for function in self.logging_functions:
            function(
                {
                    "type": "REQUEST_STARTED",
                    "request_id": request_id,
                    "route_key": self.event_parsed.route_key
                    if self.event_parsed
                    else None,
                    "event_type": self.event_parsed.event_type
                    if self.event_parsed
                    else None,
                    "connection_id": self.event_parsed.connection_id
                    if self.event_parsed
                    else None,
                    "message": "request started",
                }
            )

        try:
            self.preprocess_function()
            response_body = self.perform_action()
            self.postprocess_function()

            response = ApiGatewayResponse(
                status_code=self.success_code, body=response_body
            )

        except Exception as ex:
            response = self.process_error(exception=ex)

        for function in self.logging_functions:
            function(
                {
                    "type": "REQUEST_FINISHED",
                    "request_id": request_id,
                    "message": "request finished",
                    "status_code": response.status_code,
                }
            )

        return response

    def preprocess_function(self):
        pass

    def postprocess_function(self):
        pass

    def process_error(self, exception):
        for handler in self.error_handlers:
            if handler.is_my_exception(exception):
                return ApiGatewayResponse(
                    status_code=handler.status_code,
                    body=handler.generate_error_message(exception),
                )

        return self._process_500_errors(uncontrolled_error=exception)

    def process_unhandled_error(self, error):
        self.response = self._process_500_errors(uncontrolled_error=error)

    def _process_500_errors(self, uncontrolled_error) -> ApiGatewayResponse:
        logger.exception(uncontrolled_error)
        return ApiGatewayResponse(
            status_code=500, body={"message": "Internal Server Error"}
        )

    @abstractmethod
    def perform_action(self):
        raise NotImplementedError()

    @abstractmethod
    def render_response(self):
        raise NotImplementedError()
