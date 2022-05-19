import json
from abc import ABC
from typing import Dict

from pyverless.config import settings

from pyverless.api_gateway_handler.api_gateway_handler import (
    ApiGatewayHandler,
    ApiGatewayResponse,
)


class ApiGatewayHandlerStandalone(ApiGatewayHandler, ABC):
    headers: Dict = {}

    def render_response(self, response: ApiGatewayResponse):
        headers = {
            "Access-Control-Allow-Origin": settings.CORS_ORIGIN,
            "Access-Control-Allow-Headers": settings.CORS_HEADERS,
            "Access-Control-Allow-Methods": "*",
        }
        if self.headers:
            headers = {**headers, **self.headers}
        return {
            "statusCode": response.status_code,
            "body": json.dumps(response.body),
            "headers": headers,
        }
