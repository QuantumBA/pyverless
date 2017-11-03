import json
from unittest.mock import Mock

from pyverless.helpers import make_response, make_error_response, make_500_error_response


class TestHelpers():

    def setup_class(self):
        pass

    def test_make_response(self):

        response = make_response({'key': 'value'}, 200)

        data = json.loads(response['body'])

        assert response['statusCode'] == 200
        assert data == {'key': 'value'}

    def test_make_error_response(self):

        response = make_error_response('Error Message', 400)

        data = json.loads(response['body'])

        assert response['statusCode'] == 400
        assert data['code'] == 400
        assert data['message'] == 'Error Message'

    def test_make_500_error_response(self):

        exception = Exception('Boom!')
        context = Mock()
        context.function_name = '<function_name>'

        response = make_500_error_response(exception, context)

        data = json.loads(response['body'])

        assert response['statusCode'] == 500
        assert data['code'] == 500
        assert data['message'] == 'Internal Server Error'
