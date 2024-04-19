import json
from abc import ABC
from typing import Dict

from pyverless.config import settings

from pyverless.api_gateway_handler.api_gateway_handler import ApiGatewayHandler


class ApiGatewayHandlerStandalone(ApiGatewayHandler, ABC):
    headers: Dict = {}

    def render_response(self):
        headers = {
            "Access-Control-Allow-Origin": settings.CORS_ORIGIN,
            "Access-Control-Allow-Headers": settings.CORS_HEADERS,
            "Access-Control-Allow-Methods": "*",
        }
        if self.headers:
            headers = {**headers, **self.headers}
        return {
            "statusCode": self.response.status_code,
            "body": json.dumps(self.response.body),
            "headers": headers,
        }


class ApiGatewayWSHandlerStandalone(ApiGatewayHandler, ABC):
    headers: Dict = {}

    def render_response(self):
        return {
            "statusCode": self.response.status_code,
            "body": json.dumps(self.response.body),
        }
