import json
from abc import ABC
from typing import List, Type

from aws_lambda_powertools.event_handler.api_gateway import (
    Response,
    CORSConfig,
    APIGatewayRestResolver,
)
from pyverless.config import settings
from pyverless.decorators import warmup

from pyverless.api_gateway_handler.api_gateway_handler import (
    ApiGatewayHandler,
    ApiGatewayResponse,
)


class ApiGatewayHandlerApp(ApiGatewayHandler, ABC):
    method: int = None
    path: str = None

    def render_response(self, response: ApiGatewayResponse):
        return Response(
            status_code=response.status_code,
            content_type="application/json",
            body=json.dumps(response.body),
        )


class App:
    def __init__(self, event, context):
        cors_config = CORSConfig(allow_origin=settings.CORS_ORIGIN)
        self.app = APIGatewayRestResolver(cors=cors_config)
        self.event = event
        self.context = context

    def _add_handler(self, handler: Type[ApiGatewayHandlerApp]):
        app = self.app

        @app.route(handler.path, method=[str(handler.method)])
        def temp_function(*args, **kwargs):
            if "proxy" in self.event["pathParameters"]:
                self.event["pathParameters"].pop("proxy")
            for key_arg in kwargs:
                self.event["pathParameters"][key_arg] = kwargs[key_arg]
            return handler().lambda_handler(self.event, self.context)

    @classmethod
    def as_lambda_handler(cls, handlers: List[Type[ApiGatewayHandlerApp]]):
        """
        Returns a lambda handler function.
        """

        @warmup
        def handler(event, context):
            self = cls(event, context)

            for handler in handlers:
                self._add_handler(handler)

            return self.app.resolve(self.event, self.context)

        return handler
