import json
from abc import ABC
from typing import Dict

from pyverless.config import settings

from shared.api_gateway_handler.api_gateway_handler_v2 import ApiGatewayHandlerV2


class ApiGatewayHandlerStandalone(ApiGatewayHandlerV2, ABC):
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
