import unittest
from datetime import datetime
from enum import Enum

from pyverless.serialization import input_serializer
from tests.utils import fake_functions


class TestInputSerializer(unittest.TestCase):
    def test_base_serializer_nullable(self):
        serializer = input_serializer.BaseSerializer()
        output = serializer.serialize(None)
        self.assertIsNone(output)

    def test_base_serializer_error_nullable(self):
        serializer = input_serializer.BaseSerializer(nullable=False)
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize(None)

    def test_string_serializer(self):
        serializer = input_serializer.StringSerializer()
        test_input = fake_functions.fake_random_word()
        result = serializer.serialize(test_input)
        self.assertEqual(result, test_input)

    def test_string_serializer_error(self):
        serializer = input_serializer.StringSerializer()
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize(fake_functions.fake_random_number())

    def test_integer_serializer(self):
        serializer = input_serializer.IntegerSerializer()
        test_input = fake_functions.fake_random_number()
        result = serializer.serialize(test_input)
        self.assertEqual(result, test_input)

    def test_integer_serializer_error(self):
        serializer = input_serializer.IntegerSerializer()
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize(fake_functions.fake_random_word())

    def test_boolean_serializer(self):
        serializer = input_serializer.BooleanSerializer()
        test_input = True
        result = serializer.serialize(test_input)
        self.assertEqual(result, test_input)

    def test_boolean_serializer_error(self):
        serializer = input_serializer.BooleanSerializer()
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize(fake_functions.fake_random_word())

    def test_time_serializer(self):
        serializer = input_serializer.TimeSerializer()
        test_input = fake_functions.fake_time_str()
        result = serializer.serialize(test_input)
        self.assertEqual(result, datetime.strptime(test_input, "%H:%M").time())

    def test_time_serializer_error_format(self):
        serializer = input_serializer.TimeSerializer()
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize(fake_functions.fake_time_str(str_format="%H"))

    def test_date_serializer(self):
        serializer = input_serializer.DateSerializer()
        test_input = fake_functions.fake_date_str()
        result = serializer.serialize(test_input)
        self.assertEqual(result, datetime.strptime(test_input, "%Y-%m-%d").date())

    def test_date_serializer_error_format(self):
        serializer = input_serializer.DateSerializer()
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize(fake_functions.fake_date_str(str_format="%m-%d"))

    def test_list_serializer(self):
        serializer = input_serializer.ListSerializer(
            items_serializer=input_serializer.IntegerSerializer()
        )
        test_input = [fake_functions.fake_random_number()]
        result = serializer.serialize(test_input)
        self.assertEqual(result, test_input)

    def test_list_serializer_error_type(self):
        serializer = input_serializer.ListSerializer(
            items_serializer=input_serializer.IntegerSerializer()
        )
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize(fake_functions.fake_random_word())

    def test_list_serializer_error_items(self):
        serializer = input_serializer.ListSerializer(
            items_serializer=input_serializer.IntegerSerializer()
        )
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize([fake_functions.fake_random_word()])

    def test_dict_serializer(self):
        class SerializerTest(input_serializer.Serializer):
            test = input_serializer.IntegerSerializer()

        serializer = SerializerTest()
        test_input = {"test": fake_functions.fake_random_number()}
        result = serializer.serialize(test_input)
        self.assertEqual(result, test_input)

    def test_dict_serializer_error_type(self):
        class SerializerTest(input_serializer.Serializer):
            test = input_serializer.IntegerSerializer()

        serializer = SerializerTest()
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize(fake_functions.fake_random_word())

    def test_dict_serializer_error_mandatory_fields(self):
        class SerializerTest(input_serializer.Serializer):
            test = input_serializer.IntegerSerializer()

        serializer = SerializerTest()
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize({})

    def test_dict_serializer_error_items(self):
        class SerializerTest(input_serializer.Serializer):
            test = input_serializer.IntegerSerializer()

        serializer = SerializerTest()
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize({"test": fake_functions.fake_random_word()})

    def test_enum_serializer(self):
        class EnumTest(Enum):
            OK = "ok"
            ERROR = "error"

        serializer = input_serializer.EnumSerializer(EnumTest)
        input_enum = fake_functions.fake_random_enum(EnumTest)
        output = serializer.serialize(input_enum.value)
        self.assertEqual(output, input_enum)

    def test_enum_serializer_error_choices(self):
        class EnumTest(Enum):
            OK = "ok"
            ERROR = "error"

        serializer = input_serializer.EnumSerializer(EnumTest)
        with self.assertRaises(input_serializer.SerializationError):
            serializer.serialize("not found")
