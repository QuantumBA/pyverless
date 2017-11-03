from pyverless.decorators import warmup


@warmup
def _handler(event, context):
    return 'lambda invoked'


class TestDecorators():

    def setup_class(self):
        pass

    def test_warmup_decorator(self):
        """
        Tests the warmup decorator that allows early return of lambda handler
        funtions when they are invoked via serverless-plugin-warmup
        """

        # if 'source' key is not present in event or not set to 'serverless-plugin-warmup'
        # the lambda handler function will be invoked as normal
        response = _handler({}, {})
        assert response == 'lambda invoked'

        response = _handler({'source': 'not-warmup'}, {})
        assert response == 'lambda invoked'

        # If source key is set to 'serverless-plugin-warmup' early exit is
        # performed and response is None
        response = _handler({'source': 'serverless-plugin-warmup'}, {})
        assert not response
