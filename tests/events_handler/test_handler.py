import unittest
from dataclasses import dataclass

from pyverless.events_handler.events_handler import EventsHandler
from tests.utils.aws_events_creations import (
    create_lambda_context,
)


class TestEventsHandler(unittest.TestCase):
    def test_handler_ok_response(self):

        @dataclass
        class TestEvent:
            test_param: str

        class TestHandler(EventsHandler):
            event_parser = TestEvent

            def perform_action(self):
                event: TestEvent = self.event_parsed
                return event.test_param

        handler = TestHandler.as_handler()
        output = handler(
            {"test_param": "abc"}, create_lambda_context()
        )
        self.assertEqual(
            output,
            {'test_param': 'abc'}
        )

    def test_handler_errors(self):

        class TestHandler(EventsHandler):

            def perform_action(self):
                raise KeyError()

        handler = TestHandler.as_handler()
        with self.assertRaises(KeyError):
            handler(
                {}, create_lambda_context()
            )
