import json
from dataclasses import dataclass
from typing import Dict, Any


def create_lambda_context():
    @dataclass
    class LambdaContextTest:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContextTest


def create_api_gateway_event(
    auth: str = None,
    body: Any = None,
    path_parameters: dict = None,
    query_string: dict = None,
    multivalue_query_string: dict = None,
    method: str = None,
    path: str = None,
    headers: Dict = None,
    multivalue_headers: Dict = None,
) -> dict:
    event = {
        "requestContext": {
            "httpMethod": method,
            "resourcePath": path,
            "authorizer": {"principalId": auth},
        },
        "body": json.dumps(body) if body else {},
        "pathParameters": path_parameters if path_parameters else {},
        "queryStringParameters": query_string if query_string else {},
        "multiValueQueryStringParameters": multivalue_query_string
        if multivalue_query_string
        else {},
        "httpMethod": method,
        "path": path,
        "headers": headers if headers else {},
        "multiValueHeaders": multivalue_headers if multivalue_headers else {},
    }
    return event
