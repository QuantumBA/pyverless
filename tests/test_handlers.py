from pyverless.handlers import BaseHandler


class TestHandlers():

    class TestBaseHandler(BaseHandler):

        def perform_action(self):
            return {'key': 'value'}

    def setup_class(self):
        self.event = {}
        self.context = {}

    def test_make_response(self):
        handler = self.TestBaseHandler.as_handler()
        response = handler(self.event, self.context)

        assert response['statusCode'] == 200
        assert response['body'] == '{"key": "value"}'
