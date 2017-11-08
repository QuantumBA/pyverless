import json
from pyverless import handlers

from test_config.models import User, UserSerializer


def _(response):
    """
    Given a handler response, return the status_code and data. This is ment
    to make the test code more readable
    """
    data = json.loads(response['body'])
    status_code = response['statusCode']

    return data, status_code


class TestHandlers():

    class TestBaseHandler(handlers.BaseHandler):

        def perform_action(self):
            return {'key': 'value'}

    class TestCreateHandler(handlers.CreateHandler):
        model = User
        required_body_keys = ['email', 'password']

    class TestRetrieveHandler(handlers.RetrieveHandler):
        model = User
        serializer = UserSerializer

    class TestListHandler(handlers.ListHandler):
        model = User
        serializer = UserSerializer

    class TestUpdateHandler(handlers.UpdateHandler):
        model = User
        required_body_keys = ['email']

    class TestDeleteHandler(handlers.DeleteHandler):
        model = User

    def setup_class(self):
        self.event = {}
        self.context = {}

    def test_base_handler(self):
        handler = self.TestBaseHandler.as_handler()
        response = handler(self.event, self.context)

        assert response['statusCode'] == 200
        assert response['body'] == '{"key": "value"}'

    def test_create_handler(self):
        handler = self.TestCreateHandler.as_handler()

        # CASE: Body is empty. Missing keys
        response_body, status_code = _(handler({}, {}))

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

        # CASE: Success
        event = {
            "pathParameters": {"id": "b89ee4a1d9ac4dd5aeb242264968aa4e"},
        }

        response_body, status_code = _(handler(event, {}))

        assert status_code == 200
        assert response_body == {'email': 'one@users.com'}

    def test_list_handler(self):
        handler = self.TestListHandler.as_handler()

        # CASE: Success
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
