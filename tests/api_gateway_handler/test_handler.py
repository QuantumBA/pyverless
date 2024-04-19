import unittest

from pyverless.api_gateway_handler.api_gateway_handler import ErrorHandler
from pyverless.api_gateway_handler.api_gateway_handler_standalone import (
    ApiGatewayHandlerStandalone,
    ApiGatewayWSHandlerStandalone,
)
from tests.utils.aws_events_creations import (
    create_api_gateway_event,
    create_api_gateway_websocket_event,
    create_lambda_context,
)


class TestApiGatewayHandlerStandalone(unittest.TestCase):
    def test_handler_ok_response(self):
        class TestHandler(ApiGatewayHandlerStandalone):
            def perform_action(self):
                return {
                    "path": self.event_parsed.path,
                    "method": self.event_parsed.http_method,
                }

        handler = TestHandler.as_handler()
        output = handler(
            create_api_gateway_event(path="test", method="GET"), create_lambda_context()
        )
        self.assertEqual(
            output,
            {
                "body": '{"path": "test", "method": "GET"}',
                "headers": {
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Origin": "*",
                },
                "statusCode": 200,
            },
        )

    def test_handler_controlled_error_response(self):
        class TestHandler(ApiGatewayHandlerStandalone):
            error_handlers = [
                ErrorHandler(exception=KeyError, msg="error", status_code=400)
            ]

            def perform_action(self):
                raise KeyError()

        handler = TestHandler.as_handler()
        output = handler(
            create_api_gateway_event(path="test", method="GET"), create_lambda_context()
        )
        self.assertEqual(
            output,
            {
                "body": '{"message": "error"}',
                "headers": {
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Origin": "*",
                },
                "statusCode": 400,
            },
        )

    def test_handler_controlled_error_response_without_message(self):
        class CustomException(Exception):
            pass

        class TestHandler(ApiGatewayHandlerStandalone):
            error_handlers = [ErrorHandler(exception=CustomException, status_code=400)]

            def perform_action(self):
                raise CustomException("test")

        handler = TestHandler.as_handler()
        output = handler(
            create_api_gateway_event(path="test", method="GET"), create_lambda_context()
        )
        self.assertEqual(
            output,
            {
                "body": '{"message": "test"}',
                "headers": {
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Origin": "*",
                },
                "statusCode": 400,
            },
        )

    def test_handler_controlled_error_response_with_error_code(self):
        class TestHandler(ApiGatewayHandlerStandalone):
            error_handlers = [
                ErrorHandler(
                    exception=KeyError, msg="error", status_code=400, error_code=2
                )
            ]

            def perform_action(self):
                raise KeyError()

        handler = TestHandler.as_handler()
        output = handler(
            create_api_gateway_event(path="test", method="GET"), create_lambda_context()
        )
        self.assertEqual(
            output,
            {
                "body": '{"message": "error", "error_code": 2}',
                "headers": {
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Origin": "*",
                },
                "statusCode": 400,
            },
        )

    def test_handler_uncontrolled_error_response(self):
        class TestHandler(ApiGatewayHandlerStandalone):
            def perform_action(self):
                raise KeyError()

        handler = TestHandler.as_handler()
        output = handler(
            create_api_gateway_event(path="test", method="GET"),
            create_lambda_context(),
        )
        self.assertEqual(
            output,
            {
                "body": '{"message": "Internal Server Error"}',
                "headers": {
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Origin": "*",
                },
                "statusCode": 500,
            },
        )

    def test_handler_uncontrolled_error_in_parser_response(self):
        class TestHandler(ApiGatewayHandlerStandalone):
            def perform_action(self):
                raise KeyError()

        handler = TestHandler.as_handler()
        output = handler({}, create_lambda_context())
        self.assertEqual(
            output,
            {
                "body": '{"message": "Internal Server Error"}',
                "headers": {
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Origin": "*",
                },
                "statusCode": 500,
            },
        )


class TestApiGatewayWSHandlerStandalone(unittest.TestCase):
    def test_handler_ok_response(self):
        class TestHandler(ApiGatewayWSHandlerStandalone):
            def perform_action(self):
                return {
                    "route_key": self.event_parsed.route_key,
                    "body": self.event_parsed.body,
                    "event_type": self.event_parsed.event_type,
                }

        handler = TestHandler.as_handler()
        output = handler(
            create_api_gateway_websocket_event(body={"key": "value"}),
            create_lambda_context(),
        )
        self.assertEqual(
            output,
            {
                "body": '{"route_key": "testRouteKey", "body": {"key": "value"}, "event_type": "MESSAGE"}',
                "statusCode": 200,
            },
        )
