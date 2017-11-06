import json
import logging

from pyverless.config import settings
from pyverless.decorators import warmup
from pyverless.auth import get_user_model

CORS_ORIGIN = settings.CORS_ORIGIN
CORS_HEADERS = settings.CORS_HEADERS

User = get_user_model()


class RequestBodyMixin(object):

    required_body_keys = []
    optional_body_keys = []

    def get_body(self):

        body = {}
        missing_keys = []

        # Collect all required keys and values. Collected missing keys are
        # reported as an error.
        for key in self.required_body_keys:
            try:
                body[key] = json.loads(self.event['body'])[key]
            except KeyError:
                missing_keys.append(key)

        if missing_keys:
            self.error = ("Missing key(s): %s" % ', '.join(missing_keys), 400)
            raise Exception

        # Collect all optional keys and values.
        for key in self.optional_body_keys:
            try:
                body[key] = json.loads(self.event['body'])[key]
            except json.decoder.JSONDecodeError:
                self.error = ("Malformed body", 400)
                raise
            except KeyError:
                pass

        return body


class AuthorizationMixin(object):

    # TODO: define user object model in some configuration file
    def get_user(self):
        user_id = self.event['requestContext']['authorizer']['principalId']

        return User.nodes.get(uid=user_id)


class ObjectMixin(object):

    model = None
    serializer = None

    def get_object(self):
        object_id = self.event['pathParameters']['id']
        obj = self.get_nodeset().get_or_none(uid=object_id)

        if not obj:
            self.error = ("Resource Not Found", 404)
            raise Exception

        return obj

    def get_nodeset(self):
        return self.model.nodes


class ListMixin(object):

    model = None
    serializer = None

    def get_nodeset(self):
        return self.model.nodes


class BaseHandler(object):

    success_code = 200

    @classmethod
    def as_handler(cls):
        """
        Returns a lambda handler function.
        """
        @warmup
        def handler(event, context):
            self = cls()

            self.event = event
            self.context = context
            self.error = None

            # set user, object and/or body (that is, if the handler users the
            # apropiate mixin and the method is avaliable
            try:
                self.user = self.get_user()
            except Exception:
                pass

            try:
                self.object = self.get_object()
            except Exception:
                pass

            try:
                self.body = self.get_body()
            except Exception:
                pass

            # Perform handler action: If errors occur, render an error response
            # else, render and return the response.
            try:
                response_body = self.perform_action()
            except Exception as e:
                # Render a 500 error response on unhandled/undefined error
                if not self.error:
                    return self.render_500_error_response(e, context)

            if self.error:
                return self.render_error_response(self.error[0], self.error[1])

            return self.render_response(response_body, self.success_code)

        return handler

    def render_response(self, body, status_code):
        """
        Given a body and status_code, returns a dictionary in the format of a valid
        AWS handler response.
        As AWS API Gateway works as a proxy, lambda is in charge of setting and
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

    def render_error_response(self, message, status_code):
        """
        Given a message and error status_code, returns a dictionary in the format of a valid
        AWS handler response with our error body definition. This allows us to be consistent.
        """
        body = {
            "code": status_code,
            "message": message
        }
        response = self.render_response(body, status_code)

        return response

    def render_500_error_response(self, exception, context):
        """
        Given a exception and context, log unhandled exceptions and create an
        error response with status code 500 and message 'Internal Server Error'
        """
        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)

        try:
            logger.error('Exception in %(function)s: %(exception)s' % {
                'function': context.function_name,
                'exception': str(exception)
            })
            return self.render_error_response("Internal Server Error", 500)
        except AttributeError:  # pragma: no cover
            # This will happen while testing locally, as the context is not provided
            # and function_name can't be accessed. On production, the context of handlers
            # is provided by AWS lambda and failing handlers pass it on to here.
            raise exception


class CreateHandler(RequestBodyMixin, BaseHandler):

    success_code = 201

    def create_object(self):
        obj = self.model(**self.body).save()

        return obj

    def perform_action(self):
        obj = self.create_object()

        return obj.uid


class RetrieveHandler(ObjectMixin, BaseHandler):

    success_code = 200

    def serialize(self, instance):
        return self.serializer(instance=instance).data

    def perform_action(self):
        data = self.serialize(self.object) if self.object else None

        return data


class ListHandler(ListMixin, BaseHandler):

    success_code = 200

    def serialize(self, instance):
        return self.serializer(instance=instance).data

    def perform_action(self):
        _list = []

        for obj in self.get_nodeset().all():
            _list.append(self.serialize(obj))

        return _list


class UpdateHandler(RequestBodyMixin, ObjectMixin, BaseHandler):

    success_code = 200

    def perform_action(self):

        for key, value in self.body.items():
            setattr(self.object, key, value)

        self.object.save()

        return self.body


class DeleteHandler(ObjectMixin, BaseHandler):

    success_code = 204

    def perform_action(self):
        self.object.delete()

        return {}
