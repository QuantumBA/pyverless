from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Type


class SerializationError(Exception):
    pass


class SerializerInterface(ABC):
    @abstractmethod
    def serialize(self, input_data):
        pass


class BaseSerializer(SerializerInterface):
    def __init__(self, nullable: bool = True):
        self.nullable = nullable

    def serialize(self, input_data):
        if input_data is None:
            if not self.nullable:
                raise SerializationError("Null value in Data is not allowed")
            return None
        self.validate_data(input_data)
        return self.transform_data(input_data)

    def validate_data(self, input_data):
        pass

    def transform_data(self, input_data):
        return input_data


class Serializer(BaseSerializer):
    def validate_data(self, input_data):
        super().validate_data(input_data)
        if type(input_data) != dict:
            raise SerializationError("Data is not a dictionary")

    def transform_data(self, input_data):
        input_data = super().transform_data(input_data)
        result = {}
        for field_name in self._get_serializer_fields():
            serializer: BaseSerializer = getattr(self, field_name)
            try:
                if field_name in input_data:
                    result[field_name] = serializer.serialize(input_data[field_name])
                else:
                    raise SerializationError(f"Data is mandatory")
            except Exception as ex:
                raise SerializationError(f"Field: {field_name} Error: {str(ex)}")
        return result

    def _get_serializer_fields(self):
        keys_to_be_serializers = [
            key for key in self.__dir__() if not key.startswith("_")
        ]
        serializers = [
            key
            for key in keys_to_be_serializers
            if isinstance(getattr(self, key), BaseSerializer)
        ]
        return serializers


class ListSerializer(BaseSerializer):
    def __init__(self, items_serializer: SerializerInterface, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._items_serializer = items_serializer

    def validate_data(self, input_data):
        super().validate_data(input_data)
        if type(input_data) != list:
            raise SerializationError("Data is not a list")

    def transform_data(self, input_data):
        input_data = super().transform_data(input_data)
        result = [self._items_serializer.serialize(item) for item in input_data]
        return result


class StringSerializer(BaseSerializer):
    def validate_data(self, input_data):
        super().validate_data(input_data)
        if type(input_data) != str:
            raise SerializationError("Data is not a string")


class IntegerSerializer(BaseSerializer):
    def validate_data(self, input_data):
        super().validate_data(input_data)
        if type(input_data) != int:
            raise SerializationError("Data is not a integer")


class BooleanSerializer(BaseSerializer):
    def validate_data(self, input_data):
        super().validate_data(input_data)
        if type(input_data) != bool:
            raise SerializationError("Data is not a boolean")


class TimeSerializer(StringSerializer):
    def transform_data(self, input_data):
        input_data = super().transform_data(input_data)
        try:
            input_data = datetime.strptime(input_data, "%H:%M").time()
        except Exception:
            raise SerializationError("Data not have the format H:M")
        return input_data


class DateSerializer(StringSerializer):
    def transform_data(self, input_data):
        input_data = super().transform_data(input_data)
        try:
            input_data = datetime.strptime(input_data, "%Y-%m-%d").date()
        except Exception:
            raise SerializationError("Data not have the format Y-M-D")
        return input_data


class EnumSerializer(StringSerializer):
    def __init__(self, enum_item: Type[Enum], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum_item = enum_item

    def validate_data(self, input_data):
        super().validate_data(input_data)
        choices = [enum_option.value for enum_option in self._enum_item]
        if input_data not in choices:
            raise SerializationError(
                f"Data is not an available option, options are {','.join(choices)}"
            )

    def transform_data(self, input_data):
        input_data = super().transform_data(input_data)
        input_data = self._enum_item(input_data)
        return input_data
