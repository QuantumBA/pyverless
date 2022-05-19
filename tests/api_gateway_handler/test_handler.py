import unittest

from pyverless.api_gateway_handler.api_gateway_handler import ErrorHandler
from pyverless.api_gateway_handler.api_gateway_handler_standalone import (
    ApiGatewayHandlerStandalone,
)
from pyverless.api_gateway_handler.api_gateway_handler_app import (
    App,
    ApiGatewayHandlerApp,
)
from tests.utils.aws_events_creations import (
    create_api_gateway_event,
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
                ErrorHandler(exception=KeyError, msg={"test": "error"}, status_code=400)
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
                "body": '{"test": "error"}',
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
                "body": '{"msg": "Internal Server Error"}',
                "headers": {
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Origin": "*",
                },
                "statusCode": 500,
            },
        )


class TestApiGatewayHandlerApp(unittest.TestCase):
    def test_handler_from_app_ok_response(self):
        class TestHandler(ApiGatewayHandlerApp):
            method = "GET"
            path = "test"

            def perform_action(self):
                return {
                    "path": self.event_parsed.path,
                    "method": self.event_parsed.http_method,
                }

        handler = App.as_lambda_handler(handlers=[TestHandler])
        output = handler(
            create_api_gateway_event(path="test", method="GET"),
            create_lambda_context(),
        )
        self.assertEqual(
            output,
            {
                "body": '{"path": "test", "method": "GET"}',
                "headers": {
                    "Access-Control-Allow-Headers": "Authorization,Content-Type,X-Amz-Date,X-Amz-Security-Token,X-Api-Key",
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json",
                },
                "isBase64Encoded": False,
                "statusCode": 200,
            },
        )

    def test_handler_from_app_not_found_response(self):
        class TestHandler(ApiGatewayHandlerApp):
            method = "GET"
            path = "other"

            def perform_action(self):
                return {
                    "path": self.event_parsed.path,
                    "method": self.event_parsed.http_method,
                }

        handler = App.as_lambda_handler(handlers=[TestHandler])
        output = handler(
            create_api_gateway_event(path="test", method="GET"),
            create_lambda_context(),
        )
        self.assertEqual(
            output,
            {
                "body": '{"statusCode":404,"message":"Not found"}',
                "headers": {
                    "Access-Control-Allow-Headers": "Authorization,Content-Type,X-Amz-Date,X-Amz-Security-Token,X-Api-Key",
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json",
                },
                "isBase64Encoded": False,
                "statusCode": 404,
            },
        )

    def test_handler_from_app_controlled_error_response(self):
        class TestHandler(ApiGatewayHandlerApp):
            method = "GET"
            path = "test"

            error_handlers = [
                ErrorHandler(exception=KeyError, msg={"test": "error"}, status_code=400)
            ]

            def perform_action(self):
                raise KeyError()

        handler = App.as_lambda_handler(handlers=[TestHandler])
        output = handler(
            create_api_gateway_event(path="test", method="GET"),
            create_lambda_context(),
        )
        self.assertEqual(
            output,
            {
                "body": '{"test": "error"}',
                "headers": {
                    "Access-Control-Allow-Headers": "Authorization,Content-Type,X-Amz-Date,X-Amz-Security-Token,X-Api-Key",
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json",
                },
                "isBase64Encoded": False,
                "statusCode": 400,
            },
        )

    def test_handler_from_app_uncontrolled_error_response(self):
        class TestHandler(ApiGatewayHandlerApp):
            method = "GET"
            path = "test"

            def perform_action(self):
                raise KeyError()

        handler = App.as_lambda_handler(handlers=[TestHandler])
        output = handler(
            create_api_gateway_event(path="test", method="GET"),
            create_lambda_context(),
        )
        self.assertEqual(
            output,
            {
                "body": '{"msg": "Internal Server Error"}',
                "headers": {
                    "Access-Control-Allow-Headers": "Authorization,Content-Type,X-Amz-Date,X-Amz-Security-Token,X-Api-Key",
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json",
                },
                "isBase64Encoded": False,
                "statusCode": 500,
            },
        )
