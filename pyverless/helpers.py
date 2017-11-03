from os import getenv
import json
import logging


CORS_ORIGIN = getenv('CORS_ORIGIN', "*")
CORS_HEADERS = getenv('CORS_HEADERS', "*")


def make_response(body, status_code):
    """
    Given a body and status_code, returns a dictionary in the format of a valid
    AWS handler response.
    As AWS API Gateway works as a proxy, lambda is in cherge of setting and
    returning the applicable CORS headers. Check the next link for more info:
    http://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html
    """
    response = {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Access-Control-Allow-Origin": CORS_ORIGIN,
            "Access-Control-Allow-Headers": CORS_HEADERS,
            "Access-Control-Allow-Methods": "*"
        }
    }
    return response


def make_error_response(message, status_code):
    """
    Given a message and error status_code, returns a dictionary in the format of a valid
    AWS handler response with our error body definition. This allows us to be consistent.
    """
    body = {
        "code": status_code,
        "message": message
    }
    response = make_response(body, status_code)

    return response


def make_500_error_response(exception, context):

    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    try:
        logger.error('Exception in %(function)s: %(exception)s' % {
            'function': context.function_name,
            'exception': str(exception)
        })
        return make_error_response("Internal Server Error", 500)
    except AttributeError:  # pragma: no cover
        # This will happen while testing locally, as the context is not provided
        # and function_name can't be accessed. On production, the context of handlers
        # is provided by AWS lambda and failing handlers pass it on to here.
        raise exception
