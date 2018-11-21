import json
from pyverless import handlers

from test_config.models import User, UserSerializer

event_sqs = {'Records': [
    {
        'messageId': 'b8b2883f-678a-4279-9667-2d12c48db9ee',
        'receiptHandle': 'AQEB6Ndk2HFIfF8FFV+L7uOTrcZ5CzTo4qrDcbPts895HOxz7fQgtLKepHGctQFsPLCF2TOf6tAWDkirOCqvpena9BZWPLCYB0eAgTAQ0UjLCXocu+FiRzgH0OVrU9Xvw6CRobWgKVbEVAyedecH36PGwQFe0mhraUBS3yFTkr+IH/rSanLNoraYSSC1l4KXjEID+DgLw62c+1iMQINMG78zmaD23sJULhxT+UYtpu/8dKyjc3pc/DB681C0g/rYyKvGcswKhjS6lmWsOiDxBmLOjwl75oBhs48rFwZoWoWA37w0yGtCeJY9Gz3hiSWBlwDx2epxAnpsPY3heaLD1Ytu70rHIvCtAl6LcdCWZ0GVhriehVA7vP/FG0u9iFdpjh8VGIsJ493Y3KNaSRcpOw4PmA==',
        'body': 'aaaa',
        'attributes': {
            'ApproximateReceiveCount': '1',
            'SentTimestamp': '1542630756242',
            'SenderId': 'AIDAIF2VDLAQKPHBJH63Y',
            'ApproximateFirstReceiveTimestamp': '1542630756276',
        },
        'messageAttributes': {'attribute1': {
            'stringValue': 'asadasd',
            'stringListValues': [],
            'binaryListValues': [],
            'dataType': 'String',
        }, 'attr2': {
            'stringValue': '2',
            'stringListValues': [],
            'binaryListValues': [],
            'dataType': 'Number',
        }},
        'md5OfMessageAttributes': '8a9fb00d734faedb8f5a47d34d45cdfd',
        'md5OfBody': '74b87337454200d4d33f80c4663dc5e5',
        'eventSource': 'aws:sqs',
        'eventSourceARN': 'arn:aws:sqs:eu-west-1:378311708430:ModelEventsQueue',
        'awsRegion': 'eu-west-1',
    }]
}

event_s3 = {
    "Records": [
        {
            "eventVersion": "2.0",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-1",
            "eventTime": "1970-01-01T00:00:00.000Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "AIDAJDPLRKLG7UEXAMPLE"
            },
            "requestParameters": {
                "sourceIPAddress": "127.0.0.1"
            },
            "responseElements": {
                "x-amz-request-id": "C3D13FE58DE4C810",
                "x-amz-id-2": "FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "testConfigRule",
                "bucket": {
                    "name": "mybucket",
                    "ownerIdentity": {
                        "principalId": "A3NL1KOZZKExample"
                    },
                    "arn": "arn:aws:s3:::mybucket"
                },
                "object": {
                    "key": "HappyFace.jpg",
                    "size": 1024,
                    "eTag": "d41d8cd98f00b204e9800998ecf8427e",
                    "versionId": "096fKKXTRTtl3on89fVO.nfljtsv6qko",
                    "sequencer": "0055AED6DCD90281E5"
                }
            }
        }
    ]
}


def _(response):
    """
    Given a handler response, return the status_code and data. This is ment
    to make the test code more readable
    """
    data = json.loads(response['body'])
    status_code = response['statusCode']

    return data, status_code


class TestMixins():

    class TestAuthorizationHandler(handlers.AuthorizationMixin, handlers.BaseHandler):
        pass

    class TestRequestBodyHandler(handlers.RequestBodyMixin, handlers.BaseHandler):
        pass

    class TestS3FileHandler(handlers.S3FileMixin, handlers.BaseHandler):

        def perform_action(self):
            return self.file

    def setup_class(self):
        self.context = {}

    def test_request_body_mixin(self):

        # Case: Missing body
        event = {
            "body": None
        }

        handler = self.TestRequestBodyHandler.as_handler()
        response_body, status_code = _(handler(event, self.context))

        assert status_code == 200
        assert response_body == {}

        # Case: Malformed body
        event = {
            "body": '{"a malfomed"; "body"'
        }
        handler = self.TestRequestBodyHandler.as_handler()
        response_body, status_code = _(handler(event, self.context))

        assert status_code == 400
        assert response_body['message'] == 'Malformed body'
        assert response_body['code'] == 400

    def test_authorization_mixin(self):

        # Case: Missing authentication on calling a handler with AuthorizationMixin
        handler = self.TestAuthorizationHandler.as_handler()
        response_body, status_code = _(handler({}, self.context))

        assert status_code == 403

        # Case: Success
        event = {
            "requestContext": {"authorizer": {"principalId": 'user_id'}}
        }
        handler = self.TestAuthorizationHandler.as_handler()
        response_body, status_code = _(handler(event, self.context))

        assert status_code == 200

    def test_s3file_mixin(self):

        handler = self.TestS3FileHandler.as_handler()
        response_body, status_code = _(handler(event_s3, self.context))

        assert status_code == 200
        assert response_body['bucket'] == 'mybucket'
        assert response_body['file_name'] == 'HappyFace.jpg'


class TestHandlers():

    class TestBaseHandler(handlers.BaseHandler):

        def perform_action(self):
            return {'key': 'value'}

    class TestReadSQSHandler(handlers.ReadSQSHandler):
        pass

    class TestCreateHandler(handlers.CreateHandler):
        model = User
        required_body_keys = ['email', 'password']
        optional_body_keys = ['phone']

    class TestRetrieveHandler(handlers.RetrieveHandler):
        model = User
        serializer = UserSerializer

    class TestListHandler(handlers.ListHandler):
        model = User
        serializer = UserSerializer

    class TestUpdateHandler(handlers.UpdateHandler):
        model = User
        required_body_keys = ['email']
        serializer = UserSerializer

    class TestDeleteHandler(handlers.DeleteHandler):
        model = User

    def setup_class(self):
        self.event = {}
        self.context = {}

    def test_base_handler(self):
        handler = self.TestBaseHandler.as_handler()
        response_body, status_code = _(handler(self.event, self.context))

        assert status_code == 200
        assert response_body['key'] == 'value'

    def test_read_sqs_handler(self):
        handler = self.TestReadSQSHandler.as_handler()
        response_body, status_code = _(handler(event_sqs, self.context))

        assert status_code == 200
        assert len(response_body) == 1
        assert response_body[0]['text_message'] == 'aaaa'

    def test_create_handler(self):
        handler = self.TestCreateHandler.as_handler()

        # CASE: Body is empty. Missing keys
        response_body, status_code = _(handler({'body': None}, {}))

        assert status_code == 400
        assert response_body['code'] == 400
        assert response_body['message'] == 'Missing key(s): email, password'

        # CASE: Success
        event = {
            "body": json.dumps({'email': 'one@users.com', 'password': 'test-password'})
        }

        response_body, status_code = _(handler(event, {}))

        assert status_code == 201
        # The response body is an UID. This uid is set in the mock user defined
        # in test_config.models
        assert response_body == "b89ee4a1d9ac4dd5aeb242264968aa4e"

    def test_retrieve_handler(self):
        handler = self.TestRetrieveHandler.as_handler()

        # We want to test filtering of a list queryset when get_queryset is
        # overriden. Here is a get_queyset method returning a list.
        def get_queryset(self):

            return [
                User(uid="b89ee4a1d9ac4dd5aeb242264968aa4e", email='one@users.com', password='test-password'),
                User(uid="another-uid", email='two@users.com', password='test-password')
            ]

        self.TestRetrieveHandler.get_queryset = get_queryset

        # CASE: Success
        event = {
            "pathParameters": {"id": "b89ee4a1d9ac4dd5aeb242264968aa4e"},
        }

        response_body, status_code = _(handler(event, {}))

        assert status_code == 200
        assert response_body == {'email': 'one@users.com'}

        # CASE: Not found
        event = {
            "pathParameters": {"id": "not-an-existing-id"},
        }

        response_body, status_code = _(handler(event, {}))

        assert status_code == 404
        assert response_body['message'] == 'Resource Not Found'
        assert response_body['code'] == 404

    def test_list_handler(self):
        handler = self.TestListHandler.as_handler()

        # CASE: Success
        response_body, status_code = _(handler({}, {}))

        assert status_code == 200
        assert response_body == [{'email': 'one@users.com'}, {'email': 'two@users.com'}]

        # CASE: Success with a list queryset

        # We want to test filtering of a list queryset when get_queryset is
        # overriden. Here is a get_queyset method returning a list.
        def get_queryset(self):

            return [
                User(uid="b89ee4a1d9ac4dd5aeb242264968aa4e", email='one@users.com', password='test-password'),
                User(uid="another-uid", email='two@users.com', password='test-password')
            ]

        self.TestListHandler.get_queryset = get_queryset

        handler = self.TestListHandler.as_handler()

        response_body, status_code = _(handler({}, {}))

        assert status_code == 200
        assert response_body == [{'email': 'one@users.com'}, {'email': 'two@users.com'}]

    def test_update_handler(self):
        handler = self.TestUpdateHandler.as_handler()

        # CASE: Success
        event = {
            "pathParameters": {"id": "b89ee4a1d9ac4dd5aeb242264968aa4e"},
            "body": json.dumps({'email': 'two@users.com'})
        }

        response_body, status_code = _(handler(event, {}))

        assert status_code == 200
        assert response_body == {'email': 'two@users.com'}

    def test_delete_handler(self):
        handler = self.TestDeleteHandler.as_handler()

        # CASE: Success
        event = {
            "pathParameters": {"id": "b89ee4a1d9ac4dd5aeb242264968aa4e"},
        }

        response_body, status_code = _(handler(event, {}))

        assert status_code == 204
        assert not response_body
