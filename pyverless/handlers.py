import json
import logging
import traceback
from typing import Union, Any

import sentry_sdk
from sentry_sdk import capture_exception, configure_scope

from pyverless.config import settings
from pyverless.decorators import warmup
from pyverless.models import get_user_model
from pyverless.exceptions import BadRequest, Unauthorized, NotFound


class RequestBodyMixin(object):
    """
    Implement the get_body method that will be called to set self.body as the body
    of the request.
    """

    required_body_keys = []
    optional_body_keys = []

    def get_required_body_keys(self):
        return self.required_body_keys

    def get_body(self):

        body = {}
        missing_keys = []

        try:
            request_body = json.loads(self.event['body']) if self.event['body'] else {}
            # The next line is necessary because json.loads('null') = None.
            # 'null' may be a possible value of 'body'
            request_body = request_body if request_body else {}
        except json.decoder.JSONDecodeError:
            message = "Malformed body"
            self.error = (message, 400)
            raise BadRequest(message=message)

        # Collect all required keys and values. Collected missing keys are
        # reported as an error.
        for key in self.get_required_body_keys():
            try:
                body[key] = request_body[key]
            except KeyError:
                missing_keys.append(key)

        if missing_keys:
            message = "Missing key(s): %s" % ', '.join(missing_keys)
            self.error = (message, 400)
            raise BadRequest(message=message)

        # Collect all optional keys and values.
        for key in self.optional_body_keys:
            try:
                body[key] = request_body[key]
            except KeyError:
                pass

        return body


class SQSMessagesMixin(object):
    """
    Implement the get_messages method that will be called to set self.messages

    Each message is a dict with the following keys:

    - attributes
    - text_message
    - queue_source
    - region
    """

    def get_messages(self):
        messages = []

        try:
            temp_messages = self.event['Records'] if self.event['Records'] else []
        except json.decoder.JSONDecodeError:
            message = "Malformed message"
            self.error = (message, 400)
            raise BadRequest(message=message)

        for message in temp_messages:
            temp_message = {}

            temp_message['attributes'] = self.get_message_part(message, 'messageAttributes', message['messageId'])
            temp_message['text_message'] = self.get_message_part(message, 'body', message['messageId'])
            temp_message['queue_source'] = message['eventSourceARN']
            temp_message['region'] = message['awsRegion']

            messages.append(temp_message)

        return messages

    def get_message_part(self, message, part, message_id):

        try:
            message_part = message[part] if message[part] else {}
        except json.decoder.JSONDecodeError:
            response_text = "Malformed {} in message {}".format(part, message_id)
            self.error = (response_text, 400)
            raise BadRequest(message=response_text)

        return message_part


class S3FileMixin(object):
    """
    Implement the get_file method that will be called to set self.file

    The file is a dict with the following keys:

    - event_name
    - bucket
    - owner
    - file_name
    - size
    """

    def get_file(self):
        try:
            temp_file_event = self.event['Records'] if self.event['Records'] else []
        except json.decoder.JSONDecodeError:
            message = "Malformed message"
            self.error = (message, 400)
            raise BadRequest(message=message)

        file = {
            'event_name': temp_file_event[0]['eventName'],
            'bucket': temp_file_event[0]['s3']['bucket']['name'],
            'owner': temp_file_event[0]['s3']['bucket']['ownerIdentity']['principalId'],
            'file_name': temp_file_event[0]['s3']['object']['key'],
        }
        # on ObjectRemoved event, the size is not present
        if temp_file_event[0]['s3']['object'].get('size'):
            file['size'] = temp_file_event[0]['s3']['object']['size']

        return file

    def get_message_part(self, message, part, message_id):

        try:
            message_part = message[part] if message[part] else {}
        except json.decoder.JSONDecodeError:
            response_text = "Malformed {} in message {}".format(part, message_id)
            self.error = (response_text, 400)
            raise BadRequest(message=response_text)

        return message_part


class AuthorizationMixin(object):
    """
    Implement the get_user method that will be called to set self.user

    USER_MODEL must be set on the pyverless settings
    """

    def get_user(self):
        try:
            user_id = self.event['requestContext']['authorizer']['principalId']
        except KeyError:
            self.error = ('Unauthorized', 403)
            raise Unauthorized()

        UserModel = get_user_model()
        user = getattr(UserModel, settings.MODEL_MANAGER).get_or_none(uid=user_id)

        if user:
            return user
        else:
            self.error = ('Unauthorized', 403)
            raise Unauthorized()


class ObjectMixin(object):
    """
    Implement the get_object method that will be called to set self.object,
    the object 'id' must be present on the pathParameters.

    The user can also overwrite the get_queryset method to limit the visibility.

    The 'model' attribute must be set on the handler.
    """

    model = None
    serializer = None
    id_in_path = 'id'

    def get_object(self):
        object_id = self.event['pathParameters'][self.id_in_path]

        # When get_queryset is overriden by the user, the queryset it returns may
        # be a list. Is such case, the list has to be filtered to get the
        # desired object.
        if isinstance(self.queryset, list):

            def filt(instance):
                return instance.uid == object_id

            filtered = list(filter(filt, self.queryset))

            obj = filtered.pop() if filtered else None
        else:
            obj = self.queryset.get_or_none(uid=object_id)

        if not obj:
            self.error = ("Resource Not Found", 404)
            raise NotFound()

        return obj

    def get_queryset(self):
        return getattr(self.model, settings.MODEL_MANAGER)

    def serialize(self, instance):
        return self.serializer(instance=instance).data


class ListMixin(object):
    """
    Implement the get_queryset method that will be called to set self.queryset

    The 'model' attribute must be set on the handler and the user must overwrite
    either the 'serializer' attribute or the 'serialize' method.
    """

    model = None
    serializer = None

    def get_queryset(self):
        return getattr(self.model, settings.MODEL_MANAGER)

    def serialize(self, instance):
        return self.serializer(instance=instance).data


class BaseHandler(object):

    # type hints
    user: Any
    queryset: Any
    object: Any
    body: dict
    messages: list
    file: dict

    event: dict
    error: Union[list, tuple]
    force_error: bool

    success_code = 200

    def perform_action(self):
        """
        This method is to be overriden. Here is where the particular handler
        action is performed. Its return value is a dictionary with the response body.
        """
        return self.response_body

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
            self.user = None
            self.body = {}
            self.response_body = {}
            self.messages = {}
            self.force_error = False

            # set user, queryset, object, body and response_body (that is, if the handler
            # uses the apropiate mixin and the method is avaliable)
            pairs = [
                ('user', 'get_user'),
                ('queryset', 'get_queryset'),
                ('object', 'get_object'),
                ('body', 'get_body'),
                ('messages', 'get_messages'),
                ('file', 'get_file'),
                ('response_body', 'perform_action'),
            ]

            for attr, method in pairs:
                if hasattr(self, method):
                    try:
                        setattr(self, attr, getattr(self, method)())
                    except Exception as e:
                        if not self.error:
                            tb = traceback.format_exc()
                            return self.render_500_error_response(e, tb)
                if self.error:
                    return self.render_error_response(self.error[0], self.error[1])

            return self.render_response(self.response_body, self.success_code)

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
                "Access-Control-Allow-Origin": settings.CORS_ORIGIN,
                "Access-Control-Allow-Headers": settings.CORS_HEADERS,
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
        if not self.force_error:
            response = self.render_response(body, status_code)
        else:
            raise Exception(json.dumps(body))

        return response

    def render_500_error_response(self, e, tb):
        """
        Given a exception and traceback, log unhandled exceptions using the python
        logger and/or sentry. Also, create an http response with status code 500
        and message.
        """

        # Log errors using the python logger.
        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)

        logger.exception(e)

        # Log errors in sentry if USE_SENTRY setting variable is set to True.
        if settings.USE_SENTRY:
            sentry_sdk.init(dsn=settings.SENTRY_DNS)

            with configure_scope() as scope:

                if self.user:
                    scope.user = {'id': self.user.uid, 'email': self.user.email}

                scope.set_tag("stage", settings.STAGE)
                scope.set_extra("class", self.__class__)
                scope.set_extra("body", self.body)
                scope.set_extra("event", self.event)

            capture_exception(e)

        # Send an 500 error response with traceback and event information in the
        # response body if DEBUG setting variable is set to True.
        if settings.DEBUG:
            message = {
                "traceback": tb,
                "event": self.event
            }
        else:
            message = "Internal Server Error"

        return self.render_error_response(message, 500)


class ReadSQSHandler(SQSMessagesMixin, BaseHandler):
    """
    Handler that returns a list of SQS messages and sets the HTTP status code to 200.

    Each message is a dict with the following keys:

    - attributes
    - text_message
    - queue_source
    - region
    """

    success_code = 200

    def perform_action(self):
        return self.messages


class CreateHandler(RequestBodyMixin, BaseHandler):
    """
    Handler that reads the request body and creates the object with each (key, value) pair
    as the params for the constructor.

    The 'model' attribute must be set on the handler and the user can overwrite the 'create_object' method.
    """

    success_code = 201

    def create_object(self):
        obj = self.model(**self.body).save()

        return obj

    def perform_action(self):
        obj = self.create_object()

        return obj.uid


class RetrieveHandler(ObjectMixin, BaseHandler):
    """
    Handler that returns a serialized Object.

    The 'model' attribute must be set and 'id' must be present on the pathParameters.

    The user also has to define the 'serialize' method on the handler.
    """

    success_code = 200

    def perform_action(self):
        data = self.serialize(self.object) if self.object else None

        return data


class ListHandler(ListMixin, BaseHandler):
    """
    Handler that returns a list of serialized nodes and sets the HTTP status code to 200.

    The 'model' attribute must be set and the user must overwrite
    either the 'serializer' attribute or the 'serialize' method.
    """

    success_code = 200

    def perform_action(self):
        _list = []

        if isinstance(self.queryset, list):
            for obj in self.queryset:
                _list.append(self.serialize(obj))
        else:
            for obj in self.queryset.all():
                _list.append(self.serialize(obj))

        return _list


class UpdateHandler(RequestBodyMixin, ObjectMixin, BaseHandler):
    """
    Handler that sets self.object and for each (key, value) pair of the body
    sets self.object.key = value.

    The 'model' attribute must be set and 'id' must be present on the pathParameters.

    Returns the serialized node and sets the HTTP status code to 200
    """

    success_code = 200

    def perform_action(self):

        for key, value in self.body.items():
            setattr(self.object, key, value)

        self.object.save()

        return self.serialize(self.object)


class DeleteHandler(ObjectMixin, BaseHandler):
    """
    Handler that sets self.object, calls its delete() method and sets the HTTP status code to 204.

    The 'model' attribute must be set and 'id' must be present on the pathParameters.

    The user can also overwrite the 'get_queryset' method to limit the search.
    """

    success_code = 204

    def perform_action(self):
        self.object.delete()

        return {}
